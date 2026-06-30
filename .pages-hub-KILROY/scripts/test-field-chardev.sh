#!/usr/bin/env bash
# /dev/kilroy_field ioctl ABI static checks (layout v9)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0

check_grep() {
    local label="$1" pattern="$2" file="$3"
    if grep -q "$pattern" "$file"; then
        echo "[OK] $label"
    else
        echo "[FAIL] $label in $file"
        FAIL=1
    fi
}

echo "=== KILROY chardev ioctl tests ==="

check_grep "chardev source" "misc_register" "$ROOT/kernel/rtx/kilroy_chardev.c"
check_grep "GET_CACHE ioctl" "KILROY_IOC_GET_CACHE" "$ROOT/include/uapi/kilroy/rtx_field.h"
check_grep "GET_DIRECT ioctl" "KILROY_IOC_GET_DIRECT" "$ROOT/include/uapi/kilroy/rtx_field.h"
check_grep "GET_FLOW ioctl" "KILROY_IOC_GET_FLOW" "$ROOT/include/uapi/kilroy/rtx_field.h"
check_grep "flow struct" "struct kilroy_field_flow" "$ROOT/include/uapi/kilroy/rtx_field.h"
check_grep "Kconfig chardev" "RTX_FIELD_CHARDEV" "$ROOT/kernel/rtx/Kconfig"
check_grep "Makefile chardev" "kilroy_chardev" "$ROOT/kernel/rtx/Makefile"
check_grep "defconfig chardev" "CONFIG_RTX_FIELD_CHARDEV=y" "$ROOT/arch/x86/configs/kilroy_field_defconfig"
check_grep "FieldKilroy bridge" "pullCacheFromKernel" "$ROOT/userspace/field-kilroy/FieldKilroyKernel.cpp"
check_grep "FieldKilroy layout v9" "KILROY_LAYOUT_VERSION = 9" "$ROOT/userspace/field-kilroy/FieldKilroyKernel.hpp"

echo "=== chardev tests complete ==="
exit "$FAIL"