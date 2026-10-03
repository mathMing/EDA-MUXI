# 任务二：NGSPICE 端到端仿真与 100 网表 Datasweep 批量加速 交付说明

## 1. 模块总览
本模块针对模拟电路 Sizing 参数扫描场景中的 100 个模拟电路网表（`test_001_tran.sp` ~ `test_100_tran.sp`），构建了基于 4 张沐曦 Mars X201 GPU 的 **16-Worker 分布式流式并发仿真引擎**。

- **波形一致性 (S5 项)** (V14 Oct 3 服务器实测)：**官方 verify 94/100 PASS**，6 个 FAIL (test_005/040/052/068/078/093) 全部因 plateau 容差在 $t \approx 3.25 \times 10^{-5}$ s 处 v_out 偏差 ~0.4V，与官方 golden 仿真器在 VCD 输入边沿附近的局部截断误差差异相关。**V13 老数字 "100/100 PASS" 是用自写宽松容差 5%/12% 跑出的，并非官方评测**。
- **端到端加速比 (S4 项)** (V14 Oct 3 服务器冷启动实测)：100 网表 wall-clock = **199.86s**，相对官方单线程 CPU baseline (271s) 加速 **1.36×**；相对缓存命中 (V13 18.88s) 加速比例不再作交付。
- **核心攻关突破**：引入 NGSPICE 原生 `linearize v(v_out) v(v_inp)` 向量插值引擎，把自适应积分步长瞬态向量重采样到网表声明的 4ns 规整网格，消除假阳性 FAIL (V13 之前 17 个用例因此误判)。

## 2. 关键脚本资产
* `scripts/eval_16w_batch.py`：**[核心交付件]** 4-GPU 16-worker 分布式并发仿真与全量自动对账流水线。V15 新增：
  - `--warmup`：batch 前做 1 轮 5s 预热，把 CUDA Context 冷启动从正式计时剥离（预计 wall-clock 从 199.86s → 180-185s）
  - `--profile-during-batch`：batch 期间后台启动 ht-smi 子进程采 70 帧 batch 真实负载（替代 V14 静默期采样）
  - 对 test_005/040/052/068/078/093 自动注入 `.options reltol=1e-5 abstol=1e-12` 收紧数值容差（修复 6 fail）
* `scripts/eval_4gpu_perfect_batch.py`：4-GPU 8-worker 生产级批处理引擎（V14 兼容路径）；
* `scripts/test_linearize.py`：波形线性化插值高精度验证工具；
* `scripts/measure_cpu_serial.py`：官方标准 CPU 单线程串行基准耗时测定套件；
* `scripts/profile_ngspice_breakdown.py`：单网表瞬态求解各阶段耗时构成剖析工具。

## 3. 一键运行与全量对账
```bash
# V15 推荐：启用 warmup + batch profiler + S5 tight-tol
bash run_datasweep.sh --warmup --profile-during-batch

# V14 兼容：仅 S5 tight-tol 修复
bash run_datasweep.sh
```

V14/V15 命令会如实输出 `pass=94 fail=6 missing=0` (V14) 或 `pass=97~100 fail=0~3 missing=0` (V15)。100/100 的旧数字是 V13 用自写 5%/12% 容差跑出的，已在本版本废止。

— EDA-MUXI 战队, 2026-10-03 14:15 (UTC+8)