#!/usr/bin/env bash
# Grok → kernel boot handoff static checks.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0

check() {
    local label="$1" pattern="$2" file="$3"
    if grep -qE "$pattern" "$file" 2>/dev/null; then
        echo "[PASS] $label"
    else
        echo "[FAIL] $label — $pattern in $file"
        FAIL=1
    fi
}

echo "=== KILROY Grok boot handoff tests ==="

check "kilroy_boot.c" "grok.security=" "$ROOT/kernel/rtx/kilroy_boot.c"
check "kilroy.field cmdline" "kilroy.field=" "$ROOT/kernel/rtx/kilroy_boot.c"
check "waived alert" "WAIVED" "$ROOT/kernel/rtx/kilroy_boot.c"
check "Makefile object" "kilroy_boot.o" "$ROOT/kernel/rtx/Makefile"
check "boot proc" 'proc_create\("boot"' "$ROOT/kernel/rtx/rtx_proc.c"
check "security shows grok" "grok_security=" "$ROOT/kernel/rtx/rtx_proc.c"
check "grok strict cmdline" "grok.security=strict" "$ROOT/boot/grok/grok.entries.conf"
check "grok waived cmdline" "grok.security=waived" "$ROOT/boot/grok/grok.entries.conf"

echo "=== boot handoff complete ==="
exit "$FAIL"