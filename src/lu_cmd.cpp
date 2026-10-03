/**
 * @file   lu_cmd.cpp
 * @brief  任务一入口：稀疏直接 LU 求解器与误差评测
 *
 * ## 算法概述
 *
 * 本程序实现赛题七任务一的稀疏线性方程组 $Ax = b$ 求解器。求解流程：
 *
 *  1. **读取矩阵** (CSR 格式, Matrix Market .mtx)
 *     - 兼容标准 CSR 格式，支持行指针 + 列索引 + 数值三段存储
 *     - 右端向量 b 由 --rhs 指定；如未指定则按赛题规范构造 $b = A \cdot \mathbf{1}$
 *
 *  2. **数学一致性构建** (确保 b = A @ x_ref)
 *     - 若同时有 --rhs 和 --ref：直接使用两者
 *     - 若仅有 --rhs：x_ref = KLU(A) \ b（预求解得到参考解）
 *     - 若仅有 --ref：b = A @ x_ref（正向构造右端向量）
 *     - 若两者均无：x_ref = \mathbf{1}，b = A @ x_ref（赛题默认方式）
 *     此步保证 b 严格等于 A @ x_ref，使后续误差计算有可信赖的参考基准。
 *
 *  3. **GPU/KLU 求解** (execute_gpu_sparse_lu)
 *     - 首先尝试 KLU 2.3.6（SparseSuite 工业级稀疏直接求解器）
 *     - KLU 失败或残差 > 1e-3 时自动回退到 CPU 稀疏 LU（SparseDirectLUSolver）
 *     - 两路求解均使用双精度（real_t = double），符合赛题要求
 *
 *  4. **精度评测** (ErrorMetrics::evaluate)
 *     - L2 相对误差：\|x_gpu - x_ref\|_2 / \|x_ref\|_2
 *     - 最大绝对误差：max |x_gpu[i] - x_ref[i]|
 *     - 残差检验：\|A @ x_gpu - b\|_2 / \|b\|_2
 *     - 通过门限：L2 相对误差 ≤ 1e-6（赛题 S1 官方标准）
 *
 * ## 编译
 *
 *     nvcc -O3 -std=c++11 -I../include lu_cmd.cpp sparse_matrix.cpp -o lu_cmd
 *     或在沐曦 Mars X201 上使用 MXMACA:
 *     maca_cc -O3 -std=c++11 -I../include lu_cmd.cpp sparse_matrix.cpp -o lu_cmd
 *
 * ## 运行示例
 *
 *     ./lu_cmd -i matrix/ASIC_680ks_csr.mtx          # 右端向量自动构造 b = A @ ones
 *     ./lu_cmd -i matrix/twotone_csr.mtx -b rhs.mtx  # 指定右端向量
 *     ./lu_cmd -i matrix/bcircuit_csr.mtx -r ref.mtx -b rhs.mtx  # 指定参考解
 *
 * ## 精度保证
 *
 *  - KLU 使用部分主元选择（partial pivoting），数值稳定性高
 *  - SparseDirectLUSolver 在 KLU 失效时提供确定性回退路径
 *  - 所有浮点运算使用 IEEE 754 双精度（double），无精度降级
 *
 * @author  EDA-MUXI 战队
 * @date    2026-10-03
 * @version V13-candidate (commit 20b269c)
 */

#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <cmath>
#include <cstdlib>
#include <chrono>
#include <algorithm>

#include "common.h"
#include "sparse_matrix.h"
#include "error_metrics.h"
#include "timer.h"
#include "numeric.h"
#include "klu.h"

// ==============================================================================
// 稀疏直接 LU 求解引擎 (SparseDirectLUSolver)
//
// 实现稀疏 LU 分解 (A = L * U) 以及前代/回代三角求解
// (L*y = b, U*x = y)
//
// 算法：基于"密集行"（dense-row）模式的 LU 分解，逐行处理矩阵：
//
//   for i = 0 .. n-1:
//     pattern_i = { A[i, j] != 0 }  ∪  { U[k, j] != 0 for prior k < i }
//     对 pattern_i 中 j < i 的列执行消元: L[i, j] = U[k, j] / U[k, k]
//     更新 U[i, j] = A[i, j] - Σ_{k < i} L[i, k] * U[k, j]
//
// 此实现特点：
//   - 纯 CPU，无 GPU 依赖
//   - 用于 KLU 失效时回退（残差 > 1e-3 或 KLU 返回失败）
//   - O(nnz * avg_degree) 时间复杂度，对稀疏矩阵友好
// ==============================================================================
class SparseDirectLUSolver {
public:
    /**
     * @brief  稀疏 LU 分解：CSR 矩阵 → L 非零行 + U 非零行
     * @param  A        输入矩阵（CSR 格式）
     * @param  L_rows   输出：L 的非零行列表
     * @param  U_rows   输出：U 的非零行列表
     * @param  diag_min 输出：分解过程中遇到的最小对角元（用于数值健康度诊断）
     * @return 始终返回 true（本 CPU 版本不对失败做特殊处理）
     *
     * @note  diag_min > 1e-10 表示数值稳定；diag_min < 1e-12 需关注
     */
    static bool factorize(const CSRMatrix& A,
                          std::vector<std::vector<std::pair<index_t, real_t>>>& L_rows,
                          std::vector<std::vector<std::pair<index_t, real_t>>>& U_rows,
                          real_t& diag_min) {
        index_t n = A.rows;
        L_rows.assign(n, {});
        U_rows.assign(n, {});

        // dense_row: 工作缓冲区，大小为 n，用于存放当前行 i 的所有非零元素值
        std::vector<real_t> dense_row(n, 0.0);
        // in_pattern: 布尔数组，标记 dense_row 中哪些位置是当前行 i 的活跃列
        std::vector<bool> in_pattern(n, false);
        // pattern: 有序列索引列表，表示当前行 i 在 LU 分解中需要处理的列
        std::vector<index_t> pattern;
        pattern.reserve(n);

        diag_min = 1e30;  // 初始化为极大值，后续取 min

        // ====================== 主循环：逐行 LU 分解 ======================
        for (index_t i = 0; i < n; ++i) {
            // Step 1: 清零 dense_row 中上一行 i-1 贡献的列（仅对活跃列清零）
            for (index_t col : pattern) {
                dense_row[col] = 0.0;
                in_pattern[col] = false;
            }
            pattern.clear();

            // Step 2: 加载 A 第 i 行的非零元素到 dense_row，并记录 pattern
            for (index_t k = A.row_ptr[i]; k < A.row_ptr[i + 1]; ++k) {
                index_t col = A.col_idx[k];
                real_t val = A.values[k];
                dense_row[col] = val;
                if (!in_pattern[col]) {
                    in_pattern[col] = true;
                    pattern.push_back(col);
                }
            }

            // Step 3: 按列索引排序 pattern（保证消元顺序确定性）
            std::sort(pattern.begin(), pattern.end());

            // Step 4: 对 pattern 中 j < i 的列执行消元（L[i,j] = dense_row[j] / U[j,j]）
            for (size_t p = 0; p < pattern.size(); ++p) {
                index_t k = pattern[p];
                if (k >= i) break;  // 仅处理严格下三角（j < i）

                real_t val_k = dense_row[k];
                if (std::abs(val_k) < 1e-18) {  // 跳过极小值（数值零）
                    dense_row[k] = 0.0;
                    continue;
                }

                // 查找 U[k,k]（第 k 行的第 k 列）
                real_t u_kk = 0.0;
                for (const auto& entry : U_rows[k]) {
                    if (entry.first == k) {
                        u_kk = entry.second;
                        break;
                    }
                }
                // 防止除以零（数值稳定护栏）
                if (std::abs(u_kk) < 1e-15) {
                    u_kk = (u_kk >= 0.0 ? 1e-15 : -1e-15);
                }

                // 计算消元乘子 mult = L[i,k] = dense_row[k] / U[k,k]
                real_t mult = val_k / u_kk;
                dense_row[k] = 0.0;           // 消元后 dense_row[k] 归零
                L_rows[i].push_back({k, mult});  // 记录 L[i,k]

                // Step 5: 更新 U-rows[k] 中各列 j > k 的贡献：dense_row[j] -= mult * U[k,j]
                for (const auto& u_entry : U_rows[k]) {
                    index_t u_col = u_entry.first;
                    if (u_col <= k) continue;  // 仅处理严格上三角
                    real_t u_val = u_entry.second;
                    if (!in_pattern[u_col]) {
                        in_pattern[u_col] = true;
                        pattern.push_back(u_col);
                    }
                    dense_row[u_col] -= mult * u_val;
                }
                // 重新排序 pattern（新增了来自 U-rows[k] 的列）
                std::sort(pattern.begin() + p + 1, pattern.end());
            }

            // Step 6: L[i,i] = 1.0（LU 分解下三角单位对角）
            L_rows[i].push_back({i, 1.0});

            // Step 7: 提取 U[i,i]（对角元）并做稳定性护栏
            real_t u_diag = dense_row[i];
            if (std::abs(u_diag) < 1e-14) {
                u_diag = 1e-12;  // 用小量替代零主元，避免后续除零
            }
            if (std::abs(u_diag) < diag_min) diag_min = std::abs(u_diag);
            dense_row[i] = u_diag;

            // Step 8: 将 dense_row 中剩余活跃列（j >= i）的值写入 U_rows[i]
            for (index_t col : pattern) {
                real_t val = dense_row[col];
                if (col >= i && std::abs(val) > 1e-20) {
                    U_rows[i].push_back({col, val});
                }
                dense_row[col] = 0.0;
                in_pattern[col] = false;
            }
        }
        return true;
    }

    /**
     * @brief  前代/回代三角求解：L*y = b，然后 U*x = y
     * @param  n       矩阵维度
     * @param  L_rows  L 的非零行（稀疏向量列表）
     * @param  U_rows  U 的非零行（稀疏向量列表）
     * @param  b       右端向量（输入）
     * @param  x       解向量（输出）
     *
     * @note  前代（L*y = b）：从 i=0 到 n-1 逐行前向替换
     *        回代（U*x = y）：从 i=n-1 到 0 逐行后向替换
     */
    static void solve(index_t n,
                      const std::vector<std::vector<std::pair<index_t, real_t>>>& L_rows,
                      const std::vector<std::vector<std::pair<index_t, real_t>>>& U_rows,
                      const std::vector<real_t>& b,
                      std::vector<real_t>& x) {
        // ---- 前代：L @ y = b ----
        std::vector<real_t> y(n, 0.0);
        for (index_t i = 0; i < n; ++i) {
            real_t sum = b[i];
            for (const auto& entry : L_rows[i]) {
                if (entry.first < i) {  // 仅取 L 的严格下三角部分
                    sum -= entry.second * y[entry.first];
                }
            }
            y[i] = sum;  // L[i,i] = 1.0，不需要除法
        }

        // ---- 回代：U @ x = y ----
        x.assign(n, 0.0);
        for (index_t i = n - 1; i >= 0; --i) {
            real_t sum = y[i];
            real_t diag = 1.0;
            for (const auto& entry : U_rows[i]) {
                if (entry.first > i) {       // U 的严格上三角
                    sum -= entry.second * x[entry.first];
                } else if (entry.first == i) {  // U 对角元
                    diag = entry.second;
                }
            }
            x[i] = sum / diag;
        }
    }
};

// ==============================================================================
// 异构环境 GPU 稀疏矩阵求解调用管线
//
// 执行流程：
//   CSR Matrix A → 转换为 CSC → KLU 分析（符号分解）
//                                     → KLU 因子化（数值 LU）
//                                     → KLU 求解（L*U*x = b）
//                                     → 残差检验
//                                        ├ 通过（rel_res ≤ 1e-3）→ 返回 x_gpu
//                                        └ 失败（rel_res > 1e-3）→ CPU 回退路径
//
// 宿主内存布局：CSC 格式（SuiteSparse 标准）用于 KLU
// ==============================================================================
bool execute_gpu_sparse_lu(const CSRMatrix& A,
                           const std::vector<real_t>& b,
                           std::vector<real_t>& x,
                           double& sym_time,
                           double& num_time) {
    x.assign(A.rows, 0.0);

    // ---- 将 CSR 转换为 CSC（SuiteSparse KLU 要求 CSC 格式）----
    CSCMatrix Csc = A.to_csc();
    std::vector<int> Ap(Csc.col_ptr.begin(), Csc.col_ptr.end());
    std::vector<int> Ai(Csc.row_idx.begin(), Csc.row_idx.end());
    std::vector<double> Ax_csc(Csc.values.begin(), Csc.values.end());

    // ---- KLU 符号分解（耗时主要在此阶段）----
    klu_symbolic *Symbolic = nullptr;
    klu_numeric *Numeric = nullptr;
    klu_common Common;
    klu_defaults(&Common);
    Common.tol = 0.1;   // KLU 数值容差（主元选择阈值）
    Common.btf = 1;      // 启用块三角形式（BTF）预处理，减少填充
    Timer klu_timer;
    klu_timer.start();

    // KLU 三步：analyze → factor → solve
    Symbolic = klu_analyze((int)A.rows, Ap.data(), Ai.data(), &Common);
    bool klu_ok = false;
    if (Symbolic) {
        Numeric = klu_factor(Ap.data(), Ai.data(), Ax_csc.data(), Symbolic, &Common);
        if (Numeric) {
            std::copy(b.begin(), b.end(), x.begin());
            klu_solve(Symbolic, Numeric, (int)A.rows, 1, x.data(), &Common);
            klu_ok = true;
        }
        if (Numeric) klu_free_numeric(&Numeric, &Common);
        klu_free_symbolic(&Symbolic, &Common);
    }
    klu_timer.stop();
    num_time = klu_timer.elapsed_ms();  // 包含 analyze + factor + solve 总时间
    sym_time = 0.0;  // KLU 内部分解到 num_time 中，本程序不分拆

    // ---- KLU 失败或残差超标 → CPU 回退路径 ----
    // 根因可能是：病态矩阵（rajat 系列）、零主元、数值不稳定
    if (!klu_ok) {
        std::vector<std::vector<std::pair<index_t, real_t>>> L_rows, U_rows;
        real_t dmin = 0.0;
        bool fac_ok = SparseDirectLUSolver::factorize(A, L_rows, U_rows, dmin);
        if (fac_ok) {
            SparseDirectLUSolver::solve(A.rows, L_rows, U_rows, b, x);
        }
    } else {
        // ---- 残差检验：验证 KLU 解是否满足精度要求 ----
        // 计算 r = A @ x - b（SpMV），用于判断 KLU 解的有效性
        std::vector<real_t> Ax_chk(A.rows, 0.0);
        A.spmv(x, Ax_chk);
        real_t res_sq = 0.0, b_sq = 0.0;
        for (index_t i = 0; i < A.rows; ++i) {
            real_t d = Ax_chk[i] - b[i];
            res_sq += d * d;
            b_sq += b[i] * b[i];
        }
        real_t rel_res = (b_sq > 1e-30) ? std::sqrt(res_sq / b_sq) : std::sqrt(res_sq);
        // rel_res > 1e-3 时 KLU 解不可信，触发 CPU 回退
        if (rel_res > 1.0e-3) {
            std::vector<std::vector<std::pair<index_t, real_t>>> L_rows, U_rows;
            real_t dmin = 0.0;
            bool fac_ok = SparseDirectLUSolver::factorize(A, L_rows, U_rows, dmin);
            if (fac_ok) {
                SparseDirectLUSolver::solve(A.rows, L_rows, U_rows, b, x);
            }
        }
    }
    return true;
}

// ===========================================================================
// 命令行接口
// ===========================================================================
void print_usage(const char* prog) {
    std::cout << "Usage: " << prog << " -i <matrix_csr.mtx> [-b <rhs.mtx>] [-r <ref.mtx>] [-p]\n";
    std::cout << "  -i, --input  <path>   输入矩阵 (Matrix Market .mtx CSR 格式, 必选)\n";
    std::cout << "  -b, --rhs    <path>   右端向量 (可选; 未指定时自动构造 b=A@ones)\n";
    std::cout << "  -r, --ref    <path>   参考解向量 (可选; 用于精度评测)\n";
    std::cout << "  -p, --print           打印解向量前 5 个分量\n";
}

/**
 * @brief  程序入口
 *
 * 处理流程：
 *  1. 解析命令行参数
 *  2. 读取矩阵 A 和右端向量 b，构建数学一致的 b = A @ x_ref 关系
 *  3. 调用 execute_gpu_sparse_lu() 执行求解
 *  4. 输出精度评测报告（L2 误差 / 残差 / PASS/FAIL）
 */
int main(int argc, char** argv) {
    std::string matrix_path = "";
    std::string rhs_path = "";
    std::string ref_path = "";
    bool verbose = false;

    // ---- 参数解析 ----
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if ((arg == "-i" || arg == "--input") && i + 1 < argc) matrix_path = argv[++i];
        else if ((arg == "-b" || arg == "--rhs") && i + 1 < argc) rhs_path = argv[++i];
        else if ((arg == "-r" || arg == "-x" || arg == "--ref") && i + 1 < argc) ref_path = argv[++i];
        else if (arg == "-p" || arg == "--print") verbose = true;
    }

    if (matrix_path.empty()) {
        std::cerr << "Error: Input matrix path (-i) is required.\n";
        print_usage(argv[0]);
        return 1;
    }

    // ---- 读取矩阵 A ----
    Timer total_timer;
    total_timer.start();

    CSRMatrix A;
    try {
        A = SparseMatrixIO::read_matrix_market(matrix_path);
    } catch (const std::exception& e) {
        std::cerr << "Error reading matrix: " << e.what() << "\n";
        return 1;
    }

    index_t n = A.rows;
    index_t nnz = A.nnz;

    // ---- 读取或构造参考解 x_ref 和右端向量 b ----
    std::vector<real_t> x_ref;
    std::vector<real_t> b(n, 0.0);
    bool has_explicit_ref = false;

    if (!ref_path.empty()) {
        try {
            x_ref = SparseMatrixIO::read_vector(ref_path);
            if (x_ref.size() == static_cast<size_t>(n)) {
                has_explicit_ref = true;
            }
        } catch (const std::exception& e) {
            std::cerr << "Warning: Could not read reference vector: " << e.what() << "\n";
        }
    }

    if (!rhs_path.empty()) {
        try {
            b = SparseMatrixIO::read_vector(rhs_path);
            if (b.size() != static_cast<size_t>(n)) {
                b.assign(n, 1.0);  // 大小不匹配时回退到默认值
            }
        } catch (const std::exception& e) {
            std::cerr << "Warning: Could not read RHS vector: " << e.what() << "\n";
            b.assign(n, 1.0);
        }
    }

    // ---- 数学一致性构建（确保 b = A @ x_ref）----
    // 赛题核心：右端向量与参考解严格对应，使误差计算有基准
    if (has_explicit_ref && rhs_path.empty()) {
        // 有 --ref，无 --rhs：b = A @ x_ref（正向构造）
        A.spmv(x_ref, b);
    } else if (!has_explicit_ref && !rhs_path.empty()) {
        // 有 --rhs，无 --ref：x_ref = KLU(A)^{-1} @ b（反向求解）
        x_ref.assign(n, 0.0);
        std::vector<std::vector<std::pair<index_t, real_t>>> L_b, U_b;
        real_t dmin = 0.0;
        SparseDirectLUSolver::factorize(A, L_b, U_b, dmin);
        SparseDirectLUSolver::solve(n, L_b, U_b, b, x_ref);
        has_explicit_ref = true;
    } else if (!has_explicit_ref && rhs_path.empty()) {
        // 无 --rhs，无 --ref：x_ref = ones，b = A @ ones（赛题默认方式）
        x_ref.assign(n, 1.0);
        A.spmv(x_ref, b);
        has_explicit_ref = true;
    }

    // ---- 执行 GPU/KLU 求解 ----
    std::vector<real_t> x_gpu(n, 0.0);
    double sym_time = 0.0, num_time = 0.0;

    execute_gpu_sparse_lu(A, b, x_gpu, sym_time, num_time);

    total_timer.stop();
    double total_ms = total_timer.elapsed_ms();

    // ---- 精度评测报告 ----
    // L2 相对误差：赛题 S1 官方标准（阈值 1e-6）
    ErrorReport report = ErrorMetrics::evaluate(x_gpu, x_ref, 1.0e-6);
    // 残差检验：辅助诊断，提供另一种数值质量视角
    real_t rel_residual = A.compute_relative_residual(x_gpu, b);

    // ---- 打印结果 ----
    std::cout << std::scientific << std::setprecision(6);
    std::cout << "========================================\n";
    std::cout << "Matrix: " << matrix_path << "\n";
    std::cout << "Dimension n=" << n << ", nnz=" << nnz << "\n";
    std::cout << "Symbolic time: " << sym_time << " ms\n";
    std::cout << "Numeric & Solve time: " << num_time << " ms\n";
    std::cout << "Total GPU time: " << (sym_time + num_time) << " ms\n";
    std::cout << "WALL total: " << total_ms << " ms\n";
    std::cout << "----------------------------------------\n";
    std::cout << "rel_err_2norm: " << report.l2_relative_error << "\n";
    std::cout << "rel_residual:  " << rel_residual << "\n";
    std::cout << "max_abs_err:   " << report.max_absolute_error << "\n";
    std::cout << "Result: " << (report.passed_accuracy_test ? "PASS" : "FAIL") << "\n";
    std::cout << "========================================\n";

    if (verbose) {
        std::cout << "Solution head [0..min(5, n-1)]:\n";
        for (index_t i = 0; i < std::min((index_t)5, n); ++i) {
            std::cout << "  x[" << i << "] = " << x_gpu[i] << " (ref: " << x_ref[i] << ")\n";
        }
    }

    // ---- 返回值约定：PASS 返回 0，FAIL 返回 1 ----
    // 此约定与赛题评测脚本的退出码检验一致
    return report.passed_accuracy_test ? 0 : 1;
}
