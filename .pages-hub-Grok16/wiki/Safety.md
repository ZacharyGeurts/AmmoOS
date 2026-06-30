# Safety — depth zero, no field files

## Critical warning

**DO NOT CREATE FIELD FILES.** Nested field JSON heats neighboring fields before singularizer catches up. Use the [2D field platform](Field-Platform).

## Ironclad rules (from code)

| Rule | Value |
|------|-------|
| `max_field_depth` | **0** |
| Field-on-field | **forbidden** |
| Depth field creation | **forbidden** |
| Time | **linear** (`sovereign-linear-time`) |
| Build under heat | **never** (`never_build_under_heat`) |

Doctrine: `data/grok16-single-fabric-doctrine.json`, `NewLatest/data/single-field-depth-doctrine.json`

## Profiles

| Profile | `-ffast-math` | Thermal guard | Use |
|---------|---------------|---------------|-----|
| `field_opt` / `belt_2_0` | yes | optional | bench throughput |
| **`field_physics`** | **no** | **yes** | production NEXUS/CANVAS |

## Gates

- `g16-field-mandate` · `g16-ironclad-sanity`
- `field-depth-singularizer` · `queen-field-sanity`
- `ironclad-field-sanity` (integral simplify pass)

## ZNetwork

Default `REVIEW_ONLY` — no OS mutation until review. See [ZNetwork Connect](ZNetwork-Connect).