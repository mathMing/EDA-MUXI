#!/usr/bin/env bash
# 一键运行全赛题综合自评评分程序 (Linux / Server)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "${SCRIPT_DIR}/eval/self_evaluation.py"
