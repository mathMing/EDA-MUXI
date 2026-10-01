#pragma once

#include "common.h"
#include "sparse_matrix.h"

// ==============================================================================
// 2026 中国研究生创芯大赛·EDA 精英挑战赛 — 赛题七
// 任务一：沐曦 GPU 异构稀疏 LU 数值求解器接口声明 (MetaX GPU Sparse LU Solver)
// 适配 MetaX MXMACA (maccc) 与 NVIDIA CUDA (nvcc) 双编译器生态
// ==============================================================================

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief 执行 GPU 稀疏矩阵数值分解与三角求解管线
 * 
 * @param n           矩阵阶数 (维度)
 * @param nnz         非零元总数
 * @param row_ptr     CSR 行偏移指针数组
 * @param col_idx     CSR 列索引数组
 * @param values      CSR 矩阵非零元素值数组
 * @param b           右端常数项向量数组
 * @param x           解向量输出数组
 * @param sym_time_ms 输出参数：符号分析及数据准备耗时统计 (ms)
 * @param num_time_ms 输出参数：GPU 数值分解与内核求解耗时统计 (ms)
 * @return int        执行状态码 (0: 成功, 非0: 运行时异常)
 */
int gpu_numeric_lu_solve(index_t n,
                         index_t nnz,
                         const index_t* row_ptr,
                         const index_t* col_idx,
                         const real_t* values,
                         const real_t* b,
                         real_t* x,
                         double* sym_time_ms,
                         double* num_time_ms);

#ifdef __cplusplus
}
#endif
