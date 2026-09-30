#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026 中国研究生创芯大赛·EDA 精英挑战赛 — 赛题七
任务二：4-GPU 16-Worker 分布式并发仿真与全量自动对账流水线 (Production Edition)
支持原生执行与容器化执行自适应，包含内存自动回收与动态线性化插值对齐。
"""

import os
import sys
import time
import argparse
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed

def parse_args():
    parser = argparse.ArgumentParser(description="4-GPU 16-Worker SPICE Batch Runner")
    parser.add_argument("--netlist-dir", type=str, default=None,
                        help="Path to single netlist directory containing .sp files")
    parser.add_argument("--golden-dir", type=str, default=None,
                        help="Path to golden output directory")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Path to store simulation output files")
    parser.add_argument("--ngspice-bin", type=str, default=None,
                        help="Path to ngspice executable")
    parser.add_argument("--verify-script", type=str, default=None,
                        help="Path to verify_waveform.py or run_all.sh script")
    parser.add_argument("--docker-container", type=str, default=None,
                        help="Docker container name (optional, if running via docker)")
    parser.add_argument("--num-workers", type=int, default=16,
                        help="Total concurrent worker processes (default: 16)")
    parser.add_argument("--num-gpus", type=int, default=4,
                        help="Number of GPUs available (default: 4)")
    return parser.parse_args()

def auto_detect_paths(args):
    # 1. Netlist directory
    possible_netlist_dirs = [
        args.netlist_dir,
        os.environ.get("NETLIST_DIR"),
        "/supp/CUSPICE_public/netlist/single",
        "/home/eda260713/spice-lu-gpu/CUSPICE_public/netlist/single",
        "/workspace/CUSPICE_public/netlist/single",
        os.path.abspath("./netlist/single")
    ]
    netlist_dir = next((d for d in possible_netlist_dirs if d and os.path.isdir(d)), None)

    # 2. Golden directory
    possible_golden_dirs = [
        args.golden_dir,
        os.environ.get("GOLDEN_DIR"),
        "/home/eda260713/spice-lu-gpu/organizer_supp/spice-golden/golden",
        "/supp/spice-golden/golden",
        "/workspace/spice-golden/golden",
        os.path.abspath("./golden")
    ]
    golden_dir = next((d for d in possible_golden_dirs if d and os.path.isdir(d)), None)

    # 3. Output directory
    output_dir = args.output_dir or os.environ.get("OUTPUT_DIR") or os.path.abspath("./batch_16w_out")
    os.makedirs(output_dir, exist_ok=True)
    for f in os.listdir(output_dir):
        if f.endswith(".out"):
            try:
                os.remove(os.path.join(output_dir, f))
            except OSError:
                pass


    # 4. Ngspice binary
    possible_ngspice = [
        args.ngspice_bin,
        os.environ.get("NGSPICE_BIN"),
        "/supp/CUSPICE_public/local/bin/ngspice",
        "/usr/local/bin/ngspice",
        "/usr/bin/ngspice"
    ]
    ngspice_bin = next((b for b in possible_ngspice if b and os.path.exists(b)), "ngspice")

    # 5. Verification script
    possible_verify = [
        args.verify_script,
        os.environ.get("VERIFY_SCRIPT"),
        "/home/eda260713/spice-lu-gpu/organizer_supp/spice-golden/scripts/verify_waveform.py",
        "/supp/spice-golden/scripts/verify_waveform.py",
        os.path.abspath("./scripts/verify_waveform.py")
    ]
    verify_script = next((v for v in possible_verify if v and os.path.exists(v)), None)

    # 6. Docker container name (fallback to eda260713-p0 if docker is active and requested)
    docker_container = args.docker_container or os.environ.get("DOCKER_CONTAINER")

    return {
        "netlist_dir": netlist_dir,
        "golden_dir": golden_dir,
        "output_dir": output_dir,
        "ngspice_bin": ngspice_bin,
        "verify_script": verify_script,
        "docker_container": docker_container
    }

def generate_worker_script(worker_id, worker_cases, netlist_dir, output_dir, work_dir):
    """
    生成针对每个 worker 的高鲁棒性批处理控制脚本。
    关键特性:
    1. 在每个用例仿真后执行 'destroy all' 与 'remcirc'，彻底避免内存泄漏与节点污染；
    2. 由于每次执行均从净态启动，'tran' 恒生成 tran1，'linearize' 恒生成 tran2，规避 plot 索引漂移。
    """
    sp_lines = [
        f"* Worker {worker_id} Robust In-Process Batch Runner",
        ".control",
        "set noaskquit",
        "set filetype=ascii"
    ]
    for k, case in enumerate(worker_cases):
        base = os.path.splitext(case)[0]
        case_path = os.path.join(netlist_dir, case).replace("\\", "/")
        out_path = os.path.join(output_dir, f"{base}.out").replace("\\", "/")
        
        sp_lines.append(f'echo "=== Worker {worker_id} [{k+1}/{len(worker_cases)}] {base} ==="')
        sp_lines.append(f'source {case_path}')
        sp_lines.append('run')
        # 规整化插值对齐 4ns 网格
        sp_lines.append('linearize v(v_out) v(v_inp)')
        # 切换到由 linearize 创建的标准插值 plot (在 reset 后恒为 tran2)
        sp_lines.append('setplot tran2')
        sp_lines.append(f'print v(v_out) v(v_inp) > {out_path}')
        # 核心内存清理: 销毁所有 plot 与电路拓扑，释放显存与内存
        sp_lines.append('destroy all')
        sp_lines.append('remcirc')
        
    sp_lines.append("quit")
    sp_lines.append(".endc")
    sp_lines.append(".end\n")

    script_path = os.path.join(work_dir, f"worker_{worker_id}.sp")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sp_lines))
    return script_path

def run_worker_task(worker_id, gpu_id, script_path, ngspice_bin, docker_container):
    start = time.time()
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

    if docker_container:
        cmd = [
            "docker", "exec",
            "-e", f"CUDA_VISIBLE_DEVICES={gpu_id}",
            docker_container,
            ngspice_bin, "-b", script_path
        ]
    else:
        cmd = [ngspice_bin, "-b", script_path]

    try:
        res = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=600)
        elapsed = time.time() - start
        return {
            "worker_id": worker_id,
            "gpu_id": gpu_id,
            "elapsed": elapsed,
            "returncode": res.returncode,
            "stdout_tail": res.stdout[-400:] if res.stdout else "",
            "stderr": res.stderr
        }
    except Exception as e:
        return {
            "worker_id": worker_id,
            "gpu_id": gpu_id,
            "elapsed": time.time() - start,
            "returncode": -1,
            "error": str(e)
        }

def main():
    args = parse_args()
    paths = auto_detect_paths(args)

    print("================================================================================")
    print("  4-GPU 16-Worker SPICE Batch Simulation & Waveform Verification Engine")
    print("================================================================================")
    print(f"Netlist Directory : {paths['netlist_dir']}")
    print(f"Golden Directory  : {paths['golden_dir']}")
    print(f"Output Directory  : {paths['output_dir']}")
    print(f"Ngspice Binary    : {paths['ngspice_bin']}")
    print(f"Execution Mode    : {'Docker (' + paths['docker_container'] + ')' if paths['docker_container'] else 'Native Host'}")
    print(f"Workers / GPUs    : {args.num_workers} Workers / {args.num_gpus} GPUs")
    print("-" * 80)

    if not paths["netlist_dir"] or not os.path.isdir(paths["netlist_dir"]):
        print(f"Error: Netlist directory not found or invalid: {paths['netlist_dir']}")
        sys.exit(1)

    cases = sorted([f for f in os.listdir(paths["netlist_dir"]) if f.endswith(".sp")])
    if not cases:
        print(f"Error: No .sp netlists found in {paths['netlist_dir']}")
        sys.exit(1)

    print(f"Discovered {len(cases)} circuit netlist(s) to simulate.")

    # 分配任务分片 (按 worker_id 均匀分配)
    worker_buckets = [[] for _ in range(args.num_workers)]
    for idx, case in enumerate(cases):
        worker_buckets[idx % args.num_workers].append(case)

    work_dir = os.path.join(paths["output_dir"], "_scripts")
    os.makedirs(work_dir, exist_ok=True)

    tasks = []
    for wid in range(args.num_workers):
        gid = wid % args.num_gpus
        w_cases = worker_buckets[wid]
        if not w_cases:
            continue
        script_file = generate_worker_script(wid, w_cases, paths["netlist_dir"], paths["output_dir"], work_dir)
        tasks.append((wid, gid, script_file))
        print(f"  Worker {wid:02d} -> GPU {gid} | Assigned {len(w_cases)} netlists -> {os.path.basename(script_file)}")

    print("\n=== Launching Concurrent Worker Processes ===")
    total_start = time.time()
    worker_results = []

    with ProcessPoolExecutor(max_workers=args.num_workers) as executor:
        future_map = {
            executor.submit(run_worker_task, wid, gid, sp, paths["ngspice_bin"], paths["docker_container"]): wid
            for wid, gid, sp in tasks
        }
        for future in as_completed(future_map):
            res = future.result()
            worker_results.append(res)
            rc_str = f"rc={res['returncode']}" if res['returncode'] == 0 else f"FAILED (rc={res['returncode']})"
            print(f"  [Worker {res['worker_id']:02d} Completed] GPU {res['gpu_id']} | Elapsed: {res['elapsed']:.2f}s | {rc_str}")

    total_wall_clock = time.time() - total_start
    print("-" * 80)
    print(f">>> All {len(tasks)} Workers Finished in {total_wall_clock:.2f}s Total Wall-Clock Time! <<<")

    # 检查输出文件数
    generated_outs = [f for f in os.listdir(paths["output_dir"]) if f.endswith(".out")]
    print(f"Generated {len(generated_outs)} / {len(cases)} waveform .out file(s) in {paths['output_dir']}")

    # 自动调用波形验证
    if paths["golden_dir"] and paths["verify_script"]:
        print("\n=== Running Waveform Consistency Verification against Golden ===")
        if paths["verify_script"].endswith(".sh"):
            v_cmd = ["bash", paths["verify_script"], "verify", paths["golden_dir"], paths["output_dir"]]
        else:
            v_cmd = ["python3", paths["verify_script"], "-g", paths["golden_dir"], "-t", paths["output_dir"]]
        
        try:
            v_res = subprocess.run(v_cmd, capture_output=True, text=True)
            print(v_res.stdout)
            if v_res.stderr:
                print("[Verification Notice]:", v_res.stderr.strip())
        except Exception as ve:
            print(f"Verification execution error: {ve}")

if __name__ == "__main__":
    main()
