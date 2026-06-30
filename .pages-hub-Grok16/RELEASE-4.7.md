# Grok16 4.7.1

**Tag:** `v4.7.1` · **Compiler:** `g16 @ 16.2.0` · **Previous:** `v4.2.0` · **Platforms:** 17 (incl. RISC-V)

## Speed & comparison charts (refreshed)

Full benchmark refresh pipeline — regenerate all SVG charts and JSON reports in one command:

```bash
./scripts/grok16-toolchain.sh bench-refresh
# or stepwise: bench-triad · bench-compare · bench-all · exec-comprehensive-bench · bench-charts
```

| Chart | Asset |
|-------|-------|
| speed_demo compile + exec | `docs/assets/speed-bench-chart.svg` |
| belt triad | `docs/assets/triad-chart.svg` |
| field vs host compare | `docs/assets/compare-chart.svg` |
| bench-all profiles | `docs/assets/bench-all-chart.svg` |

Manifest: `data/bench/charts-manifest.json` · Live JSON: `data/bench/triad-latest.json`, `compare-latest.json`, `docs/field-exec-full-bench.json`

## Toolchain pairing

- **Host gcc-14** — bench-triad and bench-compare witness Ubuntu gcc-14 / g++-14
- **pythong 16.1.0-gpy16** — GPY-16 driver pairing stamped on speed bench reports
- **g16 @ 16.2.0** — belt_2_0 default single-fabric profile

## .launch chambers (ready)

Portable `queen-launch/v1` manifests ship in every `examples/*/` folder.

```bash
export GROK16_ROOT=/path/to/Grok16 SG_ROOT=/path/to/SG
./scripts/grok16-launch-verify.sh
python3 NewLatest/Queen/lib/queen-launch-chamber.py run examples/speed-demo/speed-demo.launch
```

## Multi-platform release

Source bootstrap per platform — see `data/grok16-platform-release.json` and `grok16-4.7.1-PLATFORMS.md`.

```bash
./scripts/grok16-release.sh 4.7.1 --push
```

## What's new in 4.7

- **bench-refresh** — one-shot pipeline: triad + compare + bench-all + comprehensive exec + SVG charts + manual rebuild
- **bench-charts** — `scripts/grok16-bench-charts.py` generates all comparison SVGs from live JSON
- **performance.html** — embeds triad, compare, and bench-all charts with live triad table
- **gcc-14 host pin** — speed bench chart header stamps host toolchain
- **Legacy isolation chamber** — SG/NewLatest runs old BASIC/Pascal/VB tests sealed (pairs with g16 bench gate)

## Test gate

```bash
export SG_ROOT=/path/to/SG
./scripts/grok16-test-gate.sh smoke
./scripts/grok16-toolchain.sh test-battery-release   # when g16 ready
```

## Gates

1. `grok16-test-gate.sh smoke` green
2. `bench-refresh` writes 4 charts + `charts-manifest.json`
3. `grok16-launch-verify.sh` — all example `.launch` chambers
4. Speed bench report v4.7.1 in `docs/field-exec-full-bench.json`