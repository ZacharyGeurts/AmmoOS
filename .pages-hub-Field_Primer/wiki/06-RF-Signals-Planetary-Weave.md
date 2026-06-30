# 06 — RF, Signals, and the Planetary Weave

## Three meanings of "RF" in this stack

| Context | What "RF" means |
|---------|-----------------|
| `planetary_weave.comp` | 🎨 Visual atmospheric shell layer |
| NEXUS Field Antenna | ✅ Local RF/audio/wired orchestration |
| Engine `fieldPhi` | Gate voltage / wave potential — not literal radio |

Do not equate GPU Phi with ionospheric propagation without labeling the jump.

## Planetary weave — visual layer

Earth cross-section shader with concentric shells. RF layer at:

```
#define R_RF  (R_EARTH + 1.05)   // Layer L_RF
```

Stack: core → crust → hydro → clouds → troposphere → … → **ionosphere** → **RF shell** → magnetosphere.

🎨 **Visual vocabulary** — teaches where signals "live" in the stack metaphor, not a spectrum analyzer.

## Field Antenna Orchestrator (NEXUS) — ✅

Monitors RF + audio + wired + laser reference bands:

- Optical/laser: 405–1550 nm entries
- LIDAR flow ports in registry
- GPS field anchors for triangulation metaphor
- Outputs: `field-antenna-panel.json`, `field-rf-panel.json`, `signals-field-panel.json`

## Free-space path loss (teaching reference)

\[
FSPL \propto 20\log_{10}(d) + 20\log_{10}(f)
\]

Used in NEXUS docs as ITU-R/FCC context — **not** computed inside AMOURANTHRTX shaders.

**Next:** [07 — GPU Field Engine](07-GPU-Field-Engine)