# 03 — Thermodynamics in the Engine

![Phi Thermo Flow fabric](https://raw.githubusercontent.com/ZacharyGeurts/Field_Primer/main/assets/images/fabric-triple.jpg)

*Figure 3.0 — Coupled fabric at bindings 8–10. [Illustrated chapter →](https://zacharygeurts.github.io/Field_Primer/chapters/03-thermodynamics.html)*

## Why thermodynamics in a renderer?

Every frame **destroys information** — noise injection, probes, diffusion steps. The engine tracks that cost like a power meter tracks joules. This is **accounting**, not a laboratory calorimeter.

## The three fabric channels

Created in `RayCanvas::createAnalogFieldFabric()`, bound at slots **8**, **9**, **10**:

| Fabric | Role | Shader channels |
|--------|------|-----------------|
| **Phi (Φ)** | Wave / gate potential | Binding 8 `fieldPhi` |
| **Thermo** | Heat + entropy density | Binding 9 `fieldThermo` |
| **Flow** | Advection / momentum | Binding 10 `fieldFlow` (.gb = gradients) |

**Cross-coupling:** `FieldCoupling` links all three — electrical activity heats the die; heat affects flow.

## Per-texel evolution (`CANVAS.comp`)

1. **Phi** — discrete Laplacian wave step + `WaveSpeed` + `propalacticScale` forcing
2. **Thermo** — diffusion with `ThermoAlpha`, entropy floor, coupling to Phi
3. **Flow** — gradient magnitude mixed with `GateFidelity` + Tesla relaxation

**Stability clamps:**

```
newPhi   ∈ [-2.0, 2.0]
newThermo ∈ [0.0, 1.5]
newFlow  ∈ [0.0, 1.0]
```

## Control knobs (`Options::AnalogFields`)

| Knob | Effect |
|------|--------|
| `TimeScale` | Global Δt multiplier |
| `ThermoAlpha` | Thermal diffusivity α |
| `WaveSpeed` | Phi propagation speed c |
| `GateFidelity` | 0 = soft analog … 1 = sharp gate |
| `EntropyFloor` | Minimum irreversible noise |
| `InjectStrength` | Mouse/probe energy injection |
| `PropalacticScale` | Large-wavelength forcing on Phi |
| `FieldCoupling` | Thermo ↔ Phi ↔ Flow coupling |

## CFL guard (host, before dispatch)

```
waveCFL   = (waveSpeed × fieldTimeScale) × effDt / dx
thermoCFL = (thermoAlpha × fieldTimeScale) × effDt / dx²
```

If CFL > 1, parameters scale down. Hard caps: `waveSpeed ∈ [0.01, 2.0]`, `dT ≤ 0.033`.

✅ **Implemented** on classic canvases.  
🎭 Body-temperature seeding is normalized simulation flavor, not BIOS temperature.

**Next:** [04 — Entropy](04-Entropy-Receipts-And-Oracles)