#!/usr/bin/env bash
# Build ioctl smoke binary; run if /dev/kilroy_field present.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$ROOT/build/kilroy-ioctl-test"
SRC="$ROOT/userspace/kilroy-ioctl-test/kilroy-ioctl-test.c"

echo "=== KILROY ioctl smoke ==="

command -v gcc >/dev/null 2>&1 || { echo "[SKIP] gcc missing"; exit 0; }

gcc -O2 -I"$ROOT/include/uapi" -o "$BIN" "$SRC"
echo "[PASS] built $BIN"

if [[ -c /dev/kilroy_field ]]; then
    "$BIN" && echo "[PASS] runtime ioctl on target" || exit 1
else
    echo "[SKIP] /dev/kilroy_field not present (QEMU/target boot required)"
fi