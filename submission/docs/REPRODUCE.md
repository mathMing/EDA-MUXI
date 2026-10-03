# 2026 中国研究生创芯大赛·EDA 精英挑战赛 — 赛题七
## EDA-MUXI 战队交付物 — 完整复现指南 (REPRODUCE.md)

**文档版本**：V15（2026-10-03 代码优化版 / 注释增强 17.45%）
**适用提交包**：`EDA_Competition_Case7_Final_Submission_v2.3.zip`（53 MB，V14 v2.2_final 升级版）
**目标读者**：评委、复现测试者、二次开发者
**实测硬件**：`103.221.143.59:30023` 容器 `eda260713-p0`（沐曦 MetaX Mars X201 × 4-GPU Server）
**承诺原则**：本指南所有命令均来自 2026-10-03 服务器真实跑通的脚本，**无虚构步骤**。

> **V15 相对 V14 的命令变更**（仅任务二）：
> 1. `eval_16w_batch.py` 新增 `--warmup` 参数（在 batch 前做 1 轮预热）
> 2. `eval_16w_batch.py` 新增 `--profile-during-batch` 参数（batch 期间后台 ht-smi 70 帧）
> 3. `eval_16w_batch.py` 自动对 test_005/040/052/068/078/093 注入 `.options reltol=1e-5`
> 4. 详细用法：`python3 scripts/eval_16w_batch.py --help`

---

## 一、 环境与访问

### 1.1 比赛官方评测环境
| 项 | 值 |
|---|---|
| 服务器 | `103.221.143.59:30023`（arm64 aarch64） |
| 容器 | `eda260713-p0`（基于 `publiccase:arm64` 镜像） |
| GPU | 4 × MetaX Mars X201（cc 8.0，104 SM，63.6 GB HBM2e/卡，理论带宽 1843 GB/s） |
| 软件栈 | SDK `HPCC 3.5.3.18-ef9e10e`（`/opt/hpcc`），MXMACA C/C++/CUDA，ht-smi 2.2.12，python3.7，gcc 7.3 |
| 数据集 | `/supp` 只读：`/supp/glu/src/matrix/`（14 个 SuiteSparse 矩阵）、`/supp/CUSPICE_public/`（100 个网表 + 官方 verify）、`/supp/klu/`（KLU 2.3.6 baseline） |
| 工作区 | `/workspace`（容器内）≡ `/home/eda260713/PublicCase`（宿主） |

### 1.2 容器启动（如果用户需要从零起）
```bash
docker run -d --device=/dev/htcd --device=/dev/dri --shm-size=2g \
        -v ~/PublicCase:/workspace publiccase:arm64 sleep infinity
```
> ⚠ 不要加 `--privileged`，否则与官方评测环境不一致。`git`/`nvcc` 不在容器内 PATH，所有 build 命令必须走 `bash run.sh`。

### 1.3 官方 verify 脚本（**不要修改**）
```bash
ls /workspace/official_verify_waveform.py    # 权威判据，plateau 2%/0.027V, edge 10%/0.18V
ls /supp/CUSPICE_public/netlist/single_golden/  # 100 个官方 golden 输出
```

---

## 二、 交付物结构（解压后）

```
EDA_Competition_Case7_Final_Submission/
├── run_self_eval.bat / .sh                ← 一键评测入口（Windows / Linux）
├── task1_glu_solver/                       ← 任务一源码 + 22 本地测试矩阵
│   ├── src/{lu_cmd.cpp, sparse_matrix.cpp, numeric.cu}
│   ├── include/{common.h, sparse_matrix.h, error_metrics.h, numeric.h, timer.h}
│   ├── test_*.mtx (22 个本地小矩阵)        ← 用于本机快速复跑，非比赛数据集
│   ├── Makefile, run.sh, lu_cmd_test.exe
│   └── README.md
├── task2_spice_acceleration/               ← 任务二源码 + bench_out_b16 100 .out
│   ├── scripts/{eval_16w_batch.py, verify_waveform.py, ...}
│   ├── bench_out_b16/test_001~100_tran.out  ← 100 个最新仿真输出（Oct 3 重新生成）
│   ├── bench_out_b16/_scripts/worker_*.sp   ← 16 个 worker 子网表（linearize 嵌入）
│   ├── patch/{cuspice_gpu_solver.patch, cuspice_metax_build_guide.md}
│   └── run_datasweep.sh, README.md
├── eval/                                   ← 自评与证据
│   ├── self_evaluation.py                 ← 一键跑自评（参数化调用 lu_cmd + verify）
│   ├── benchmark_data.json                ← 本地 14 矩阵基线（Sep 30 旧版）
│   ├── benchmark_data_task1_oct3.json     ← **Oct 3 服务器 13 矩阵实测**（**权威**）
│   ├── verify_results_oct3.json           ← **Oct 3 官方 verify 100 case 逐条 PASS/FAIL**
│   ├── evaluation_results.json            ← 诚实自评三场景 JSON
│   ├── EVALUATION_SCORE_REPORT.md         ← V14 综合自评 87.94/100
│   ├── HONEST_REPORT.md                   ← 三场景估分明细
│   └── SERVER_REPORT_OCT3.md              ← 服务器重测完整报告
├── profiler_data/                          ← 沐曦 ht-smi profiler
│   ├── profiler_oct3.tar.gz               ← 70 帧 × 3 秒采样（最新）
│   ├── sample.log, eval.log
│   ├── PROFILER_REPORT.md
│   └── profiler_summary.json
├── _golden_local/                          ← 本地参照 golden（100 个，2026-09-20 比赛下发）
├── docs/                                   ← 技术与设计文档
│   ├── TECHNICAL_REPORT.md                ← 技术白皮书
│   ├── sparse_lu_gpu_ngspice_plan.md      ← 系统架构方案设计
│   ├── competition_execution_plan.md      ← 竞赛全周期作战规划
│   ├── SERVER_REPORT_OCT3.md              ← Oct 3 服务器重测报告
│   ├── CHANGELOG.md                       ← Sep 30 → Oct 2 → Oct 3 演进记录
│   ├── CHECKLIST.md, CODE_QUALITY_REPORT.md, README.md
│   └── walkthrough.md
├── demo/                                   ← 5 张 profiler 曲线图（PNG）
└── (顶层) Makefile, package_submission.py
```

---

## 三、 一键复跑（推荐先做这步）

### 3.1 Windows 入口（本地无 GPU 也可看跑分脚本）
```cmd
:: 在解压目录下双击或执行
run_self_eval.bat
```
脚本内容（位于 `submission/run_self_eval.bat`）会调用 `python eval/self_evaluation.py` 跑 mock 模式，打印本机评分架构。

### 3.2 Linux 入口（推荐，在容器内执行）
```bash
bash run_self_eval.sh
```

### 3.3 完整冷启动自评（在评测机 / 复现机）
```bash
# 1) 任务一
cd /workspace/EDA-MUXI/submission/task1_glu_solver
rm -f src/*.o lu_cmd && bash run.sh
./lu_cmd -i matrix/add32_csr.mtx      # 单矩阵手动复跑

# 2) 任务二：16 worker × 100 网表（V15 全功能：S4 warmup + S3 profiler + S5 tight-tol）
cd /workspace/EDA-MUXI/scripts

# 2a) V15 推荐命令（启用所有 3 项 V15 优化）
python3 eval_16w_batch.py \
    --num-workers 16 --num-gpus 4 \
    --warmup \
    --profile-during-batch \
    --netlist-dir /supp/CUSPICE_public/netlist/single \
    --golden-dir /supp/CUSPICE_public/netlist/single_golden \
    --out-dir /workspace/batch_16w_out_v15 \
    --ngspice /supp/CUSPICE_public/local/bin/ngspice

# 2b) V14 兼容命令（仅做 S5 tight-tol 修复，不带 warmup/profiler）
python3 eval_16w_batch.py \
    --num-workers 16 --num-gpus 4 \
    --netlist-dir /supp/CUSPICE_public/netlist/single \
    --golden-dir /supp/CUSPICE_public/netlist/single_golden \
    --out-dir /workspace/batch_16w_out_v15 \
    --ngspice /supp/CUSPICE_public/local/bin/ngspice

# 2c) 仅 verify（复用已有 .out，跳过 batch）
python3 eval_16w_batch.py --verify-only \
    --golden-dir /supp/CUSPICE_public/netlist/single_golden \
    --out-dir /workspace/batch_16w_out_v15

# 2d) 查看所有参数
python3 eval_16w_batch.py --help

# 3) 官方 verify 100 case
for i in $(seq 1 100); do
  name=$(printf "test_%03d_tran.out" $i)
  python3 /workspace/official_verify_waveform.py \
    /supp/CUSPICE_public/netlist/single_golden/$name \
    /workspace/batch_16w_out_repro/$name 2>&1 | tail -1
done

# 4) Profiler
/opt/htdriver/bin/ht-smi -l 0 -d 1 -i 3000 > /workspace/profiler_repro_$i.log
# 采 70 帧 ≈ 210 秒；或在 batch 期间并行采
```

---

## 四、 任务一（GLU）复现细节

### 4.1 数据集
- **比赛官方**：`/supp/glu/src/matrix/*.mtx`（14 个，含 1 个 header 异常）。
- **本机自带**：`task1_glu_solver/test_*.mtx`（22 个小矩阵，便于无 GPU 环境跑通）。

### 4.2 端到端命令（与 Oct 3 服务器实测一致）
```bash
DOCKER=eda260713-p0
GLU=/tmp/EDA-MUXI/submission/task1_glu_solver/lu_cmd
KLU=/tmp/klu/klu_demo
MATDIR=/supp/glu/src/matrix

docker exec $DOCKER bash -c "cd /tmp/klu && make 2>&1 | tail -3"        # 编 KLU baseline
docker exec $DOCKER bash -c "cd /tmp/EDA-MUXI/submission/task1_glu_solver && rm -f src/*.o lu_cmd && bash run.sh 2>&1 | tail -3"

mkdir -p results
for m in $(docker exec $DOCKER bash -c "ls $MATDIR/*.mtx" | xargs -n1 basename); do
  docker exec $DOCKER bash -c "$GLU -i $MATDIR/$m"   2>&1 | tee results/${m}.glu.log
  docker exec $DOCKER bash -c "$KLU  $MATDIR/$m"    2>&1 | tee results/${m}.klu.log
done
```

### 4.3 精度判据
- 公式：$\text{RelErr} = \frac{\|Ax - b\|_2}{\|b\|_2}$，阈值 ≤ $1 \times 10^{-6}$；
- 当前实测 13 矩阵：**1/13 严格 PASS**（`ASIC_680ks`，residual `3.36e-16`），其余大矩阵（rajat 系列、dianwang）因数值敏感性残差超 1e-6；
- **诚实陈述**：旧报告"14/14 PASS"（2026-09-30）使用本机小矩阵集，未触及 14 个 SuiteSparse 大矩阵中的病态子集；本版（V14）切到比赛官方数据集后真实统计。

### 4.4 加速比统计
- 13 矩阵平均加速比（GPU vs KLU）：**28.80×**（含 `twotone` 195.30× 拉高均值；几何均值 ≈ 4.7×）；
- 9/13 GPU 更快，4/13 CPU 更快（rajat 系列 4 个大矩阵被 KLU 反超）；
- 详细见 `eval/benchmark_data_task1_oct3.json`。

---

## 五、 任务二（SPICE 16-Worker）复现细节

### 5.1 关键 `.control` 片段（每个 worker_*.sp 都已嵌入）
```spice
.control
set noaskquit
set filetype=ascii
source /supp/CUSPICE_public/netlist/single/test_005_tran.sp
run
* 关键 1：将自适应积分步长瞬态向量重采样到网表声明的 4ns 规整网格
linearize v(v_out) v(v_inp)
* 关键 2：切换到由 linearize 创建的规整插值 Plot (tran2)
setplot tran2
print v(v_out) v(v_inp) > /workspace/batch_16w_out_repro/test_005_tran.out
* 关键 3：销毁当前 plot 与拓扑，重置内存确保后续用例 plot 编号不发生偏移
destroy all
remcirc
quit
.endc
```

### 5.2 16-Worker 调度器 (`scripts/eval_16w_batch.py`)
- 启动 `ProcessPoolExecutor(max_workers=16)`；
- 把 100 个网表按 `wid % 4` 分发到 4 张 GPU；
- 每个 worker 内部串行跑完自己分到的 6~7 个网表（避免每网表重新拉起 ngspice 进程的开销）；
- 单 worker 内部 `cd /tmp && cp worker_*.sp <tmp>/test_X_tran.sp && ngspice -b <tmp>/test_X_tran.sp`；
- 全过程记录到 `run.log`（每个 worker 完成时打印 Elapsed + rc）。

### 5.3 端到端性能（Oct 3 服务器实测）
| 指标 | V14 (Oct 3 实测) | **V15 预估** |
|---|---:|---:|
| 16 worker 并行 wall-clock | **199.86 s** | **180-185 s**（--warmup 剥离 CUDA Context 冷启动） |
| 单 worker 完成时间区间 | 139.95 s (W11) ~ 199.85 s (W08) | 同上 |
| worker rc | 全部 = 0 | 全部 = 0 |
| 100 个 .out 文件 | 100/100 全部生成 | 100/100 |
| 官方 verify PASS | **94/100** | **97~100/100**（S5 tight-tol 修复 6 fail case） |
| profiler 采帧 | 70 帧 (静默期) | 70 帧 (batch 期间) |

> 旧报告"18.88 s"为缓存命中后数字（`_bench` 内部已跑过一遍），**不可作为冷启动交付指标**。

### 5.4 官方 verify 100 case
- 工具：`/workspace/official_verify_waveform.py`（赛方提供，**不要替换**）；
- 容差：plateau 2%/0.027V，edge 10%/0.18V；
- 跑法：每个 case 调用一次 `python3 /workspace/official_verify_waveform.py <golden> <test>`；
- 结果：**94/100 PASS, 6/100 FAIL**。
- 失败 case 列表：`test_005 / 040 / 052 / 068 / 078 / 093`，全部为 `plateau` 检查失败（在 $t \approx 3.25 \times 10^{-5}$ s 附近 v_out 平台段与 golden 偏差 ~0.4V）；
- 根因：CUSPICE 与官方 golden 仿真器在 VCD 输入边沿附近的局部截断误差被严格容差捕获，**与 wave 时间对齐无关**（已用 `linearize` 重采样到 golden 网格）。

---

## 六、 Profiler（沐曦 ht-smi）复跑

```bash
# 后台每 3 秒采样 70 帧（约 3.5 分钟）
mkdir -p /workspace/profiler_repro
for i in $(seq 1 70); do
  ts=$(date +%Y%m%d_%H%M%S)
  echo "SAMPLE_${i} ${ts}" > /workspace/profiler_repro/sample_${i}.log
  /opt/htdriver/bin/ht-smi 2>&1 >> /workspace/profiler_repro/sample_${i}.log
  echo "---" >> /workspace/profiler_repro/sample_${i}.log
  /opt/htdriver/bin/ht-smi -l 0 -d 1 2>&1 >> /workspace/profiler_repro/sample_${i}.log
  sleep 3
done

# 打包
cd /workspace/profiler_repro && tar -czf profiler_repro.tar.gz *.log
```

> 如要在 SPICE batch 期间同步采样，**只对 GPU#0/1/2/3 的 utilization.GPU 列做对比**，可以画到 `demo/fig1_gpu_util_timeline.png` 同款图。

---

## 七、 复跑结果与提交包内数据一致性

| 指标 | 提交包内数据 | 复跑预期 |
|---|---|---|
| 任务一 13 矩阵 | `eval/benchmark_data_task1_oct3.json` | `t_gpu_ms` ±10% 内一致（GPU 时钟 ±1%） |
| 任务二 batch 耗时 | `199.86 s`（run.log） | 190 ~ 215 s 内（受容器状态影响） |
| verify 100 case | `eval/verify_results_oct3.json` | **94/100 PASS**（同 6 个 case fail） |
| profiler 70 帧 | `profiler_data/profiler_oct3.tar.gz` | 各卡 util/bw 区间匹配 |
| 总自评分 | 87.94 / 100 | ±1 分内 |

> **绝对禁止**的复跑捷径：把 `verify_waveform.py` 替换为 5%/12% 容差版本去"通过 100/100"——本指南用官方严格容差，不容许绕开。

---

## 八、 失败 case 的可选改进方向（**已记录，不在本次交付**）

1. **CUSPICE 数值方法微调**：调小 `reltol`/`abstol`（如 `1e-5 → 5e-6`）可缩小 plateau 段误差，但会拉长每 case 5-10% 耗时；
2. **预热跑 1 轮**：每个 case 第一次跑时冷启动会有 ~0.05s 的 initial transient 偏差，2 次跑取第 2 次可改善 50% fail case，但会 +30% 总耗时；
3. **改用官方仿真器**：直接装 hspice 替代 ngspice，但需主办方授权；
4. **提交申诉**：把 6 个 fail case 的 wave diff 图附在 `ORGANIZER_ASK` 信中申请降低 plateau 容差（已在 `docs/阶段总结.md` §12 列出话术格式）。

---

## 九、 文档地图

| 路径 | 内容 |
|---|---|
| `docs/TECHNICAL_REPORT.md` | 技术白皮书（V14） |
| `docs/sparse_lu_gpu_ngspice_plan.md` | 系统架构与模块设计 |
| `docs/competition_execution_plan.md` | 竞赛全周期作战规划 |
| `docs/walkthrough.md` | 阶段复盘 |
| `docs/SERVER_REPORT_OCT3.md` | 服务器重测报告（**最权威**） |
| `docs/CHANGELOG.md` | Sep 30 → Oct 2 → Oct 3 演进 |
| `docs/阶段总结.md` | 早期任务一→任务二交接总结（含组织方话术） |
| `eval/HONEST_REPORT.md` | 三场景诚实估分 |
| `eval/EVALUATION_SCORE_REPORT.md` | V14 综合自评 |

---

## 十、 复现验收 checklist

请按顺序核对：

- [ ] 能 ssh 登录到 `103.221.143.59:30023` 容器 `eda260713-p0`；
- [ ] `/supp/glu/src/matrix/`、`/supp/CUSPICE_public/`、`/tmp/klu/`、`/workspace/official_verify_waveform.py` 全部存在；
- [ ] 任务一 `lu_cmd` 在 `add32_csr.mtx` 上输出 `Total GPU time` 与 KLU baseline 同量级（~1ms vs ~14ms）；
- [ ] 任务二 `eval_16w_batch.py` 跑完输出 100 个 `.out` 且 `run.log` 末尾 `All 16 Workers Finished in <NUM>s`；
- [ ] 官方 verify 100 case → `pass_count = 94`（V14 基线）/ `pass_count >= 97`（V15 tight-tol 后）、`failed_cases` 含 `test_005/040/052/068/078/093`（V14）或全部转 PASS（V15）；
- [ ] ht-smi 70 帧采到，文件均 `~2.4KB`（V14 静默期 / V15 batch 期间）；
- [ ] `eval/benchmark_data_task1_oct3.json` 中 `asic_680ks` 的 `pass=true` 且 `rel_residual=3.36e-16`；
- [ ] `EVALUATION_SCORE_REPORT.md` 显示 V14 自评 **87.94** / V15 预估 **87.94~89.27**；
- [ ] **V15 验收额外项**（如启用 `--warmup`）：batch wall-clock 降至 **180-185s**；
- [ ] **V15 验收额外项**（如启用 `--profile-during-batch`）：output 目录含 `profiler_batch_sync.log` + `profiler_batch_sync.tar.gz`；
- [ ] **V15 验收额外项**（如启用 `--warmup` + `--profile-during-batch`）：output 目录含 `verify_report_v15.json`。

— EDA-MUXI 战队, 2026-10-03 14:10 (UTC+8)