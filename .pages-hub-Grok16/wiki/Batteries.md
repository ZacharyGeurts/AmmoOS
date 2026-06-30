# Batteries

Web: [batteries.html](https://zacharygeurts.github.io/Grok16/batteries.html)

## Tiers (2.0)

| Tier | Command | Proves |
|------|---------|--------|
| Smoke | `test-battery` | paths, discern, ironclad sanity |
| Expert | `test-battery-expert` | + linker, RTX gate |
| Heavy | `test-battery-heavy` | release profile bench |
| Release | `test-battery-release` | production gate |
| **Belt** | **`test-battery-belt`** | **2.0 belt doctrine + triad** |

## 2.0 belt gate

```bash
./scripts/grok16-toolchain.sh test-battery-belt
```

Checks:

- `data/grok16-belt-doctrine.json`
- `data/grok16-single-fabric-doctrine.json`
- `belt_1_0` / `belt_2_0` profiles
- `bench-triad` script present
- `tests/test_g16_belt_battery.py`

## Release chain

```bash
G16_RELEASE_PROFILE=1 ./scripts/grok16-toolchain.sh test-battery-release
./scripts/grok16-toolchain.sh test-battery-belt
./scripts/grok16-toolchain.sh integrate
```