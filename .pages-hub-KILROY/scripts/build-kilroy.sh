#!/usr/bin/env bash
# Build KILROY Field OS boot image (Linux-compatible substrate + Field Die overlay).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=kilroy-compat-path.sh
source "$ROOT/scripts/kilroy-compat-path.sh"
COMPAT="$KILROY_COMPAT_SRC"
JOBS="${JOBS:-$(nproc)}"
OUT="${OUT:-$ROOT/build}"

for tool in flex bison bc; do
    command -v "$tool" >/dev/null 2>&1 || {
        echo "[kilroy] missing: $tool — sudo apt install flex bison bc libssl-dev libelf-dev"
        exit 1
    }
done

if [[ ! -f "$COMPAT/Makefile" ]]; then
    echo "[kilroy] compat substrate missing: $COMPAT"
    echo "[kilroy] run: ./scripts/kilroy-stage-compat.sh"
    exit 1
fi

echo "=== KILROY Field OS build ==="
echo "    identity:  KILROY (Field, Linux-compatible)"
echo "    abi:       kilroy-field-1.0"
echo "    substrate: $COMPAT"
echo "    proc:      /proc/kilroy_field/{status,security,stack,power,thermo,slots,cpu,ram,flow,cache,direct}"

if [[ -x "$ROOT/scripts/gen-field-stack.sh" ]]; then
    "$ROOT/scripts/gen-field-stack.sh" 2>/dev/null || true
fi
if [[ -x "$ROOT/scripts/gen-ai-wishes.sh" ]]; then
    "$ROOT/scripts/gen-ai-wishes.sh" 2>/dev/null || true
fi
if [[ -x "$ROOT/scripts/gen-hostess-comfort.sh" ]]; then
    "$ROOT/scripts/gen-hostess-comfort.sh" 2>/dev/null || true
fi

if [[ -x "$ROOT/scripts/kilroy-become-substrate.sh" ]]; then
    "$ROOT/scripts/kilroy-become-substrate.sh"
elif [[ -x "$ROOT/scripts/kilroy-sync-compat.sh" ]]; then
    "$ROOT/scripts/kilroy-sync-compat.sh" "$ROOT" "$COMPAT"
fi

cd "$COMPAT"
if [[ ! -f .config ]] || ! grep -q 'CONFIG_RTX_FIELD_DIE=y' .config 2>/dev/null; then
    make defconfig
    cat arch/x86/configs/kilroy_field_defconfig >> .config
    for frag in "$ROOT/config/"*.config; do
        [[ -f "$frag" ]] && cat "$frag" >> .config
    done
    yes '' | make olddefconfig >/dev/null
fi

make -j"$JOBS" bzImage modules
mkdir -p "$OUT"
cp -f arch/x86/boot/bzImage "$OUT/bzImage"
cp -f .config "$OUT/config"
echo "[kilroy] Field OS image -> $OUT/bzImage (LOCALVERSION=-kilroy)"

if [[ "${GROK_IMAGE:-1}" == "1" && -x "$ROOT/scripts/grok-mkimage.sh" ]]; then
    echo "[kilroy] building Grok boot ISO (set GROK_IMAGE=0 to skip)"
    "$ROOT/scripts/grok-mkimage.sh" || echo "[kilroy] Grok ISO skipped (install xorriso + run grok-fetch.sh)"
fi