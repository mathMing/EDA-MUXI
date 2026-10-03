* Worker 6 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 6 [1/6] test_007_tran ==="
source /supp/CUSPICE_public/netlist/single/test_007_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_007_tran.out
destroy all
remcirc
echo "=== Worker 6 [2/6] test_023_tran ==="
source /supp/CUSPICE_public/netlist/single/test_023_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_023_tran.out
destroy all
remcirc
echo "=== Worker 6 [3/6] test_039_tran ==="
source /supp/CUSPICE_public/netlist/single/test_039_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_039_tran.out
destroy all
remcirc
echo "=== Worker 6 [4/6] test_055_tran ==="
source /supp/CUSPICE_public/netlist/single/test_055_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_055_tran.out
destroy all
remcirc
echo "=== Worker 6 [5/6] test_071_tran ==="
source /supp/CUSPICE_public/netlist/single/test_071_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_071_tran.out
destroy all
remcirc
echo "=== Worker 6 [6/6] test_087_tran ==="
source /supp/CUSPICE_public/netlist/single/test_087_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_087_tran.out
destroy all
remcirc
quit
.endc
.end
