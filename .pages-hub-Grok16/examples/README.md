# Grok16 examples

All examples use **gnu++26** and `g++16 @ 16.0.0`.

| Example | Profile | Build |
|---------|---------|-------|
| `minimal-cmake-project` | default | `cmake -DCMAKE_TOOLCHAIN_FILE=../cmake/grok16-toolchain.cmake` |
| `field-nexus-bench` | `field_opt` | `./scripts/grok16-toolchain.sh field-bench` |
| `ai-matrix-bench` | `ai` | `G16_BENCH_PROFILE=ai ./scripts/grok16-toolchain.sh bench` |
| `field-canvas-kernel` | `field_compute` | see `field-canvas-kernel/CMakeLists.txt` |

AI profile direct compile:

```bash
g++16 -std=gnu++26 -O3 -march=native -ftree-vectorize -funroll-loops \
  -DGROK16_PROFILE_AI=1 -I. -o ai_bench ai-matrix-bench/matrix_bench.cpp
```