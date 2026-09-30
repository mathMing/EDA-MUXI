import subprocess

sp_content = """* Test linearize
.control
set noaskquit
set filetype=ascii
source /supp/CUSPICE_public/netlist/single/test_005_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print v(v_out) v(v_inp) > /workspace/test_005_linearized.out
quit
.endc
.end
"""

with open("/home/eda260713/PublicCase/test_linearize.sp", "w") as f:
    f.write(sp_content)

print("Running ngspice with linearize...")
cmd = [
    "docker", "exec", "eda260713-p0",
    "/supp/CUSPICE_public/local/bin/ngspice", "-b", "/workspace/test_linearize.sp"
]
res = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", res.returncode)
if res.stdout:
    print("STDOUT:", res.stdout[-300:])
if res.stderr:
    print("STDERR:", res.stderr[-300:])

print("\nVerifying output against golden...")
v_cmd = [
    "python3",
    "/home/eda260713/spice-lu-gpu/organizer_supp/spice-golden/scripts/verify_waveform.py",
    "/home/eda260713/spice-lu-gpu/organizer_supp/spice-golden/golden/test_005_tran.out",
    "/home/eda260713/PublicCase/test_005_linearized.out"
]
v_res = subprocess.run(v_cmd, capture_output=True, text=True)
print(v_res.stdout)
if v_res.stderr:
    print("STDERR:", v_res.stderr)
