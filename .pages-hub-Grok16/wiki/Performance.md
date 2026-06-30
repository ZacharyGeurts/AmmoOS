# Performance

Web: [performance.html](https://zacharygeurts.github.io/Grok16/performance.html) · [speed-bench.html](https://zacharygeurts.github.io/Grok16/speed-bench.html)

## Speed bench (5.1 — report v5.0.0)

**Suite:** `speed_demo` @ `1.1.0` · **3s execution window** · Schema: `grok16-field-exec-full-bench/v5`

```bash
./scripts/grok16-toolchain.sh bench-refresh
# or stepwise:
SPEED_DEMO_TARGET_SEC=3 ./scripts/grok16-toolchain.sh exec-full-bench
./scripts/grok16-toolchain.sh exec-compare
./scripts/grok16-toolchain.sh bench-charts
```

| Runner | Compile (ms) | ops/s | vs host |
|--------|-------------:|------:|--------|
| **C++ g16 belt_2_0** | BSP cache | **102.8M** | **+1.7%** vs g++ |
| C++ host g++ -O2 | BSP cache | 101.1M | baseline |
| CMake host g++ -O2 | BSP cache | 98.9M | −2.2% |
| C g16 belt_1_0 | BSP cache | 99.5M | **+2.1%** vs gcc |
| C host gcc -O2 | BSP cache | 97.4M | baseline |
| C g16 belt_2_0 | BSP cache | 95.7M | −1.7% |
| Python host CPython 3 | — | 0.84M | baseline |
| Python gpy-16 GrokVM | — | 0.76M | −10% |

Charts: `docs/assets/speed-bench-chart.svg`, `triad-chart.svg`, `compare-chart.svg`, `bench-all-chart.svg`

Artifacts: `docs/SPEED-BENCH-REPORT.md` · `docs/field-exec-full-bench.json` · Wiki: [Speed-Bench](Speed-Bench)

## Overall (human read)

| Lane | Verdict |
|------|---------|
| **C/C++ execution** | Grok16 **wins peak throughput** on `belt_2_0` (102.8M ops/s) and **matches or beats** host on C/C++ cold runs after BSP cache |
| **Compile time** | Host gcc/g++ still **faster to compile**; g16 pays compile cost for belt profiles |
| **Triad runtime** | `belt_1_0` finishes the nexus bench in **half the wall time** of host g++ (2 ms vs 4 ms) |
| **Python** | Interpreter lane — host CPython still ahead on micro-bench; gpy-16 is uncompiled doctrine |
| **Reliability** | Self-monitor: **15/15 runs OK**, zero drops, zero timeouts |

**Bottom line:** Use Grok16 when you want sovereign compile + field belt execution at **host parity or better** on the FieldX86 kernel. Use `field_physics` for production FP truth; use `belt_2_0` for peak ops/s.

## Belt triad (2.0)

```bash
./scripts/grok16-toolchain.sh bench-triad
./scripts/grok16-toolchain.sh bench-charts
```

Workload: `field-nexus-bench` (240 frames, FieldX86 + entropy + wave + NEXUS). Host witness: **gcc-14**.

| Toolchain | Profile | compile_ms | run wall_ms | binary bytes |
|-----------|---------|------------|-------------|--------------|
| host `g++` | `-O3 -march=native` | 2078 | 4 | 27264 |
| `g16` | **belt_1_0** | 4961 | **2** | 22696 |
| `g16` | **belt_2_0** | 5068 | 3 | 22824 |

Artifact: `data/bench/triad-latest.json` · Chart: `docs/assets/triad-chart.svg`

## bench-all profiles

```bash
./scripts/grok16-toolchain.sh bench-all
```

| Profile | compile_ms | kernel wall_ms |
|---------|------------|----------------|
| belt_1_0 | 6305 | 2.89 |
| belt_2_0 | 9962 | 3.66 |
| field_opt | 6337 | 3.08 |
| field_physics | 7636 | 4.06 |
| vulkan_rtx | 876 | 2.14 |

Artifact: `data/bench/latest_field_opt.json` · Chart: `docs/assets/bench-all-chart.svg`

## Field vs host compare

```bash
./scripts/grok16-toolchain.sh bench-compare
```

Artifact: `data/bench/compare-latest.json` · Chart: `docs/assets/compare-chart.svg`

## Related

- [Speed Bench](Speed-Bench) — full runner table + plate meld
- [MCP](MCP) — `grok16_speed_bench` tool for agents
- [Profiles](Profiles) — belt_1_0, belt_2_0, field_opt, expert
- [Release 5.1](Release) — stack fabric + bench gates