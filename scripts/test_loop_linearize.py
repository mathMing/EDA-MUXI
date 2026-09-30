import subprocess

script = """
import subprocess

sp_lines = [
    "* Loop Linearize Test",
    ".control",
    "set noaskquit",
    "set filetype=ascii"
]

cases = ["test_001_tran", "test_005_tran", "test_006_tran"]

for i, case in enumerate(cases):
    sp_lines.append(f"source /supp/CUSPICE_public/netlist/single/{case}.sp")
    sp_lines.append("run")
    sp_lines.append("linearize v(v_out) v(v_inp)")
    # Check what plot is current or set to tran{2*i + 2}
    # In ngspice, linearize sets current plot to tran{2*i+2}
    sp_lines.append(f"setplot tran{2*i + 2}")
    sp_lines.append(f"print v(v_out) v(v_inp) > /workspace/loop_{case}.out")

sp_lines.append("quit")
sp_lines.append(".endc")
sp_lines.append(".end")

with open("/home/eda260713/PublicCase/test_loop.sp", "w") as f:
    f.write("\\n".join(sp_lines))

print("Executing test_loop.sp...")
res = subprocess.run([
    "docker", "exec", "eda260713-p0",
    "/supp/CUSPICE_public/local/bin/ngspice", "-b", "/workspace/test_loop.sp"
], capture_output=True, text=True)

print("Return code:", res.returncode)

for case in cases:
    v_cmd = [
        "python3",
        "/home/eda260713/spice-lu-gpu/organizer_supp/spice-golden/scripts/verify_waveform.py",
        "-q",
        f"/home/eda260713/spice-lu-gpu/organizer_supp/spice-golden/golden/{case}.out",
        f"/home/eda260713/PublicCase/loop_{case}.out"
    ]
    v_res = subprocess.run(v_cmd, capture_output=True, text=True)
    print(f"{case}: {v_res.stdout.strip()}")
"""

with open("x:/EDA/scripts/run_loop_remote.py", "w") as f:
    f.write(script)
