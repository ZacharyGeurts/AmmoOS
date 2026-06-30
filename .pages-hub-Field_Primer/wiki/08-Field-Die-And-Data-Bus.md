# 08 — Field Die and Data Bus

## Field Die — ✅

- **64 MiB** guest RAM (`GUEST_RAM_BYTES`)
- VGA text at guest `0xB8000`
- C: mirror at `0x01000000`
- **Not DOSBox** — same SSBO mapped host + GPU

## Execution model

1. **GPU:** `x86.comp` interprets guest instructions, renders Big Grin HUD (172×48)
2. **Host assist:** `FieldX86Emu` when `ControlHostCpu` set

## `data_bus[64]` — telemetry spine

| Slots | Content |
|-------|---------|
| `[0–1]` | Pump generation, cycles/frame |
| `[2–15]` | RAM, VGA, FAT layer telemetry |
| `[16–23]` | Analog FCC floats (TimeScale … FieldCoupling) |
| `[24–28]` | ThermoAccountant mirrors |
| `[32–41]` | Input (keyboard, mouse) |
| `[42]` | AmouranthOS chrome flags |
| `[57–63]` | Audio, BIOS, IO, drives |

Tesla valve bias → slots **31** and **34**.

## Field layers (L0–L9)

Ten composable layers: RAM, VGA, FAT, MSCDEX, Audio, IO, BIOS — pumped via `FieldLayer::pumpAll()`.

## ZMM1024 tile cache

Tail region in `FieldX86Die` SSBO — shader-side fabric sample cache for HUD hex dumps.

**Next:** [09 — FCC & Tesla](09-FCC-Tesla-Stability)