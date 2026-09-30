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
    ls -l /home/eda260713/spice-lu-gpu/organizer_supp/spice-golden/scripts/verify_waveform.py /supp/CUSPICE_public/scripts/verify_waveform.py
    md5sum /home/eda260713/spice-lu-gpu/organizer_supp/spice-golden/scripts/verify_waveform.py /supp/CUSPICE_public/scripts/verify_waveform.py
    head -n 25 /home/eda260713/spice-lu-gpu/organizer_supp/spice-golden/scripts/verify_waveform.py
    """
    stdin, stdout, stderr = client.exec_command(cmd)
    print(stdout.read().decode('utf-8', errors='ignore'))
    client.close()

if __name__ == "__main__":
    run()
