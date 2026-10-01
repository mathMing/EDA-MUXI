#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026 中国研究生创芯大赛·EDA 精英挑战赛 — 赛题七
任务二：100 网表波形一致性校验工具 (verify_waveform.py)

功能:
- 比较 test_NNN.out 与 golden_NNN.out 波形输出
- 计算 V(v_out) / V(v_inp) 的 L2 / L_inf 相对误差
- 输出 pass=100 fail=0 missing=0 标准格式
- 容忍网格步长差异 (linearize 后已对齐 4ns 网格)

用法:
    python3 verify_waveform.py -g <golden_dir> -t <test_dir>
    python3 verify_waveform.py verify <golden_dir> <test_dir>
"""

import os
import sys
import glob
import argparse
import numpy as np


def parse_ngspice_out(filepath):
    """
    解析 ngspice print 输出 (.out) 文件:
    - 跳过非数据行 (header / footer)
    - 提取时间列 t 与两路波形 v(v_out), v(v_inp)
    - 返回 dict { 't': array, 'v_out': array, 'v_inp': array }
    """
    if not os.path.exists(filepath):
        return None

    data_lines = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            s = line.strip()
            # 跳过空行、表头、index 行
            if not s:
                continue
            if s.startswith(('*', '.', '#', 'Index', 'No.')):
                continue
            # 数据行: 至少 3 个数字
            parts = s.split()
            if len(parts) >= 3:
                try:
                    t = float(parts[0])
                    v1 = float(parts[1])
                    v2 = float(parts[2])
                    data_lines.append((t, v1, v2))
                except ValueError:
                    continue

    if not data_lines:
        return None

    arr = np.array(data_lines, dtype=np.float64)
    return {
        't': arr[:, 0],
        'v_out': arr[:, 1],
        'v_inp': arr[:, 2],
    }


def align_signals(t_g, v_g, t_t, v_t, tol=1e-9):
    """
    网格对齐: 将测试信号 v_t 插值到 golden 的 t_g 网格
    (t_g 通常由 linearize 后是均匀 4ns 步长)
    """
    if len(t_g) == 0 or len(t_t) == 0:
        return v_g, v_t

    # 截断到共同时间区间
    t_min = max(t_g[0], t_t[0])
    t_max = min(t_g[-1], t_t[-1])

    # 选择共同范围内的 t_g
    mask_g = (t_g >= t_min - tol) & (t_g <= t_max + tol)
    t_g_sel = t_g[mask_g]
    v_g_sel = v_g[mask_g]

    if len(t_g_sel) < 2:
        return v_g_sel, np.zeros_like(v_g_sel)

    # 线性插值 v_t 到 t_g_sel
    v_t_sel = np.interp(t_g_sel, t_t, v_t)
    return v_g_sel, v_t_sel


def compute_metrics(v_g, v_t):
    """
    计算波形相对误差:
    - L2 norm: ||v_g - v_t||_2 / ||v_g||_2
    - L_inf norm: max|v_g - v_t| / max|v_g|
    """
    if len(v_g) != len(v_t) or len(v_g) == 0:
        return None, None
    diff = v_g - v_t
    norm_g_l2 = np.linalg.norm(v_g)
    norm_diff_l2 = np.linalg.norm(diff)
    l2_err = norm_diff_l2 / norm_g_l2 if norm_g_l2 > 1e-15 else norm_diff_l2

    norm_g_inf = np.max(np.abs(v_g))
    norm_diff_inf = np.max(np.abs(diff))
    linf_err = norm_diff_inf / norm_g_inf if norm_g_inf > 1e-15 else norm_diff_inf

    return l2_err, linf_err


def verify_case(golden_path, test_path, tol_l2=1e-2, tol_linf=1e-1):
    """验证单个用例的波形一致性"""
    golden = parse_ngspice_out(golden_path)
    test = parse_ngspice_out(test_path)

    if golden is None:
        return False, "golden_missing", None, None
    if test is None:
        return False, "test_missing", None, None

    # 对齐 V(v_out) (主要波形)
    v_g, v_t = align_signals(golden['t'], golden['v_out'], test['t'], test['v_out'])
    l2_err, linf_err = compute_metrics(v_g, v_t)

    if l2_err is None:
        return False, "alignment_failed", None, None

    passed = (l2_err < tol_l2) and (linf_err < tol_linf)
    return passed, "PASS" if passed else "FAIL", l2_err, linf_err


def parse_args():
    parser = argparse.ArgumentParser(description="NGSPICE Waveform Consistency Verifier")
    parser.add_argument("-g", "--golden-dir", type=str, required=False,
                        help="Directory containing golden .out files")
    parser.add_argument("-t", "--test-dir", type=str, required=False,
                        help="Directory containing test .out files")
    parser.add_argument("--tol-l2", type=float, default=1e-2,
                        help="L2 relative error tolerance (default: 1e-2)")
    parser.add_argument("--tol-linf", type=float, default=1e-1,
                        help="L_inf relative error tolerance (default: 1e-1)")
    return parser.parse_args()


def main():
    args = parse_args()

    # Support "verify golden_dir test_dir" form
    if len(sys.argv) >= 4 and sys.argv[1] == "verify":
        golden_dir = sys.argv[2]
        test_dir = sys.argv[3]
    else:
        if not args.golden_dir or not args.test_dir:
            print("Usage: verify_waveform.py verify <golden_dir> <test_dir>")
            print("       verify_waveform.py -g <golden_dir> -t <test_dir>")
            sys.exit(1)
        golden_dir = args.golden_dir
        test_dir = args.test_dir

    if not os.path.isdir(golden_dir):
        print(f"Error: Golden directory not found: {golden_dir}")
        sys.exit(1)
    if not os.path.isdir(test_dir):
        print(f"Error: Test directory not found: {test_dir}")
        sys.exit(1)

    golden_files = sorted(glob.glob(os.path.join(golden_dir, "*.out")))
    print("================================================================================")
    print(f"  Waveform Verification: {len(golden_files)} Golden Cases")
    print(f"  Golden: {golden_dir}")
    print(f"  Test:   {test_dir}")
    print(f"  Tolerance: L2 < {args.tol_l2:.2e}, L_inf < {args.tol_linf:.2e}")
    print("-" * 80)

    pass_count = 0
    fail_count = 0
    missing_count = 0
    failed_cases = []

    for gf in golden_files:
        base = os.path.splitext(os.path.basename(gf))[0]
        tf = os.path.join(test_dir, f"{base}.out")
        if not os.path.exists(tf):
            missing_count += 1
            print(f"  [{base:20s}] MISSING")
            continue

        passed, status, l2_err, linf_err = verify_case(
            gf, tf, args.tol_l2, args.tol_linf
        )
        if passed:
            pass_count += 1
            if l2_err is not None:
                print(f"  [{base:20s}] PASS  (L2={l2_err:.2e}, Linf={linf_err:.2e})")
            else:
                print(f"  [{base:20s}] PASS")
        else:
            fail_count += 1
            failed_cases.append(base)
            print(f"  [{base:20s}] {status}  (L2={l2_err}, Linf={linf_err})")

    print("-" * 80)
    print(f"  pass={pass_count} fail={fail_count} missing={missing_count}")
    print("================================================================================")

    if missing_count > 0 or fail_count > 0:
        if failed_cases:
            print(f"Failed cases: {failed_cases[:5]}...")
        sys.exit(1)


if __name__ == "__main__":
    main()