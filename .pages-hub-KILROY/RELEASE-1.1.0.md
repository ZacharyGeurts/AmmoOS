# KILROY 1.1.0 — Sanctuary

**Released:** 2026-06-30  
**Codename:** Sanctuary  
**ABI:** `kilroy-field-1.0` · layout 9

KILROY Field OS — Linux-compatible, not Linux. **Field 1** is canonical at `127.0.0.1`. The GitHub Pages front door now runs an interactive KILROY terminal.

## Stack pairing

| Sibling | Version | Role |
|---------|---------|------|
| **Grok16** | 5.1.0 | Canonical compiler — `g16`, field_physics |
| **AmmoOS** | 2.0.0-beta3 | Field desktop inside Queen |
| **Queen** | secured shell | Browser + RTX |
| **ZNetwork** | pipe | Loopback sovereignty |
| **NEXUS C2** | :9477 | Command, underlay-f9 |

## What's new in 1.1.0

- **Live terminal** on [zacharygeurts.github.io/KILROY](https://zacharygeurts.github.io/KILROY/) — boot sim + `spin`, `releases`, `status`
- **Full platform matrix** — Linux ELF (5 arches), bare-elf, Darwin, iOS, Windows PE, Android NDK bootstrap packs
- **Field One doctrine** — non-Field-1 fields scanned hostile, consolidated to Field 1

## Quick start (Linux x86_64)

```bash
curl -LO https://github.com/ZacharyGeurts/KILROY/releases/download/v1.1.0/kilroy-1.1.0-linux-gnu-x86_64.tar.gz
tar -xzf kilroy-1.1.0-linux-gnu-x86_64.tar.gz
./scripts/grok-boot-qemu.sh   # or extract bzImage from platforms/linux-gnu-x86_64/
```

## Platform downloads

See `kilroy-1.1.0-PLATFORMS.md` and [releases.html](https://zacharygeurts.github.io/KILROY/releases.html) for SHA-256 checksums.