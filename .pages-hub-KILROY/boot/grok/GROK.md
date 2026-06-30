# Grok Bootloader

**Field-native boot for KILROY. Not GRUB.**

Intuitive menu · in-place editing · themes · mandatory security · speedup hints.
Clean and simple — [100 wishes](WISHES.md) without menu bloat.

## Controls

See [HELP.md](HELP.md): ↑↓ move · Enter boot · **E edit in place** · themes in `themes/`.

## Security (mandatory)

Major firmware requirements — fix BIOS or use explicit **Boot waived** entry:

| Major | Action |
|-------|--------|
| Secure Boot | ON (UEFI) |
| TPM 2.0 | ON |
| IOMMU / VT-d | ON |
| NX / XD | ON |
| CSM | OFF |
| Boot order | Internal disk before USB |

Full list: [security/MANIFEST](security/MANIFEST)

```bash
./scripts/grok-firmware-audit.sh   # run before install
```

Minor items warn; **strict** boot uses `grok.security=strict`. Waive only via menu entry.

## Speedups (suggested)

ReBAR, Above 4G, NVMe native, XMP — [speedups/MANIFEST](speedups/MANIFEST).

## Themes

| Theme | File |
|-------|------|
| field (default) | `themes/field/` |
| midnight | `themes/midnight/` |
| dawn | `themes/dawn/` |
| mono | `themes/mono/` |

```bash
echo midnight > boot/grok/themes/ACTIVE
./scripts/grok-compose.sh
./scripts/grok-mkimage.sh
```

## Compose (don’t hand-edit grok.conf)

```
grok.base.conf + themes/ACTIVE + grok.entries.conf → grok.conf
```

```bash
./scripts/grok-compose.sh
```

## Build & install

```bash
./scripts/build-kilroy.sh
./scripts/grok-mkimage.sh
./scripts/grok-boot-qemu.sh
sudo ./scripts/grok-install.sh /boot/efi
```

## Layout on boot media

```
/boot/grok/grok.conf       # composed menu
/boot/grok/themes/         # wallpapers + palette
/boot/grok/security/       # mandatory MANIFEST
/boot/grok/speedups/       # ReBAR etc.
/boot/kilroy/bzImage
/EFI/BOOT/BOOTX64.EFI
```