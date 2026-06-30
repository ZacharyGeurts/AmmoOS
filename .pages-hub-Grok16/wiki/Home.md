# Grok16 5.2 — Stack Fabric + C64 Ultimate pair

**Grok16 5.x is the sovereign Field compiler line.** **5.2.0** documents pairing with the new **Commodore 64 Ultimate** FPGA hardware. **g16 does not run on classic 6510 silicon.**

| | |
|---|---|
| **Distro** | `5.2.0` · tag `v5.2.0` |
| **Compiler** | `g16` @ `16.2.0` (`Grok16-5.2.0`) |
| **AmmoOS pair** | [AmmoOS 2.0 Stack](https://github.com/ZacharyGeurts/AmmoOS) |
| **C64 pair** | [C64 Ultimate](C64) — `pair-c64-ultimate` (host-only g16) |
| **Bootstrap** | 17 platforms — Linux, Android, Darwin, iOS, Windows, bare-ELF, RISC-V |
| **Agents** | [MCP stdio](MCP) |

## Read this first

> **DO NOT CREATE FIELD FILES.** Use the **[2D field platform](Field-Platform)** — placement on the plane *is* field at depth 0.

## What ships in 5.2.0

- **C64 Ultimate pair** — new FPGA hardware from [commodore.net](https://commodore.net/computer/); chip battery `retro_c64` for Queen CHIPS
- **AmmoLang ship** — adaptive timing ledger for release gates
- **Stack fabric G1–G15** — sealed receipts, MCP stdio, truth gate
- **g16 prefix** — self-hosted toolchain on host platforms only

## Quick start

```bash
git clone https://github.com/ZacharyGeurts/Grok16.git
cd Grok16 && git checkout v5.2.0
export G16_PREFIX="$(pwd)" G16_BELT_PROFILE=belt_2_0 SG_ROOT=/path/to/SG
./scripts/grok16-toolchain.sh rebuild
./scripts/grok16-toolchain.sh verify
```

## Links

- [Release 5.2](Release) · [C64 pair](C64) · [Speed Bench](Speed-Bench)
- **Web manual:** https://zacharygeurts.github.io/Grok16/