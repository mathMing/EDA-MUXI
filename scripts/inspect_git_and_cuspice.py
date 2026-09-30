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
        "cd ~/PublicCase && git status && git log -n 5 --oneline",
        "ls -la /supp",
        "ls -la /supp/CUSPICE_public",
        "docker exec eda260713-p0 ls -la /supp/CUSPICE_public",
        "ls -la ~/spice-lu-gpu"
    ]
    run_commands(cmds)
