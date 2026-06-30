#!/usr/bin/env bash
# Local CI entry — mirrors .github/workflows/kilroy-test.yml
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export FULL_BUILD="${FULL_BUILD:-1}"
export GROK_FULL_BUILD="${GROK_FULL_BUILD:-0}"

echo "############################################"
echo "# KILROY CI"
echo "############################################"

for tool in flex bison bc gcc pythong; do
    command -v "$tool" >/dev/null 2>&1 || {
        echo "[ci] missing: $tool"
        exit 1
    }
done

cd "$ROOT"
./scripts/test-all.sh

if command -v qemu-system-x86_64 >/dev/null 2>&1; then
    echo "[ci] QEMU boot capture (optional)"
    ./scripts/qemu-boot-capture.sh || echo "[ci] QEMU capture skipped/failed (no display/initrd ok)"
fi

echo "[ci] ALL PASS"