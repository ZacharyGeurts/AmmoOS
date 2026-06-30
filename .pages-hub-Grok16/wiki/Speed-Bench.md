# Speed Bench v5.1.0

Live JSON: `docs/field-exec-full-bench.json` · triad: `data/bench/triad-latest.json`

Host: Linux x86_64 · `g16` @ 16.2.0 · suite `speed_demo` @ 1.1.0 · 3 s window

## Winners (measured 2026-06-27)

| Category | Result |
|----------|--------|
| **Fastest execution** | **102.8M ops/s** — C++ g16 `belt_2_0` |
| **C++ host g++ -O2** | **101.1M ops/s** |
| **C belt_1_0** | **99.5M ops/s** |
| **C host gcc -O2** | **97.4M ops/s** |
| **Python host CPython** | **0.84M ops/s** (interpreter — no compile) |
| **Python gpy-16** | **0.76M ops/s** |
| **Self-monitor** | 15 runs, 0 dropped, 0 timeouts |

**Overall:** Grok16 matches or beats host gcc/g++ on the FieldX86 kernel at steady state. Compile time is higher; execution throughput peaks on `belt_2_0`.

## Belt triad (`bench-triad`)

Workload: `field-nexus-bench` — 240 frames, FieldX86 + entropy + wave + NEXUS.  
Updated: **2026-06-29**

| Toolchain | Profile | compile_ms | run wall_ms | binary bytes |
|-----------|---------|------------|-------------|--------------|
| host `g++` | `-O3 -march=native` | 2078 | 4 | 27264 |
| `g16` | `belt_1_0` | 4961 | **2** | 22696 |
| `g16` | `belt_2_0` | 5068 | 3 | 22824 |

`belt_1_0` runs **2× faster** wall time than host on this triad workload.

## bench-all profiles (kernel wall)

| Profile | compile_ms | run_ms | kernel |
|---------|------------|--------|--------|
| `field_opt` | 6337 | 7 | wall ~3.08 ms |
| `belt_1_0` | 6305 | 6 | wall ~2.89 ms |
| `belt_2_0` | 9962 | 11 | wall ~3.66 ms |
| `field_physics` | 7636 | 13 | wall ~4.06 ms · **safe FP** |
| `vulkan_rtx` | 876 | 4 | wall ~2.14 ms |

`nexus_checksum` may be `-nan` under `-ffast-math` — use **`field_physics`** when checksum truth matters.

## Reproduce

```bash
export G16_PREFIX="$(pwd)"
./scripts/grok16-toolchain.sh bench-triad
./scripts/grok16-toolchain.sh bench-refresh
./scripts/grok16-toolchain.sh exec-full-bench
```

Via MCP: `grok16_speed_bench` · `grok16_toolchain exec-full-bench`

Charts: `docs/assets/speed-bench-chart.svg`, `triad-chart.svg`, `compare-chart.svg`

Web: [Speed Bench manual](https://zacharygeurts.github.io/Grok16/speed-bench.html)