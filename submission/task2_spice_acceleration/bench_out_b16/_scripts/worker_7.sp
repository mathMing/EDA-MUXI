* Worker 7 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 7 [1/6] test_008_tran ==="
source /supp/CUSPICE_public/netlist/single/test_008_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_008_tran.out
destroy all
remcirc
echo "=== Worker 7 [2/6] test_024_tran ==="
source /supp/CUSPICE_public/netlist/single/test_024_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_024_tran.out
destroy all
remcirc
echo "=== Worker 7 [3/6] test_040_tran ==="
source /supp/CUSPICE_public/netlist/single/test_040_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_040_tran.out
destroy all
remcirc
echo "=== Worker 7 [4/6] test_056_tran ==="
source /supp/CUSPICE_public/netlist/single/test_056_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_056_tran.out
destroy all
remcirc
echo "=== Worker 7 [5/6] test_072_tran ==="
source /supp/CUSPICE_public/netlist/single/test_072_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_072_tran.out
destroy all
remcirc
echo "=== Worker 7 [6/6] test_088_tran ==="
source /supp/CUSPICE_public/netlist/single/test_088_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_088_tran.out
destroy all
remcirc
quit
.endc
.end
