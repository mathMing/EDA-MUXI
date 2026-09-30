import paramiko

HOST = "103.221.143.59"
PORT = 30023
USER = "eda260713"
PASS = "X3BUTjRd"

def run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
    
    # We will test running with rusage before and after source, run, and print
    script = """* Profile breakdown
.control
set noaskquit
set filetype=ascii

echo "=== MARK 0: Start ==="
rusage
echo "=== MARK 1: Sourcing test_001 ==="
source /supp/CUSPICE_public/netlist/single/test_001_tran.sp
rusage
echo "=== MARK 2: Running simulation ==="
run
rusage
echo "=== MARK 3: Printing output ==="
print v(v_out) v(v_inp) > /workspace/profile_001.out
rusage
echo "=== MARK 4: Sourcing test_002 ==="
source /supp/CUSPICE_public/netlist/single/test_002_tran.sp
rusage
echo "=== MARK 5: Running simulation 2 ==="
run
rusage
echo "=== MARK 6: Done ==="
quit
.endc
.end
"""
    sftp = client.open_sftp()
    with sftp.file("/home/eda260713/PublicCase/profile_run.sp", "w") as f:
        f.write(script)
    sftp.close()
    
    cmd = """
    time docker exec -e CUDA_VISIBLE_DEVICES=0 eda260713-p0 /supp/CUSPICE_public/local/bin/ngspice -b /workspace/profile_run.sp
    """
    print("Profiling in-process execution breakdown...")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    print("STDOUT:\n", stdout.read().decode('utf-8', errors='ignore'))
    print("STDERR:\n", stderr.read().decode('utf-8', errors='ignore'))
    client.close()

if __name__ == "__main__":
    run()
