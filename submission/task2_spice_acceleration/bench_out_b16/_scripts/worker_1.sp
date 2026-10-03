* Worker 1 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 1 [1/7] test_002_tran ==="
source /supp/CUSPICE_public/netlist/single/test_002_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_002_tran.out
destroy all
remcirc
echo "=== Worker 1 [2/7] test_018_tran ==="
source /supp/CUSPICE_public/netlist/single/test_018_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_018_tran.out
destroy all
remcirc
echo "=== Worker 1 [3/7] test_034_tran ==="
source /supp/CUSPICE_public/netlist/single/test_034_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_034_tran.out
destroy all
remcirc
echo "=== Worker 1 [4/7] test_050_tran ==="
source /supp/CUSPICE_public/netlist/single/test_050_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_050_tran.out
destroy all
remcirc
echo "=== Worker 1 [5/7] test_066_tran ==="
source /supp/CUSPICE_public/netlist/single/test_066_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_066_tran.out
destroy all
remcirc
echo "=== Worker 1 [6/7] test_082_tran ==="
source /supp/CUSPICE_public/netlist/single/test_082_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_082_tran.out
destroy all
remcirc
echo "=== Worker 1 [7/7] test_098_tran ==="
source /supp/CUSPICE_public/netlist/single/test_098_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_098_tran.out
destroy all
remcirc
quit
.endc
.end
