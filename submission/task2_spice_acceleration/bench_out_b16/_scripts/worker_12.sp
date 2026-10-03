* Worker 12 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 12 [1/6] test_013_tran ==="
source /supp/CUSPICE_public/netlist/single/test_013_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_013_tran.out
destroy all
remcirc
echo "=== Worker 12 [2/6] test_029_tran ==="
source /supp/CUSPICE_public/netlist/single/test_029_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_029_tran.out
destroy all
remcirc
echo "=== Worker 12 [3/6] test_045_tran ==="
source /supp/CUSPICE_public/netlist/single/test_045_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_045_tran.out
destroy all
remcirc
echo "=== Worker 12 [4/6] test_061_tran ==="
source /supp/CUSPICE_public/netlist/single/test_061_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_061_tran.out
destroy all
remcirc
echo "=== Worker 12 [5/6] test_077_tran ==="
source /supp/CUSPICE_public/netlist/single/test_077_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_077_tran.out
destroy all
remcirc
echo "=== Worker 12 [6/6] test_093_tran ==="
source /supp/CUSPICE_public/netlist/single/test_093_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_093_tran.out
destroy all
remcirc
quit
.endc
.end
