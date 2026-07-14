#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Safe AmmoOS GUI (Cinnamon) + Queen desktop icons — QEMU harness.
# Uses stand-in Field image by default (SPEAR_FIELD1=img). Set SPEAR_FIELD1=host for real Field1.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ISO_CANDIDATES=(
  "${SPEAR_ISO:-}"
  "/home/zachary/Desktop/SG/NewLatest/Spear/out/spear-22.3-cinnamon-64bit-20260713.iso"
  "$ROOT/out/spear-22.3.1-field-cinnamon-64bit-20260713.iso"
  "$ROOT/out/spear-22.3.2-field-lean-cinnamon-64bit-20260713.iso"
  "$ROOT/out/spear-latest.iso"
)
ISO=""
for c in "${ISO_CANDIDATES[@]}"; do
  [[ -n "$c" && -f "$c" ]] || continue
  # skip tiny field-product ISOs
  sz=$(stat -c%s "$c" 2>/dev/null || echo 0)
  (( sz > 500000000 )) || continue
  ISO=$c; break
done
[[ -n "$ISO" ]] || { echo "no full cinnamon ISO found"; exit 1; }

OUT="$ROOT/out"
mkdir -p "$OUT/qemu-logs"
CACHE="${SPEAR_KERNEL_CACHE:-/tmp/spear-ammoos-gui-full}"
mkdir -p "$CACHE"
if [[ ! -f "$CACHE/vmlinuz" || ! -f "$CACHE/initrd.lz" || "$(cat "$CACHE/ISO_SOURCE" 2>/dev/null || true)" != "$ISO" ]]; then
  echo "extracting casper from $ISO"
  TMP=$(mktemp -d)
  xorriso -indev "$ISO" -osirrox on \
    -extract /casper/vmlinuz "$TMP/vmlinuz" \
    -extract /casper/initrd.lz "$TMP/initrd.lz"
  cp -f "$TMP/vmlinuz" "$CACHE/vmlinuz"
  cp -f "$TMP/initrd.lz" "$CACHE/initrd.lz"
  chmod 644 "$CACHE/vmlinuz" "$CACHE/initrd.lz"
  echo "$ISO" >"$CACHE/ISO_SOURCE"
  rm -rf "$TMP"
fi

UUID=$(xorriso -indev "$ISO" -osirrox on -extract /.disk/casper-uuid-generic /tmp/casper-uuid-ammoos 2>/dev/null; tr -d '\n' </tmp/casper-uuid-ammoos 2>/dev/null || true)
UUID=${UUID:-6e72f523-dc09-4880-8910-93ffa64401c5}

FDISK="${SPEAR_FIELD_DISK:-$OUT/field-disk.img}"
if [[ "${SPEAR_FIELD1:-img}" == "host" && -b /dev/disk/by-label/FIELD1 ]]; then
  FDISK=$(readlink -f /dev/disk/by-label/FIELD1)
elif [[ ! -f "$FDISK" ]]; then
  qemu-img create -f raw "$FDISK" 8G
fi
if [[ -f "$FDISK" ]] && command -v spear >/dev/null; then
  spear ffat-probe "$FDISK" 2>/dev/null | grep -q 'ffat=yes' || spear ffat-force "$FDISK" || true
fi

STAMP=$(date +%Y%m%d-%H%M%S)
SERIAL="$OUT/qemu-logs/spear-ammoos-gui-${STAMP}.log"
echo "$SERIAL" >"$OUT/qemu-logs/current-serial.path"
MEM="${SPEAR_QEMU_MEM:-4G}"

# Safe normal desktop: no long systemd.mask list (breaks generator on some boots)
APPEND="boot=casper uuid=${UUID} username=spear hostname=spear spear_mode=normal spear_harden=1 quiet loglevel=3 fsck.mode=skip raid=noautodetect noresume apparmor=1 security=apparmor console=tty0 console=ttyS0,115200n8 ---"

echo "ISO=$ISO"
echo "SERIAL=$SERIAL"
echo "FIELD=$FDISK"
echo "Queen desktop icon is on the guest Spearmint desktop (Exec=/usr/local/bin/queen)."
echo "Host safe Queen: queen  (profile ~/.queen/profile-safe)"

exec qemu-system-x86_64 \
  -name Spear-AmmoOS-GUI \
  -enable-kvm -m "$MEM" -smp "${SPEAR_SMP:-4}" -cpu host \
  -machine q35,accel=kvm \
  -display gtk,gl=off,window-close=on \
  -vga std \
  -device virtio-net-pci,netdev=n0 -netdev user,id=n0 \
  -cdrom "$ISO" \
  -kernel "$CACHE/vmlinuz" -initrd "$CACHE/initrd.lz" -append "$APPEND" \
  -drive "file=$FDISK,format=raw,if=none,id=field1,cache=writeback" \
  -device virtio-blk-pci,drive=field1,serial=FIELD1 \
  -serial "file:$SERIAL" \
  -monitor none
  # Guest poweroff exits QEMU; guest reboot reboots guest. Never -no-shutdown/-no-reboot (those pause as [Paused]).