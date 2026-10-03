* Worker 11 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 11 [1/6] test_012_tran ==="
source /supp/CUSPICE_public/netlist/single/test_012_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_012_tran.out
destroy all
remcirc
echo "=== Worker 11 [2/6] test_028_tran ==="
source /supp/CUSPICE_public/netlist/single/test_028_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_028_tran.out
destroy all
remcirc
echo "=== Worker 11 [3/6] test_044_tran ==="
source /supp/CUSPICE_public/netlist/single/test_044_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_044_tran.out
destroy all
remcirc
echo "=== Worker 11 [4/6] test_060_tran ==="
source /supp/CUSPICE_public/netlist/single/test_060_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_060_tran.out
destroy all
remcirc
echo "=== Worker 11 [5/6] test_076_tran ==="
source /supp/CUSPICE_public/netlist/single/test_076_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_076_tran.out
destroy all
remcirc
echo "=== Worker 11 [6/6] test_092_tran ==="
source /supp/CUSPICE_public/netlist/single/test_092_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_092_tran.out
destroy all
remcirc
quit
.endc
.end
