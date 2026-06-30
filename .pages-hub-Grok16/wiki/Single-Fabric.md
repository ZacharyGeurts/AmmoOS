# Single fabric (2.0)

Field Research Ch. 5: [Single Fabric & Belt 2.0](https://zacharygeurts.github.io/Field_Research/chapters/05-single-fabric-belt.html)

Web: [concepts.html](https://zacharygeurts.github.io/Grok16/concepts.html)

**Single fabric** is the Grok16 2.0 technology: fixed-size **knowing** on one belt die — not nested fields, not monolithic blast.

## Doctrine

`data/grok16-single-fabric-doctrine.json`

## Rules

| Layer | Rule |
|-------|------|
| Belt | `belt_2_0` — 8192 redata chunk, wave-massive, **single-location reads** |
| Field | One amplitude at depth 0 — parallel I/O fans in, truth stays single |
| Time | Linear sovereign clock — `ironclad:time:1`, not geometry `t` |
| Safety | Depth-field creation **forbidden** — stripped at every gate |

## Profiles

| Profile | Role |
|---------|------|
| `belt_1_0` | 1.0 baseline (aliases `field_opt`) — triad compare |
| `belt_2_0` | **2.0 production** — single fabric dispatch |

```bash
export G16_BELT_PROFILE=belt_2_0
./scripts/grok16-toolchain.sh bench-triad
```

## Citation

`ironclad:field_sanity:5` — parallel I/O may fan in; truth stays one amplitude at layer 0.