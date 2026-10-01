# ==============================================================================
# 2026 中国研究生创芯大赛·EDA 精英挑战赛 — 赛题七
# 任务一：基于沐曦 GPU / 异构环境的稀疏矩阵求解器 (lu_cmd)
# ==============================================================================

# 自动自适应编译器探测: 优先支持 MACA/CUDA 工具链，通用平台回退到 g++
NVCC ?= $(shell which maccc 2>/dev/null || which nvcc 2>/dev/null)
CXX  ?= $(shell which g++ 2>/dev/null || which clang++ 2>/dev/null || echo g++)

CXXFLAGS = -O3 -std=c++11 -Wall -Wextra
INCLUDES = -I./include

# 适配沐曦 HPCC 软件栈
ifneq ($(wildcard /opt/hpcc/include),)
    INCLUDES += -I/opt/hpcc/include
endif
# 沐曦 C500 通过 cu-bridge 提供 CUDA 兼容运行时
ifneq ($(wildcard /home/eda260713/cu-bridge/CUDA_DIR/lib64/libcuda.so),)
    LDFLAGS += -L/home/eda260713/cu-bridge/CUDA_DIR/lib64 -lcuda
endif
# 仅在运行时库实际存在时链接 maca (避免服务器无 GPU 库时链接失败)
ifneq ($(wildcard /opt/hpcc/lib64/libmaca_runtime.so),)
    LDFLAGS += -L/opt/hpcc/lib64 -lmaca_runtime
endif

# 源文件与目标对象定义
CPP_SRCS = src/sparse_matrix.cpp src/lu_cmd.cpp
CU_SRCS  = src/numeric.cu

CPP_OBJS = $(CPP_SRCS:.cpp=.o)
CU_OBJS  = $(CU_SRCS:.cu=.o)

TARGET = lu_cmd

all: $(TARGET)

$(TARGET): $(CPP_OBJS) $(CU_OBJS)
ifneq ($(NVCC),)
	$(NVCC) $(CXXFLAGS) $(INCLUDES) -o $@ $(CPP_OBJS) $(CU_OBJS) $(LDFLAGS)
else
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $(CPP_OBJS) $(CU_OBJS) $(LDFLAGS)
endif

%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

%.o: %.cu
ifneq ($(NVCC),)
	$(NVCC) -O3 -std=c++11 $(INCLUDES) -c $< -o $@
else
	$(CXX) $(CXXFLAGS) -x c++ $(INCLUDES) -c $< -o $@
endif

clean:
	rm -f src/*.o $(TARGET)

.PHONY: all clean
