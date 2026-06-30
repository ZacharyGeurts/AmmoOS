# KILROY Field OS — Grok Memory Index

**KILROY** · **Field** · **Linux-compatible** · **Not Linux**  
**Version:** KILROY 1.0 · **ABI:** `kilroy-field-1.0` · **Layout:** v9 · **Magic:** `KILR`  
**Linux:** full 7.1.1 substrate + Field overlay

| File | Purpose |
|------|---------|
| [../FIELD.md](../FIELD.md) | Identity manifesto |
| [01_PROJECT_OVERVIEW.md](01_PROJECT_OVERVIEW.md) | Field OS architecture |
| [02_FILE_MANIFEST.md](02_FILE_MANIFEST.md) | Every file in SG/KILROY |
| [03_PHYSICS_MODEL.md](03_PHYSICS_MODEL.md) | Phi/Thermo/FCC/Flow |
| [04_ABI_AND_UNITS.md](04_ABI_AND_UNITS.md) | micro/submicro, compat ABI |
| [05_BUILD_AND_TEST.md](05_BUILD_AND_TEST.md) | Build Field OS image |
| [06_ACHIEVEMENTS_AND_NEXT.md](06_ACHIEVEMENTS_AND_NEXT.md) | Done vs next |
| [07_SESSION_LOG.md](07_SESSION_LOG.md) | Change log |
| [08_CMAKE_BUILD.md](08_CMAKE_BUILD.md) | CMake menu |
| [09_PERFORMANCE.md](09_PERFORMANCE.md) | vs compat substrate |
| [10_SECURITY.md](10_SECURITY.md) | NEXUS field guard |

## Quick resume

```bash
cd /home/default/Desktop/SG/KILROY
./scripts/kilroy-stage-compat.sh
./scripts/test-all.sh
./scripts/build-kilroy.sh
```

## Trees

| Path | Role |
|------|------|
| `SG/KILROY` | **Canonical Field OS source** |
| `SG/linux-kernel/linux-7.1.1` | Compat substrate staging |
| `AMOURANTHRTX/FieldKilroy` | Userspace field engine |

## Last state (2026-06-22)

- **Identity rewrite:** KILROY Field OS, Linux-compatible, not Linux
- Field Die + NEXUS guard + `/proc/kilroy_field/security`
- `build/bzImage` · LOCALVERSION=-kilroy