import os
import sys
import time
import subprocess
from concurrent.futures import ProcessPoolExecutor

HOST_NETLIST_DIR = "/home/eda260713/spice-lu-gpu/CUSPICE_public/netlist/single"
CONTAINER_NETLIST_DIR = "/supp/CUSPICE_public/netlist/single"
GOLDEN_DIR = "/home/eda260713/spice-lu-gpu/organizer_supp/spice-golden/golden"
RUN_ALL_SCRIPT = "/home/eda260713/spice-lu-gpu/organizer_supp/spice-golden/scripts/run_all.sh"
NGSPICE_BIN = "/supp/CUSPICE_public/local/bin/ngspice"

HOST_OUT_DIR = "/home/eda260713/PublicCase/batch_16w_out"
CONTAINER_OUT_DIR = "/workspace/batch_16w_out"

os.makedirs(HOST_OUT_DIR, exist_ok=True)
for f in os.listdir(HOST_OUT_DIR):
    if f.endswith(".out"):
        os.remove(os.path.join(HOST_OUT_DIR, f))

cases = sorted([f for f in os.listdir(HOST_NETLIST_DIR) if f.endswith(".sp")])
print(f"Total netlists found: {len(cases)}")

# 16 workers total: 4 workers per GPU across 4 GPUs
num_workers = 16
num_gpus = 4
worker_buckets = [[] for _ in range(num_workers)]
for idx, case in enumerate(cases):
    worker_buckets[idx % num_workers].append(case)

def generate_worker_script(worker_id, worker_cases):
    sp_lines = [
        f"* Worker {worker_id} Linearized Batch Runner",
        ".control",
        "set noaskquit",
        "set filetype=ascii"
    ]
    for k, case in enumerate(worker_cases):
        base = os.path.splitext(case)[0]
        sp_lines.append(f'echo "=== Worker {worker_id} [{k+1}/{len(worker_cases)}] {base} ==="')
        sp_lines.append(f'source {CONTAINER_NETLIST_DIR}/{case}')
        sp_lines.append('run')
        sp_lines.append('linearize v(v_out) v(v_inp)')
        sp_lines.append(f'setplot tran{2*k + 2}')
        sp_lines.append(f'print v(v_out) v(v_inp) > {CONTAINER_OUT_DIR}/{base}.out')
    sp_lines.append("quit")
    sp_lines.append(".endc")
    sp_lines.append(".end\n")

    script_name = f"linear_w16_{worker_id}.sp"
    host_path = f"/home/eda260713/PublicCase/{script_name}"
    container_path = f"/workspace/{script_name}"
    with open(host_path, "w") as f:
        f.write("\n".join(sp_lines))
    return container_path

def run_worker(worker_id, gpu_id, container_script):
    start = time.time()
    cmd = [
        "docker", "exec",
        "-e", f"CUDA_VISIBLE_DEVICES={gpu_id}",
        "eda260713-p0",
        NGSPICE_BIN, "-b", container_script
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start
    return worker_id, gpu_id, elapsed, res.returncode

print(f"\n=== Generating scripts for {num_workers} workers across {num_gpus} GPUs ===")
tasks = []
for wid in range(num_workers):
    gid = wid % num_gpus
    script_path = generate_worker_script(wid, worker_buckets[wid])
    tasks.append((wid, gid, script_path))
    print(f"Worker {wid} (GPU {gid}): assigned {len(worker_buckets[wid])} cases -> {script_path}")

print(f"\n=== Launching {num_workers} Workers Concurrently across 4 GPUs ===")
total_start = time.time()

with ProcessPoolExecutor(max_workers=num_workers) as executor:
    futures = [executor.submit(run_worker, wid, gid, sp) for wid, gid, sp in tasks]
    for f in futures:
        wid, gid, elapsed, rc = f.result()
        print(f"Worker {wid} (GPU {gid}) FINISHED: elapsed={elapsed:.2f}s, rc={rc}")

total_elapsed = time.time() - total_start
print(f"\n>>> ALL {num_workers} WORKERS COMPLETED in {total_elapsed:.2f}s Wall-clock time! <<<")

out_files = [f for f in os.listdir(HOST_OUT_DIR) if f.endswith(".out")]
print(f"Generated {len(out_files)} output files in {HOST_OUT_DIR}")

print("\n=== Running Official Verification across all 100 cases ===")
v_cmd = ["bash", RUN_ALL_SCRIPT, "verify", GOLDEN_DIR, HOST_OUT_DIR]
v_res = subprocess.run(v_cmd, capture_output=True, text=True)
print(v_res.stdout)
if v_res.stderr:
    print("[STDERR]:", v_res.stderr)
