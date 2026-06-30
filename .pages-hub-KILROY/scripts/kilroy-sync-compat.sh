#!/usr/bin/env bash
# Overlay KILROY 1.0 Field source onto full Linux-compatible compat substrate.
set -euo pipefail
SRC="${1:?KILROY Field source root}"
DST="${2:?compat substrate tree}"

echo "[kilroy-sync] KILROY 1.0 overlay: $SRC -> $DST"

mkdir -p "$DST/include/uapi/kilroy" "$DST/include/uapi/linux" \
         "$DST/include/linux" "$DST/kernel/rtx" "$DST/init" \
         "$DST/arch/x86/include/asm" "$DST/arch/x86/entry" "$DST/arch/x86/configs" \
         "$DST/Documentation/kilroy" "$DST/Documentation/kilroy/config"

# UAPI + kernel identity
cp -f "$SRC/include/uapi/kilroy/rtx_field.h" "$DST/include/uapi/kilroy/"
cp -f "$SRC/include/uapi/linux/rtx_field.h" "$DST/include/uapi/linux/" 2>/dev/null || true
cp -f "$SRC/include/linux/kilroy_field.h" "$DST/include/linux/"

# Field Die (sources + build)
cp -f "$SRC/kernel/rtx/"* "$DST/kernel/rtx/"

# Init (canonical — replaces Linux banners)
cp -f "$SRC/init/kilroy-banner.c" "$SRC/init/kilroy-uts.c" \
      "$SRC/init/version-timestamp.c" "$DST/init/"

# x86 Field entry (full entry overlay)
cp -f "$SRC/arch/x86/include/asm/rtx_field.h" "$DST/arch/x86/include/asm/"
cp -f "$SRC/arch/x86/entry/rtx_field.S" "$DST/arch/x86/entry/"
cp -f "$SRC/arch/x86/entry/syscall_64.c" "$DST/arch/x86/entry/"
cp -f "$SRC/arch/x86/entry/entry_64.S" "$DST/arch/x86/entry/" 2>/dev/null || true
cp -f "$SRC/arch/x86/entry/Makefile" "$DST/arch/x86/entry/" 2>/dev/null || true
cp -f "$SRC/arch/x86/configs/kilroy_field_defconfig" "$DST/arch/x86/configs/"
cp -f "$SRC/arch/x86/configs/kilroy_field_defconfig" "$DST/arch/x86/configs/kilroy_defconfig"

# Docs + config fragments + port manifest
cp -f "$SRC/Documentation/kilroy/"*.rst "$DST/Documentation/kilroy/" 2>/dev/null || true
cp -f "$SRC/config/"*.config "$DST/Documentation/kilroy/config/" 2>/dev/null || true
cp -f "$SRC/compat/PORT_MAP.md" "$DST/Documentation/kilroy/PORT_MAP.md" 2>/dev/null || true
cp -f "$SRC/compat/LINUX_MANIFEST.md" "$DST/Documentation/kilroy/LINUX_MANIFEST.md" 2>/dev/null || true
cp -f "$SRC/FIELD_STATUS.md" "$DST/Documentation/kilroy/FIELD_STATUS.md" 2>/dev/null || true
cp -f "$SRC/KILROY_VERSION" "$DST/KILROY_VERSION" 2>/dev/null || true

if ! grep -q 'CONFIG_RTX_FIELD_DIE.*rtx' "$DST/kernel/Makefile" 2>/dev/null; then
    echo "[kilroy-sync] merging Field Die into kernel/Makefile"
    {
        echo ""
        echo "# KILROY Field Die (compat substrate overlay)"
        cat "$SRC/integration/kernel-Makefile.snippet"
    } >>"$DST/kernel/Makefile"
fi
if grep -q 'CONFIG_RTX_FIELD_DIE.*rtx' "$DST/Makefile" 2>/dev/null; then
    sed -i '/# KILROY Field Die/,+2d' "$DST/Makefile" 2>/dev/null || true
fi

if [[ -f "$DST/init/Kconfig" ]] && ! grep -q 'kernel/rtx/Kconfig' "$DST/init/Kconfig" 2>/dev/null; then
    {
        echo ""
        echo "# KILROY Field Die"
        cat "$SRC/integration/init-Kconfig.snippet"
    } >>"$DST/init/Kconfig"
fi

# Identity transforms (banners, UTS, Makefile, main.c)
if [[ -x "$SRC/scripts/kilroy-apply-identity.sh" ]]; then
    "$SRC/scripts/kilroy-apply-identity.sh" "$DST"
fi

echo "[kilroy-sync] KILROY 1.0 overlay complete ($(ls "$DST/kernel/rtx" | wc -l) files in kernel/rtx)"