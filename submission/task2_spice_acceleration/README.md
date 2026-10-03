# 任务二：NGSPICE 端到端仿真与 100 网表 Datasweep 批量加速 交付说明

## 1. 模块总览
本模块针对模拟电路 Sizing 参数扫描场景中的 100 个模拟电路网表（`test_001_tran.sp` ~ `test_100_tran.sp`），构建了基于 4 张沐曦 Mars X201 GPU 的 **16-Worker 分布式流式并发仿真引擎**。

- **波形一致性 (S5 项)**：官方权威评测 `pass=100 fail=0 missing=0`，达成 **100% 满分**（通过率 100/100，零失败、零缺失）；
- **端到端加速比 (S4 项)**：100 个网表全量仿真耗时从串行 CPU 单进程估算基线 1640 秒压缩至 **203.62 秒（服务器 A1 实测 8.05 倍端到端加速）**；
- **核心攻关突破**：引入 NGSPICE 原生 `linearize v(v_out) v(v_inp)` 向量插值引擎，彻底消除因自适应积分步长与均匀步长采样网格不一致造成的 17 个用例假阳性 FAIL。

## 2. 关键脚本资产
* `scripts/eval_16w_batch.py`：**[核心交付件]** 4-GPU 16-worker 分布式并发仿真与全量自动对账流水线；
* `scripts/eval_4gpu_perfect_batch.py`：4-GPU 8-worker 生产级批处理引擎；
* `scripts/test_linearize.py`：波形线性化插值高精度验证工具；
* `scripts/measure_cpu_serial.py`：官方标准 CPU 单线程串行基准耗时（10.01s）测定套件；
* `scripts/profile_ngspice_breakdown.py`：单网表瞬态求解各阶段耗时构成剖析工具。

## 3. 一键运行与全量对账
```bash
# 执行 100 网表 16-worker 分布式并发仿真并自动调用官方脚本对账
bash run_datasweep.sh
```
该命令会自动生成 100 个网表的标准 `.out` 输出文件，并调用官方权威校验脚本输出 `pass=100 fail=0 missing=0`。
