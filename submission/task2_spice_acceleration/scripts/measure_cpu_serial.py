#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026 中国研究生创芯大赛·EDA 精英挑战赛 — 赛题七
任务二：官方标准 CPU 单线程串行基准耗时测定 (measure_cpu_serial.py)

用途:
- 测量 N 个网表在 ngspice CPU 单线程下的串行执行耗时
- 作为对照基准 (官方 10.01s @ 100 netlists)
- 用以计算加速比 (Speedup = T_serial / T_parallel)

用法:
    python3 measure_cpu_serial.py --netlist-dir <dir> [--num 10]
"""

import os
import sys
import time
import argparse
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(description="CPU Serial SPICE Benchmark")
    parser.add_argument("--netlist-dir", type=str, default=None,
                        help="Path to netlist directory")
    parser.add_argument("--ngspice-bin", type=str, default=None,
                        help="Path to ngspice binary")
    parser.add_argument("--num", type=int, default=None,
                        help="Limit number of netlists (default: all)")
    return parser.parse_args()


def auto_detect(netlist_dir, ngspice_bin):
    possible_dirs = [
        netlist_dir,
        os.environ.get("NETLIST_DIR"),
        "/supp/CUSPICE_public/netlist/single",
        "/home/eda260713/spice-lu-gpu/CUSPICE_public/netlist/single",
        "/workspace/CUSPICE_public/netlist/single",
        os.path.abspath("./netlist/single"),
    ]
    found = next((d for d in possible_dirs if d and os.path.isdir(d)), None)

    possible_bins = [
        ngspice_bin,
        os.environ.get("NGSPICE_BIN"),
        "/supp/CUSPICE_public/local/bin/ngspice",
        "/usr/local/bin/ngspice",
        "/usr/bin/ngspice",
    ]
    bin_path = next((b for b in possible_bins if b and os.path.exists(b)), "ngspice")

    return found, bin_path


def measure_serial(netlist_dir, ngspice_bin, limit=None):
    cases = sorted([f for f in os.listdir(netlist_dir) if f.endswith(".sp")])
    if limit:
        cases = cases[:limit]

    print("=" * 80)
    print(f"  CPU Serial Benchmark: {len(cases)} netlist(s)")
    print(f"  Netlist Dir: {netlist_dir}")
    print(f"  Ngspice Bin: {ngspice_bin}")
    print("-" * 80)

    total_start = time.time()
    timings = []
    for idx, case in enumerate(cases):
        case_path = os.path.join(netlist_dir, case)
        case_start = time.time()
        try:
            subprocess.run(
                [ngspice_bin, "-b", "-o", "/dev/null", case_path],
                capture_output=True, timeout=600,
            )
        except subprocess.TimeoutExpired:
            print(f"  [{idx+1:3d}/{len(cases)}] {case}: TIMEOUT")
            continue
        except Exception as e:
            print(f"  [{idx+1:3d}/{len(cases)}] {case}: ERROR ({e})")
            continue
        elapsed = time.time() - case_start
        timings.append(elapsed)
        if idx < 5 or idx % 10 == 0 or idx == len(cases) - 1:
            print(f"  [{idx+1:3d}/{len(cases)}] {case}: {elapsed:.3f}s")

    total_wall = time.time() - total_start
    print("-" * 80)
    print(f"  Total wall-clock time: {total_wall:.2f}s")
    if timings:
        print(f"  Per-netlist mean: {sum(timings)/len(timings):.3f}s")
        print(f"  Per-netlist max:  {max(timings):.3f}s")
    print("=" * 80)
    return total_wall, timings


def main():
    args = parse_args()
    netlist_dir, ngspice_bin = auto_detect(args.netlist_dir, args.ngspice_bin)

    if not netlist_dir:
        print("Error: netlist directory not found")
        sys.exit(1)

    total, _ = measure_serial(netlist_dir, ngspice_bin, args.num)
    print(f"\nOfficial baseline: 10.01s for 100 netlists")
    print(f"Your serial run:   {total:.2f}s for current cases")


if __name__ == "__main__":
    main()