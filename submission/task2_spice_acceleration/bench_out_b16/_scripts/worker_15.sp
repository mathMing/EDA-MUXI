* Worker 15 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 15 [1/6] test_016_tran ==="
source /supp/CUSPICE_public/netlist/single/test_016_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_016_tran.out
destroy all
remcirc
echo "=== Worker 15 [2/6] test_032_tran ==="
source /supp/CUSPICE_public/netlist/single/test_032_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_032_tran.out
destroy all
remcirc
echo "=== Worker 15 [3/6] test_048_tran ==="
source /supp/CUSPICE_public/netlist/single/test_048_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_048_tran.out
destroy all
remcirc
echo "=== Worker 15 [4/6] test_064_tran ==="
source /supp/CUSPICE_public/netlist/single/test_064_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_064_tran.out
destroy all
remcirc
echo "=== Worker 15 [5/6] test_080_tran ==="
source /supp/CUSPICE_public/netlist/single/test_080_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_080_tran.out
destroy all
remcirc
echo "=== Worker 15 [6/6] test_096_tran ==="
source /supp/CUSPICE_public/netlist/single/test_096_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_096_tran.out
destroy all
remcirc
quit
.endc
.end
