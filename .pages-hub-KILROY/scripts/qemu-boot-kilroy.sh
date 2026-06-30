#!/usr/bin/env bash
# Boot KILROY Field OS in QEMU — prefers Grok ISO; falls back to direct bzImage.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ISO="${ISO:-$ROOT/build/grok-kilroy.iso}"
IMAGE="${IMAGE:-$ROOT/build/bzImage}"
MEMORY="${MEMORY:-2G}"
TIMEOUT="${TIMEOUT:-45}"

if [[ -f "$ISO" && -x "$ROOT/scripts/grok-boot-qemu.sh" ]]; then
    exec "$ROOT/scripts/grok-boot-qemu.sh"
fi

if [[ ! -f "$IMAGE" ]]; then
    echo "[kilroy-qemu] missing $IMAGE — run ./scripts/build-kilroy.sh first"
    exit 1
fi

if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
    echo "[kilroy-qemu] install qemu-system-x86"
    exit 1
fi

echo "=== KILROY QEMU smoke boot ==="
echo "    image: $IMAGE"
echo "    mem:   $MEMORY"
echo "    hint:  look for 'KILROY Field OS' in serial output"

timeout "$TIMEOUT" qemu-system-x86_64 \
    -m "$MEMORY" \
    -kernel "$IMAGE" \
    -append "console=ttyS0 quiet" \
    -nographic \
    -no-reboot \
    -monitor none \
    2>&1 | tee /tmp/kilroy-qemu.log || true

if grep -qi 'KILROY Field OS' /tmp/kilroy-qemu.log; then
    echo "[PASS] KILROY banner seen in QEMU serial log"
    exit 0
fi

echo "[FAIL] KILROY banner not found — see /tmp/kilroy-qemu.log"
exit 1