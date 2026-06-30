#!/usr/bin/env bash
# Static checks for KILROY 1.0 complete Linux port infrastructure.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0

check() {
    [[ -e "$1" ]] && echo "[PASS] $2" || { echo "[FAIL] $2"; FAIL=1; }
}

echo "=== KILROY 1.0 complete port tests ==="
check "$ROOT/KILROY_VERSION" "KILROY_VERSION"
check "$ROOT/compat/LINUX_MANIFEST.md" "LINUX_MANIFEST.md"
check "$ROOT/scripts/kilroy-port-complete.sh" "port-complete script"
grep -q 'kilroy-apply-identity' "$ROOT/scripts/kilroy-sync-compat.sh" && \
    echo "[PASS] sync invokes apply-identity" || { echo "[FAIL] sync missing identity"; FAIL=1; }
grep -q 'UTS_SYSNAME' "$ROOT/scripts/kilroy-apply-identity.sh" && \
    echo "[PASS] apply-identity patches uts.h" || { echo "[FAIL] uts patch"; FAIL=1; }
grep -q 'kilroy-become-substrate' "$ROOT/CMakeLists.txt" && \
    echo "[PASS] CMake uses become-substrate" || { echo "[FAIL] CMake sync path"; FAIL=1; }
grep -q 'RTX_FIELD_CACHE_SLOT' "$ROOT/cmake/KILROYFragments.cmake" && \
    echo "[PASS] CMake CACHE fragment" || { echo "[FAIL] CMake fragments"; FAIL=1; }
[[ ! -f "$ROOT/arch/x86/configs/rtx_field_defconfig" ]] && \
    echo "[PASS] deprecated rtx_field_defconfig removed" || { echo "[FAIL] stale defconfig"; FAIL=1; }
check "$ROOT/Documentation/kilroy/linux-substrate.rst" "linux-substrate.rst"
echo "=== complete port tests done ==="
exit "$FAIL"