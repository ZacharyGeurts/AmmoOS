#!/usr/bin/env bash
# Verify KILROY identity markers in compat substrate after become-substrate.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=kilroy-compat-path.sh
source "$ROOT/scripts/kilroy-compat-path.sh"
SUBSTRATE="$KILROY_COMPAT_SRC"
FAIL=0

check() {
    local label="$1" path="$2" pattern="$3"
    if grep -qE "$pattern" "$path" 2>/dev/null; then
        echo "[PASS] $label"
    else
        echo "[FAIL] $label — missing '$pattern' in $path"
        FAIL=1
    fi
}

echo "=== KILROY substrate identity verify ==="
echo "    substrate: $SUBSTRATE"

[[ -f "$SUBSTRATE/Makefile" ]] || { echo "[FAIL] substrate missing"; exit 1; }

check "root KILROY marker" "$SUBSTRATE/KILROY" "kilroy-field-1.0"
check "FIELD.md present" "$SUBSTRATE/FIELD.md" "We are \\*\\*not Linux"
check "Makefile NAME=Field" "$SUBSTRATE/Makefile" '^NAME = Field'
check "version banner" "$SUBSTRATE/init/version-timestamp.c" "KILROY Field OS"
check "kilroy-banner.c" "$SUBSTRATE/init/kilroy-banner.c" "kilroy_field_banner"
check "main.c early banner" "$SUBSTRATE/init/main.c" "kilroy_field_banner"
check "Field Die in kernel/Makefile" "$SUBSTRATE/kernel/Makefile" 'CONFIG_RTX_FIELD_DIE.*rtx'
if grep -q 'CONFIG_RTX_FIELD_DIE.*rtx' "$SUBSTRATE/Makefile" 2>/dev/null; then
    echo "[FAIL] root Makefile still has rtx/ — should be kernel/Makefile only"
    FAIL=1
else
    echo "[PASS] root Makefile clean (no rtx/)"
fi
check "proc status source" "$SUBSTRATE/kernel/rtx/rtx_proc.c" 'compat=%s'
check "UAPI kilroy path" "$SUBSTRATE/include/uapi/kilroy/rtx_field.h" 'KILROY_FIELD_CODENAME.*"Field"'
check "docs index" "$SUBSTRATE/Documentation/kilroy/index.rst" "KILROY Field OS"
check "identity module" "$SUBSTRATE/kernel/rtx/kilroy_identity.c" "kilroy_field_abi"
check "Grok boot module" "$SUBSTRATE/kernel/rtx/kilroy_boot.c" "grok.security"
check "boot proc" "$SUBSTRATE/kernel/rtx/rtx_proc.c" 'proc_create\("boot"'
check "kilroy-uts" "$SUBSTRATE/init/kilroy-uts.c" "KILROY_OS_NAME"
check "uts.h KILROY" "$SUBSTRATE/include/linux/uts.h" 'UTS_SYSNAME "KILROY"'
check "KILROY_VERSION" "$SUBSTRATE/KILROY_VERSION" "KILROY Field OS 1.0"
check "LINUX_MANIFEST" "$SUBSTRATE/Documentation/kilroy/LINUX_MANIFEST.md" "complete Linux"
check "LOCALVERSION" "$SUBSTRATE/.config" 'CONFIG_LOCALVERSION="-kilroy"' 2>/dev/null || \
    echo "[WARN] .config missing or LOCALVERSION not set — run build-kilroy.sh"

echo "=== substrate verify complete ==="
exit "$FAIL"