* Worker 13 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 13 [1/6] test_014_tran ==="
source /supp/CUSPICE_public/netlist/single/test_014_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_014_tran.out
destroy all
remcirc
echo "=== Worker 13 [2/6] test_030_tran ==="
source /supp/CUSPICE_public/netlist/single/test_030_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_030_tran.out
destroy all
remcirc
echo "=== Worker 13 [3/6] test_046_tran ==="
source /supp/CUSPICE_public/netlist/single/test_046_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_046_tran.out
destroy all
remcirc
echo "=== Worker 13 [4/6] test_062_tran ==="
source /supp/CUSPICE_public/netlist/single/test_062_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_062_tran.out
destroy all
remcirc
echo "=== Worker 13 [5/6] test_078_tran ==="
source /supp/CUSPICE_public/netlist/single/test_078_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_078_tran.out
destroy all
remcirc
echo "=== Worker 13 [6/6] test_094_tran ==="
source /supp/CUSPICE_public/netlist/single/test_094_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_094_tran.out
destroy all
remcirc
quit
.endc
.end
