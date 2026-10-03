* Worker 10 Robust In-Process Batch Runner
.control
set noaskquit
set filetype=ascii
echo "=== Worker 10 [1/6] test_011_tran ==="
source /supp/CUSPICE_public/netlist/single/test_011_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_011_tran.out
destroy all
remcirc
echo "=== Worker 10 [2/6] test_027_tran ==="
source /supp/CUSPICE_public/netlist/single/test_027_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_027_tran.out
destroy all
remcirc
echo "=== Worker 10 [3/6] test_043_tran ==="
source /supp/CUSPICE_public/netlist/single/test_043_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_043_tran.out
destroy all
remcirc
echo "=== Worker 10 [4/6] test_059_tran ==="
source /supp/CUSPICE_public/netlist/single/test_059_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_059_tran.out
destroy all
remcirc
echo "=== Worker 10 [5/6] test_075_tran ==="
source /supp/CUSPICE_public/netlist/single/test_075_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_075_tran.out
destroy all
remcirc
echo "=== Worker 10 [6/6] test_091_tran ==="
source /supp/CUSPICE_public/netlist/single/test_091_tran.sp
run
linearize v(v_out) v(v_inp)
setplot tran2
print time v(v_out) v(v_inp) > /workspace/bench_out/b16/test_091_tran.out
destroy all
remcirc
quit
.endc
.end
