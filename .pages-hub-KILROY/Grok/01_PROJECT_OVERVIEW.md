# KILROY — Field OS Overview

## Identity

**KILROY is Field. KILROY is Linux-compatible. KILROY is not Linux.**

KILROY is a **Field operating system** with a native in-kernel **Field Die** (`kernel/rtx/`). The linux-7.1.1 compat substrate provides boot infrastructure and POSIX passthrough — it is not our product name.

Codename: **Taco** (release 1.0.0). Identity: **Field** (not AmouranthOS, not Linux).

## Field Die

The Field Die classifies every x86-64 syscall:

1. **HostPassthrough** — Linux-compatible apps unchanged
2. **Fabric** — Phi/Thermo/Flow debit, entropy floor, FCC guard
3. **RAM field** — mmap/brk accounting, ZMM1024 entropy grid

Telemetry: `/proc/kilroy_field/*`

## 6-slot model

| Slot | Field name | Implementation |
|------|------------|----------------|
| 0 | TIME | genesis, seal, entropy XOR |
| 1 | RAM | ZMM1024, pressure, bandwidth |
| 2 | THERMO | budget, FCC scale, accountant |
| 3 | CONTEXT | per-syscall seal + NEXUS guard |
| 4 | CPU | fabric ops, DVFS tiers, phi coupling |
| 5 | FLOW | Tesla valve momentum |

## Design goals

- **Field-first** — physics is kernel identity, not a driver
- **Linux-compatible** — binary passthrough for userspace
- **Micro/submicro** — 1e-6 / 1e-9 fixed-point (legacy milli on proc writes < 10000)
- **Non-intrusive security** — NEXUS guard, 4-slot tamper, consumer whitelist

## Trees

| Path | Role |
|------|------|
| `SG/KILROY` | **Canonical Field OS source** → [github.com/ZacharyGeurts/KILROY](https://github.com/ZacharyGeurts/KILROY) |
| `SG/linux-kernel/linux-7.1.1` | Compat substrate staging (sync target) |
| `AMOURANTHRTX/FieldKilroy` | Userspace field engine |

## Related

- [FIELD.md](../FIELD.md) — identity manifesto
- [10_SECURITY.md](10_SECURITY.md) — NEXUS field guard