import sys
import paramiko

HOST = "103.221.143.59"
PORT = 30023
USER = "eda260713"
PASS = "X3BUTjRd"

def run_commands(commands):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
    
    for cmd in commands:
        print(f"\n==========================================")
        print(f">>> [CMD]: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
        out = stdout.read().decode('utf-8', errors='ignore').strip()
        err = stderr.read().decode('utf-8', errors='ignore').strip()
        if out:
            print(out)
        if err:
            print(f"[STDERR]: {err}")
            
    client.close()

if __name__ == "__main__":
    cmds = [
        "docker exec eda260713-p0 ls -la /supp/CUSPICE_public/scripts",
        "docker exec eda260713-p0 ls -la /supp/CUSPICE_public/netlist",
        "docker exec eda260713-p0 head -n 30 /supp/CUSPICE_public/scripts/verify_waveform.py",
        "docker exec eda260713-p0 ls -la /supp/CUSPICE_public/local/bin",
        "docker exec eda260713-p0 which ngspice || echo 'no ngspice in PATH'",
        "docker exec eda260713-p0 ls -la /supp/CUSPICE_public/cuspice | head -n 30"
    ]
    run_commands(cmds)
