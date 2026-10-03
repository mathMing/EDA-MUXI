* Worker 14 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 14 [1/6] test_015_tran ==="
source /supp/CUSPICE_public/netlist/single/test_015_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_015_tran.out
destroy all
remcirc
echo "=== Worker 14 [2/6] test_031_tran ==="
source /supp/CUSPICE_public/netlist/single/test_031_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_031_tran.out
destroy all
remcirc
echo "=== Worker 14 [3/6] test_047_tran ==="
source /supp/CUSPICE_public/netlist/single/test_047_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_047_tran.out
destroy all
remcirc
echo "=== Worker 14 [4/6] test_063_tran ==="
source /supp/CUSPICE_public/netlist/single/test_063_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_063_tran.out
destroy all
remcirc
echo "=== Worker 14 [5/6] test_079_tran ==="
source /supp/CUSPICE_public/netlist/single/test_079_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_079_tran.out
destroy all
remcirc
echo "=== Worker 14 [6/6] test_095_tran ==="
source /supp/CUSPICE_public/netlist/single/test_095_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_095_tran.out
destroy all
remcirc
quit
.endc
.end
