# Release 5.2.0 — C64 Ultimate pair + 17 bootstrap platforms

Tag: `v5.2.0` · `distro_version: 5.2.0` · `g16` @ `16.2.0`  
Pairs with: **[AmmoOS 2.0 Stack](https://github.com/ZacharyGeurts/AmmoOS)** · **[C64 Ultimate](https://commodore.net/computer/)**

## Shipped in 5.2.0

- **C64 Ultimate hardware pair** — `pair-c64-ultimate` · g16 stays on host · [C64 wiki](C64)
- **17 bootstrap platforms** — Linux, Android, Darwin, iOS, Windows, bare-ELF, RISC-V
- **AmmoLang ship** — `grok16_ship.aml` adaptive timing
- **GPY-16 built-in** — `pythong` → `Grok16/bin/gpy-16`

**Not shipped:** g16 on classic MOS 6510 / breadbin C64.

## Carried from 5.1.0

- Stack fabric G1–G15, MCP stdio, truth gate, ZNetwork wire profile
- belt_2_0, field_physics, AmmoOS integrate hooks

## Validation gates

```bash
./scripts/grok16-toolchain.sh verify
./scripts/grok16-test-gate.sh smoke
./scripts/grok16-launch-verify.sh
```

Full notes: `RELEASE-5.2.0.md` in repo.