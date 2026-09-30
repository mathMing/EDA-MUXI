import paramiko

HOST = "103.221.143.59"
PORT = 30023
USER = "eda260713"
PASS = "X3BUTjRd"

def run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
    
    cmd = "docker exec eda260713-p0 grep -E '(\\.include|/workspace|\\.lib|tran)' /supp/CUSPICE_public/netlist/single/test_001_tran.sp"
    stdin, stdout, stderr = client.exec_command(cmd)
    print("Includes & directives in test_001_tran.sp:")
    print(stdout.read().decode('utf-8', errors='ignore'))
    client.close()

if __name__ == "__main__":
    run()
