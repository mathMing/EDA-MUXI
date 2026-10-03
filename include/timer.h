#pragma once

#include "common.h"

class Timer {
public:
    Timer() { reset(); }

    void reset() {
        start_time_ = std::chrono::high_resolution_clock::now();
        stopped_ = false;
    }

    // PATCH debug-mode H1: Timer 缺 start()/stop() 接口，与 GpuTimer 对称
    // start() = reset 时间戳并清除 stopped 标志
    // stop() 仅记录结束时刻，elapsed_ms 仍基于 start_time 计算
    void start() { reset(); }
    void stop() {
        stop_time_ = std::chrono::high_resolution_clock::now();
        stopped_ = true;
    }

    double elapsed_ms() const {
        auto end_time = stopped_ ? stop_time_
                                : std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> duration = end_time - start_time_;
        return duration.count();
    }

    double elapsed_us() const {
        auto end_time = stopped_ ? stop_time_
                                : std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::micro> duration = end_time - start_time_;
        return duration.count();
    }

    double elapsed_s() const {
        return elapsed_ms() / 1000.0;
    }

private:
    std::chrono::time_point<std::chrono::high_resolution_clock> start_time_;
    std::chrono::time_point<std::chrono::high_resolution_clock> stop_time_;
    bool stopped_ = false;
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
