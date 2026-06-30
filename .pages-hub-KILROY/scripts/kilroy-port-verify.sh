#!/usr/bin/env bash
# Verify Linux→KILROY port completeness on substrate.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=kilroy-compat-path.sh
source "$ROOT/scripts/kilroy-compat-path.sh"
SUBSTRATE="$KILROY_COMPAT_SRC"
FAIL=0

need() {
    local label="$1" path="$2" pat="${3:-.}"
    if [[ -f "$path" ]] && grep -qE "$pat" "$path" 2>/dev/null; then
        echo "[PASS] $label"
    else
        echo "[FAIL] $label ($path)"
        FAIL=1
    fi
}

echo "=== KILROY port verify ==="
echo "    substrate: $SUBSTRATE"

need "Field Die rtx_core" "$SUBSTRATE/kernel/rtx/rtx_core.c" "KILROY"
need "kilroy_boot" "$SUBSTRATE/kernel/rtx/kilroy_boot.c" "grok.security"
need "kilroy-uts" "$SUBSTRATE/init/kilroy-uts.c" "KILROY_OS_NAME"
need "version banner" "$SUBSTRATE/init/version-timestamp.c" "KILROY Field OS"
need "syscall fabric" "$SUBSTRATE/arch/x86/entry/syscall_64.c" "kilroy_nexus"
need "cache field" "$SUBSTRATE/kernel/rtx/kilroy_cache_field.c" "lru_add_drain"
need "direct field" "$SUBSTRATE/kernel/rtx/kilroy_direct_field.c" "MAP_ANONYMOUS"
need "layout v9" "$SUBSTRATE/include/uapi/kilroy/rtx_field.h" "KILROY_LAYOUT_VERSION.*9"
need "proc cache" "$SUBSTRATE/kernel/rtx/rtx_proc.c" 'proc_create\("cache"'
need "proc direct" "$SUBSTRATE/kernel/rtx/rtx_proc.c" 'proc_create\("direct"'
need "chardev ioctl" "$SUBSTRATE/kernel/rtx/kilroy_chardev.c" "misc_register"
need "ioctl GET_CACHE" "$SUBSTRATE/include/uapi/kilroy/rtx_field.h" "KILROY_IOC_GET_CACHE"
need "UAPI kilroy" "$SUBSTRATE/include/uapi/kilroy/rtx_field.h" "KILROY_FIELD_CODENAME"
need "config identity" "$SUBSTRATE/Documentation/kilroy/config/kilroy-identity.config" "RTX_FIELD_DIE"
need "config production" "$SUBSTRATE/Documentation/kilroy/config/kilroy-production.config" "BLK_DEV_NVME"
need "port map on substrate" "$SUBSTRATE/Documentation/kilroy/porting.rst" "PORT_MAP"
need "grok doc" "$SUBSTRATE/Documentation/kilroy/grok.rst" "Grok"

RTX_N="$(find "$SUBSTRATE/kernel/rtx" -maxdepth 1 -type f 2>/dev/null | wc -l)"
[[ "$RTX_N" -ge 20 ]] && echo "[PASS] kernel/rtx file count ($RTX_N)" || {
    echo "[FAIL] kernel/rtx count $RTX_N"
    FAIL=1
}

echo "=== port verify complete ==="
exit "$FAIL"