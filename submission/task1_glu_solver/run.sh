#!/usr/bin/env bash
# ==============================================================================
# 2026 中国研究生创芯大赛·EDA 精英挑战赛 — 赛题七
# 任务一构建与运行脚本
# 调用规约: bash run.sh [matrix_file]
# ==============================================================================

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# 1. 清理并重新构建
echo "=== [Task 1] Building GPU Sparse LU Solver (lu_cmd) ==="
rm -f src/*.o lu_cmd
make clean && make -j4

# 2. 若传入矩阵参数，则直接执行测试
if [ -n "$1" ]; then
    echo "=== Running Solver on Matrix: $1 ==="
    ./lu_cmd -i "$1" "${@:2}"
else
    echo "=== Build Complete! Usage: ./lu_cmd -i <matrix_csr.mtx> [-b <rhs.mtx>] [-r <ref.mtx>] ==="
fi
