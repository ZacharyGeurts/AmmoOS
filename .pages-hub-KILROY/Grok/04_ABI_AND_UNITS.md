# KILROY Field OS — ABI & Units

## Identity strings

```
KILROY_OS_NAME        = "KILROY"
KILROY_FIELD_CODENAME = "Field"
KILROY_COMPAT_SUBSTRATE = "linux-7.1.1"
KILROY_FIELD_ABI      = "kilroy-field-1.0"
LOCALVERSION          = -kilroy
```

`/proc/kilroy_field/status` first line:

```
name=KILROY codename=Field compat=linux-7.1.1 magic=0x... abi=kilroy-field-1.0 layout=v9
```

## Linux-compatible passthrough

Userspace binaries built for Linux x86-64 run unchanged. Field ioctl/proc extensions are additive. Magic `'KILR'` replaces legacy `'RTXF'` — recompile Field-aware modules only.

## Units

| Unit | Scale | Primary use |
|------|-------|-------------|
| micro | 1e-6 | thermo, FCC, phi |
| submicro | 1e-9 | pressure, flow momentum |
| legacy milli | 1e-3 | proc writes when value < 10000 |

See `kernel/rtx/kilroy_units.h`.