#!/usr/bin/env bash
# KILROY layout v9 — CACHE + DIRECT field static checks (beyond legacy caching)
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

echo "=== KILROY nocache field tests (layout v9) ==="

check_grep "layout v9" "KILROY_LAYOUT_VERSION.*9" "$ROOT/include/uapi/kilroy/rtx_field.h"
check_grep "slot6 CACHE" "KILROY_SLOT_CACHE.*6" "$ROOT/include/uapi/kilroy/rtx_field.h"
check_grep "slot7 DIRECT" "KILROY_SLOT_DIRECT.*7" "$ROOT/include/uapi/kilroy/rtx_field.h"
check_grep "cache struct" "struct kilroy_field_cache" "$ROOT/include/uapi/kilroy/rtx_field.h"
check_grep "direct struct" "struct kilroy_field_direct" "$ROOT/include/uapi/kilroy/rtx_field.h"

check_file "$ROOT/kernel/rtx/kilroy_cache_field.c"
check_file "$ROOT/kernel/rtx/kilroy_direct_field.c"
check_grep "Kconfig CACHE" "RTX_FIELD_CACHE_SLOT" "$ROOT/kernel/rtx/Kconfig"
check_grep "Kconfig DIRECT" "RTX_FIELD_DIRECT_SLOT" "$ROOT/kernel/rtx/Kconfig"
check_grep "Makefile cache obj" "kilroy_cache_field" "$ROOT/kernel/rtx/Makefile"
check_grep "Makefile direct obj" "kilroy_direct_field" "$ROOT/kernel/rtx/Makefile"
check_grep "defconfig CACHE" "CONFIG_RTX_FIELD_CACHE_SLOT=y" "$ROOT/arch/x86/configs/kilroy_field_defconfig"
check_grep "defconfig DIRECT" "CONFIG_RTX_FIELD_DIRECT_SLOT=y" "$ROOT/arch/x86/configs/kilroy_field_defconfig"
check_grep "identity CACHE" "CONFIG_RTX_FIELD_CACHE_SLOT=y" "$ROOT/config/kilroy-identity.config"
check_grep "identity DIRECT" "CONFIG_RTX_FIELD_DIRECT_SLOT=y" "$ROOT/config/kilroy-identity.config"
check_file "$ROOT/config/kilroy-nocache.config"
check_grep "nocache THP off" "CONFIG_TRANSPARENT_HUGEPAGE=n" "$ROOT/config/kilroy-nocache.config"

check_grep "syscall cache tick" "kilroy_cache_field_tick" "$ROOT/arch/x86/entry/syscall_64.c"
check_grep "syscall direct tick" "kilroy_direct_field_tick" "$ROOT/arch/x86/entry/syscall_64.c"
check_grep "syscall mmap direct" "kilroy_direct_field_post_mmap" "$ROOT/arch/x86/entry/syscall_64.c"
if grep -q "linux/cache.h" "$ROOT/arch/x86/entry/syscall_64.c" 2>/dev/null; then
    echo "[FAIL] syscall_64.c still includes linux/cache.h"
    FAIL=1
else
    echo "[OK] syscall_64 without linux/cache.h"
fi

check_grep "proc cache node" 'proc_create("cache"' "$ROOT/kernel/rtx/rtx_proc.c"
check_grep "proc direct node" 'proc_create("direct"' "$ROOT/kernel/rtx/rtx_proc.c"
check_grep "status slot6" "slot6_cache" "$ROOT/kernel/rtx/rtx_proc.c"
check_grep "status slot7" "slot7_direct" "$ROOT/kernel/rtx/rtx_proc.c"
check_grep "shed layers" "lru_add_drain" "$ROOT/kernel/rtx/kilroy_cache_field.c"
check_grep "drop slab" "drop_slab" "$ROOT/kernel/rtx/kilroy_cache_field.c"

check_grep "kilroy-status cache" '"cache"' "$ROOT/userspace/kilroy-status/kilroy-status.c"
check_grep "kilroy-status direct" '"direct"' "$ROOT/userspace/kilroy-status/kilroy-status.c"
check_file "$ROOT/Documentation/kilroy/fields-nocache.rst"

echo "=== nocache field tests complete ==="
exit "$FAIL"