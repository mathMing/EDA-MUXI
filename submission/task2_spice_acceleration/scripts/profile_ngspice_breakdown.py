#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026 中国研究生创芯大赛·EDA 精英挑战赛 — 赛题七
任务二：单网表瞬态求解各阶段耗时剖析工具 (profile_ngspice_breakdown.py)

用途:
- 运行单网表并统计 ngspice 各阶段耗时 (parse, setup, matrix solve, output)
- 通过 stdout 中 'Elapsed' / 'Time' 标记识别阶段

用法:
    python3 profile_ngspice_breakdown.py --netlist <sp_file> [--ngspice-bin ngspice]
"""

import os
import sys
import re
import time
import argparse
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(description="NGSPICE Stage Profiler")
    parser.add_argument("--netlist", type=str, required=True,
                        help="Path to ngspice netlist (.sp)")
    parser.add_argument("--ngspice-bin", type=str, default=None,
                        help="Path to ngspice binary")
    return parser.parse_args()


def auto_detect(ngspice_bin):
    candidates = [
        ngspice_bin,
        os.environ.get("NGSPICE_BIN"),
        "/supp/CUSPICE_public/local/bin/ngspice",
        "/usr/local/bin/ngspice",
        "/usr/bin/ngspice",
    ]
    return next((b for b in candidates if b and os.path.exists(b)), "ngspice")


def profile(netlist, ngspice_bin):
    print("=" * 80)
    print(f"  NGSPICE Profile Breakdown")
    print(f"  Netlist:  {netlist}")
    print(f"  Binary:   {ngspice_bin}")
    print("=" * 80)

    wall_start = time.time()
    try:
        res = subprocess.run(
            [ngspice_bin, "-b", netlist],
            capture_output=True, text=True, timeout=300,
        )
    except subprocess.TimeoutExpired:
        print("FAIL: Simulation timed out")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    wall_elapsed = time.time() - wall_start

    print(f"  Total wall time: {wall_elapsed:.3f}s")
    print(f"  Return code:     {res.returncode}")
    print("-" * 80)

    # Parse internal timing lines from stdout
    # Typical ngspice output:
    #   "Circuit initialization ... 0.001 seconds"
    #   "Transient analysis ... 0.123 seconds"
    #   "Matrix solve ... 0.456 seconds"
    #   "Total elapsed time: 0.789 seconds"
    patterns = {
        'parse':       r'(?:parsing|parse|reading)[^\n]*?([\d.]+)\s*(?:seconds|ms)',
        'init':        r'(?:initializ|setup|cktsetup)[^\n]*?([\d.]+)\s*(?:seconds|ms)',
        'matrix_solve':r'(?:matrix|solve)[^\n]*?([\d.]+)\s*(?:seconds|ms)',
        'output':      r'(?:output|print|write)[^\n]*?([\d.]+)\s*(?:seconds|ms)',
        'total':       r'(?:total|elapsed|wall)\s*[: ]\s*([\d.]+)\s*(?:seconds|ms)',
    }

    findings = {}
    combined = (res.stdout or "") + "\n" + (res.stderr or "")
    for stage, pat in patterns.items():
        matches = re.findall(pat, combined, re.IGNORECASE)
        if matches:
            try:
                vals = [float(m) for m in matches]
                findings[stage] = sum(vals)
            except ValueError:
                pass

    if findings:
        print("  Stage breakdown (from internal timing):")
        total_internal = 0
        for stage, t in findings.items():
            print(f"    {stage:20s}: {t:.3f}s")
            total_internal += t
        print(f"    {'sum':20s}: {total_internal:.3f}s")
        print("-" * 80)
        if abs(total_internal - wall_elapsed) > 1.0:
            print(f"  Note: Internal sum ({total_internal:.3f}s) differs from wall ({wall_elapsed:.3f}s)")
    else:
        print("  No internal timing markers found in stdout/stderr.")
        print("  Suggestion: Re-run with NGSPICE internal timing enabled (e.g., set numtim = 1)")

    print("=" * 80)
    print(f"  Wall-clock total: {wall_elapsed:.3f}s")
    print("=" * 80)


def main():
    args = parse_args()
    if not os.path.exists(args.netlist):
        print(f"Error: netlist not found: {args.netlist}")
        sys.exit(1)

    ngspice_bin = auto_detect(args.ngspice_bin)
    profile(args.netlist, ngspice_bin)


if __name__ == "__main__":
    main()