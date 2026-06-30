# KILROY Field OS — Identity

## The rewrite

We are **not Linux anymore**. We are **Field**. We are **KILROY**.

Linux is our **compatibility layer** — not our name, not our architecture story, not what we ship as identity. KILROY is a Field operating system that happens to run the Linux userspace ABI so your tools, games, and scripts keep working.

## What KILROY is

**KILROY** = Field OS with a native **Field Die** at the syscall boundary.

Every syscall passes through Field classification:

- **HostPassthrough** — Linux-compatible POSIX path, zero semantic change
- **Fabric** — Phi / Thermo / Flow physics debit and FCC guard
- **RAM field** — ZMM1024 memory fabric, pressure, entropy

Field state is first-class: TIME, RAM, THERMO, CONTEXT, CPU, FLOW, CACHE, DIRECT (layout v9) — not afterthought cgroup stats.

**Beyond caching:** Linux page cache stays for ABI compat; Field Die sheds slab/LRU retention under pressure and routes anonymous maps through the DIRECT field.

## What we call things

| Term | Meaning |
|------|---------|
| **KILROY** | The OS. The product. The bootable Field image. |
| **Field** | Native physics + integrity layer (`kernel/rtx/`) |
| **Field Die** | In-syscall scheduler for field operations |
| **Compat substrate** | linux-7.1.1 lineage tree — boot foundation only |
| **Linux-compatible** | glibc/POSIX/ioctl binary passthrough |

Never say "KILROY Linux kernel" in user-facing text. Say **KILROY Field OS, Linux-compatible**.

## ABI

```
name:     KILROY
codename: Field
abi:      kilroy-field-1.0
magic:    0x4B494C52 ('KILR')
compat:   linux-7.1.1 (substrate pin, not identity)
```

## Security (NEXUS field awareness)

- 4-slot tamper verify (TIME/MEMORY/THERMO/CONTEXT)
- NEXUS behavioral guard (amortized, consumer-safe)
- `/proc/kilroy_field/security`

## Boot chain (Grok — not GRUB)

```
Power-on → Grok Bootloader (graphical menu)
        → KILROY Field OS bzImage
        → Field Die active (/proc/kilroy_field/)
```

Grok is the field-native boot manager. GRUB is deprecated. See `boot/grok/GROK.md`.

## KILROY 1.0 = all of Linux + Field

The **complete** linux-7.1.1 tree is the compat substrate (`compat/linux-7.1.1`). Every Linux driver, mm, fs, and net subsystem ships unchanged in semantics. KILROY adds Field Die, identity, and Grok boot on top. See `compat/LINUX_MANIFEST.md`.

## Build chain

```
SG/KILROY (canonical Field source)
    → kilroy-sync-compat.sh
    → compat substrate tree (linux-7.1.1)
    → bzImage (LOCALVERSION=-kilroy)
    → grok-mkimage.sh → grok-kilroy.iso
```

We edit **KILROY**. The compat tree is staging output.

## Related

- **AMOURANTHRTX FieldKilroy** — userspace field pump
- **NEXUS-Shield** — endpoint field security (userspace companion)