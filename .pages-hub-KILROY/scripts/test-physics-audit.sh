#!/usr/bin/env bash
# KILROY 1.0 — verify physics constants are micro/submicro (not stale milli internals)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0

check_absent() {
    local path="$1" pattern="$2" label="$3"
    if grep -qE "$pattern" "$path" 2>/dev/null; then
        echo "[FAIL] $label: found '$pattern' in $path"
        FAIL=1
    else
        echo "[PASS] $label"
    fi
}

check_present() {
    local path="$1" pattern="$2" label="$3"
    if grep -qE "$pattern" "$path" 2>/dev/null; then
        echo "[PASS] $label"
    else
        echo "[FAIL] $label: missing '$pattern' in $path"
        FAIL=1
    fi
}

echo "=== KILROY 1.0 physics audit ==="

# No stale internal milli field names in kernel sources
for f in "$ROOT"/kernel/rtx/*.c "$ROOT"/kernel/rtx/*.h; do
    [[ "$(basename "$f")" == "kilroy_units.h" ]] && continue
    check_absent "$f" 'budget_milli|pressure_milli|entropy_milli|phi_milli|rate_milli' \
        "no stale _milli internals in $(basename "$f")"
done

# ASM hot path uses micro constants
check_present "$ROOT/arch/x86/include/asm/rtx_field.h" 'RTX_ENTROPY_FLOOR_MICRO.*2000' \
    "ASM entropy floor = 2000 micro (legacy 2 milli)"
check_present "$ROOT/arch/x86/include/asm/rtx_field.h" 'RTX_FABRIC_DEBIT_ASM_MICRO.*100' \
    "ASM fabric debit = 100 micro (submicro-precision path)"

# UAPI phi
check_present "$ROOT/include/uapi/kilroy/rtx_field.h" 'KILROY_FIELD_PHI_MICRO.*618000' \
    "UAPI phi micro = 618000"
check_present "$ROOT/include/uapi/kilroy/rtx_field.h" 'KILROY_VERSION_STRING.*"1.0"' \
    "KILROY version 1.0"

# Power burst thresholds in micro
check_present "$ROOT/kernel/rtx/rtx_power.c" 'KILROY_MICRO_FROM_MILLI\(200\)' \
    "burst thermo threshold uses micro"
check_present "$ROOT/kernel/rtx/rtx_power.c" '10 \* KILROY_SUBMICRO_PER_MICRO' \
    "RAM pressure permille→percent fix"

# Proc legacy compat
check_present "$ROOT/kernel/rtx/rtx_proc.c" 'kilroy_norm_micro' \
    "proc thermo write normalizes legacy milli"
check_present "$ROOT/kernel/rtx/rtx_proc.c" 'compat=%s' \
    "status shows compat substrate pin"
check_present "$ROOT/include/uapi/kilroy/rtx_field.h" 'KILROY_FIELD_CODENAME.*"Field"' \
    "UAPI codename is Field"
check_present "$ROOT/include/uapi/kilroy/rtx_field.h" 'KILROY_LAYOUT_VERSION.*9' \
    "UAPI layout v9"
check_present "$ROOT/include/uapi/kilroy/rtx_field.h" 'KILROY_SLOT_CACHE' \
    "UAPI CACHE slot"
check_present "$ROOT/include/uapi/kilroy/rtx_field.h" 'KILROY_SLOT_DIRECT' \
    "UAPI DIRECT slot"

echo "=== audit complete ==="
exit "$FAIL"