#!/usr/bin/env bash
# Build Grok boot media for KILROY Field OS (replaces GRUB chain).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENDOR="${GROK_LIMINE_SRC:-$ROOT/boot/grok/vendor/limine}"
BZIMAGE="${BZIMAGE:-$ROOT/build/bzImage}"
OUT="${OUT:-$ROOT/build}"
STAGING="$OUT/grok-staging"

IMG="$OUT/grok-kilroy.img"
ISO="$OUT/grok-kilroy.iso"
PART_OFFSET=1048576

limine_path() {
    local name="$1"
    if [[ -e "$VENDOR/$name" ]]; then
        echo "$VENDOR/$name"
        return
    fi
    find "$VENDOR" -maxdepth 4 -name "$name" -print -quit
}

stage_tree() {
    rm -rf "$STAGING"
    mkdir -p "$STAGING/EFI/BOOT" \
             "$STAGING/boot/grok" \
             "$STAGING/boot/kilroy" \
             "$STAGING/boot/limine"

    cp -f "$BOOTX64" "$STAGING/EFI/BOOT/BOOTX64.EFI"
    cp -f "$BIOS_SYS" "$STAGING/boot/limine-bios.sys"
    cp -f "$ROOT/boot/grok/grok.conf" "$STAGING/boot/grok/grok.conf"
    cp -f "$ROOT/boot/grok/grok.conf" "$STAGING/boot/limine.conf"
    cp -f "$ROOT/boot/grok/grok.conf" "$STAGING/limine.conf"
    cp -a "$ROOT/boot/grok/themes" "$STAGING/boot/grok/"
    cp -a "$ROOT/boot/grok/security" "$STAGING/boot/grok/"
    cp -a "$ROOT/boot/grok/speedups" "$STAGING/boot/grok/"
    cp -f "$ROOT/boot/grok/HELP.md" "$ROOT/boot/grok/WISHES.md" \
          "$ROOT/boot/grok/grok.base.conf" "$ROOT/boot/grok/grok.entries.conf" \
          "$STAGING/boot/grok/"
    cp -f "$ROOT/boot/grok/version.txt" "$STAGING/boot/grok/"
    cp -f "$BZIMAGE" "$STAGING/boot/kilroy/bzImage"
    [[ -f "$ROOT/build/initramfs.cpio.gz" ]] && \
        cp -f "$ROOT/build/initramfs.cpio.gz" "$STAGING/boot/kilroy/"
    if [[ -f "$ROOT/boot/grok/memtest/memtest86+.efi" ]]; then
        mkdir -p "$STAGING/boot/memtest"
        cp -f "$ROOT/boot/grok/memtest/memtest86+.efi" "$STAGING/boot/memtest/"
    fi
    [[ -d "$ROOT/boot/grok/docs" ]] && cp -a "$ROOT/boot/grok/docs" "$STAGING/boot/grok/"
    cp -f "$ROOT/FIELD.md" "$STAGING/boot/grok/FIELD.md"

    cat >"$STAGING/README.txt" <<'EOF'
GROK Bootloader — KILROY Field OS
=================================
Linux-compatible · Not Linux · Not GRUB
EOF
}

copy_to_fat() {
    local target="$1"
    mcopy -i "$target" -s "$STAGING/EFI" ::/EFI
    mcopy -i "$target" -s "$STAGING/boot" ::/boot
    mcopy -i "$target" "$STAGING/limine.conf" ::/limine.conf
    mcopy -i "$target" "$STAGING/README.txt" ::/README.txt
}

mkimage_disk() {
    echo "[grok-mkimage] building Grok disk image (BIOS+UEFI FAT)"
    rm -f "$IMG"
    dd if=/dev/zero of="$IMG" bs=1M count=512 status=none
    parted -s "$IMG" mklabel msdos mkpart primary fat32 2048s 100%
    parted -s "$IMG" set 1 boot on
    mformat -i "${IMG}@@${PART_OFFSET}" -F -v KILROY ::
    copy_to_fat "${IMG}@@${PART_OFFSET}"
    "$LIMINE" bios-install "$IMG"
    echo "[grok-mkimage] Grok disk image -> $IMG"
    ls -lh "$IMG"
}

mkimage_iso() {
    command -v xorriso >/dev/null 2>&1 || return 1
    echo "[grok-mkimage] building Grok hybrid ISO"
    cp -f "$BIOS_CD" "$STAGING/boot/limine-bios-cd.bin"
    cp -f "$UEFI_CD" "$STAGING/boot/limine-uefi-cd.bin"
    rm -f "$ISO"
    xorriso -as mkisofs -R -r -J \
        -b boot/limine-bios-cd.bin \
        -no-emul-boot -boot-load-size 4 -boot-info-table \
        -hfsplus -apm-block-size 2048 \
        --efi-boot boot/limine-uefi-cd.bin \
        -efi-boot-part --efi-boot-image --protective-msdos-label \
        "$STAGING" -o "$ISO"
    "$LIMINE" bios-install "$ISO"
    echo "[grok-mkimage] Grok ISO -> $ISO"
    ls -lh "$ISO"
}

echo "=== Grok mkimage (KILROY Field OS) ==="

[[ -f "$BZIMAGE" ]] || {
    echo "[grok-mkimage] missing $BZIMAGE — run ./scripts/build-kilroy.sh"
    exit 1
}

for tool in pythong mcopy mformat parted dd; do
    command -v "$tool" >/dev/null 2>&1 || {
        echo "[grok-mkimage] missing: $tool"
        exit 1
    }
done

[[ -x "$ROOT/scripts/grok-fetch.sh" ]] && "$ROOT/scripts/grok-fetch.sh"

LIMINE="$(limine_path limine)"
BIOS_SYS="$(limine_path limine-bios.sys)"
BIOS_CD="$(limine_path limine-bios-cd.bin)"
UEFI_CD="$(limine_path limine-uefi-cd.bin)"
BOOTX64="$(limine_path BOOTX64.EFI)"

for f in "$LIMINE" "$BIOS_SYS" "$BOOTX64"; do
    [[ -n "$f" && -f "$f" ]] || {
        echo "[grok-mkimage] compat file missing — run grok-fetch.sh"
        exit 1
    }
done

"$ROOT/scripts/grok-compose.sh"
if [[ -x "$ROOT/rootfs/build-initramfs.sh" ]]; then
    "$ROOT/rootfs/build-initramfs.sh" || echo "[grok-mkimage] initramfs skipped (need gcc)"
fi
stage_tree
mkimage_disk
mkimage_iso || echo "[grok-mkimage] ISO skipped (install xorriso for hybrid ISO)"