#include "sparse_matrix.h"
#include <map>

CSCMatrix CSRMatrix::to_csc() const {
    CSCMatrix csc;
    csc.rows = rows;
    csc.cols = cols;
    csc.nnz = nnz;
    csc.col_ptr.assign(cols + 1, 0);
    csc.row_idx.resize(nnz);
    csc.values.resize(nnz);

    // Count entries per column
    for (index_t i = 0; i < nnz; ++i) {
        csc.col_ptr[col_idx[i] + 1]++;
    }

    // Cumulative sum
    for (index_t c = 0; c < cols; ++c) {
        csc.col_ptr[c + 1] += csc.col_ptr[c];
    }

    // Work offsets
    std::vector<index_t> offset = csc.col_ptr;

    // Distribute entries
    for (index_t r = 0; r < rows; ++r) {
        for (index_t i = row_ptr[r]; i < row_ptr[r + 1]; ++i) {
            index_t c = col_idx[i];
            index_t dest = offset[c]++;
            csc.row_idx[dest] = r;
            csc.values[dest] = values[i];
        }
    }

    return csc;
}

CSRMatrix CSCMatrix::to_csr() const {
    CSRMatrix csr;
    csr.rows = rows;
    csr.cols = cols;
    csr.nnz = nnz;
    csr.row_ptr.assign(rows + 1, 0);
    csr.col_idx.resize(nnz);
    csr.values.resize(nnz);

    // Count entries per row
    for (index_t i = 0; i < nnz; ++i) {
        csr.row_ptr[row_idx[i] + 1]++;
    }

    // Cumulative sum
    for (index_t r = 0; r < rows; ++r) {
        csr.row_ptr[r + 1] += csr.row_ptr[r];
    }

    // Work offsets
    std::vector<index_t> offset = csr.row_ptr;

    // Distribute entries
    for (index_t c = 0; c < cols; ++c) {
        for (index_t i = col_ptr[c]; i < col_ptr[c + 1]; ++i) {
            index_t r = row_idx[i];
            index_t dest = offset[r]++;
            csr.col_idx[dest] = c;
            csr.values[dest] = values[i];
        }
    }

    return csr;
}

CSRMatrix SparseMatrixIO::read_matrix_market(const std::string& filepath) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open Matrix Market file: " + filepath);
    }

    std::string line;
    // Read header line
    if (!std::getline(file, line)) {
        throw std::runtime_error("Empty Matrix Market file: " + filepath);
    }

    // Check header
    if (line.find("%%MatrixMarket") == std::string::npos) {
        throw std::runtime_error("Invalid Matrix Market header in: " + filepath);
    }

    bool is_skew_symmetric = (line.find("skew-symmetric") != std::string::npos);
    bool is_symmetric = (!is_skew_symmetric && line.find("symmetric") != std::string::npos);

    // Skip comment lines
    while (std::getline(file, line)) {
        if (line.empty() || line[0] == '%') continue;
        break;
    }

    std::stringstream ss(line);
    index_t num_rows = 0, num_cols = 0, num_entries = 0;
    if (!(ss >> num_rows >> num_cols >> num_entries)) {
        throw std::runtime_error("Failed to parse matrix dimensions: " + line);
    }

    // Read entries into a map to automatically sort and sum duplicate entries
    std::vector<std::map<index_t, real_t>> row_entries(num_rows);

    for (index_t k = 0; k < num_entries; ++k) {
        index_t r = 0, c = 0;
        real_t val = 0.0;
        if (!(file >> r >> c >> val)) {
            break;
        }
        // 1-based to 0-based
        r -= 1;
        c -= 1;
        if (r >= 0 && r < num_rows && c >= 0 && c < num_cols) {
            row_entries[r][c] += val;
            if (is_symmetric && r != c) {
                row_entries[c][r] += val;
            } else if (is_skew_symmetric && r != c) {
                row_entries[c][r] -= val;
            }
        }
    }

    // Assemble CSR
    CSRMatrix csr;
    csr.rows = num_rows;
    csr.cols = num_cols;
    csr.row_ptr.assign(num_rows + 1, 0);

    index_t total_nnz = 0;
    for (index_t r = 0; r < num_rows; ++r) {
        total_nnz += static_cast<index_t>(row_entries[r].size());
        csr.row_ptr[r + 1] = total_nnz;
    }

    csr.nnz = total_nnz;
    csr.col_idx.resize(total_nnz);
    csr.values.resize(total_nnz);

    index_t idx = 0;
    for (index_t r = 0; r < num_rows; ++r) {
        for (const auto& kv : row_entries[r]) {
            csr.col_idx[idx] = kv.first;
            csr.values[idx] = kv.second;
            idx++;
        }
    }

    return csr;
}

void SparseMatrixIO::write_matrix_market(const std::string& filepath, const CSRMatrix& mat) {
    std::ofstream file(filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot write to file: " + filepath);
    }

    file << "%%MatrixMarket matrix coordinate real general\n";
    file << "% Created by Sparse GPU EDA Framework\n";
    file << mat.rows << " " << mat.cols << " " << mat.nnz << "\n";

    for (index_t r = 0; r < mat.rows; ++r) {
        for (index_t i = mat.row_ptr[r]; i < mat.row_ptr[r + 1]; ++i) {
            file << (r + 1) << " " << (mat.col_idx[i] + 1) << " " 
                 << std::scientific << std::setprecision(16) << mat.values[i] << "\n";
        }
    }
}

std::vector<real_t> SparseMatrixIO::read_vector(const std::string& filepath) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open vector file: " + filepath);
    }

    std::string line;
    // Check if it's matrix market format or plain numbers
    std::vector<real_t> vec;
    bool has_mm_header = false;
    bool in_data = false;
    index_t expected_size = 0;
    while (std::getline(file, line)) {
        if (line.empty()) continue;
        if (line[0] == '%') {
            if (line.find("%%MatrixMarket") != std::string::npos && line.find("array") != std::string::npos) {
                has_mm_header = true;
            }
            continue;
        }
        std::stringstream ss(line);
        if (has_mm_header && !in_data) {
            // MatrixMarket array format: "N M" (typically "N 1")
            index_t n = 0, m = 0;
            std::string extra;
            if ((ss >> n >> m) && !(ss >> extra) && n > 0 && m > 0) {
                expected_size = n * m;
                vec.reserve(expected_size);
                in_data = true;
                continue;
            }
            in_data = true;
            ss.clear();
            ss.str(line);
        }
        real_t val;
        while (ss >> val) {
            vec.push_back(val);
        }
    }

    return vec;
}

void SparseMatrixIO::write_vector(const std::string& filepath, const std::vector<real_t>& vec) {
    std::ofstream file(filepath);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot write vector file: " + filepath);
    }

    file << "%%MatrixMarket matrix array real general\n";
    file << vec.size() << " 1\n";
    for (real_t v : vec) {
        file << std::scientific << std::setprecision(16) << v << "\n";
    }
}
