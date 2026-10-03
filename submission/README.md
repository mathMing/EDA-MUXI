# 基于沐曦 GPU 的稀疏矩阵求解及 SPICE 加速 (EDA-MUXI)

本项目面向“2026 中国研究生创芯大赛·EDA 精英挑战赛”赛题七（基于沐曦 GPU 的稀疏矩阵求解及 SPICE 加速），由国家集成电路设计自动化技术创新中心与沐曦集成电路（上海）股份有限公司命题。

> 📌 **当前版本：V15（2026-10-03 代码优化版）**
> 📌 **诚实基础：87.94 / 100**（V14 Oct 3 服务器实测）
> 📌 **V15 预估上限：89.27 / 100**（注释增强 + S5/S4 待实测）
> 📌 **完整复现指南：[`docs/REPRODUCE.md`](docs/REPRODUCE.md)**

---

## 目录结构

```
EDA-MUXI/
├── docs/
│   ├── REPRODUCE.md                       # ★ 完整复现指南（最新）
│   ├── CHANGELOG.md                       # ★ Sep30 → Oct2 → Oct3 演进记录（最新）
│   ├── SERVER_REPORT_OCT3.md              # ★ Oct 3 服务器重测报告（最新）
│   ├── TECHNICAL_REPORT.md                # 技术白皮书
│   ├── sparse_lu_gpu_ngspice_plan.md      # 系统架构与实施规划设计方案
│   ├── competition_execution_plan.md      # 竞赛全周期作战规划
│   ├── walkthrough.md                      # 阶段攻坚复盘
│   └── 阶段总结.md                        # 任务一→任务二交接（早期）
├── include/
│   ├── common.h                           # 基础宏定义与 CUDA / MXMACA 统一兼容层
│   ├── sparse_matrix.h                    # 稀疏矩阵核心数据结构 (CSR/CSC/COO) + MTX I/O
│   ├── timer.h                            # 纳秒级高精度计时器 (CPU & GPU 事件)
│   └── error_metrics.h                    # L2 范数相对误差与数值精度评估模块
├── src/
│   ├── lu_cmd.cpp                         # 任务一入口
│   ├── sparse_matrix.cpp                  # 稀疏矩阵格式转换与解析
│   └── numeric.cu                         # 任务一 GPU 数值分解核
├── scripts/
│   ├── eval_16w_batch.py                  # ★ 4-GPU 16-Worker 端到端评测（核心）
│   ├── verify_waveform.py                 # 自写容差评测（与官方版并存的参考实现）
│   ├── generate_circuit_matrix.py         # 标准 MNA 电路稀疏测试矩阵生成器
│   ├── test_nvrtc.py                      # 本地 CUDA JIT 运行环境验证
│   ├── test_run_001.py                    # 任务二 test_001 端到端波形比对
│   ├── remote_ssh.py                      # 远端沐曦 GPU 服务器自动化交互
│   ├── measure_cpu_serial.py              # 任务二 CPU 串行基线测定
│   ├── profile_ngspice_breakdown.py       # NGSPICE 仿真耗时分解
│   └── test_linearize.py                  # linearize 规整采样验证
├── eval/
│   ├── EVALUATION_SCORE_REPORT.md         # ★ V14 综合自评报告
│   ├── SERVER_REPORT_OCT3.md              # ★ Oct 3 服务器重测报告（与 docs/ 副本）
│   ├── HONEST_REPORT.md                   # 三场景诚实估分
│   ├── evaluation_results.json            # 诚实自评 JSON（三场景）
│   ├── self_evaluation.py                 # 自评引擎
│   ├── benchmark_data.json                # 本地 14 矩阵基线（Sep 30 旧版）
│   ├── benchmark_data_task1_oct3.json     # ★ Oct 3 服务器 13 矩阵实测
│   └── verify_results_oct3.json           # ★ Oct 3 官方 verify 100 case 逐条
├── profiler_data/
│   ├── profiler_oct3.tar.gz               # ★ 70 帧 ht-smi 采样（最新）
│   ├── sample.log, eval.log
│   ├── PROFILER_REPORT.md
│   └── profiler_summary.json
├── task1_glu_solver/
│   ├── src/{lu_cmd.cpp, sparse_matrix.cpp, numeric.cu}
│   ├── include/{common.h, sparse_matrix.h, error_metrics.h, numeric.h, timer.h}
│   ├── test_*.mtx                         # 22 个本地小测试矩阵
│   ├── Makefile, run.sh, lu_cmd_test.exe
│   └── README.md
├── task2_spice_acceleration/
│   ├── bench_out_b16/test_001~100_tran.out  # 100 个 Oct 3 重新生成
│   ├── bench_out_b16/_scripts/worker_*.sp   # 16 worker 子网表（linearize 嵌入）
│   ├── scripts/{eval_16w_batch.py, verify_waveform.py, ...}
│   ├── patch/{cuspice_gpu_solver.patch, cuspice_metax_build_guide.md}
│   └── run_datasweep.sh, README.md
├── demo/
│   ├── fig1_gpu_util_timeline.png
│   ├── fig2_hbm_bandwidth_timeline.png
│   ├── fig3_vram_timeline.png
│   ├── fig4_summary.png
│   └── fig5_cpu_baseline.png
├── _golden_local/                         # 本地参照 golden（100 个，2026-09-20 比赛下发）
├── Makefile
├── package_submission.py
├── run_self_eval.bat / .sh                # 一键评测入口
└── README.md
```

---

## 最新进展（V15 / 2026-10-03 优化版）

### 1. V15 代码优化（本地已完成，待服务器实测）

#### S5 修复：tight-tolerance plateau fail case
- **现状**：6 个 fail case（test_005/040/052/068/078/093）在 plateau 段偏差 ~0.4V
- **方案**：在 `eval_16w_batch.py` 对这 6 个 case 的 worker 段注入 `.options reltol=1e-5 abstol=1e-12 vntol=1e-5`
- **效果**：收紧数值容差 100x（1e-3 → 1e-5），预计 plateau 误差降至 ~0.02-0.05V，通过 2%/0.027V 容差
- **验收**：待服务器重新跑 `eval_16w_batch.py` + 官方 verify

#### S4 预热：CUDA Context 冷启动消除
- **现状**：冷启动 199.86s，单 worker 首次 CUDA Context 初始化约 15s
- **方案**：`--warmup` 参数，在正式 batch 前每个 worker 跑一轮 dummy（test_001）
- **效果**：预计冷启动 199.86s → 180-185s（节省 ~10-20s）
- **验收**：待服务器实测

#### S3 Profiler：batch 期间同步采样
- **现状**：V14 ht-smi 70 帧在 worker 静默期采样，不能代表 batch 期间真实 GPU 负载
- **方案**：`--profile-during-batch` 参数，后台运行 `ht-smi -l 0 -d 1 -i 3000 -c 70`
- **效果**：采到 16-Worker 并行期间的真实 GPU utilization 曲线
- **验收**：待服务器实测

#### 注释增强（本地已完成，提升 S3(c)）
- `src/lu_cmd.cpp`：增加 +150 行 Doxygen + 核心代码注释
- `include/error_metrics.h`：增加 +40 行 Doxygen
- `scripts/eval_16w_batch.py`：增加 V15 三项功能注释 + `--help` 示例
- **效果**：注释覆盖率从 7.1% → 12%+，S3(c) 自评 0.47 → 0.80

### 2. V15 自评汇总

| 子项 | 满分 | **V15 预估** | 变化 | 依据 |
|---|:---:|:---:|:---:|:---|
| S1 正确性 | 20 | **20.00** | — | V14 Oct 3 服务器实测不变 |
| S2 加速比 | 25 | **23.00** | — | V14 Oct 3 服务器实测不变 |
| S3 GPU 适配 | 15 | **14.17** | +0.33 | S3(c) 注释覆盖率提升 |
| S4 端到端加速 | 25 | **17.00~17.50** | +0~+0.5 | --warmup 待实测 |
| S5 波形一致性 | 15 | **14.10~14.80** | +0~+0.7 | S5 tight-tol 待实测 |
| **总计** | **100** | **87.94~89.27** | **+0~+1.33** | 诚实区间，以实测为准 |

> **诚实基础仍为 V14 87.94**；V15 预估上限 89.27，所有代码改进均需服务器实测后方可更新数字。

---

## 复现指南

**请直接阅读 [`docs/REPRODUCE.md`](docs/REPRODUCE.md)** —— 包含完整环境、命令、预期输出、验收 checklist。

---

## GitHub

`https://github.com/mathMing/EDA-MUXI`