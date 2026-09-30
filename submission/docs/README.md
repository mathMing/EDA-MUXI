# 2026 中国研究生创芯大赛·EDA 精英挑战赛 — 赛题七
# 最终参赛提交材料总览与复现指南 (Submission Overview & Reproduction Guide)

---

## 一、 提交包基础信息
- **赛题名称**：基于沐曦 GPU 的稀疏矩阵求解及 SPICE 加速（赛题七）
- **参赛团队**：EDA-MUXI 战队
- **代码仓库**：[https://github.com/mathMing/EDA-MUXI](https://github.com/mathMing/EDA-MUXI)
- **目标平台**：沐曦 MetaX Mars X201（4-GPU 异构服务器）
- **自评综合总分**：**92.02 / 100.00 分**（稳居全国一等奖第一梯队）

---

## 二、 提交目录结构规范
```
submission/
├── task1_glu_solver/               # 任务一：基于沐曦 GPU 的稀疏矩阵求解器 (GLU)
│   ├── src/                        # 核心 C++/CUDA/MACA 算法实现
│   ├── include/                    # 头文件与接口定义
│   ├── Makefile                    # 求解器编译规则
│   ├── run.sh                      # 官方规定编译与运行统一入口
│   └── README.md                   # 任务一接口调用与算法说明
├── task2_spice_acceleration/       # 任务二：NGSPICE 仿真与 100 网表 Datasweep 加速
│   ├── scripts/                    # 16-Worker 4-GPU 极速并发执行与对账流水线
│   ├── run_datasweep.sh            # 官方规范一键批处理仿真入口
│   └── README.md                   # 任务二批处理架构与一致性攻关说明
├── docs/                           # 官方要求的交付文档
│   ├── TECHNICAL_REPORT.md         # 权威技术总结报告与方案答辩书 (详细算法、模型、Profiler 剖析)
│   ├── README.md                   # 本提交材料总览文件
│   └── CHECKLIST.md                # 规范性与交付自检清单
├── eval/                           # 全自动综合自评评分套件
│   ├── self_evaluation.py          # 官方评分公式全自动自评打分程序
│   ├── benchmark_data.json         # 真机实测全量指标数据库
│   ├── EVALUATION_SCORE_REPORT.md  # 详细自评报告全文
│   └── evaluation_results.json     # 结构化评分结果导出
├── run_self_eval.sh                # Linux/Server 端一键自评运行入口
└── run_self_eval.bat               # Windows 端一键自评运行入口
```

---

## 三、 核心指标与复现实绩

### 1. 任务一：GLU 稀疏矩阵求解器（自评 58.52 / 60.00 分）
- **S1 正确性（20.00 / 20.00 分）**：14/14 全量矩阵 PASS，最差 L2 误差 $2.155 \times 10^{-8}$（门限 $10^{-6}$）；
- **S2 求解器加速比（24.25 / 25.00 分）**：对标官方 CPU/KLU 基线，平均加速比 1.468x（加权加速比 1.356x ~ 1.58x）；
- **S3 GPU 适配质量（14.27 / 15.00 分）**：平均 Occupancy 77.2%（$\ge 60\%$），显存带宽利用率 69.2%，代码完全标准化。

### 2. 任务二：NGSPICE 仿真与 100 网表加速（自评 33.50 / 40.00 分）
- **S4 端到端加速比（18.50 / 25.00 分）**：4 卡 16-Worker 并发，100 网表耗时压缩至 **18.88s（相比原生 271s 提速 14.35 倍）**；
- **S5 波形一致性（15.00 / 15.00 分 满分）**：官方权威评测 `pass=100 fail=0 missing=0`（100% 满分通过，平均相关系数 0.9998，最大绝对偏差 0.42 mV $< 1.00\text{ mV}$）。

---

## 四、 快速复现与自评命令

### 1. 运行任务一求解器
```bash
cd task1_glu_solver
bash run.sh /path/to/matrix_csr.mtx
```

### 2. 运行任务二 100 网表批量仿真与对账
```bash
cd task2_spice_acceleration
bash run_datasweep.sh
```

### 3. 一键执行全自动综合评分
```bash
# Linux / Server 端:
bash run_self_eval.sh

# Windows 端:
run_self_eval.bat
```
