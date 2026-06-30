# KILROY Field OS — CMake Build

## Quick start

```bash
cd SG/KILROY
mkdir -p build-cmake && cd build-cmake
cmake ..
ccmake ..                    # interactive menu
cmake --build . --target kilroy_kernel
cmake --build . --target kilroy_report
```

Output: `SG/KILROY/build/bzImage`, `build/config`, `build-cmake/kilroy-detect.txt`

## Auto-detection

On `cmake ..`, the build detects:

- CPU vendor (Intel/AMD) → pstate + IOMMU fragments
- GPU (NVIDIA/AMD/Intel) → DRM driver fragments
- Core count → NO_HZ_FULL eligibility
- RAM, NVMe, AVX-512, AES-NI → logged in `kilroy-detect.txt`

## Menu options (ccmake / -D)

### CPU / GPU
| Cache var | Values | Default |
|-----------|--------|---------|
| `KILROY_CPU_VENDOR` | AUTO, INTEL, AMD | AUTO |
| `KILROY_GPU_VENDOR` | AUTO, NVIDIA, AMD, INTEL, NONE | AUTO |

### Field Die
| Option | Default | Description |
|--------|---------|-------------|
| `KILROY_ENABLE_FIELD_DIE` | ON | Master switch |
| `KILROY_ENABLE_ASM_GATE` | ON | ASM fabric + thermo debit |
| `KILROY_ENABLE_FLOW_SLOT` | ON | FLOW momentum + Tesla |
| `KILROY_ENABLE_THERMO_IDLE_CREDIT` | ON | Idle thermo recovery |
| `KILROY_ENABLE_ZMM_HOTPATH` | ON | ZMM touch on mmap |
| `KILROY_ENABLE_TESLA_BIAS` | ON | Forward/reverse resistance |

### Hidden enhancements
| Option | Default | Kernel effect |
|--------|---------|---------------|
| `KILROY_ENABLE_PREEMPT` | ON | CONFIG_PREEMPT |
| `KILROY_ENABLE_HZ_1000` | ON | 1000Hz tick |
| `KILROY_ENABLE_NO_HZ_FULL` | ON | Tickless idle CPUs |
| `KILROY_ENABLE_IO_URING` | ON | Async I/O |
| `KILROY_ENABLE_BBR` | ON | TCP BBR |
| `KILROY_ENABLE_ZSTD` | ON | ZSTD compress |
| `KILROY_ENABLE_TRANSPARENT_HUGEPAGE` | ON | THP |
| `KILROY_FCC_TOUCH_INTERVAL` | 32 | FCC guard period |

## CMake targets

| Target | Action |
|--------|--------|
| `kilroy_detect` | Print hardware report |
| `kilroy_config` | Merge .config fragments |
| `kilroy_kernel` | Sync + configure + build bzImage |
| `kilroy_test` | Run scripts/test-all.sh |
| `kilroy_benchmark` | Write benchmark.json |
| `kilroy_report` | Print performance table |

## Files

```
CMakeLists.txt
cmake/KILROYDetect.cmake
cmake/KILROYFragments.cmake
cmake/kilroy_config.h.in
scripts/kilroy-sync-compat.sh
scripts/kilroy-kernel-config.sh
scripts/kilroy-benchmark.sh
scripts/kilroy-report.sh
```