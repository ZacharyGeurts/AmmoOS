#!/usr/bin/env bash
# Install KILROY production rootfs onto TEAM (or any) block device / partition.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEVICE="${1:-${KILROY_ROOT_DEVICE:-/dev/nvme1n1p1}}"
STAGING="$ROOT/rootfs/production-staging"
MNT="${MNT:-/mnt/kilroy-field}"

[[ -b "$DEVICE" ]] || { echo "[install] not a block device: $DEVICE"; exit 1; }

echo "=== KILROY production rootfs install ==="
echo "    target: $DEVICE"

"$ROOT/rootfs/build-production-rootfs.sh"

if ! blkid "$DEVICE" | grep -q 'TYPE="ext4"'; then
    echo "[install] formatting $DEVICE ext4 label=KILROY_FIELD"
    sudo mkfs.ext4 -F -L KILROY_FIELD "$DEVICE"
fi

sudo mkdir -p "$MNT"
if mountpoint -q "$MNT"; then
    sudo umount "$MNT"
fi
sudo mount "$DEVICE" "$MNT"

echo "[install] rsync rootfs -> $DEVICE"
sudo rsync -aHAX --delete "$STAGING"/ "$MNT"/

sudo mkdir -p "$MNT"/{proc,sys,dev,run}
sudo mknod -m 622 "$MNT/dev/console" c 5 1 2>/dev/null || true
sudo mknod -m 666 "$MNT/dev/null" c 1 3 2>/dev/null || true

sync
sudo umount "$MNT"
echo "[install] KILROY_FIELD rootfs on $DEVICE"
echo "    label: KILROY_FIELD"
echo "    boot:  Grok with root=LABEL=KILROY_FIELD"
blkid "$DEVICE"