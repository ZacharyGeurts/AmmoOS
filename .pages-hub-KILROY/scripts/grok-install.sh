#!/usr/bin/env bash
# Install Grok bootloader to a mounted ESP or block device (replaces GRUB).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR="${GROK_LIMINE_SRC:-$ROOT/boot/grok/vendor/limine}"
BZIMAGE="${BZIMAGE:-$ROOT/build/bzImage}"
TARGET="${1:-}"

usage() {
    cat <<EOF
Usage: sudo $0 <mountpoint|block-device>

Examples:
  sudo $0 /boot/efi
  sudo $0 /mnt/esp
  sudo $0 /dev/nvme0n1p1   # mounts to /tmp/grok-esp-*

Grok replaces GRUB on the target ESP. GRUB packages may remain but firmware
should prefer EFI/BOOT/BOOTX64.EFI (Grok).
EOF
}

[[ -n "$TARGET" ]] || { usage; exit 1; }
[[ "$(id -u)" -eq 0 ]] || { echo "[grok-install] run as root"; exit 1; }
[[ -f "$BZIMAGE" ]] || { echo "[grok-install] missing $BZIMAGE"; exit 1; }

"$ROOT/scripts/grok-fetch.sh"
"$ROOT/scripts/grok-compose.sh"

limine_path() {
    local name="$1"
    [[ -e "$VENDOR/$name" ]] && echo "$VENDOR/$name" && return
    find "$VENDOR" -maxdepth 4 -name "$name" -print -quit
}

MNT=""
CLEANUP_MNT=0
if [[ -b "$TARGET" ]]; then
    MNT="$(mktemp -d /tmp/grok-esp-XXXXXX)"
    mount "$TARGET" "$MNT"
    CLEANUP_MNT=1
else
    MNT="$TARGET"
fi

cleanup() {
    [[ "$CLEANUP_MNT" -eq 1 ]] && umount "$MNT" 2>/dev/null || true
}
trap cleanup EXIT

BOOTX64="$(limine_path BOOTX64.EFI)"
BIOS_SYS="$(limine_path limine-bios.sys)"
LIMINE="$(limine_path limine)"

mkdir -p "$MNT/EFI/BOOT" "$MNT/boot/grok" "$MNT/boot/kilroy"

cp -f "$BOOTX64" "$MNT/EFI/BOOT/BOOTX64.EFI"
cp -f "$BIOS_SYS" "$MNT/boot/limine-bios.sys" 2>/dev/null || true
cp -f "$ROOT/boot/grok/grok.conf" "$MNT/boot/grok/grok.conf"
cp -f "$ROOT/boot/grok/grok.conf" "$MNT/boot/limine.conf"
cp -f "$ROOT/boot/grok/grok.conf" "$MNT/limine.conf"
cp -r --no-preserve=ownership "$ROOT/boot/grok/themes" "$MNT/boot/grok/"
cp -r --no-preserve=ownership "$ROOT/boot/grok/security" "$MNT/boot/grok/"
cp -r --no-preserve=ownership "$ROOT/boot/grok/speedups" "$MNT/boot/grok/"
cp -f "$ROOT/boot/grok/HELP.md" "$ROOT/boot/grok/WISHES.md" \
      "$ROOT/boot/grok/grok.base.conf" "$ROOT/boot/grok/grok.entries.conf" \
      "$MNT/boot/grok/"
cp -f "$ROOT/boot/grok/version.txt" "$MNT/boot/grok/"
cp -f "$BZIMAGE" "$MNT/boot/kilroy/bzImage"

echo "[grok-install] run grok-firmware-audit.sh on next boot host if not done"

# Deprecate GRUB: move aside if present (non-destructive)
if [[ -d "$MNT/EFI/ubuntu" || -d "$MNT/EFI/grub" ]]; then
    GRUB_BAK="$MNT/EFI/_grub_deprecated_$(date +%Y%m%d)"
    mkdir -p "$GRUB_BAK"
    [[ -d "$MNT/EFI/ubuntu" ]] && mv "$MNT/EFI/ubuntu" "$GRUB_BAK/" 2>/dev/null || true
    [[ -d "$MNT/EFI/grub" ]] && mv "$MNT/EFI/grub" "$GRUB_BAK/" 2>/dev/null || true
    echo "[grok-install] GRUB EFI entries moved to $GRUB_BAK"
fi

if [[ -b "$TARGET" && -n "$LIMINE" ]]; then
    "$LIMINE" bios-install "$TARGET" 2>/dev/null || \
        echo "[grok-install] bios-install skipped (UEFI-only media OK)"
fi

echo "[grok-install] Grok installed on $TARGET"
echo "  EFI:    $MNT/EFI/BOOT/BOOTX64.EFI"
echo "  kernel: $MNT/boot/kilroy/bzImage"
echo "  config: $MNT/boot/grok/grok.conf"