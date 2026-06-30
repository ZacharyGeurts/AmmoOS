# Grok16 5.2.0 — C64 Ultimate pair + AmmoLang Ship

**Released:** 2026-06-29  
**Tag:** `v5.2.0` · **Compiler:** `g16` @ `16.2.0` (`Grok16-5.2.0`)  
**Pairs with:** [AmmoOS 2.0 Stack](https://github.com/ZacharyGeurts/AmmoOS) · [Commodore 64 Ultimate](https://commodore.net/computer/)

Grok16 5.2.0 documents pairing with the **new Commodore 64 Ultimate** (C64U / C64CU FPGA hardware). **g16 does not run on classic 6510 silicon.**

## What changed

- **C64 Ultimate hardware pair** — `pair-c64-ultimate` in platform release manifest (not a g16 bootstrap target)
- **Chip battery** — `retro_c64` (6510, SID, VIC-II, CIA) for Queen CHIPS / combinatorics
- **AmmoLang ship** — `grok16_ship.aml` adaptive timing (`last_ms + 3s` hang guard)
- **GPY-16 built-in** — `pythong` → `Grok16/bin/gpy-16` when legacy GrokPy is absent
- **17 bootstrap platforms** + **1 hardware pair** (C64 Ultimate)

## Carried from 5.1.0

- Stack fabric G1–G15, MCP stdio, truth gate, ZNetwork wire profile
- belt_2_0 single fabric, field_physics safety, AmmoOS integrate hooks

## Validation

```bash
./scripts/grok16-toolchain.sh verify
./scripts/grok16-test-gate.sh smoke
./scripts/grok16-launch-verify.sh
./scripts/grok16-release.sh 5.2.0 --no-gh
```

## Install

```bash
git clone https://github.com/ZacharyGeurts/Grok16.git
cd Grok16 && git checkout v5.2.0
export G16_PREFIX="$(pwd)" G16_BELT_PROFILE=belt_2_0 SG_ROOT=/path/to/SG
./scripts/grok16-toolchain.sh rebuild
./scripts/grok16-toolchain.sh verify
```

## Manual

- **Web:** https://zacharygeurts.github.io/Grok16/
- **Wiki:** https://github.com/ZacharyGeurts/Grok16/wiki
- **C64 pair:** https://github.com/ZacharyGeurts/Grok16/wiki/C64