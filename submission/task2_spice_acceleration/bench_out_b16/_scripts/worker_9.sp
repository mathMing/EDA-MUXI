* Worker 9 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 9 [1/6] test_010_tran ==="
source /supp/CUSPICE_public/netlist/single/test_010_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_010_tran.out
destroy all
remcirc
echo "=== Worker 9 [2/6] test_026_tran ==="
source /supp/CUSPICE_public/netlist/single/test_026_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_026_tran.out
destroy all
remcirc
echo "=== Worker 9 [3/6] test_042_tran ==="
source /supp/CUSPICE_public/netlist/single/test_042_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_042_tran.out
destroy all
remcirc
echo "=== Worker 9 [4/6] test_058_tran ==="
source /supp/CUSPICE_public/netlist/single/test_058_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_058_tran.out
destroy all
remcirc
echo "=== Worker 9 [5/6] test_074_tran ==="
source /supp/CUSPICE_public/netlist/single/test_074_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_074_tran.out
destroy all
remcirc
echo "=== Worker 9 [6/6] test_090_tran ==="
source /supp/CUSPICE_public/netlist/single/test_090_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_090_tran.out
destroy all
remcirc
quit
.endc
.end
