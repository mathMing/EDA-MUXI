import sys
import paramiko

HOST = "103.221.143.59"
PORT = 30023
USER = "eda260713"
PASS = "X3BUTjRd"

def test_connection():
    print(f"Connecting to {USER}@{HOST}:{PORT}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
        print("SSH Connection SUCCESSFUL!")
        
        # Run basic info commands
        commands = [
            "uname -a",
            "hostname",
            "uptime",
            "docker ps -a",
            "ls -la /public",
            "ls -la /public/competition_case7"
        ]
        
        for cmd in commands:
            print(f"\n>>> Running: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
            out = stdout.read().decode('utf-8', errors='ignore').strip()
            err = stderr.read().decode('utf-8', errors='ignore').strip()
            if out:
                print(out)
            if err:
                print(f"[STDERR]: {err}")
                
        client.close()
    except Exception as e:
        print(f"SSH Connection FAILED: {e}")
        return False
    return True

if __name__ == "__main__":
    test_connection()
