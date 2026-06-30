# KILROY Field OS — Status

**Identity:** KILROY Field OS **1.0** · Linux-compatible · **Not Linux**  
**Substrate:** complete linux-7.1.1 (~105k files) + Field overlay (`compat/LINUX_MANIFEST.md`)

## Field source (canonical) ✅

All Field-native code lives in `SG/KILROY/`:

- [x] Field Die `kernel/rtx/` (25+ core files + flow + thermo_idle + nexus_guard + cache/direct)
- [x] Layout v9 CACHE + DIRECT fields — shed legacy cache retention, direct map telemetry
- [x] x86 Field entry `arch/x86/entry/`
- [x] UAPI `include/uapi/kilroy/rtx_field.h` — name=KILROY, codename=Field
- [x] Kernel identity `kernel/rtx/kilroy_identity.c` + `include/linux/kilroy_field.h`
- [x] Canonical substrate patches `init/`, `config/`, `integration/`, `Documentation/kilroy/`
- [x] Linux→KILROY port map `compat/PORT_MAP.md` + `kilroy-apply-identity.sh` + `kilroy-port-verify.sh`
- [x] Userspace `kilroy-status` CLI + `field-kilroy` ioctl bridge + production config fragments
- [x] `/dev/kilroy_field` ioctl ABI (GET_CACHE/GET_DIRECT/GET_FLOW) + `Documentation/kilroy/ioctl.rst`
- [x] Grok memtest menu entry (wish #83) + `scripts/qemu-boot-capture.sh`
- [x] NEXUS security guard + `/proc/kilroy_field/security`
- [x] **Field stack #1** — Field_Primer + Final_Eye + World_Redata + AMOURANTHRTX + Queen (`/proc/kilroy_field/stack`)
- [x] FIELDC targets `field/compiler/*.fld` + `scripts/field-recompile.sh` after field updates
- [x] Grok boot handoff `kilroy_boot.c` + `/proc/kilroy_field/boot`
- [x] Compat path resolver `kilroy-compat-path.sh` + `compat/linux-7.1.1` pin
- [x] `uname` sysname → KILROY (`kilroy-uts.c`, CONFIG_RTX_FIELD_UTS_NAME)
- [x] Field init ramdisk + Grok QEMU entry + `ci-run.sh` / GitHub workflow
- [x] **Production rootfs** on TEAM `nvme1n1` · LABEL=KILROY_FIELD · Grok on `/boot/efi`
- [x] Tests + Grok memory + CMake build
- [x] Event-driven DVFS · ASM 100µ fabric debit · DRM GPU FCC mirror · `/proc/kilroy_field/gpu`
- [x] `bench-nocache-field.sh` · `kilroy-ioctl-test` · `kilroy-gen-syscalls.sh` (386 syscalls)
- [x] Grok: memtest EFI bundled · PXE/snapshot entries · Windows coexist doc · enroll-config script
- [x] TEAM rootfs refreshed · Grok on `/boot/efi` · CI QEMU + ioctl workflow

## Compat substrate (KILROY becoming)

- [x] Pin: `SG/linux-kernel/linux-7.1.1`
- [x] `kilroy-become-substrate.sh` — sync + identity + banner + docs in tree
- [x] Field Die in `kernel/Makefile` (fixed root Makefile erroneous merge)
- [x] Boot banner: `KILROY Field OS (Linux-compatible) version ...`
- [x] `kilroy-verify-substrate.sh` + `qemu-boot-kilroy.sh`
- [x] **Grok Bootloader 1.1** — GRUB replaced; themes · in-place edit · 100 wishes · mandatory BIOS security · ReBAR hints

## Build

```bash
cd SG/KILROY
./scripts/kilroy-stage-compat.sh
./scripts/build-kilroy.sh          # also builds Grok disk image
./scripts/grok-boot-qemu.sh        # QEMU via Grok (graphical if display available)
```

Output: `build/bzImage` · `build/grok-kilroy.img` · `LOCALVERSION=-kilroy`

## Boot verify

```bash
cat /proc/kilroy_field/status
cat /proc/kilroy_field/boot      # Grok handoff: grok_security=strict
cat /proc/kilroy_field/cache     # shed_count, retention_micro
cat /proc/kilroy_field/direct    # direct_ratio_micro, coherence_ops
# name=KILROY codename=Field compat=linux-7.1.1 abi=kilroy-field-1.0 layout=v9
```

## ABI

| Field | Value |
|-------|-------|
| OS | KILROY |
| Codename | Field |
| ABI | kilroy-field-1.0 |
| Layout | v9 |
| Magic | KILR |
| Compat | linux-7.1.1 (substrate, not identity) |