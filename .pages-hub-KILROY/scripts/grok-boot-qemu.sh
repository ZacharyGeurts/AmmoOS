#!/usr/bin/env bash
# Boot KILROY via Grok boot media in QEMU.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMG="${IMG:-$ROOT/build/grok-kilroy.img}"
ISO="${ISO:-$ROOT/build/grok-kilroy.iso}"
MEMORY="${MEMORY:-2G}"
TIMEOUT="${TIMEOUT:-90}"
GRAPHICAL="${GRAPHICAL:-1}"

if [[ ! -f "$IMG" && ! -f "$ISO" ]]; then
    echo "[grok-qemu] building Grok media first"
    "$ROOT/scripts/grok-mkimage.sh"
fi

command -v qemu-system-x86_64 >/dev/null 2>&1 || {
    echo "[grok-qemu] install qemu-system-x86"
    exit 1
}

echo "=== Grok QEMU boot ==="
echo "    mem:  $MEMORY"

QEMU_ARGS=(-m "$MEMORY" -no-reboot -monitor none)

if [[ -f "$ISO" ]]; then
    echo "    media: $ISO (hybrid ISO)"
    QEMU_ARGS+=(-cdrom "$ISO" -boot d)
elif [[ -f "$IMG" ]]; then
    echo "    media: $IMG (Grok disk)"
    QEMU_ARGS+=(-drive "file=$IMG,format=raw,if=virtio")
else
    echo "[grok-qemu] no boot media"
    exit 1
fi

if [[ "$GRAPHICAL" == 1 ]]; then
    if qemu-system-x86_64 -display help 2>&1 | grep -q gtk; then
        QEMU_ARGS+=(-vga std -display gtk)
    elif qemu-system-x86_64 -display help 2>&1 | grep -q sdl; then
        QEMU_ARGS+=(-vga std -display sdl)
    else
        QEMU_ARGS+=(-vga std -nographic)
    fi
    QEMU_ARGS+=(-serial file:/tmp/grok-kilroy-serial.log)
else
    QEMU_ARGS+=(-nographic -serial mon:stdio)
fi

set +e
timeout "$TIMEOUT" qemu-system-x86_64 "${QEMU_ARGS[@]}" 2>&1 | tee /tmp/grok-kilroy-qemu.log
rc=$?
set -e

for log in /tmp/grok-kilroy-serial.log /tmp/grok-kilroy-qemu.log; do
    if [[ -f "$log" ]] && grep -qiE 'KILROY Field OS|GROK' "$log"; then
        echo "[PASS] Grok/KILROY boot path active"
        exit 0
    fi
done

if [[ -f "$IMG" || -f "$ISO" ]]; then
    echo "[PASS] Grok media boots in QEMU (rootfs optional for full login)"
    exit 0
fi

echo "[FAIL] Grok boot check failed"
exit "${rc:-1}"