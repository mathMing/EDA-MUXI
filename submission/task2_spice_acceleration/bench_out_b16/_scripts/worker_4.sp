* Worker 4 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 4 [1/6] test_005_tran ==="
source /supp/CUSPICE_public/netlist/single/test_005_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_005_tran.out
destroy all
remcirc
echo "=== Worker 4 [2/6] test_021_tran ==="
source /supp/CUSPICE_public/netlist/single/test_021_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_021_tran.out
destroy all
remcirc
echo "=== Worker 4 [3/6] test_037_tran ==="
source /supp/CUSPICE_public/netlist/single/test_037_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_037_tran.out
destroy all
remcirc
echo "=== Worker 4 [4/6] test_053_tran ==="
source /supp/CUSPICE_public/netlist/single/test_053_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_053_tran.out
destroy all
remcirc
echo "=== Worker 4 [5/6] test_069_tran ==="
source /supp/CUSPICE_public/netlist/single/test_069_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_069_tran.out
destroy all
remcirc
echo "=== Worker 4 [6/6] test_085_tran ==="
source /supp/CUSPICE_public/netlist/single/test_085_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_085_tran.out
destroy all
remcirc
quit
.endc
.end
