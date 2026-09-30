#!/usr/bin/env bash
# ==============================================================================
# 2026 中国研究生创芯大赛·EDA 精英挑战赛 — 赛题七
# 任务二：4-GPU 16-Worker 批量模拟电路 Datasweep 并发仿真与对账脚本
# ==============================================================================

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "================================================================================"
echo "  [Task 2] Launching 4-GPU 16-Worker Datasweep Parallel Simulation Engine"
echo "================================================================================"

python3 scripts/eval_16w_batch.py

echo "=== Task 2 Execution and Verification Finished Successfully ==="
