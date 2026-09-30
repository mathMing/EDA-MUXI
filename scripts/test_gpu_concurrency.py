import time
import subprocess
from concurrent.futures import ProcessPoolExecutor

NETLIST_DIR = "/supp/CUSPICE_public/netlist/single"
GPU_NGSPICE = "/supp/CUSPICE_public/local/bin/ngspice"
OUT_DIR = "/workspace/concurrency_test"

cases = [f"test_{i:03d}_tran" for i in range(1, 17)]  # 16 cases

def run_one(case_name, gpu_id):
    sp = f"{NETLIST_DIR}/{case_name}.sp"
    out = f"{OUT_DIR}/{case_name}.out"
    cmd = [
        "docker", "exec",
        "-e", f"CUDA_VISIBLE_DEVICES={gpu_id}",
        "eda260713-p0",
        GPU_NGSPICE, "-b", "-o", out, sp
    ]
    t0 = time.time()
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t1 = time.time()
    return case_name, t1 - t0, res.returncode

def main():
    subprocess.run(["docker", "exec", "eda260713-p0", "mkdir", "-p", OUT_DIR])
    
    # Test 1: Run 4 cases concurrently on GPU 0
    print("=== Testing 4 concurrent processes on GPU 0 ===")
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=4) as ex:
        futures = [ex.submit(run_one, cases[i], 0) for i in range(4)]
        for f in futures:
            name, el, rc = f.result()
            print(f"  {name}: {el:.2f}s, rc={rc}")
    t1 = time.time()
    print(f"Total wall time for 4 cases on 1 GPU: {t1 - t0:.2f}s (Average: {(t1 - t0)/4:.2f}s/case)")

    # Test 2: Run 8 cases concurrently on GPU 0
    print("\n=== Testing 8 concurrent processes on GPU 0 ===")
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(run_one, cases[i+4], 0) for i in range(8)]
        for f in futures:
            name, el, rc = f.result()
            print(f"  {name}: {el:.2f}s, rc={rc}")
    t1 = time.time()
    print(f"Total wall time for 8 cases on 1 GPU: {t1 - t0:.2f}s (Average: {(t1 - t0)/8:.2f}s/case)")

if __name__ == "__main__":
    main()
