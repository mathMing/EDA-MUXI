import paramiko
import time

HOST = "103.221.143.59"
PORT = 30023
USER = "eda260713"
PASS = "X3BUTjRd"

def run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
    
    cmd = """
    mkdir -p /home/eda260713/PublicCase/cpu_serial_out
    rm -rf /home/eda260713/PublicCase/cpu_serial_out/*
    
    echo "=== Measuring Official CPU Serial Baseline (JOBS=1) on 100 netlists ==="
    time docker exec eda260713-p0 bash -c '
        NGSPICE=/workspace/ngspice_cpu_install/bin/ngspice
        OUT=/workspace/cpu_serial_out
        NETDIR=/supp/CUSPICE_public/netlist/single
        
        find "$NETDIR" -maxdepth 1 -name "*.sp" | sort | while read sp; do
            name=$(basename "$sp" .sp)
            "$NGSPICE" -b "$sp" -o "$OUT/$name.out" > /dev/null 2>&1
        done
        echo "Completed serial run: $(ls $OUT/*.out | wc -l) files"
    '
    """
    
    print("Starting CPU Serial baseline measurement...")
    start_t = time.time()
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    
    for line in stdout:
        print(line, end="")
    err = stderr.read().decode('utf-8', errors='ignore')
    if err:
        print("\n[STDERR]:\n", err)
        
    print(f"\nSerial measurement completed in {time.time() - start_t:.2f}s")
    client.close()

if __name__ == "__main__":
    run()
