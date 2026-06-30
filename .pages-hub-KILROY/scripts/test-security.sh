#!/usr/bin/env bash
# KILROY security module static checks
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0

check_file() {
    local f="$1"
    if [[ -f "$f" ]]; then
        echo "[OK] $f"
    else
        echo "[FAIL] missing $f"
        FAIL=1
    fi
}

check_grep() {
    local label="$1" pattern="$2" file="$3"
    if grep -q "$pattern" "$file"; then
        echo "[OK] $label"
    else
        echo "[FAIL] $label in $file"
        FAIL=1
    fi
}

echo "=== KILROY security tests ==="

check_file "$ROOT/kernel/rtx/kilroy_nexus_guard.c"
check_file "$ROOT/kernel/rtx/kilroy_nexus_guard.h"
check_grep "NEXUS_GUARD Kconfig" "RTX_FIELD_NEXUS_GUARD" "$ROOT/kernel/rtx/Kconfig"
check_grep "Makefile object" "kilroy_nexus_guard" "$ROOT/kernel/rtx/Makefile"
check_grep "defconfig enabled" "CONFIG_RTX_FIELD_NEXUS_GUARD=y" "$ROOT/arch/x86/configs/kilroy_field_defconfig"
check_grep "syscall hook" "kilroy_nexus_guard_evaluate" "$ROOT/arch/x86/entry/syscall_64.c"
check_grep "proc security" 'proc_create("security"' "$ROOT/kernel/rtx/rtx_proc.c"
check_grep "proc boot" 'proc_create("boot"' "$ROOT/kernel/rtx/rtx_proc.c"
check_grep "Grok handoff" "kilroy_boot" "$ROOT/kernel/rtx/Makefile"
check_grep "consumer whitelist" "kilroy_nexus_whitelisted_nr" "$ROOT/kernel/rtx/kilroy_nexus_guard.c"
check_grep "hardened defconfig" "CONFIG_HARDENED_USERCOPY=y" "$ROOT/arch/x86/configs/kilroy_field_defconfig"

if [[ "$FAIL" -eq 0 ]]; then
    echo "[kilroy-test] security PASS"
    exit 0
fi
echo "[kilroy-test] security FAIL"
exit 1