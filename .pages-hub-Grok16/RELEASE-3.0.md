# Grok16 3.0.0

**Tag:** `v3.0.0` · **Compiler:** `g16 @ 16.2.0` · **Previous:** `v2.0.0`

## Speed bench (report v3.0.0)

Grok16 3.0 ships a **versioned compile + execution benchmark** — separating wave-convert time from timed field runs on identical `speed_demo` kernel.

| Stamp | Value |
|-------|-------|
| Report | `3.0.0` |
| Distro | `3.0.0` (`v3.0.0`) |
| Bench suite | `speed_demo` @ `1.0.0` |
| Schema | `grok16-field-exec-full-bench/v3` |

Doctrine: `data/grok16-speed-bench-version.json`

### Winners (reference host, 3s window)

| Category | Winner | Compile | Execution |
|----------|--------|--------:|----------:|
| **Fastest execution** | C++ g16 belt_2_0 | 2,494 ms | **85.3M ops/s** |
| **Fastest compile** | C g16 belt_2_0 | **318 ms** | 79.5M ops/s |
| **Best Python** | host CPython 3 | — | **778K ops/s** |
| **Best amortized first-run** | C g16 belt_2_0 | 318 ms | 60.3M effective |

Python has **no compile** — interpreter lane only. C/C++ use chamber **compile ahead** (cached on singular plane).

## Uncompiled execution

| Lane | Dev behavior |
|------|--------------|
| **Python** | True interpreter — ~0.72–0.78M ops/s |
| **C / C++** | No line-by-line interpreter — chamber compile ahead → ~80–85M ops/s |
| **CMake** | Configure + build once; bin reused |

Doctrine: `data/field-exec-uncompiled-doctrine.json` · Queen `.launch` chamber: `Queen/lib/queen-launch-singular-field.py`

## Manual & wiki (Queen theme)

- **Web:** [speed-bench.html](https://zacharygeurts.github.io/Grok16/speed-bench.html) · [uncompiled.html](https://zacharygeurts.github.io/Grok16/uncompiled.html) · [cmake-linking.html](https://zacharygeurts.github.io/Grok16/cmake-linking.html)
- **Wiki:** [Speed-Bench](https://github.com/ZacharyGeurts/Grok16/wiki/Speed-Bench) · [Uncompiled-Execution](https://github.com/ZacharyGeurts/Grok16/wiki/Uncompiled-Execution) · [CMake-and-Linking](https://github.com/ZacharyGeurts/Grok16/wiki/CMake-and-Linking)
- **Report:** [docs/SPEED-BENCH-REPORT.md](docs/SPEED-BENCH-REPORT.md) · JSON: [docs/field-exec-full-bench.json](docs/field-exec-full-bench.json)

## Checkout & gates

```bash
git clone https://github.com/ZacharyGeurts/Grok16.git
cd Grok16
git checkout v3.0.0
export G16_PREFIX="$(pwd)"
export G16_BELT_PROFILE=belt_2_0
G16_RELEASE_PROFILE=1 ./scripts/grok16-toolchain.sh rebuild
./scripts/grok16-toolchain.sh test-battery-release
./scripts/grok16-toolchain.sh test-battery-belt
SPEED_DEMO_TARGET_SEC=3 ./scripts/grok16-toolchain.sh exec-full-bench
./scripts/grok16-toolchain.sh exec-compare
./scripts/grok16-toolchain.sh integrate
```

## Highlights

- `field-exec-full-bench.py` — stamps distro/g16/suite versions on every run
- `exec-full-bench` / `exec-compare` toolchain hooks
- `examples/speed-demo/` — C, C++, Python, CMake, `.launch` chamber
- Queen-themed manual (navy `#060a12`, gold, emerald/cyan accents)
- SVG diagrams: compile vs exec, uncompiled chamber flow, CMake/link pipeline
- Single fabric + safety from 2.0 unchanged — `belt_2_0` default

## Upgrade from 2.0.0

1. `git checkout v3.0.0`
2. `G16_BELT_PROFILE=belt_2_0 G16_RELEASE_PROFILE=1 ./scripts/grok16-toolchain.sh rebuild`
3. `test-battery-release` then `test-battery-belt`
4. `SPEED_DEMO_TARGET_SEC=3 ./scripts/grok16-toolchain.sh exec-full-bench` — compare to published JSON
5. `./scripts/grok16-integrate.sh` to publish env to SG consumers