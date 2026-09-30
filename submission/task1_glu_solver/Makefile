# ==============================================================================
# 2026 中国研究生创芯大赛·EDA 精英挑战赛 — 赛题七
# 任务一：基于沐曦 GPU 的大规模稀疏矩阵求解器 (GLU)
# ==============================================================================

CXX = nvcc
CXXFLAGS = -O3 -lineinfo -std=c++11 --expt-relaxed-constexpr
INCLUDES = -I./include -I/opt/hpcc/include
LDFLAGS = -L/opt/hpcc/lib64 -lcudart -lcusparse -lcublas

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
