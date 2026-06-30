#!/usr/bin/env bash
# QEMU boot log capture — CI smoke for Field Die + layout v9 proc nodes.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${IMAGE:-$ROOT/build/bzImage}"
INITRD="${INITRD:-$ROOT/build/initramfs.cpio.gz}"
LOG="${LOG:-$ROOT/build/qemu-boot.log}"
MEMORY="${MEMORY:-2G}"
TIMEOUT="${TIMEOUT:-90}"

if [[ ! -f "$IMAGE" ]]; then
    echo "[qemu-capture] missing $IMAGE — run ./scripts/build-kilroy.sh"
    exit 1
fi

if [[ ! -f "$INITRD" && -x "$ROOT/scripts/test-initramfs.sh" ]]; then
    "$ROOT/scripts/test-initramfs.sh" >/dev/null 2>&1 || true
fi

if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
    echo "[qemu-capture] install qemu-system-x86"
    exit 1
fi

mkdir -p "$(dirname "$LOG")"
echo "[qemu-capture] log -> $LOG"

ARGS=(-m "$MEMORY" -kernel "$IMAGE"
    -append "root=/dev/ram0 rw init=/init console=ttyS0 kilroy.field=1 grok.security=strict"
    -nographic -no-reboot -monitor none)

[[ -f "$INITRD" ]] && ARGS+=(-initrd "$INITRD")

timeout "$TIMEOUT" qemu-system-x86_64 "${ARGS[@]}" 2>&1 | tee "$LOG" || true

PASS=0
grep -qi 'KILROY Field OS' "$LOG" && PASS=1
grep -q 'slot6_cache\|kilroy_field' "$LOG" && PASS=$((PASS + 1))
grep -q 'field-init\|kilroy_field' "$LOG" && PASS=$((PASS + 1))

if [[ "$PASS" -ge 2 ]]; then
    echo "[PASS] QEMU boot capture ($PASS/3 markers)"
    exit 0
fi

echo "[FAIL] QEMU boot capture — see $LOG"
exit 1