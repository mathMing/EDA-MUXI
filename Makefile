# ==============================================================================
# 2026 中国研究生创芯大赛·EDA 精英挑战赛 — 赛题七
# 任务一：基于沐曦 GPU / 异构环境的稀疏矩阵求解器 (lu_cmd)
# ==============================================================================

# 自动自适应编译器: 优先支持 MACA/CUDA 工具链，通用平台回退到 g++
CXX ?= $(shell which maccc 2>/dev/null || which nvcc 2>/dev/null || which g++ 2>/dev/null || echo g++)

CXXFLAGS = -O3 -std=c++11 -Wall
INCLUDES = -I./include

# 适配沐曦 HPCC 软件栈
ifneq ($(wildcard /opt/hpcc/include),)
    INCLUDES += -I/opt/hpcc/include
endif
ifneq ($(wildcard /opt/hpcc/lib64),)
    LDFLAGS += -L/opt/hpcc/lib64
endif

SRCS = src/sparse_matrix.cpp src/lu_cmd.cpp
OBJS = $(SRCS:.cpp=.o)
TARGET = lu_cmd

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $(OBJS) $(LDFLAGS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -f src/*.o $(TARGET)

.PHONY: all clean
