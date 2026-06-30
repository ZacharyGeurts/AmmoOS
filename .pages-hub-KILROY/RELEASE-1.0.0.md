# KILROY 1.0.0 — Taco

**Released:** 2026-06-29  
**Codename:** Taco  
**ABI:** `kilroy-field-1.0` · layout 9

KILROY is the Field OS kernel — Linux-compatible, not Linux. The Field Die classifies every syscall; the compat substrate (linux-7.1.1 lineage) is boot foundation only.

## Stack pairing

| Sibling | Version | Role |
|---------|---------|------|
| **Grok16** | 5.0.1 | Canonical compiler — `g16`, `ammoos` profile, belt_2_0 |
| **AmmoOS** | 1.9.9h | Field desktop inside Queen — loopback `127.0.0.1` |
| **Queen** | secured shell | Browser + RTX — AmmoOS embedded |
| **ZNetwork** | pipe | Loopback sovereignty |
| **NEXUS C2** | :9477 | Command, underlay-f9 Tristate |

Stack order: **Hardware → NEXUS C2 → ZNetwork → Queen → AmmoOS**. KILROY owns syscall truth underneath.

## What ships

- **Field Die source** — `kernel/rtx/` (TIME, RAM, THERMO, CONTEXT, CPU, FLOW, CACHE, DIRECT)
- **Integration overlays** — `integration/`, `arch/x86/`, UAPI headers
- **Userspace** — `kilroy-status`, `kilroy-ioctl-test`, `field-kilroy/` C++ bridge
- **Grok boot** — Limine multi-arch EFI, themes, memtest, ISO builder
- **Per-platform bins** — Grok16-target matrix (see `kilroy-1.0.0-PLATFORMS.md`)
- **x86_64 boot image** — `bzImage` + initramfs + production rootfs staging

## Quick start (Linux x86_64)

```bash
git clone https://github.com/ZacharyGeurts/KILROY.git
cd KILROY && git checkout v1.0.0
./scripts/kilroy-stage-compat.sh    # fetch compat substrate pin
./scripts/build-kilroy.sh
./scripts/test-ioctl-smoke.sh
```

Prebuilt: extract `kilroy-1.0.0-linux-gnu-x86_64.tar.gz` → `build/bzImage`, `usr/bin/kilroy-status`.

## Validation

```bash
./scripts/check-field-stack.sh
./scripts/test-units.sh
export SG_ROOT=/path/to/SG
./Grok16/scripts/grok16-verify-ammoos.sh   # stack integration gate
```

## Platform model

Grok16 ships 17+ targets. KILROY release ships:

1. **Full overlay source** (this repo)
2. **Compiled userspace** per ELF target where `g16` cross-build applies
3. **Full kernel image** on `linux-gnu-x86_64` (primary)
4. **Boot firmware** (Limine EFI) for x86, ARM, RISC-V, LoongArch

Darwin, iOS, and Windows PE targets ship source + bootstrap docs; kernel image build is host-specific.

---

*Taco — the field kernel that finally has a plate. Ship it.*