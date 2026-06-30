# Build & Test — KILROY Field OS

## Build Field image

```bash
cd SG/KILROY
./scripts/kilroy-stage-compat.sh
./scripts/build-kilroy.sh
# -> build/bzImage  LOCALVERSION=-kilroy
```

CMake:

```bash
cd build-cmake && cmake .. && cmake --build . --target kilroy_kernel
```

## Test suite

```bash
./scripts/test-all.sh
# units + physics audit + security + Field Die compile
```

## Boot verify

```bash
cat /proc/kilroy_field/status
# name=KILROY codename=Field compat=linux-7.1.1 abi=kilroy-field-1.0

cat /proc/kilroy_field/security
```

## Workflow

1. Edit **SG/KILROY** (canonical Field source)
2. `./scripts/kilroy-sync-compat.sh` overlays onto compat substrate
3. `./scripts/build-kilroy.sh` produces Field OS boot image

Never treat the compat substrate tree as canonical source.