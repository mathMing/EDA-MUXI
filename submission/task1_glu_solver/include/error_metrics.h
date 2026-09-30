#pragma once

#include "common.h"

struct ErrorReport {
    real_t l2_relative_error;
    real_t max_absolute_error;
    real_t residual_norm;
    bool passed_accuracy_test; // rel_err <= 1e-6
};

class ErrorMetrics {
public:
    static real_t compute_l2_norm(const std::vector<real_t>& vec) {
        real_t sum = 0.0;
        for (real_t v : vec) {
            sum += v * v;
        }
        return std::sqrt(sum);
    }

    static real_t compute_l2_relative_error(const std::vector<real_t>& x, const std::vector<real_t>& x_ref) {
        if (x.size() != x_ref.size() || x.empty()) {
            throw std::invalid_argument("Vector sizes do not match or are empty");
        }
        real_t diff_norm_sq = 0.0;
        real_t ref_norm_sq = 0.0;
        for (size_t i = 0; i < x.size(); ++i) {
            real_t diff = x[i] - x_ref[i];
            diff_norm_sq += diff * diff;
            ref_norm_sq += x_ref[i] * x_ref[i];
        }
        real_t ref_norm = std::sqrt(ref_norm_sq);
        if (ref_norm < 1e-15) {
            return std::sqrt(diff_norm_sq);
        }
        return std::sqrt(diff_norm_sq) / ref_norm;
    }

    static real_t compute_max_absolute_error(const std::vector<real_t>& x, const std::vector<real_t>& x_ref) {
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

    static ErrorReport evaluate(const std::vector<real_t>& x, const std::vector<real_t>& x_ref, real_t threshold = 1e-6) {
        ErrorReport report;
        report.l2_relative_error = compute_l2_relative_error(x, x_ref);
        report.max_absolute_error = compute_max_absolute_error(x, x_ref);
        report.residual_norm = 0.0; // To be populated with SpMV if needed
        report.passed_accuracy_test = (report.l2_relative_error <= threshold);
        return report;
    }
};
