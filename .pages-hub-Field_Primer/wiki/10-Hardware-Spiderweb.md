# 10 — Hardware Spiderweb and Sub-Micron Simulation

## `hardwareFabric` — ✅

`updateHardwareFromAnalogFields()` each frame:

1. Samples avg Phi, Thermo, Flow
2. Computes `voltageFactor`, `thermalThrottle`, `parallelEff`
3. Updates per-core `operationalFreqMHz`, util, temp, power
4. Updates spiderweb `edges[].currentUtil`
5. Accumulates `simulatedChipCycles`

**Read-only mirror** of GPU fabric — not a second simulation.

## Mastery tiers

| Tier | Controls |
|------|----------|
| **Puny** | Status log, real sysfs clocks |
| **Adept** | Target clock, thermal sensitivity, `SimulateSubMicron` |
| **Tidewalker** | Spiderweb graph, vendor override, `SubMicronDetail` |

## Sub-micron claim — mixed

| Claim | Reality |
|-------|---------|
| ✅ Adaptive resolution 320×200 → 4K+ | Implemented |
| ✅ SDF epsilons + accumulation | Implemented |
| 🎭 "Zero-cost sub-micron SEM fidelity" | Procedural detail at pixel scale — not electron microscopy |

## Precision field (NEXUS)

`precision-field.py` — GPS-anchored entity map, spiderweb nodes, thermal-earth bodies. Cousin metaphor to engine spiderweb, separate codebase.

**Next:** [11 — Observability](11-Observability-Operator-Tools)