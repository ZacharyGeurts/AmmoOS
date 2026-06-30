# KILROY Field Security

Field-native security on the syscall boundary — not a Linux security module.

## Layers

| Layer | Field component |
|-------|-----------------|
| Integrity | 4-slot tamper verify |
| Behavior | NEXUS guard (amortized) |
| Predictive | score correlation → vigil tighten |
| Consumer-safe | syscall whitelist |

## Proc

```bash
cat /proc/kilroy_field/security
```

## Build

```bash
./scripts/kilroy-stage-compat.sh
./scripts/build-kilroy.sh
```

Userspace companion: [NEXUS-Shield](https://github.com/ZacharyGeurts/NEXUS-Shield).