* Worker 2 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 2 [1/7] test_003_tran ==="
source /supp/CUSPICE_public/netlist/single/test_003_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_003_tran.out
destroy all
remcirc
echo "=== Worker 2 [2/7] test_019_tran ==="
source /supp/CUSPICE_public/netlist/single/test_019_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_019_tran.out
destroy all
remcirc
echo "=== Worker 2 [3/7] test_035_tran ==="
source /supp/CUSPICE_public/netlist/single/test_035_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_035_tran.out
destroy all
remcirc
echo "=== Worker 2 [4/7] test_051_tran ==="
source /supp/CUSPICE_public/netlist/single/test_051_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_051_tran.out
destroy all
remcirc
echo "=== Worker 2 [5/7] test_067_tran ==="
source /supp/CUSPICE_public/netlist/single/test_067_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_067_tran.out
destroy all
remcirc
echo "=== Worker 2 [6/7] test_083_tran ==="
source /supp/CUSPICE_public/netlist/single/test_083_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_083_tran.out
destroy all
remcirc
echo "=== Worker 2 [7/7] test_099_tran ==="
source /supp/CUSPICE_public/netlist/single/test_099_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_099_tran.out
destroy all
remcirc
quit
.endc
.end
