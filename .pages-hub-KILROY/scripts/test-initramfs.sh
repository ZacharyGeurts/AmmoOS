#!/usr/bin/env bash
# Field initramfs build smoke test.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0

echo "=== KILROY initramfs tests ==="

check_file() {
    [[ -f "$1" ]] && echo "[PASS] $2" || { echo "[FAIL] $2"; FAIL=1; }
}

check_file "$ROOT/userspace/field-init/field-init.c" "field-init.c"
check_file "$ROOT/rootfs/build-initramfs.sh" "build-initramfs.sh"
grep -q 'initramfs.cpio.gz' "$ROOT/boot/grok/grok.entries.conf" && \
    echo "[PASS] grok entries reference initramfs" || { echo "[FAIL] grok initramfs"; FAIL=1; }
grep -q 'QEMU ramdisk' "$ROOT/boot/grok/grok.entries.conf" && \
    echo "[PASS] QEMU ramdisk entry" || { echo "[FAIL] ramdisk entry"; FAIL=1; }

if command -v gcc >/dev/null 2>&1; then
    "$ROOT/rootfs/build-initramfs.sh"
    check_file "$ROOT/build/initramfs.cpio.gz" "initramfs.cpio.gz built"
    if gzip -dc "$ROOT/build/initramfs.cpio.gz" | cpio -t 2>/dev/null | grep -qE '(^|/)init$'; then
        echo "[PASS] cpio contains /init"
    else
        echo "[FAIL] cpio missing init"
        FAIL=1
    fi
else
    echo "[SKIP] gcc not available"
fi

echo "=== initramfs tests complete ==="
exit "$FAIL"