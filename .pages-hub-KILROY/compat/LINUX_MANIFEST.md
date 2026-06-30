# KILROY 1.0 — complete Linux substrate manifest

**KILROY Field OS 1.0** = **all of Linux 7.1.1** (compat substrate) + **Field-native overlay** (canonical `SG/KILROY/`).

We ship the **entire** linux-7.1.1 tree. We do **not** fork every file into `SG/KILROY/`. Canonical holds only Field-native deltas; the substrate holds everything else unchanged except identity patches.

## Layers

| Layer | Path | Role |
|-------|------|------|
| **Substrate (100% Linux)** | `compat/linux-7.1.1` | Full kernel: drivers, mm, fs, net, arch, lib, tools… |
| **Field overlay** | `SG/KILROY/` → sync | Field Die, syscall gate, UAPI, init identity |
| **Identity transform** | `kilroy-apply-identity.sh` | NAME=Field, banners, UTS, docs, configs |
| **Boot/userspace** | `boot/grok/`, `rootfs/`, `userspace/` | Grok, production root, Field CLI |

## What stays Linux (unchanged semantics)

- All POSIX/glibc ABI — syscall table, VFS, page cache, block layer, networking
- Driver model — NVMe, DRM, PCI, USB, etc.
- Build system — Kbuild, `make bzImage`, modules

## What becomes KILROY 1.0 (identity + Field)

| Surface | KILROY value |
|---------|----------------|
| OS name | `KILROY` (`uname -s`, banners, os-release) |
| Product | Field OS · Linux-compatible · **Not Linux** |
| ABI | `kilroy-field-1.0` · layout v9 |
| Release | `7.1.1-kilroy` (substrate pin visible) |
| Compat pin | `linux-7.1.1` (in telemetry only) |
| Field Die | `kernel/rtx/` — syscall boundary physics |
| Boot | Grok (not GRUB) |

## Verify complete port

```bash
./scripts/kilroy-port-complete.sh   # substrate size + overlay checklist
./scripts/kilroy-become-substrate.sh
./scripts/build-kilroy.sh
```

## File counts (typical)

- Substrate source files: ~70k+ (full Linux tree)
- Canonical Field overlay: ~120 files in `SG/KILROY/`
- Synced into substrate: overlay paths in `compat/PORT_MAP.md`