# Compat Substrate

KILROY is **not Linux**. The compat substrate (linux-7.1.1 lineage) is the boot/kernel foundation only.

## Canonical paths

| Path | Role |
|------|------|
| `SG/KILROY/` | **Edit here** — Field-native source |
| `SG/compat/linux-7.1.1/` | Preferred substrate pin (symlink OK) |
| `SG/linux-kernel/linux-7.1.1/` | Legacy location (still supported) |

Scripts resolve via `kilroy-compat-path.sh`:

```bash
./scripts/kilroy-compat-link.sh   # compat/ → legacy symlink
eval "$(./scripts/kilroy-compat-path.sh)"
```

## Workflow

```
SG/KILROY → kilroy-become-substrate.sh → compat tree → bzImage + Grok image
```

Do not develop Field features in the substrate. Sync from KILROY, build, verify.