#!/usr/bin/env bash
# Merge KILROY CMake fragments into kernel .config
set -euo pipefail
KSRC="${1:?}"
AUTO_FRAG="${2:?}"
OPT_FRAG="${3:?}"

cd "$KSRC"
if [[ ! -f .config ]]; then
    make defconfig
fi
# Base Field Die fragment + CMake auto + menu options
cat arch/x86/configs/kilroy_field_defconfig "$AUTO_FRAG" "$OPT_FRAG" >> .config
for frag in Documentation/kilroy/config/*.config; do
    [[ -f "$frag" ]] && cat "$frag" >> .config
done
make olddefconfig
echo "[kilroy-cmake] kernel configured"