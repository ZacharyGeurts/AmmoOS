# Grok16 2.0.0

**Tag:** `v2.0.0` · **Compiler:** `g16 @ 16.2.0` · **Previous:** `v1.0.0`

## Single fabric

Grok16 2.0 is built around **single fabric knowing**:

- **One belt die** — `belt_2_0` chunked redata (8192), wave-massive dispatch, single-location reads
- **One field amplitude** — parallel I/O may fan in; panel truth stays depth 0
- **One linear time** — sovereign `linear_ns` seals melds (`ironclad:time:1`)

Doctrine: `data/grok16-single-fabric-doctrine.json`

## Safety (wired at integrate)

| Gate | Rule |
|------|------|
| Depth field | **Sealed and destroyed** — `field_depth` eradicated at HTTP, browser, field-net, sanity; cannot persist |
| Ironclad field sanity | Integral one-pass — meld receipt requires `depth_field_impossible` |
| Sovereign time | Linear only — wall clock witness-only |
| G16 mandate | `G16_FIELD_SAFETY_MANDATE_v1` on every field target |

## Checkout & gates

```bash
git clone https://github.com/ZacharyGeurts/Grok16.git
cd Grok16
git checkout v2.0.0
export G16_PREFIX="$(pwd)"
export G16_BELT_PROFILE=belt_2_0
G16_RELEASE_PROFILE=1 ./scripts/grok16-toolchain.sh rebuild
./scripts/grok16-toolchain.sh test-battery-release
./scripts/grok16-toolchain.sh test-battery-belt
./scripts/grok16-toolchain.sh bench-triad
./scripts/grok16-toolchain.sh integrate
```

## Belt triad (this machine, reference)

| Toolchain | Profile | compile_ms | run wall_ms | binary bytes |
|-----------|---------|------------|-------------|--------------|
| host `g++` | `-O3 -march=native` | ~2575 | ~3 | ~27264 |
| `g16` | `belt_1_0` | ~2377 | ~3 | ~22712 |
| `g16` | `belt_2_0` | ~3708 | ~5 | ~22840 |

See [PERFORMANCE.md](PERFORMANCE.md).

## Highlights

- `belt_2_0` default profile on distro 2.0
- `grok16-integrate.sh` — auto-wire Queen, World_Redata, ZOCR, PythonG
- `test-battery-belt` — 2.0 validation atop release tier
- Ironclad meld — time linear + single fabric + field sanity verses
- `bench-triad` — host gcc vs belt_1_0 vs belt_2_0

## Upgrade from 1.0.0

1. `git checkout v2.0.0`
2. `G16_BELT_PROFILE=belt_2_0 G16_RELEASE_PROFILE=1 ./scripts/grok16-toolchain.sh rebuild`
3. `test-battery-release` then `test-battery-belt`
4. `./scripts/grok16-integrate.sh` to publish env to SG consumers