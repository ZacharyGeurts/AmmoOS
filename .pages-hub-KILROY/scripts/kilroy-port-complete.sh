#!/usr/bin/env bash
# KILROY 1.0 — verify full Linux substrate + complete Field overlay.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=kilroy-compat-path.sh
source "$ROOT/scripts/kilroy-compat-path.sh"
SUBSTRATE="$KILROY_COMPAT_SRC"
FAIL=0

need() {
    local label="$1" path="$2"
    if [[ -e "$path" ]]; then
        echo "[PASS] $label"
    else
        echo "[FAIL] $label — $path"
        FAIL=1
    fi
}

need_grep() {
    local label="$1" pat="$2" file="$3"
    if [[ -f "$file" ]] && grep -qE "$pat" "$file" 2>/dev/null; then
        echo "[PASS] $label"
    else
        echo "[FAIL] $label ($file)"
        FAIL=1
    fi
}

echo "=== KILROY 1.0 complete port verify ==="
echo "    canonical: $ROOT"
echo "    substrate: $SUBSTRATE"

# Full Linux tree presence
for d in kernel arch include lib drivers fs mm net block crypto sound init scripts tools; do
    need "linux/$d" "$(readlink -f "$SUBSTRATE")/$d"
done
need "linux Makefile" "$(readlink -f "$SUBSTRATE")/Makefile"
need "linux Kconfig" "$(readlink -f "$SUBSTRATE")/Kconfig"
SUBSTRATE_FILES="$(find -L "$SUBSTRATE" -type f 2>/dev/null | wc -l)"
[[ "$SUBSTRATE_FILES" -ge 50000 ]] && echo "[PASS] substrate file count ($SUBSTRATE_FILES)" || {
    echo "[FAIL] substrate too small ($SUBSTRATE_FILES) — run kilroy-stage-compat.sh"
    FAIL=1
}

# Canonical KILROY 1.0 markers
need "KILROY_VERSION" "$ROOT/KILROY_VERSION"
need "LINUX_MANIFEST" "$ROOT/compat/LINUX_MANIFEST.md"
need "PORT_MAP" "$ROOT/compat/PORT_MAP.md"

# Overlay synced (post become-substrate)
RTX_N="$(find "$SUBSTRATE/kernel/rtx" -maxdepth 1 -type f 2>/dev/null | wc -l)"
[[ "$RTX_N" -ge 25 ]] && echo "[PASS] kernel/rtx overlay ($RTX_N files)" || {
    echo "[FAIL] kernel/rtx count $RTX_N — run kilroy-become-substrate.sh"
    FAIL=1
}

need_grep "Field Die Kconfig" "RTX_FIELD_DIE" "$SUBSTRATE/kernel/rtx/Kconfig"
need_grep "chardev" "kilroy_chardev" "$SUBSTRATE/kernel/rtx/Makefile"
need_grep "drm fcc" "kilroy_drm_field" "$SUBSTRATE/kernel/rtx/Makefile"
need_grep "syscall fabric" "kilroy_cache_field_tick" "$SUBSTRATE/arch/x86/entry/syscall_64.c"
need_grep "ASM gate" "rtx_syscall_preflight" "$SUBSTRATE/arch/x86/entry/rtx_field.S"
need_grep "layout v9" "KILROY_LAYOUT_VERSION.*9" "$SUBSTRATE/include/uapi/kilroy/rtx_field.h"
need_grep "identity NAME" '^NAME = Field' "$SUBSTRATE/Makefile"
need_grep "KILROY banner string" "KILROY Field OS" "$SUBSTRATE/init/version-timestamp.c"
need_grep "main.c hook" "kilroy_field_banner" "$SUBSTRATE/init/main.c"
need_grep "uts sysname KILROY" 'UTS_SYSNAME "KILROY"' "$SUBSTRATE/include/linux/uts.h"
need_grep "kilroy-uts module" "kilroy-uts" "$SUBSTRATE/init/Makefile"
need_grep "proc gpu" 'proc_create\("gpu"' "$SUBSTRATE/kernel/rtx/rtx_proc.c"
need_grep "docs ioctl" "ioctl" "$SUBSTRATE/Documentation/kilroy/index.rst"
need_grep "config identity" "RTX_FIELD_DIE" "$SUBSTRATE/Documentation/kilroy/config/kilroy-identity.config"
need_grep "config nocache" "TRANSPARENT_HUGEPAGE" "$SUBSTRATE/Documentation/kilroy/config/kilroy-nocache.config"
need_grep "substrate marker" "kilroy-field-1.0" "$SUBSTRATE/KILROY"

CANONICAL_N="$(find "$ROOT" -type f \( -path "$ROOT/kernel/*" -o -path "$ROOT/arch/*" \
    -o -path "$ROOT/include/*" -o -path "$ROOT/init/*" -o -path "$ROOT/userspace/*" \
    -o -path "$ROOT/config/*" -o -path "$ROOT/Documentation/kilroy/*" \) 2>/dev/null | wc -l)"
echo "[INFO] canonical Field sources: $CANONICAL_N files"

echo "=== complete port verify: $([[ $FAIL -eq 0 ]] && echo PASS || echo FAIL) ==="
exit "$FAIL"