#!/usr/bin/env bash
# Apply KILROY 1.0 identity overlays to full Linux compat substrate.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SUBSTRATE="${1:?substrate tree}"

apply_init_makefile() {
    if grep -q 'kilroy-banner' "$SUBSTRATE/init/Makefile" 2>/dev/null; then
        return
    fi
    {
        echo ""
        echo "# KILROY Field OS init"
        cat "$ROOT/integration/init-Makefile.overlay"
    } >>"$SUBSTRATE/init/Makefile"
}

apply_makefile_identity() {
    if ! grep -q 'KILROY Field OS' "$SUBSTRATE/Makefile" 2>/dev/null; then
        sed -i '1a\
# KILROY Field OS — Linux-compatible. Not a Linux distribution.\
# Canonical Field source: SG/KILROY — compat substrate overlay.\
' "$SUBSTRATE/Makefile"
    fi
    sed -i 's/^NAME = .*/NAME = Field/' "$SUBSTRATE/Makefile"
}

apply_uts_sysname() {
    local uts="$SUBSTRATE/include/linux/uts.h"
    [[ -f "$uts" ]] || return
    if grep -q 'UTS_SYSNAME "Linux"' "$uts" 2>/dev/null; then
        sed -i 's/#define UTS_SYSNAME "Linux"/#define UTS_SYSNAME "KILROY" \/* KILROY 1.0 *\//' "$uts"
        echo "[kilroy-identity] uts.h UTS_SYSNAME -> KILROY"
    fi
}

echo "[kilroy-identity] KILROY 1.0 -> $SUBSTRATE"

apply_makefile_identity

# init/
cp -f "$ROOT/init/kilroy-banner.c" "$ROOT/init/kilroy-uts.c" \
      "$ROOT/init/version-timestamp.c" "$SUBSTRATE/init/"
apply_init_makefile

if ! grep -q 'kilroy_field_banner' "$SUBSTRATE/init/main.c" 2>/dev/null; then
    sed -i '/pr_notice("%s", linux_banner);/r '"$ROOT/integration/init-main.snippet" \
        "$SUBSTRATE/init/main.c"
fi

apply_uts_sysname

# Root + docs
cp -f "$ROOT/FIELD.md" "$ROOT/README.md" "$SUBSTRATE/"
cp -f "$ROOT/integration/substrate-KILROY" "$SUBSTRATE/KILROY"
cp -f "$ROOT/KILROY_VERSION" "$SUBSTRATE/KILROY_VERSION"
mkdir -p "$SUBSTRATE/Documentation/kilroy"
cp -f "$ROOT/Documentation/kilroy/"*.rst "$SUBSTRATE/Documentation/kilroy/" 2>/dev/null || true
cp -f "$ROOT/FIELD.md" "$SUBSTRATE/Documentation/kilroy/overview.rst"
cp -f "$ROOT/boot/grok/GROK.md" "$SUBSTRATE/Documentation/kilroy/grok-boot.md" 2>/dev/null || true
cp -f "$ROOT/compat/PORT_MAP.md" "$SUBSTRATE/Documentation/kilroy/PORT_MAP.md" 2>/dev/null || true
cp -f "$ROOT/compat/LINUX_MANIFEST.md" "$SUBSTRATE/Documentation/kilroy/LINUX_MANIFEST.md" 2>/dev/null || true
cp -f "$ROOT/FIELD_STATUS.md" "$SUBSTRATE/Documentation/kilroy/FIELD_STATUS.md" 2>/dev/null || true

mkdir -p "$SUBSTRATE/include/linux"
cp -f "$ROOT/include/linux/kilroy_field.h" "$SUBSTRATE/include/linux/"

cp -f "$ROOT/arch/x86/configs/kilroy_field_defconfig" \
    "$SUBSTRATE/arch/x86/configs/kilroy_defconfig"
cp -f "$ROOT/arch/x86/configs/kilroy_field_defconfig" \
    "$SUBSTRATE/arch/x86/configs/kilroy_field_defconfig"

# Config fragments staged for merge
mkdir -p "$SUBSTRATE/Documentation/kilroy/config"
cp -f "$ROOT/config/"*.config "$SUBSTRATE/Documentation/kilroy/config/"

if [[ -f "$SUBSTRATE/.config" ]]; then
    sed -i 's/^CONFIG_LOCALVERSION=.*/CONFIG_LOCALVERSION="-kilroy"/' "$SUBSTRATE/.config"
    sed -i 's/^CONFIG_LOCALVERSION_AUTO=.*/CONFIG_LOCALVERSION_AUTO=n/' "$SUBSTRATE/.config"
fi

echo "[kilroy-identity] KILROY 1.0 applied"