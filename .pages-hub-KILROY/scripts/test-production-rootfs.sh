#!/usr/bin/env bash
# Verify KILROY production rootfs scripts and optional TEAM device label.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0
DEVICE="${KILROY_ROOT_DEVICE:-/dev/nvme1n1p1}"

check() {
    [[ -e "$1" ]] && echo "[PASS] $2" || { echo "[FAIL] $2"; FAIL=1; }
}

echo "=== KILROY production rootfs tests ==="
check "$ROOT/rootfs/build-production-rootfs.sh" "build script"
check "$ROOT/rootfs/install-team-drive.sh" "install script"

if [[ -f "$ROOT/rootfs/production-staging/etc/os-release" ]]; then
    grep -q 'KILROY Field OS' "$ROOT/rootfs/production-staging/etc/os-release" && \
        echo "[PASS] os-release identity" || { echo "[FAIL] os-release"; FAIL=1; }
fi

if blkid "$DEVICE" 2>/dev/null | grep -q 'LABEL="KILROY_FIELD"'; then
    echo "[PASS] TEAM device labeled KILROY_FIELD ($DEVICE)"
else
    echo "[WARN] $DEVICE not labeled KILROY_FIELD (not installed yet)"
fi

grep -q 'LABEL=KILROY_FIELD' "$ROOT/boot/grok/grok.entries.conf" && \
    echo "[PASS] Grok uses LABEL=KILROY_FIELD" || { echo "[FAIL] grok root"; FAIL=1; }

echo "=== production rootfs tests complete ==="
exit "$FAIL"