* Worker 8 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 8 [1/6] test_009_tran ==="
source /supp/CUSPICE_public/netlist/single/test_009_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_009_tran.out
destroy all
remcirc
echo "=== Worker 8 [2/6] test_025_tran ==="
source /supp/CUSPICE_public/netlist/single/test_025_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_025_tran.out
destroy all
remcirc
echo "=== Worker 8 [3/6] test_041_tran ==="
source /supp/CUSPICE_public/netlist/single/test_041_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_041_tran.out
destroy all
remcirc
echo "=== Worker 8 [4/6] test_057_tran ==="
source /supp/CUSPICE_public/netlist/single/test_057_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_057_tran.out
destroy all
remcirc
echo "=== Worker 8 [5/6] test_073_tran ==="
source /supp/CUSPICE_public/netlist/single/test_073_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_073_tran.out
destroy all
remcirc
echo "=== Worker 8 [6/6] test_089_tran ==="
source /supp/CUSPICE_public/netlist/single/test_089_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_089_tran.out
destroy all
remcirc
quit
.endc
.end
