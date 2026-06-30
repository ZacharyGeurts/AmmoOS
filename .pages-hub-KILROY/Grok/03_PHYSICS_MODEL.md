# KILROY 1.0 — Physics Model (per file)

Units: **micro** = 1e-6 unity, **submicro** = 1e-9 unity.  
Golden ratio gate: **φ = 618000 micro** (legacy 618 milli).

## Constants map

| Concept | micro | submicro | Legacy milli |
|---------|-------|----------|--------------|
| φ (phi) | 618000 | 618000000 | 618 |
| Thermo init / boundary | 310000 | — | 310 |
| Entropy floor | 2000 | 2000000 | 2 |
| Fabric debit/syscall | 1000 | 1000000 | 1 |
| FCC scale max | 1000000 | — | 1000 |
| FCC aggressive thresh | 920000 | — | 920 |
| FCC entropy floor | — | 14000000 | 14 |

## Per-file physics

### `kilroy_units.h`
- Conversion macros `KILROY_MICRO_FROM_MILLI`, `KILROY_SUBMICRO_FROM_MILLI`
- `kilroy_norm_micro(v)`: v&lt;10000 → treat as milli
- `kilroy_norm_submicro(v)`: v&lt;10000 → milli→submicro; else passthrough

### `rtx_core.c` — Thermo accountant
- Per-CPU `rtx_thermo_budget_micro`, init 310000
- `rtx_thermo_debit()`: subtract 1000 micro (1 milli) per fabric syscall; floor at 2000 micro
- `rtx_thermo_credit(micro)`: cap at 1500000 micro
- Default FCC: time=1e6, alpha=860000, wave=710000, gate=φ, inject=2800000, coupling=770000

### `rtx_thermo.c` — Fabric classification
- Fabric syscalls: 123, 124, 165, 261, 278 (sched/affinity, yield, rusage, prlimit, getrandom)

### `rtx_fcc.c` — FCC harmonics guard
- Computes scale 0–1000000 from wave/thermo/inject/coupling/time overshoot
- Entropy feedback: &gt;400000µ → clamp 850000; &gt;800000µ → 700000
- Aggressive mode (&lt;920000µ scale): pulls thermo budget down
- `rtx_fcc_fabric_voltage_ok()`: scale≥850000µ, cryo needs thermo≥120000µ

### `rtx_field.S` — ASM hot path
- RAM hint: brk/mmap/munmap/mprotect
- Fabric: inline debit 1000µ if budget &gt; 2000µ else -EAGAIN
- Avoids C call on every fabric syscall when ASM_GATE enabled

### `syscall_64.c` — Orchestration
- Order: slot verify → context tick → RAM pre → FCC touch → fabric voltage → thermo → dispatch → RAM post
- Memory post: mmap/munmap/brk page accounting + `kilroy_ram_field_post_touch`

### `rtx_slots.c` — TIME + RAM slot
- ZMM1024 entropy grid, 256MB safety margin
- Time seal on init; tamper → SIGKILL path via security

### `rtx_hw_field.c` — CPU + RAM fields
- RAM pressure: permille = min(1000, alloc*1000/usable); stored as permille × 1e9 submicro
- CPU phi coupling: drifts ±1000µ toward φ on fabric/idle
- Syscall rate: windowed count × 1e9 submicro/s

### `rtx_power.c` — DVFS tiers
- **Burst** when: φ≥618000, thermo&gt;200000, entropy&lt;350000, fcc≥920000, activity mod
- **Cryo**: fcc&lt;850000 or thermo&lt;60000
- **Eco**: fcc&lt;950000 or thermo&lt;120000 or RAM&gt;85%
- **Nom**: default
- Freq spans: cryo 12.5%, eco 50%, nom 75%, burst 100%

### `kilroy_cache_field.c` — CACHE field (slot 6)
- Ticks on memory syscalls; counts `bypass_ops`
- RAM pressure from slot1 feeds `pressure_micro` (0–1000000 scale)
- Shed when pressure ≥ 650000µ and syscall gen hits mask; min 5s between sheds
- Shed path: `lru_add_drain()` + `drop_slab()` — legacy retention shed, Field coherence stays hot
- `retention_micro` = 1000000 − min(pressure, 1000000)

### `kilroy_direct_field.c` — DIRECT field (slot 7)
- Post-mmap hook: `MAP_ANONYMOUS` → direct_maps/direct_bytes; else cached_maps
- Coherence ops on mmap/munmap/brk/mprotect syscalls
- `direct_ratio_micro` = direct_maps × 1e6 / (direct + cached)

### `rtx_proc.c` — Userspace boundary
- Writes normalize legacy milli; reads show micro + legacy_permille/milli labels
- `/proc/kilroy_field/cache` and `/proc/kilroy_field/direct` (layout v9)

## Physics ↔ userspace (`FieldRtxFieldAbs.hpp`)

| Constant | Float | Micro/submicro |
|----------|-------|----------------|
| ENTROPY_FLOOR | 0.002 | 2000000 submicro |
| BOUNDARY_THERMO | 0.31 | 310000 micro |
| FIELD_PHI | 0.618 | 618000 micro |
| TESLA_ENTROPY_K | 0.15 | used in thermo budget equation |