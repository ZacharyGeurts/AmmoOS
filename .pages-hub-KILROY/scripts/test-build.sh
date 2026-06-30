#!/usr/bin/env bash
# KILROY Field OS — compile Field Die + optional full image
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=kilroy-compat-path.sh
source "$ROOT/scripts/kilroy-compat-path.sh"
KSRC="${KSRC:-$KILROY_COMPAT_SRC}"
FULL="${FULL_BUILD:-0}"
JOBS="${JOBS:-$(nproc)}"

for tool in flex bison bc gcc; do
    command -v "$tool" >/dev/null || { echo "[FAIL] missing: $tool"; exit 1; }
done

echo "=== KILROY Field OS build test ==="
echo "    KSRC=$KSRC"

# Sync delta before build
if [[ -x "$ROOT/scripts/kilroy-sync-compat.sh" ]]; then
    "$ROOT/scripts/kilroy-sync-compat.sh" "$ROOT" "$KSRC"
fi

cd "$KSRC"
if [[ ! -f .config ]] || ! grep -q 'CONFIG_RTX_FIELD_NEXUS_GUARD' .config 2>/dev/null; then
    make defconfig
    cat arch/x86/configs/kilroy_field_defconfig >> .config
    yes '' | make olddefconfig >/dev/null
fi

echo "[kilroy-test] building kernel/rtx/ ..."
make -j"$JOBS" kernel/rtx/
echo "[kilroy-test] kernel/rtx: PASS"

if [[ "$FULL" == "1" ]]; then
    echo "[kilroy-test] full bzImage build ..."
    make -j"$JOBS" bzImage
    OUT="$ROOT/build"
    mkdir -p "$OUT"
    cp -f arch/x86/boot/bzImage "$OUT/bzImage"
    cp -f .config "$OUT/config"
    echo "[kilroy-test] bzImage -> $OUT/bzImage"
fi