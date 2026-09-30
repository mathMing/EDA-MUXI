#pragma once

#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <cstdint>
#include <chrono>
#include <algorithm>
#include <stdexcept>
#include <fstream>
#include <sstream>
#include <iomanip>

// Compatibility macros for CUDA and MetaX MXMACA
#if defined(__MACA__) || defined(__MXMACA__)
    #include <maca_runtime.h>
    #define GPU_HOST __host__
    #define GPU_DEVICE __device__
    #define GPU_GLOBAL __global__
    #define GPU_INLINE __forceinline__
    #define WARP_SIZE 32
#elif defined(__CUDACC__)
    #include <cuda_runtime.h>
    #define GPU_HOST __host__
    #define GPU_DEVICE __device__
    #define GPU_GLOBAL __global__
    #define GPU_INLINE __forceinline__
    #define WARP_SIZE 32
#else
    #define GPU_HOST
    #define GPU_DEVICE
    #define GPU_GLOBAL
    #define GPU_INLINE inline
    #define WARP_SIZE 32
#endif

// Precision definition: Default double precision for circuit MNA simulation
using real_t = double;
using index_t = int32_t;

// GPU Error Checking Macro
#if defined(__CUDACC__) || defined(__MACA__) || defined(__MXMACA__)
#define CHECK_GPU_ERROR(val) check_gpu((val), #val, __FILE__, __LINE__)
inline void check_gpu(cudaError_t result, const char *const func, const char *const file, const int line) {
    if (result != cudaSuccess) {
        std::cerr << "GPU Runtime Error at " << file << ":" << line << " code=" << result 
                  << " \"" << cudaGetErrorString(result) << "\" in " << func << std::endl;
        throw std::runtime_error("GPU runtime error");
    }
}
#else
#define CHECK_GPU_ERROR(val) ((void)0)
#endif
