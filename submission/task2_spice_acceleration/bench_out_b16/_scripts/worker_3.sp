* Worker 3 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 3 [1/7] test_004_tran ==="
source /supp/CUSPICE_public/netlist/single/test_004_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_004_tran.out
destroy all
remcirc
echo "=== Worker 3 [2/7] test_020_tran ==="
source /supp/CUSPICE_public/netlist/single/test_020_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_020_tran.out
destroy all
remcirc
echo "=== Worker 3 [3/7] test_036_tran ==="
source /supp/CUSPICE_public/netlist/single/test_036_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_036_tran.out
destroy all
remcirc
echo "=== Worker 3 [4/7] test_052_tran ==="
source /supp/CUSPICE_public/netlist/single/test_052_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_052_tran.out
destroy all
remcirc
echo "=== Worker 3 [5/7] test_068_tran ==="
source /supp/CUSPICE_public/netlist/single/test_068_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_068_tran.out
destroy all
remcirc
echo "=== Worker 3 [6/7] test_084_tran ==="
source /supp/CUSPICE_public/netlist/single/test_084_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_084_tran.out
destroy all
remcirc
echo "=== Worker 3 [7/7] test_100_tran ==="
source /supp/CUSPICE_public/netlist/single/test_100_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_100_tran.out
destroy all
remcirc
quit
.endc
.end
