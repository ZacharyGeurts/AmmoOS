# 01 — Preface: What Is a Field?

## Plain English

A **field** is not one physics thing in this stack. It is any **continuous quantity stored over space** that other systems read and write every tick:

- GPU images (Phi, Thermo, Flow)
- A 64 MiB guest RAM die on the GPU
- JSON telemetry describing network flows

A **program** is a recipe. A **field** is the **state of the kitchen** — heat on every burner, not just the timer.

## Three field families

| Family | Where | What it stores |
|--------|-------|----------------|
| GPU analog fabric | Vulkan bindings 8–10 | Phi, Thermo, Flow |
| Field Die | `FieldX86Die` SSBO binding 1 | x86 guest, VGA, tile cache |
| Packet field | NEXUS `field jsonl` | TX/RX, ports, corroboration |

## Key terms

- **Binding** — Vulkan slot where a buffer or image attaches
- **FieldSocket** — Per-dispatch push-constant control block
- **Holographic boundary** — HDR frame pair + fabric; where rendering pays thermodynamic cost
- **Operator** — The human at the keyboard. Not the daemon. Not the shader.

## Status labels (used throughout this manual)

| Label | Meaning |
|-------|---------|
| ✅ **Implemented** | In source; you can grep it |
| 🎭 **Metaphor** | Poetic naming; useful intuition |
| 📖 **Philosophy** | Operator discipline, not a measured constant |
| 🎨 **Visual** | Shader art, not instrumentation |

## What this manual is not

- Not a substitute for reading headers (`Pipeline.hpp`, `FieldRtxFieldAbs.hpp`)
- Not a promise that every poetic name maps to SI units
- Not cloud security — everything here is **local-first**

**Next:** [02 — Fields: From Pixels to Packets](02-Fields-From-Pixels-To-Packets)