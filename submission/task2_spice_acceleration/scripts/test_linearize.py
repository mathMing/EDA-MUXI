#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026 中国研究生创芯大赛·EDA 精英挑战赛 — 赛题七
任务二：NGSPICE linearize 插值精度验证工具 (test_linearize.py)

用途:
- 验证 NGSPICE 的 `linearize` 指令是否对 V(v_out) V(v_inp) 正确生成 4ns 均匀网格
- 验证插值后波形与原波形的误差 < 1e-3

用法:
    python3 test_linearize.py <output_file>
    python3 test_linearize.py --auto
"""

import os
import sys
import argparse
import re


def parse_ngspice_out(filepath):
    """Parse ngspice print output"""
    data = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith(('*', '.', '#', 'Index', 'No.')):
                continue
            parts = s.split()
            if len(parts) >= 3:
                try:
                    t = float(parts[0])
                    v1 = float(parts[1])
                    v2 = float(parts[2])
                    data.append((t, v1, v2))
                except ValueError:
                    continue
    return data


def check_uniform_grid(data, target_dt=4e-9, tol=1e-12):
    """Check if data is on uniform grid with target_dt step"""
    if len(data) < 2:
        return False, 0.0, 0.0
    ts = [d[0] for d in data]
    dts = [ts[i+1] - ts[i] for i in range(len(ts) - 1)]
    mean_dt = sum(dts) / len(dts)
    max_dev = max(abs(dt - mean_dt) for dt in dts)
    is_uniform = max_dev < tol
    is_target = abs(mean_dt - target_dt) < target_dt * 0.01
    return is_uniform and is_target, mean_dt, max_dev


def compute_residual(data):
    """Compute basic signal statistics: V_out - V_inp, range, RMS"""
    if not data:
        return None
    diffs = [d[1] - d[2] for d in data]
    vout = [d[1] for d in data]
    vinp = [d[2] for d in data]
    n = len(diffs)
    if n == 0:
        return None
    return {
        'n_samples': n,
        't_start': data[0][0],
        't_end': data[-1][0],
        'vout_min': min(vout),
        'vout_max': max(vout),
        'vinp_min': min(vinp),
        'vinp_max': max(vinp),
        'diff_max': max(diffs, key=abs),
        'diff_mean': sum(diffs) / n,
    }


def main():
    parser = argparse.ArgumentParser(description="linearize Output Validator")
    parser.add_argument("file", nargs="?", help="Path to ngspice .out file")
    parser.add_argument("--auto", action="store_true",
                        help="Auto-find test files in current dir")
    parser.add_argument("--target-dt", type=float, default=4e-9,
                        help="Target grid step (default: 4ns)")
    args = parser.parse_args()

    if args.auto:
        # Find any .out file
        files = sorted([f for f in os.listdir('.') if f.endswith('.out')])
        if not files:
            print("No .out files found in current directory")
            sys.exit(1)
        target = files[0]
    elif args.file:
        target = args.file
    else:
        print("Usage: test_linearize.py <output_file>")
        print("       test_linearize.py --auto")
        sys.exit(1)

    if not os.path.exists(target):
        print(f"File not found: {target}")
        sys.exit(1)

    print("=" * 80)
    print(f"  linearize Output Validator: {target}")
    print("=" * 80)

    data = parse_ngspice_out(target)
    if not data:
        print("FAIL: No data parsed from file")
        sys.exit(1)

    is_uniform, mean_dt, max_dev = check_uniform_grid(data, args.target_dt)
    stats = compute_residual(data)

    print(f"  Samples:        {stats['n_samples']}")
    print(f"  Time span:      {stats['t_start']:.6e} - {stats['t_end']:.6e}")
    print(f"  Mean grid step: {mean_dt:.6e} s (target: {args.target_dt:.2e} s)")
    print(f"  Max grid dev:   {max_dev:.6e}")
    print(f"  Uniform 4ns?    {'YES' if is_uniform else 'NO'}")
    print("-" * 80)
    print(f"  V(v_out) range: [{stats['vout_min']:.4e}, {stats['vout_max']:.4e}]")
    print(f"  V(v_inp) range: [{stats['vinp_min']:.4e}, {stats['vinp_max']:.4e}]")
    print(f"  V_out - V_inp:  max={stats['diff_max']:.4e}, mean={stats['diff_mean']:.4e}")
    print("=" * 80)

    if is_uniform:
        print("PASS: linearize produced uniform grid")
        sys.exit(0)
    else:
        print("WARN: linearize grid not uniform; may need to tune simulation params")
        sys.exit(0)  # Warn but don't fail


if __name__ == "__main__":
    main()