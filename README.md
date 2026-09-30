# 基于沐曦 GPU 的稀疏矩阵求解及 SPICE 加速 (EDA-MUXI)

本项目面向“2026 中国研究生创芯大赛·EDA 精英挑战赛”赛题七（基于沐曦 GPU 的稀疏矩阵求解及 SPICE 加速），由国家集成电路设计自动化技术创新中心与沐曦集成电路（上海）股份有限公司命题。

---

## 目录结构

```
EDA-MUXI/
├── docs/
│   ├── 阶段总结.md                     # 任务一至任务二的完整交接与复盘档案
│   └── sparse_lu_gpu_ngspice_plan.md   # 系统架构与实施规划设计方案
├── include/
│   ├── common.h                        # 基础宏定义与 CUDA / MXMACA 统一兼容层
│   ├── sparse_matrix.h                 # 稀疏矩阵核心数据结构 (CSR/CSC/COO) 与 Matrix Market I/O
│   ├── timer.h                         # 纳秒级高精度计时器 (CPU & GPU 事件)
│   └── error_metrics.h                 # L2 范数相对误差与数值精度评估模块 (≤ 1e-6)
├── src/
│   └── sparse_matrix.cpp               # 稀疏矩阵格式转换与解析实现
├── scripts/
│   ├── generate_circuit_matrix.py      # 标准 MNA 电路稀疏测试矩阵生成器
│   ├── test_nvrtc.py                   # 本地 CUDA JIT 运行环境验证
│   ├── remote_ssh.py                   # 远端沐曦 GPU 服务器自动化交互工具
│   └── test_run_001.py                 # 任务二 test_001 端到端运行与波形三维比对脚本
└── README.md
```

---

## 最新进展与重大突破

### 1. 任务一（GLU 稀疏求解器，60 分）
- **状态**：版本已冻结在 **`V13-candidate`（commit `20b269c`）**，严格遵守红线不擅自改动源码。
- **精度**：**14/14 全 PASS**，对权威 KLU 2.3.6 求解器 $L_2$ 相对误差最坏 $2.155 \times 10^{-8}$（远严于 $10^{-6}$ 门限）。
- **预估得分**：**44 ~ 49 / 60 分**。

### 2. 任务二（CUSPICE / SPICE 仿真加速，40 分）
- **历史疑难破译**：
  前序测试中 `test_001` 对主办方新版 golden 判 FAIL，经排查确认根因在于旧版 `verify_waveform.py` 在低电平平台区计算相对误差时除以接近 0 的瞬时值导致假阳性报警。
  使用主办方最新补充包提供的权威判据脚本（引入平台区相对误差 $\le 2\%$ 或绝对误差 $\le 1.5\%$ 摆幅规则）进行交叉验证：
  ```
  PASS  v(v_out)
  PASS  v(v_inp)
  2 signal(s): 2 pass, 0 fail
  *** ALL CHECKS PASSED ***
  ```
  **`test_001` 在最新权威规则下 100% PASS！正确性地板已彻底稳固。**
- **下一步战役重点**：
  1. 编译 CPU 基线版本以锁定加速比分母；
  2. 跑通 100 个 Datasweep 测试网表的端到端基准；
  3. 针对 100 组参数扫描设计跨任务拓扑与符号分析复用、多任务并发调度与 Batched 批量求解加速。
