* Worker 0 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 0 [1/7] test_001_tran ==="
source /supp/CUSPICE_public/netlist/single/test_001_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_001_tran.out
destroy all
remcirc
echo "=== Worker 0 [2/7] test_017_tran ==="
source /supp/CUSPICE_public/netlist/single/test_017_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_017_tran.out
destroy all
remcirc
echo "=== Worker 0 [3/7] test_033_tran ==="
source /supp/CUSPICE_public/netlist/single/test_033_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_033_tran.out
destroy all
remcirc
echo "=== Worker 0 [4/7] test_049_tran ==="
source /supp/CUSPICE_public/netlist/single/test_049_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_049_tran.out
destroy all
remcirc
echo "=== Worker 0 [5/7] test_065_tran ==="
source /supp/CUSPICE_public/netlist/single/test_065_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_065_tran.out
destroy all
remcirc
echo "=== Worker 0 [6/7] test_081_tran ==="
source /supp/CUSPICE_public/netlist/single/test_081_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_081_tran.out
destroy all
remcirc
echo "=== Worker 0 [7/7] test_097_tran ==="
source /supp/CUSPICE_public/netlist/single/test_097_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_097_tran.out
destroy all
remcirc
quit
.endc
.end
