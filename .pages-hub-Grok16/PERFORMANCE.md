# Grok16 Performance — G16 @ 16.2.0 / distro 5.0.0 belt

Measured on **Linux x86_64** with self-hosted `g16 (Grok16-16.2.0)`, **gnu++26** (`__cplusplus=202400`).

## Thermal / FP safety — `field_opt` vs `field_physics`

**`field_opt` and `belt_2_0` use `-ffast-math` and unlimited vectorization.** That is correct for raw throughput benchmarks, but it can:

- Relax IEEE-754 ordering and break **entropy checksum invariants** (e.g. `nexus_checksum` may report `-nan`).
- Create **sustained compute hotspots** in NEXUS/CANVAS kernels on FieldX86 dies.

**Use `field_physics` for production Field workloads that must preserve FP/entropy invariants:**

```bash
export GROK16_FIELD_PROFILE=field_physics   # CMake consumers
G16_BENCH_PROFILE=field_physics ./scripts/grok16-toolchain.sh bench
```

`field_physics` = belt_2_0 dispatch + Hostess gates + **`grok16-thermal-guard.cmake`** — **no `-ffast-math`**, `-fvect-cost-model=dynamic` instead of `unlimited`.

| Profile | `-ffast-math` | Thermal guard | Use |
|---------|---------------|---------------|-----|
| `field_opt` | yes | optional | bench / max throughput |
| `belt_2_0` | yes | via field.cmake | default distro belt |
| **`field_physics`** | **no** | **yes** | NEXUS/CANVAS sustained kernels |

## Belt triad (`bench-triad`) — host gcc vs belt 1.0 vs belt 2.0

Workload: `field-nexus-bench` (240 frames, FieldX86 + entropy + wave + NEXUS).

| Toolchain | Profile | compile_ms | run wall_ms | binary bytes |
|-----------|---------|------------|-------------|--------------|
| host `g++` | `-O3 -march=native` (gnu++20) | ~2575 | ~3 | ~27264 |
| `g16` | **belt_1_0** (1.0 field_opt baseline) | ~2377 | ~3 | ~22712 |
| `g16` | **belt_2_0** (chunked redata, Hostess+LTO) | ~3708 | ~5 | ~22840 |

**Takeaways:**
- **belt_1_0** matches host runtime; compile ~8% faster than host g++ on same source.
- **belt_2_0** trades compile time for production belt (8192 redata chunk, wave-massive, Hostess gates); runtime ~5ms with larger die (512 slots).
- Triad artifact: `data/bench/triad-latest.json`

```bash
./scripts/grok16-toolchain.sh bench-triad
./scripts/grok16-toolchain.sh integrate   # auto-wire SG consumers + triad
./scripts/grok16-toolchain.sh test-battery-belt
```

Host: local SG desktop build (partial prefix layout; driver uses `-B$GROK16_GCC_BUILD/gcc/` when needed).

## Field-Opt vs baseline (field-nexus-bench)

Workload: 240 frames × 512 FieldX86 ops + entropy fold + wave phase decouple + NEXUS behavioral scoring.

| Build | Flags | kernel wall_ms | binary bytes |
|-------|-------|----------------|--------------|
| Baseline | `-std=gnu++26 -O2` | 2.65 | 17144 |
| **Field-Opt** | `field_opt` profile (`-O3 -march=native -ftree-vectorize -funroll-loops -ffast-math -fopenmp-simd`) | **2.11–2.19** | 22616 |

**Throughput gain:** ~**19%** faster kernel wall time vs `-O2` baseline on the same source (2.65 ms → 2.15 ms avg).

## Profile suite (`./scripts/grok16-toolchain.sh bench-all`)

Results from `data/bench/latest.json` (2026-06-25):

| Profile | Workload | compile_ms | run_ms | binary_bytes | kernel metric |
|---------|----------|------------|--------|--------------|---------------|
| `field_opt` | field-nexus-bench | 874 | 4 | 22616 | wall_ms **2.19** |
| `ai` | ai-matrix-bench 64×64 | 735 | 6 | 18232 | wall_ms **4.01** |
| `field_compute` | field-canvas-kernel | 543 | 3 | 16240 | wave dispatch OK |
| `vulkan_rtx` | field-nexus + AVX2/FMA flags | 876 | 4 | 22728 | wall_ms **2.14** |

## Reproduce

```bash
export G16_PREFIX="$(pwd)"
./scripts/grok16-toolchain.sh field-bench
./scripts/grok16-toolchain.sh bench-all
cat data/bench/latest.json
```

### PGO (optional next step)

```bash
./scripts/grok16-toolchain.sh profile          # → data/pgo/
G16_ENABLE_PGO=1 ./scripts/grok16-toolchain.sh field-bench
```

### Production toolchain rebuild

```bash
G16_RELEASE_PROFILE=1 ./scripts/grok16-toolchain.sh rebuild
./scripts/grok16-toolchain.sh field-bench
```

## Stack verification (redata / ZAC)

Grok16 compiles **World_Redata L2** (`build-cpp.sh`). Gates:

```bash
cd ../World_Redata
./build-cpp.sh
PYTHONPATH=. pythong -m redata.cli parity    # PYTHON ↔ C++ roundtrip
PYTHONPATH=. pythong -m redata.cli security  # binary hardening + Grok16 manifest
```

Parity confirms WRDT/WRZC bytes roundtrip through the G16-built `world-redata` binary — the redata pipeline contract for L0–L1 → L2.

## Notes

- `nexus_checksum` under `-ffast-math` may report `-nan`; use **`field_physics`** when checksum truth matters; wall_ms is the primary throughput metric for bench triads.
- Thin LTO (`-flto=thin`) falls back to `-flto` when the installed g++16 does not support thin.
- Full install prefix (`lib/gcc/.../include`) removes the need for `-B` driver workaround.