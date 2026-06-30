# Commodore 64 (classic) — Queen CHIPS

**Web:** [c64-classic.html](https://zacharygeurts.github.io/Grok16/c64-classic.html)  
**Catalog:** `004-computers/c64` · **Stack:** `retro_c64`

The 1982 breadbin Commodore 64 — MOS **6510**, VIC-II, SID (6581/8580), dual CIA 6526. Queen CHIPS scaffold for emulation; **not** a Grok16 bootstrap or linker target.

## Silicon stack

| Die | Role |
|-----|------|
| `c64_6510` | MOS 6510 CPU |
| `c64_vic2` | VIC-II video |
| `c64_sid6581` / `c64_sid8580` | SID audio |
| `c64_cia1` / `c64_cia2` | CIA peripherals |

## Queen Game Room

- System id: `c64`
- `app_id: C64` · `CHIPS/C64`
- Status: scaffold (CHIPS header path)

## What we do not claim

- No `g16` on MOS 6510
- No `G16_LINK_TARGET=retro-c64-mos6510`

See [C64-Ultimate](C64-Ultimate) for the 2025 FPGA hardware pair (separate catalog page).