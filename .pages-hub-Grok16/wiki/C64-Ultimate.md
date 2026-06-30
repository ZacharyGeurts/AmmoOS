# Commodore 64 Ultimate — hardware pair

**Web:** [c64-ultimate.html](https://zacharygeurts.github.io/Grok16/c64-ultimate.html)  
**Pair ID:** `pair-c64-ultimate` · **Catalog:** `004-computers/c64_ultimate`

**Grok16 does not run on classic Commodore 64 silicon.** This lane documents pairing with the **new** FPGA hardware from [commodore.net](https://commodore.net/computer/) and the `c64_ultimate_fpga` chip battery used by Queen.

## The new C64 (2025–2026)

| Model | Form | Ship |
|-------|------|------|
| **Commodore 64 Ultimate** (`c64u`) | Breadbin | 2025 |
| **Commodore 64C Ultimate** (`c64cu`) | Slimline (original 1986 tooling) | Late 2026 |

**Core:** AMD Xilinx Artix-7 FPGA (cycle-accurate) · dual SID sockets (6581/8580) · HDMI/USB/Wi-Fi · `.PRG`/`.D64`/`.TAP` media.

## What Grok16 does here

| Layer | Role |
|-------|------|
| **Host** | Build and run `g16` on Linux/macOS/Windows — normal bootstrap platforms |
| **Chip battery** | `c64_ultimate_fpga` — FPGA core, HDMI bridge, SID sockets |
| **Queen** | Game room `c64_ultimate` · `app_id: C64U` · `pair/C64Ultimate` |
| **C64 Ultimate** | Runs Commodore media — Grok16 does not deploy `g16` onto the machine |

```bash
export G16_PREFIX="$(pwd)" G16_BELT_PROFILE=belt_2_0
./scripts/grok16-toolchain.sh rebuild
```

Load `.PRG`/`.D64` on the C64 Ultimate via USB/CommoServe — that is C64 software, not a g16 binary.

## Classic C64 is separate

Breadbin 1982 hardware is catalogued under [C64-Classic](C64-Classic) (`retro_c64`) — not this pair.

Doctrine: `data/grok16-platform-release.json` (`pair-c64-ultimate`) · `data/g16-linker-doctrine.json` (`hardware_pairs`).

## Related

- [C64](C64) (index) · [Platforms](Platforms) · [Batteries](Batteries) · [Release](Release)