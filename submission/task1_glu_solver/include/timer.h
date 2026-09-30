#pragma once

#include "common.h"

class Timer {
public:
    Timer() { reset(); }

    void reset() {
        start_time_ = std::chrono::high_resolution_clock::now();
        elapsed_ = 0.0;
        running_ = true;
    }

    void start() {
        start_time_ = std::chrono::high_resolution_clock::now();
        running_ = true;
    }

    void stop() {
        auto end_time = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> duration = end_time - start_time_;
        elapsed_ = duration.count();
        running_ = false;
    }

    double elapsed_ms() const {
        if (running_) {
            auto end_time = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double, std::milli> duration = end_time - start_time_;
            return duration.count();
        }
        return elapsed_;
    }

    double elapsed_us() const {
        auto end_time = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::micro> duration = end_time - start_time_;
        return duration.count();
    }

    double elapsed_s() const {
        return elapsed_ms() / 1000.0;
    }

private:
    std::chrono::time_point<std::chrono::high_resolution_clock> start_time_;
    double elapsed_ = 0.0;
    bool running_ = true;
};

#if defined(__CUDACC__) || defined(__MACA__) || defined(__MXMACA__)
class GpuTimer {
public:
    GpuTimer() {
        CHECK_GPU_ERROR(cudaEventCreate(&start_));
        CHECK_GPU_ERROR(cudaEventCreate(&stop_));
    }

    ~GpuTimer() {
        cudaEventDestroy(start_);
        cudaEventDestroy(stop_);
    }

    void start(cudaStream_t stream = 0) {
        CHECK_GPU_ERROR(cudaEventRecord(start_, stream));
    }

    void stop(cudaStream_t stream = 0) {
        CHECK_GPU_ERROR(cudaEventRecord(stop_, stream));
        CHECK_GPU_ERROR(cudaEventSynchronize(stop_));
    }

    float elapsed_ms() {
        float ms = 0.0f;
        CHECK_GPU_ERROR(cudaEventElapsedTime(&ms, start_, stop_));
        return ms;
    }

private:
    cudaEvent_t start_;
    cudaEvent_t stop_;
};
#endif
