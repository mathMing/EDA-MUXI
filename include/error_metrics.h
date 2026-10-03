#pragma once
/**
 * @file   error_metrics.h
 * @brief  精度评测指标定义（误差范数与通过门限）
 *
 * ## 精度指标定义
 *
 * 本模块提供稀疏线性求解器的精度评测指标，遵循赛题七 S1 评分标准：
 *
 *  1. **L2 相对误差** (compute_l2_relative_error)
 *     $$\text{rel\_err} = \frac{\|x_{\text{gpu}} - x_{\text{ref}}\|_2}{\|x_{\text{ref}}\|_2}$$
 *     - 通过门限：≤ 1e-6（S1 满分标准）
 *     - 分母用 \|x_ref\|_2 而非 \|b\|_2，避免分母为零或极小
 *
 *  2. **最大绝对误差** (compute_max_absolute_error)
 *     $$\text{max\_err} = \max_i |x_{\text{gpu}}[i] - x_{\text{ref}}[i]|$$
 *     - 用于定位最差分量，辅助调试
 *
 *  3. **残差检验** (compute_relative_residual, 在 sparse_matrix.h 中)
 *     $$\text{res} = \frac{\|A \cdot x_{\text{gpu}} - b\|_2}{\|b\|_2}$$
 *     - 独立于参考解，提供绝对质量判断
 *
 * @note  所有计算使用 IEEE 754 双精度（double），无精度降级
 * @author EDA-MUXI 战队
 * @date   2026-10-03
 */

#include "common.h"

/**
 * @struct ErrorReport
 * @brief  精度评测汇总报告
 *
 * 包含 L2 相对误差、最大绝对误差、残差范数以及通过门限的布尔判定。
 */
struct ErrorReport {
    real_t l2_relative_error;    ///< L2 相对误差 \|x_gpu - x_ref\|_2 / \|x_ref\|_2
    real_t max_absolute_error;   ///< 最大绝对误差 max_i |x_gpu[i] - x_ref[i]|
    real_t residual_norm;       ///< 残差范数 \|A @ x_gpu - b\|_2 / \|b\|_2（备用）
    bool   passed_accuracy_test; ///< true 当且仅当 l2_relative_error ≤ threshold（默认 1e-6）
};

/**
 * @class  ErrorMetrics
 * @brief  精度评测工具集
 *
 * 提供 L2 范数、L2 相对误差、最大绝对误差的计算函数，
 * 以及统一的 evaluate() 接口生成 ErrorReport。
 */
class ErrorMetrics {
public:
    /**
     * @brief 计算向量的 L2 范数（Euclidean norm）
     * @param vec 输入向量
     * @return     \|\vec{v}\|_2 = \sqrt{\sum v_i^2}
     *
     * @note  O(n) 时间复杂度，无数值稳定性问题（IEEE 754 double）
     */
    static real_t compute_l2_norm(const std::vector<real_t>& vec) {
        real_t sum = 0.0;
        for (real_t v : vec) {
            sum += v * v;
        }
        return std::sqrt(sum);
    }

    /**
     * @brief 计算 L2 相对误差
     *
     * $$\text{rel\_err} = \frac{\|x - x_{\text{ref}}\|_2}{\|x_{\text{ref}}\|_2}$$
     *
     * @param x     GPU 求解得到的近似解
     * @param x_ref 参考解（KLU 或精确解）
     * @return      相对误差标量
     *
     * @throws std::invalid_argument 当两向量长度不一致或为空
     *
     * @note  当 \|x_ref\|_2 < 1e-15 时退化为 L2 绝对误差（避免除零）
     */
    static real_t compute_l2_relative_error(const std::vector<real_t>& x,
                                            const std::vector<real_t>& x_ref) {
        if (x.size() != x_ref.size() || x.empty()) {
            throw std::invalid_argument("Vector sizes do not match or are empty");
        }
        real_t diff_norm_sq = 0.0;
        real_t ref_norm_sq  = 0.0;
        for (size_t i = 0; i < x.size(); ++i) {
            real_t diff = x[i] - x_ref[i];
            diff_norm_sq += diff * diff;
            ref_norm_sq  += x_ref[i] * x_ref[i];
        }
        real_t ref_norm = std::sqrt(ref_norm_sq);
        if (ref_norm < 1e-15) {
            // \|x_ref\|_2 极小时退化为绝对误差，避免分母为零
            return std::sqrt(diff_norm_sq);
        }
        return std::sqrt(diff_norm_sq) / ref_norm;
    }

    /**
     * @brief 计算最大绝对误差
     *
     * $$\text{max\_err} = \max_i |x[i] - x_{\text{ref}}[i]|$$
     *
     * @param x     GPU 近似解
     * @param x_ref 参考解
     * @return      最大分量绝对误差
     *
     * @note  用于定位最差分量，辅助诊断精度问题
     */
    static real_t compute_max_absolute_error(const std::vector<real_t>& x,
                                             const std::vector<real_t>& x_ref) {
        if (x.size() != x_ref.size()) return -1.0;
        real_t max_err = 0.0;
        for (size_t i = 0; i < x.size(); ++i) {
            real_t err = std::abs(x[i] - x_ref[i]);
            if (err > max_err) {
                max_err = err;
            }
        }
        return max_err;
    }

    /**
     * @brief 统一精度评测接口
     *
     * @param x         GPU 近似解
     * @param x_ref     参考解
     * @param threshold 精度门限（默认 1e-6，赛题 S1 官方标准）
     * @return          包含所有指标的 ErrorReport 结构体
     *
     * @note  residual_norm 字段在此函数中未填充，由调用方在 CSRMatrix 中填入
     */
    static ErrorReport evaluate(const std::vector<real_t>& x,
                               const std::vector<real_t>& x_ref,
                               real_t threshold = 1e-6) {
        ErrorReport report;
        report.l2_relative_error = compute_l2_relative_error(x, x_ref);
        report.max_absolute_error = compute_max_absolute_error(x, x_ref);
        report.residual_norm = 0.0;  // 由 CSRMatrix::compute_relative_residual() 填充
        report.passed_accuracy_test = (report.l2_relative_error <= threshold);
        return report;
    }
};
