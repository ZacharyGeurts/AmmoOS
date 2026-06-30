#!/usr/bin/env bash
# Build KILROY production rootfs tree (busybox + Field identity).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAGING="${STAGING:-$ROOT/rootfs/production-staging}"
if [[ -z "${BUSYBOX:-}" ]]; then
    for candidate in /usr/bin/busybox /bin/busybox "$(command -v busybox 2>/dev/null || true)"; do
        [[ -n "$candidate" && -x "$candidate" ]] || continue
        if ! ldd "$candidate" >/dev/null 2>&1; then
            BUSYBOX="$candidate"
            break
        fi
    done
    BUSYBOX="${BUSYBOX:-$(command -v busybox)}"
fi

[[ -n "$BUSYBOX" ]] || { echo "[rootfs] busybox required"; exit 1; }

echo "[rootfs] staging -> $STAGING"
rm -rf "$STAGING"
mkdir -p "$STAGING"/{bin,sbin,etc,proc,sys,dev,run,tmp,root,home,usr/bin,boot/kilroy,var/log,lib/modules}

cp -f "$BUSYBOX" "$STAGING/bin/busybox"
chmod 755 "$STAGING/bin/busybox"
(
    cd "$STAGING"
    for app in sh ash mount umount ls cat echo sleep reboot poweroff init \
               mdev mkdir mknod ln grep sed awk dmesg uname hostname getty login \
               sulogin find cp mv rm chmod chown mkfs.ext4 blkid; do
        ln -sf /bin/busybox "bin/$app" 2>/dev/null || true
    done
    ln -sf /bin/busybox sbin/init
    ln -sf /bin/busybox bin/login
)

cat >"$STAGING/etc/os-release" <<'EOF'
NAME="KILROY"
PRETTY_NAME="KILROY Field OS"
ID=kilroy
ID_LIKE=linux
VERSION="1.0"
VERSION_ID="1.0"
VARIANT="Field"
VARIANT_ID=field
KILROY_ABI=kilroy-field-1.0
KILROY_COMPAT=linux-7.1.1
EOF

cat >"$STAGING/etc/hostname" <<'EOF'
KILROY-Field
EOF

cat >"$STAGING/etc/fstab" <<'EOF'
# KILROY Field OS — production root
LABEL=KILROY_FIELD  /       ext4  defaults,noatime  0 1
tmpfs               /tmp    tmpfs defaults,mode=1777  0 0
tmpfs               /run    tmpfs defaults,mode=755   0 0
proc                /proc   proc  defaults          0 0
sysfs               /sys    sysfs defaults          0 0
EOF

cat >"$STAGING/etc/inittab" <<'EOF'
# KILROY Field init (busybox)
::sysinit:/etc/init.d/rcS
::respawn:/sbin/getty -L tty1 115200 vt100
::respawn:/sbin/getty -L ttyS0 115200 vt100
::ctrlaltdel:/sbin/reboot
::shutdown:/bin/umount -a -r
EOF

mkdir -p "$STAGING/etc/init.d"
cat >"$STAGING/etc/init.d/rcS" <<'EOF'
#!/bin/sh
# KILROY Field OS boot
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev 2>/dev/null || /bin/mdev -s
mount -a
hostname KILROY-Field
if [ -r /proc/kilroy_field/status ]; then
    echo "=== KILROY Field OS ==="
    cat /proc/kilroy_field/status
    cat /proc/kilroy_field/boot 2>/dev/null
    cat /proc/kilroy_field/cache 2>/dev/null
    cat /proc/kilroy_field/direct 2>/dev/null
fi
if [ -c /dev/kilroy_field ]; then
    echo "ioctl: /dev/kilroy_field (layout v9)"
fi
echo "KILROY Field rootfs ready — Linux-compatible"
EOF
chmod 755 "$STAGING/etc/init.d/rcS"

cat >"$STAGING/etc/issue" <<'EOF'
KILROY Field OS — Linux-compatible. Not Linux.
EOF

cat >"$STAGING/etc/motd" <<'EOF'
Welcome to KILROY Field OS.
  kilroy-status all
  cat /proc/kilroy_field/cache
  ioctl ABI: /dev/kilroy_field
EOF

cat >"$STAGING/etc/passwd" <<'EOF'
root:x:0:0:KILROY Field root:/root:/bin/sh
EOF

cat >"$STAGING/etc/group" <<'EOF'
root:x:0:
EOF

cat >"$STAGING/etc/shadow" <<'EOF'
root::0:0:99999:7:::
EOF

chmod 644 "$STAGING/etc/shadow"
chmod 1777 "$STAGING/tmp"

# KILROY userspace CLIs
if command -v gcc >/dev/null 2>&1; then
    if [[ -f "$ROOT/userspace/kilroy-status/kilroy-status.c" ]]; then
        gcc -O2 -static -o "$STAGING/usr/bin/kilroy-status" \
            "$ROOT/userspace/kilroy-status/kilroy-status.c" 2>/dev/null && \
            echo "[rootfs] kilroy-status CLI" || true
    fi
    if [[ -f "$ROOT/userspace/kilroy-ioctl-test/kilroy-ioctl-test.c" ]]; then
        gcc -O2 -static -I"$ROOT/include/uapi" \
            -o "$STAGING/usr/bin/kilroy-ioctl-test" \
            "$ROOT/userspace/kilroy-ioctl-test/kilroy-ioctl-test.c" 2>/dev/null && \
            echo "[rootfs] kilroy-ioctl-test" || true
    fi
fi

# Kernel artifacts when present
[[ -f "$ROOT/build/bzImage" ]] && cp -f "$ROOT/build/bzImage" "$STAGING/boot/kilroy/"
# shellcheck source=kilroy-compat-path.sh
source "$ROOT/scripts/kilroy-compat-path.sh"
KVER="$(make -s -C "$KILROY_COMPAT_SRC" kernelrelease 2>/dev/null || true)"
if [[ -n "$KVER" && -d "$KILROY_COMPAT_SRC/lib/modules/$KVER" ]]; then
    echo "[rootfs] copying modules $KVER"
    cp -a "$KILROY_COMPAT_SRC/lib/modules/$KVER" "$STAGING/lib/modules/"
fi

echo "[rootfs] production tree ready ($(du -sh "$STAGING" | cut -f1))"