#!/usr/bin/env bash
# KILROY uname identity static checks.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0

check() {
    local label="$1" pattern="$2" file="$3"
    if grep -qE "$pattern" "$file" 2>/dev/null; then
        echo "[PASS] $label"
    else
        echo "[FAIL] $label"
        FAIL=1
    fi
}

echo "=== KILROY UTS tests ==="
check "kilroy-uts.c" "KILROY_OS_NAME" "$ROOT/init/kilroy-uts.c"
check "Kconfig UTS" "RTX_FIELD_UTS_NAME" "$ROOT/kernel/rtx/Kconfig"
check "defconfig UTS" "CONFIG_RTX_FIELD_UTS_NAME=y" "$ROOT/arch/x86/configs/kilroy_field_defconfig"
check "boot proc uname" "uname_sysname=" "$ROOT/kernel/rtx/rtx_proc.c"
check "init Makefile snippet" "kilroy-uts" "$ROOT/integration/init-uts-Makefile.snippet"
echo "=== UTS tests complete ==="
exit "$FAIL"