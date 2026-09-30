import paramiko

HOST = "103.221.143.59"
PORT = 30023
USER = "eda260713"
PASS = "X3BUTjRd"

def run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
    
    cmd = """
    docker exec eda260713-p0 grep -rn "cudaSetDevice" /supp/CUSPICE_public/cuspice/src/ || true
    docker exec eda260713-p0 grep -rn "USE_CUSPICE" /supp/CUSPICE_public/cuspice/src/ | head -n 30 || true
    """
    stdin, stdout, stderr = client.exec_command(cmd)
    print("CUSPICE device setup grep:")
    print(stdout.read().decode('utf-8', errors='ignore'))
    client.close()

if __name__ == "__main__":
    run()
