# Linux → KILROY 1.0 port map

**Complete port:** full `linux-7.1.1` substrate + canonical `SG/KILROY/` overlay. See `LINUX_MANIFEST.md`.

Canonical edits live in `SG/KILROY/`. Compat tree (`compat/linux-7.1.1`) receives overlays + identity transforms.

## Full Linux substrate (not copied — pinned tree)

| Subsystem | Substrate path | KILROY 1.0 |
|-----------|----------------|------------|
| Core kernel | `kernel/{sched,mm,fs,net,block,drivers,...}` | Unmodified Linux semantics |
| Architecture | `arch/x86/` (except Field entry) | + Field syscall gate |
| Libraries | `lib/`, `include/` (except kilroy) | POSIX/Linux ABI |
| Build | `Makefile`, `Kconfig`, `scripts/` | NAME=Field identity |
| Modules | `drivers/`, `sound/`, `crypto/` | Full Linux driver set |

## Field overlay (copy/sync)

| Linux substrate path | KILROY canonical |
|---------------------|------------------|
| `kernel/rtx/` (+ Makefile, Kconfig) | `kernel/rtx/` |
| `arch/x86/entry/syscall_64.c` | `arch/x86/entry/` |
| `arch/x86/entry/rtx_field.S` | `arch/x86/entry/` |
| `arch/x86/entry/entry_64.S` | `arch/x86/entry/` |
| `arch/x86/entry/Makefile` | `arch/x86/entry/` |
| `arch/x86/include/asm/rtx_field.h` | `arch/x86/include/asm/` |
| `include/uapi/kilroy/` | `include/uapi/kilroy/` |
| `include/uapi/linux/rtx_field.h` | `include/uapi/linux/` (compat shim) |
| `include/linux/kilroy_field.h` | `include/linux/` |
| `init/kilroy-banner.c` | `init/` |
| `init/kilroy-uts.c` | `init/` |
| `init/version-timestamp.c` | `init/` |
| `init/main.c` banner hook | `integration/init-main.snippet` |
| `init/Makefile` kilroy objects | `integration/init-Makefile.overlay` |
| `include/linux/uts.h` UTS_SYSNAME | `kilroy-apply-identity.sh` patch |
| `Makefile` NAME=Field | `integration/Makefile-identity.snippet` |
| `Documentation/kilroy/` | `Documentation/kilroy/` |
| `arch/x86/configs/kilroy_*` | `arch/x86/configs/` |
| Root `KILROY`, `FIELD.md`, `KILROY_VERSION` | `integration/substrate-KILROY`, `FIELD.md`, `KILROY_VERSION` |

## Config fragments (merged at build)

| Fragment | Canonical |
|----------|-----------|
| Identity | `config/kilroy-identity.config` |
| Production | `config/kilroy-production.config` |
| Nocache | `config/kilroy-nocache.config` |
| Defconfig overlay | `arch/x86/configs/kilroy_field_defconfig` |

## Grok / rootfs / userspace (outside kernel tree)

| Role | KILROY |
|------|--------|
| Bootloader | `boot/grok/` |
| Production rootfs | `rootfs/` |
| Field init stub | `userspace/field-init/` |
| Field status CLI | `userspace/kilroy-status/` |
| FieldKilroy engine | `userspace/field-kilroy/` |
| ioctl smoke test | `userspace/kilroy-ioctl-test/` |
| ioctl ABI | `kernel/rtx/kilroy_chardev.c` → `/dev/kilroy_field` |
| CMake build | `cmake/`, `CMakeLists.txt` |
| CI | `.github/workflows/kilroy-test.yml` |

## Apply pipeline

```
kilroy-stage-compat.sh     → pin linux-7.1.1 tree
kilroy-sync-compat.sh      → copy Field sources + docs + configs
kilroy-apply-identity.sh   → banners, UTS, Makefile, main.c, uts.h
kilroy-become-substrate.sh → sync + identity + verify
kilroy-port-complete.sh    → full Linux + overlay audit
build-kilroy.sh              → bzImage KILROY 1.0
```