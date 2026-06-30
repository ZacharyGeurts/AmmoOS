# KILROY 1.1.0 — Sanctuary

**Live hub (terminal + spin up):** [**zacharygeurts.github.io/KILROY**](https://zacharygeurts.github.io/KILROY/) — interactive KILROY terminal, always on, everyone fires up their own field node at `127.0.0.1`.

![Release](https://img.shields.io/badge/release-1.1.0_Sanctuary-green)
![Pages](https://img.shields.io/badge/Pages-KILROY_hub-3ecf8e)
![ABI](https://img.shields.io/badge/ABI-kilroy--field--1.0-blue)
![Grok16](https://img.shields.io/badge/Grok16-5.0.1-gold)
![AmmoOS](https://img.shields.io/badge/AmmoOS-2.0.0--beta3-purple)

**Field OS — Linux-compatible. Not Linux.**

**Stack nav:** [AmmoOS STACK-NAV](https://github.com/ZacharyGeurts/AmmoOS/blob/main/STACK-NAV.md) · [Profile hub](https://zacharygeurts.github.io/ZacharyGeurts/stack.html) · [Queen](https://github.com/ZacharyGeurts/Queen) · [ZNetwork](https://github.com/ZacharyGeurts/ZNetwork)

KILROY is the **Field** operating system: syscall-scheduled physics (Phi, Thermo, Flow, FCC), native integrity, and AMOURANTHRTX field fabric — with **full Linux userspace compatibility**. You run glibc apps, shell scripts, and containers unchanged. Underneath is Field, not a Linux distribution.

## Identity

| We are | We are not |
|--------|------------|
| **KILROY** — Field OS | A Linux distro or rebrand |
| **Field-native** — 6-slot Field Die in every syscall | An out-of-tree Linux module project |
| **Linux-compatible** — POSIX ABI passthrough | Dependent on Linux as our name or soul |

The **compat substrate** (linux-7.1.1 lineage) is a boot foundation — like firmware for Field. It is not what we call ourselves.

## Stack (2026)

KILROY is the **PC core** (ZNetwork absorbed) under **Hardware → NEXUS C2 → KILROY → AmmoOS → Queen**. AmmoOS desktop uses **AMOURANTHRTX**; Queen is standalone. Load: `./scripts/kilroy-load-os.sh`. Pairs **Grok16 5.2.0** + **AmmoOS 2.0.0-beta3.1**. See `docs/STACK-INTEGRATION.md`.

## Quick launch

```bash
git clone https://github.com/ZacharyGeurts/KILROY.git
cd KILROY && git checkout v1.1.0
./scripts/kilroy-become-substrate.sh   # fix Linux → KILROY in compat tree
./scripts/test-all.sh
./scripts/build-kilroy.sh
```

Boot image: `build/bzImage` · `LOCALVERSION=-kilroy`  
Boot loader: **Grok** (not GRUB) → `build/grok-kilroy.img`  
Ramdisk: `build/initramfs.cpio.gz` · `uname -s` → **KILROY**

## Field telemetry

```bash
cat /proc/kilroy_field/status    # name=KILROY codename=Field compat=linux
cat /proc/kilroy_field/security  # NEXUS guard
```

## Grok boot (replaces GRUB)

Intuitive menu · **E** to edit in place · 4 themes · mandatory BIOS security audit · ReBAR/speedup hints.

```bash
./scripts/grok-compose.sh       # theme + entries → grok.conf
./scripts/grok-firmware-audit.sh  # fix BIOS before strict boot
./scripts/grok-mkimage.sh       # bootable disk image
./scripts/grok-boot-qemu.sh     # QEMU smoke test
sudo ./scripts/grok-install.sh /boot/efi   # bare metal ESP
```

See `boot/grok/WISHES.md` (100 wishes) · `boot/grok/HELP.md` (keys)

## CI

```bash
./scripts/ci-run.sh    # local
# or push — .github/workflows/kilroy-test.yml
```

## Layout

```
SG/KILROY/          ← canonical Field OS source (edit here)
  boot/grok/        ← Grok bootloader (graphical, fast, safe)
  kernel/rtx/       ← Field Die (native)
  arch/x86/entry/   ← Field syscall fabric
  compat/           ← Linux-compat staging notes
  Grok/             ← agent memory
  scripts/          ← build, test, stage
```

## Docs

- [FIELD.md](FIELD.md) — identity manifesto
- [Grok/01_PROJECT_OVERVIEW.md](Grok/01_PROJECT_OVERVIEW.md) — architecture
- [Grok/10_SECURITY.md](Grok/10_SECURITY.md) — NEXUS field guard

Part of [AMOURANTHRTX](https://github.com/ZacharyGeurts/AMOURANTHRTX). Test in a VM before bare metal.