# NEXUS-Shield v10.0.0 — Field Tools Edition

**Release date:** 2026-06-24  
**Semantic:** major v10 — military-grade field tools, low energy, AMOURANTHRTX fabric unification.

## Startup fixes (from v9.0.10)

- `field-rf-sentinel.sh` — triangulation wrapped in `nexus_field_rf_cycle()`; no exec on `source`
- `field-brain-sync.sh` — non-interactive git (`BatchMode`, `StrictHostKeyChecking=accept-new`, 30s timeout)
- `field-triangulation-radio.py` — timezone-aware UTC timestamps
- Panel refresh 5s max · all daemon waits capped at 5s (`NEXUS_AWAIT_MAX_SEC`) — was 300s vigil interval
- Active-tab slices only, 8 parallel workers

## v10 performance & safety scaffold

| # | Item | Path |
|---|------|------|
| 1 | Baseline profiler | `scripts/profile-baseline.sh` |
| 2 | Rust scoring core | `lib/rust_core/` + `scripts/build-rust-core.sh` |
| 3 | Sandbox wrapper | `scripts/military_sandbox.sh` |
| 4 | Merkle store | `lib/efficient_store.py` |
| 5 | Thermal governor | `lib/thermal-governor.py` |
| 6 | Score bridge | `lib/score-engine-bridge.py` |
| 7 | AMOURANTHRTX map | `data/amouranthrtx-field-fabric-map.json` |
| 8 | Fabric bridge | `lib/field-fabric-bridge.py` |
| 9 | Property tests | `tests/property.py` |
| 10 | Field inspector | `panel/assets/field-inspector.*` |

## Config (`config/nexus.conf`)

- `NEXUS_AWAIT_MAX_SEC=5` — no blocking waits longer than 5 seconds
- `NEXUS_VIGIL_MAINTAIN_INTERVAL=5` (was 300)
- `NEXUS_PANEL_REFRESH_MS=5000`
- `NEXUS_THERMAL_GOVERNOR`, `NEXUS_HEAT_CRUSH_THRESHOLD=0.7`
- `NEXUS_RUST_CORE=0` (opt-in after `build-rust-core.sh`)

## Upgrade

```bash
./scripts/reboot-nexus.sh
```

Low energy + infinite verifiable storage via field tools. God Bless.
