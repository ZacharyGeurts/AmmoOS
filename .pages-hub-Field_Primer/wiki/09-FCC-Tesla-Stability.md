# 09 — FCC Guard, Tesla Valve, and Stability

## CFL harmonics guard — ✅

Before fabric evolution:

```
waveCFL   = c·Δt/Δx        must stay ≤ 1
thermoCFL = α·Δt/Δx²      must stay ≤ 1
```

Host scales parameters down if violated.

**Plain English:** The engine refuses to run diffusion so hot the simulation explodes into NaN.

## Tesla valve — directional bias

From `FieldRtxFieldAbs.hpp`:

```
TESLA_R_FORWARD = 0.18
TESLA_R_REVERSE = 3.2
FIELD_PHI_MILLI = 618    // golden-ratio gate hint
```

Reverse "flow" on hardware spiderweb edges is damped more than forward. Published to `data_bus[31, 34]`.

🎭 Named after Tesla's fluidic diode — **directional resistance metaphor** in code.

## KILROY FCC (kernel parallel)

Scale 0–1,000,000 µ from overshoot; entropy feedback clamps aggressive modes when kernel field stack is active.

**Next:** [10 — Hardware Spiderweb](10-Hardware-Spiderweb)