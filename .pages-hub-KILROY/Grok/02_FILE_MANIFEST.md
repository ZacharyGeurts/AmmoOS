# KILROY Field OS — File Manifest

Canonical source: `SG/KILROY/`. Compat substrate is staging only. See `compat/PORT_MAP.md`.

## Identity docs

| File | Role |
|------|------|
| `README.md` | Field OS landing + quick launch |
| `FIELD.md` | Identity manifesto |
| `FIELD_STATUS.md` | Build/status checklist |
| `compat/README.md` | Compat substrate paths |
| `compat/PORT_MAP.md` | Linux→KILROY file port map |

## Kernel port (`init/`, `config/`)

| File | Role |
|------|------|
| `init/kilroy-banner.c` | Early boot banner |
| `init/kilroy-uts.c` | uname sysname → KILROY |
| `init/version-timestamp.c` | Linux banner string replacement |
| `integration/init-main.snippet` | main.c banner hook |
| `integration/init-Makefile.overlay` | init/ object list |
| `config/kilroy-identity.config` | Field Die + LOCALVERSION |
| `config/kilroy-production.config` | NVMe ext4 production root |

## UAPI

| File | Role |
|------|------|
| `include/uapi/kilroy/rtx_field.h` | Field ABI |
| `include/uapi/linux/rtx_field.h` | Linux-compat shim |
| `include/linux/kilroy_field.h` | Kernel exports |

## Field Die (`kernel/rtx/`)

All `rtx_*`, `kilroy_*` modules (boot, identity, nexus, flow, …).

## Boot & rootfs

| Path | Role |
|------|------|
| `boot/grok/` | Grok bootloader |
| `rootfs/` | Production busybox root |
| `userspace/field-init/` | Ramdisk PID1 |
| `userspace/kilroy-status/` | `/proc/kilroy_field` CLI |

## Scripts

| File | Role |
|------|------|
| `scripts/kilroy-sync-compat.sh` | Copy Field → substrate |
| `scripts/kilroy-apply-identity.sh` | Identity overlays |
| `scripts/kilroy-become-substrate.sh` | Full transform |
| `scripts/kilroy-port-verify.sh` | Port completeness check |
| `scripts/build-kilroy.sh` | bzImage + Grok |
| `scripts/test-all.sh` | Full test suite |