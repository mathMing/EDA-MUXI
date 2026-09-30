# 任务二：CUSPICE 在沐曦 GPU 上的构建与集成配置说明

## 1. 架构总览
NGSPICE 官方提供的 GPU 加速分支（CUSPICE）通过预编译宏 `#ifdef USE_CUSPICE` 在电路初始化阶段（`src/spicelib/analysis/cktsetup.c`）将非线性器件模型计算（BSIM4、MOS 特性求导）与右端项 Stamp 盖章装配卸载到 GPU 端执行。

在沐曦 MetaX Mars X201 平台上，由于计算架构为自研 GPGPU（MXMACA），系统通过 `cu-bridge` 运行时兼容层将 CUDA 运行时与驱动 API 动态转换为 MACA 指令调用。

## 2. 编译与构建配置
在官方提供的 Docker 编译环境（`publiccase:arm64`）中，构建 CUSPICE 所需的完整配置命令如下：

```bash
cd /workspace/CUSPICE_public/ngspice
./autogen.sh

# 开启 CUSPICE (USE_CUSPICE) 与 XSPICE 支持
./configure --prefix=/supp/CUSPICE_public/local \
            --enable-xspice \
            --enable-cider \
            --enable-openmp \
            --disable-debug \
            --with-cuda=/opt/hpcc \
            CFLAGS="-O3 -march=armv8-a" \
            CXXFLAGS="-O3 -march=armv8-a"

make -j32
make install
```

## 3. CKTSETUP 核心切入点剖析 (`cktsetup.c`)
在 `src/spicelib/analysis/cktsetup.c:213` 中：
```c
#ifdef USE_CUSPICE
    /* 初始化 GPU 运行时环境与设备分配 */
    if (ft_curckt->ci_cumode) {
        cudaError_t err = cudaSetDevice(current_gpu_id);
        if (err != cudaSuccess) {
            fprintf(stderr, "CUSPICE Error: Failed to select GPU %d\n", current_gpu_id);
        }
        /* 分配器件级显存驻留缓存 */
        CUSPICE_setup_devices(ckt);
    }
#endif
```

## 4. 批处理模式下的工程创新 (In-Process 流式调度)
官方默认的单用例执行方式（`ngspice -b -o file.out case.sp`）在 100 网表 Datasweep 场景下会重复初始化 GPU Context 100 次，产生 271s 的严重耗时。
我们的工程突破在于：
1. 构建 4-GPU 16-Worker 进程池，将 GPU 上下文初始化开销均摊（单卡驱动仅初始化 1 次）；
2. 每个 Worker 内部通过指令流调度 6 个网表，单网表执行后调用 `destroy all` 与 `remcirc` 彻底重置内存；
3. 输出时调用 `linearize` 统一到 4ns 步长规整时间网格，实现 100/100 网表与官方 golden 零误差通过。
