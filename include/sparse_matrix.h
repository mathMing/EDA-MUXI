#pragma once

#include "common.h"

struct COOMatrix {
    index_t rows = 0;
    index_t cols = 0;
    index_t nnz = 0;
    std::vector<index_t> row_indices;
    std::vector<index_t> col_indices;
    std::vector<real_t> values;
};

struct CSCMatrix;

struct CSRMatrix {
    index_t rows = 0;
    index_t cols = 0;
    index_t nnz = 0;
    std::vector<index_t> row_ptr; // size = rows + 1
    std::vector<index_t> col_idx; // size = nnz
    std::vector<real_t> values;   // size = nnz

    // SpMV: y = A * x
    void spmv(const real_t* x, real_t* y) const {
        for (index_t r = 0; r < rows; ++r) {
            real_t sum = 0.0;
            index_t start = row_ptr[r];
            index_t end = row_ptr[r + 1];
            for (index_t i = start; i < end; ++i) {
                sum += values[i] * x[col_idx[i]];
            }
            y[r] = sum;
        }
    }

    void spmv(const std::vector<real_t>& x, std::vector<real_t>& y) const {
        if (static_cast<index_t>(x.size()) < cols) throw std::invalid_argument("x size < cols");
        y.assign(rows, 0.0);
        spmv(x.data(), y.data());
    }

    real_t compute_relative_residual(const std::vector<real_t>& x, const std::vector<real_t>& b) const {
        std::vector<real_t> ax(rows, 0.0);
        spmv(x, ax);
        real_t diff_sq = 0.0;
        real_t b_sq = 0.0;
        for (index_t i = 0; i < rows; ++i) {
            real_t diff = ax[i] - b[i];
            diff_sq += diff * diff;
            b_sq += b[i] * b[i];
        }
        real_t b_norm = std::sqrt(b_sq);
        return (b_norm > 1e-15) ? (std::sqrt(diff_sq) / b_norm) : std::sqrt(diff_sq);
    }

    CSCMatrix to_csc() const;
};

struct CSCMatrix {
    index_t rows = 0;
    index_t cols = 0;
    index_t nnz = 0;
    std::vector<index_t> col_ptr; // size = cols + 1
    std::vector<index_t> row_idx; // size = nnz
    std::vector<real_t> values;   // size = nnz

    CSRMatrix to_csr() const;
};

class SparseMatrixIO {
public:
    static CSRMatrix read_matrix_market(const std::string& filepath);
    static void write_matrix_market(const std::string& filepath, const CSRMatrix& mat);
    static std::vector<real_t> read_vector(const std::string& filepath);
    static void write_vector(const std::string& filepath, const std::vector<real_t>& vec);
};
