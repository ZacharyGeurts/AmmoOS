#!/usr/bin/env bash
# Build minimal KILROY Field initramfs for Grok QEMU ramdisk boot.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/userspace/field-init/field-init.c"
STAGING="$ROOT/rootfs/staging"
OUT="${OUT:-$ROOT/build/initramfs.cpio.gz}"

mkdir -p "$STAGING"/{proc,sys,dev,newroot}

echo "[initramfs] compiling field-init"
gcc -O2 -static -Wall -Wextra -o "$STAGING/init" "$SRC"

if [[ ! -e "$STAGING/dev/console" ]]; then
    sudo mknod -m 622 "$STAGING/dev/console" c 5 1 2>/dev/null || \
        mknod -m 622 "$STAGING/dev/console" c 5 1 2>/dev/null || \
        echo "[initramfs] warn: no /dev/console node"
fi
if [[ ! -e "$STAGING/dev/null" ]]; then
    mknod -m 666 "$STAGING/dev/null" c 1 3 2>/dev/null || true
fi

mkdir -p "$(dirname "$OUT")"
(
    cd "$STAGING"
    find . -print0 | sort -z | cpio --null -o --format=newc | gzip -9
) >"$OUT"

echo "[initramfs] -> $OUT ($(wc -c <"$OUT") bytes)"