# 2D field platform — auto-field, no field files

Doctrine: `data/grok16-field-platform-doctrine.json`

## Warning

**DO NOT CREATE FIELD FILES.**

Writing standalone field files — `.field` JSON, depth-field layers, subfield launch files, nested amplitude stacks — **heats other fields** on the SG fabric. Each file is a second amplitude source. Gates flatten it, but the thermo cost lands on adjacent dies first.

| Forbidden | Use instead |
|-----------|-------------|
| `.field` / depth-field JSON | Place entity on **2D platform** |
| Subfield lattice files | **Single amplitude** at depth 0 |
| Field-on-field stacks | **Defield** when resting on a field surface |

Enforcement: `field-depth-singularizer`, `ironclad-field-sanity`, `g16-field-mandate`, AmmoCode instill (`max_field_depth: 0`).

## 2D platform rule

The operator plane is flat **(x, y)**. Everything placed on the plane is **auto-field**:

- One belt amplitude (`belt_2_0` default)
- `max_field_depth: 0` always
- Parallel I/O may fan in; panel truth collapses to **one** amplitude

Modules (from code):

| Role | Path |
|------|------|
| Plate amplitude | `NewLatest/lib/field-plate-field.py` |
| Panel truth | `NewLatest/lib/field-panel-field.py` |
| Parallel I/O | `NewLatest/lib/field-panel-parallel.py` |
| Seal + destroy stray depth | `NewLatest/lib/field-depth-singularizer.py` |
| Simplify pass | `Grok16/forge/g16-field-sanity.py` |

## AmmoCode on the platform

AmmoCode **is** a field — flat, no subfields. When the host surface is already fielded, AmmoCode **defields** (never stacks).

Doctrine: `data/g16-ammocode-field-doctrine.json` · instill: `lib/g16-ammocode-field-instill.py`

## Production profile

Sustained kernels on the platform: **`field_physics`** (thermal guard, no `-ffast-math`).

```bash
export GROK16_FIELD_PROFILE=field_physics
G16_BENCH_PROFILE=field_physics ./scripts/grok16-toolchain.sh bench
```

Bench-only throughput: `belt_2_0` / `field_opt` — see [Speed Bench](Speed-Bench).