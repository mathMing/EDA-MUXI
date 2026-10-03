* Worker 5 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 5 [1/6] test_006_tran ==="
source /supp/CUSPICE_public/netlist/single/test_006_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_006_tran.out
destroy all
remcirc
echo "=== Worker 5 [2/6] test_022_tran ==="
source /supp/CUSPICE_public/netlist/single/test_022_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_022_tran.out
destroy all
remcirc
echo "=== Worker 5 [3/6] test_038_tran ==="
source /supp/CUSPICE_public/netlist/single/test_038_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_038_tran.out
destroy all
remcirc
echo "=== Worker 5 [4/6] test_054_tran ==="
source /supp/CUSPICE_public/netlist/single/test_054_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_054_tran.out
destroy all
remcirc
echo "=== Worker 5 [5/6] test_070_tran ==="
source /supp/CUSPICE_public/netlist/single/test_070_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_070_tran.out
destroy all
remcirc
echo "=== Worker 5 [6/6] test_086_tran ==="
source /supp/CUSPICE_public/netlist/single/test_086_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_086_tran.out
destroy all
remcirc
quit
.endc
.end
