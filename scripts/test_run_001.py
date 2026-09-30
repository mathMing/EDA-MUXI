import paramiko

HOST = "103.221.143.59"
PORT = 30023
USER = "eda260713"
PASS = "X3BUTjRd"

def run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
    
    # 1. Run official ngspice inside container on test_001_tran.sp
    run_cmd = """
    docker exec eda260713-p0 /supp/CUSPICE_public/local/bin/ngspice -b -o /workspace/test_001_run.out /supp/CUSPICE_public/netlist/single/test_001_tran.sp
    """
    print("Running ngspice on test_001_tran.sp...")
    stdin, stdout, stderr = client.exec_command(run_cmd, timeout=120)
    print("STDOUT:", stdout.read().decode('utf-8', errors='ignore'))
    print("STDERR:", stderr.read().decode('utf-8', errors='ignore'))
    
    # 2. Check the output file size
    check_cmd = "ls -lh ~/PublicCase/test_001_run.out"
    stdin, stdout, stderr = client.exec_command(check_cmd)
    print("Generated file:\n", stdout.read().decode('utf-8', errors='ignore'))

    # 3. Compare using NEW organizer_supp verify_waveform.py against spice-golden/golden
    verify_new_cmd = """
    python3 /home/eda260713/spice-lu-gpu/organizer_supp/spice-golden/scripts/verify_waveform.py \
        /home/eda260713/spice-lu-gpu/organizer_supp/spice-golden/golden/test_001_tran.out \
        /home/eda260713/PublicCase/test_001_run.out
    """
    print("\n--- Testing with NEW verify_waveform.py ---")
    stdin, stdout, stderr = client.exec_command(verify_new_cmd, timeout=30)
    print("NEW VERIFY STDOUT:\n", stdout.read().decode('utf-8', errors='ignore'))
    print("NEW VERIFY STDERR:\n", stderr.read().decode('utf-8', errors='ignore'))

    # 4. Compare using OLD verify_waveform.py inside container
    verify_old_cmd = """
    docker exec eda260713-p0 python3 /supp/CUSPICE_public/scripts/verify_waveform.py \
        /supp/CUSPICE_public/netlist/single_golden/test_001_tran.out \
        /workspace/test_001_run.out
    """
    print("\n--- Testing with OLD verify_waveform.py against single_golden ---")
    stdin, stdout, stderr = client.exec_command(verify_old_cmd, timeout=30)
    print("OLD VERIFY STDOUT:\n", stdout.read().decode('utf-8', errors='ignore'))
    print("OLD VERIFY STDERR:\n", stderr.read().decode('utf-8', errors='ignore'))

    # 5. Compare using OLD verify_waveform.py against NEW golden
    verify_old_against_new_golden_cmd = """
    python3 /home/eda260713/spice-lu-gpu/CUSPICE_public/scripts/verify_waveform.py \
        /home/eda260713/spice-lu-gpu/organizer_supp/spice-golden/golden/test_001_tran.out \
        /home/eda260713/PublicCase/test_001_run.out
    """
    print("\n--- Testing with OLD verify_waveform.py against NEW golden ---")
    stdin, stdout, stderr = client.exec_command(verify_old_against_new_golden_cmd, timeout=30)
    print("OLD VERIFY (against NEW golden) STDOUT:\n", stdout.read().decode('utf-8', errors='ignore'))
    print("OLD VERIFY (against NEW golden) STDERR:\n", stderr.read().decode('utf-8', errors='ignore'))

    client.close()

if __name__ == "__main__":
    run()
