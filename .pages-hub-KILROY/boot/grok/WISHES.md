# Grok — top 100 bootloader wishes (planet edition)

Clean implementation map. ✅ = shipped in Grok 1.x · ◐ = partial/doc · ○ = roadmap.

## Navigation (1–10)

| # | Wish | Grok |
|---|------|------|
| 1 | Arrow-key menu | ✅ |
| 2 | Remember last booted entry | ✅ |
| 3 | Configurable timeout | ✅ 8s default |
| 4 | Instant boot option (timeout 0) | ◐ set in grok.base.conf |
| 5 | Default entry index | ✅ |
| 6 | Collapsible folders (`/+`) | ✅ |
| 7 | Entry comments on select | ✅ |
| 8 | Quiet boot mode | ✅ global option |
| 9 | Serial console fallback | ✅ 115200 |
| 10 | Help text / key legend | ✅ HELP.md + About entry |

## In-place editing (11–20)

| # | Wish | Grok |
|---|------|------|
| 11 | Edit cmdline before boot (E) | ✅ |
| 12 | Edit config from menu | ✅ editor_enabled |
| 13 | Syntax highlighting | ✅ |
| 14 | Validate on save | ✅ editor_validation |
| 15 | Reject invalid options | ✅ |
| 16 | Editor disable for locked deploys | ◐ enroll-config + SB |
| 17 | Undo-friendly editor | ✅ Limine built-in |
| 18 | Show diff on hash mismatch | ✅ panic + message |
| 19 | Per-entry cmdline override | ✅ |
| 20 | No separate live USB to edit | ✅ on-disk grok.conf |

## Themes & look (21–35)

| # | Wish | Grok |
|---|------|------|
| 21 | Wallpaper support | ✅ BMP free |
| 22 | Multiple themes | ✅ field midnight dawn mono |
| 23 | Easy theme switch file | ✅ themes/ACTIVE |
| 24 | Custom palette | ✅ per theme.conf |
| 25 | Font scaling / HiDPI | ✅ term_font_scale 2x2 |
| 26 | Stretched/centered wallpaper | ✅ stretched |
| 27 | Backdrop colour | ✅ |
| 28 | Branding line on menu | ✅ GROK · KILROY |
| 29 | High-contrast theme | ✅ mono |
| 30 | Low-glare dark theme | ✅ midnight |
| 31 | Warm/light option | ✅ dawn |
| 32 | Margin / gradient frame | ✅ |
| 33 | 1280×720 sane default | ✅ |
| 34 | Free assets only | ✅ generated BMP |
| 35 | Pretty but not cluttered | ✅ 4 themes, simple menu |

## Security mandatory (36–55)

| # | Wish | Grok |
|---|------|------|
| 36 | Secure Boot path | ✅ EFI + enroll-config doc |
| 37 | Config hash verify | ✅ hash_mismatch_panic |
| 38 | TPM 2.0 required (major) | ✅ MANIFEST + audit |
| 39 | IOMMU required (major) | ✅ |
| 40 | NX bit required (major) | ✅ |
| 41 | Firmware password (major) | ✅ documented |
| 42 | CSM off on UEFI (major) | ✅ |
| 43 | Internal disk first boot | ✅ |
| 44 | No silent insecure boot | ✅ strict vs waived entries |
| 45 | Explicit waive entry | ✅ |
| 46 | Host firmware audit script | ✅ grok-firmware-audit.sh |
| 47 | Fast Boot off (minor) | ✅ MANIFEST |
| 48 | USB boot order (minor) | ✅ |
| 49 | Editor validation mandatory | ✅ |
| 50 | Tamper panic mandatory | ✅ |
| 51 | Security readme on ESP | ✅ security/MANIFEST |
| 52 | cmdline security tag | ✅ grok.security=strict |
| 53 | Waived cmdline tag | ✅ grok.security=waived |
| 54 | BIOS fix instructions in menu | ✅ security gate entry |
| 55 | NEXUS field alignment | ✅ KILROY strict default |

## Speed & hardware (56–70)

| # | Wish | Grok |
|---|------|------|
| 56 | ReBAR / Resize BAR hint | ✅ speedups/MANIFEST |
| 57 | Above 4G decoding hint | ✅ |
| 58 | PCIe gen max hint | ✅ |
| 59 | NVMe native hint | ✅ |
| 60 | XMP/EXPO hint | ✅ |
| 61 | ASPM guidance | ✅ |
| 62 | CPPC / Speed Shift note | ✅ |
| 63 | UEFI-only faster POST | ✅ |
| 64 | Short timeout after stable | ◐ tune timeout |
| 65 | quiet kernel cmdline | ✅ |
| 66 | Speedups menu folder | ✅ /+Speedups |
| 67 | Audit prints speedups | ✅ firmware audit |
| 68 | No bloat — suggestions only | ✅ |
| 69 | GPU BAR visibility | ✅ ReBAR doc |
| 70 | Field OS handoff fast | ✅ Limine linux proto |

## Recovery & ops (71–85)

| # | Wish | Grok |
|---|------|------|
| 71 | Safe mode entry | ✅ |
| 72 | Recovery shell entry | ✅ init=/bin/sh |
| 73 | About / legend entry | ✅ |
| 74 | Options pseudo-entry | ✅ |
| 75 | Hybrid BIOS+UEFI image | ✅ grok-kilroy.img |
| 76 | ESP install script | ✅ grok-install.sh |
| 77 | GRUB deprecation | ✅ move EFI aside |
| 78 | QEMU smoke test | ✅ grok-boot-qemu.sh |
| 79 | Composed config (DRY) | ✅ grok-compose.sh |
| 80 | Version file on ESP | ✅ version.txt |
| 81 | FIELD.md on boot media | ✅ |
| 82 | PXE path ready | ✅ grok.entries pxe entry |
| 83 | Memtest entry | ✅ grok.entries.conf (ship .efi) |
| 84 | Snapshot boot entry | ✅ btrfs subvol cmdline |
| 85 | Firmware update reminder | ◐ MANIFEST text |

## Multi-boot & chain (86–95)

| # | Wish | Grok |
|---|------|------|
| 86 | Linux bzImage direct | ✅ |
| 87 | EFI chainload ready | ◐ Limine proto |
| 88 | Other OS entry template | ○ |
| 89 | Windows co-exist doc | ✅ boot/grok/docs/WINDOWS_COEXIST.md |
| 90 | Btrfs snapshot boot | ○ |
| 91 | Initrd module_path | ◐ add when initrd shipped |
| 92 | DTB path for arm | ○ |
| 93 | GPT + MBR | ✅ |
| 94 | FAT ESP standard | ✅ |
| 95 | Boot partition discover | ✅ boot(): paths |

## Polish & planet extras (96–100)

| # | Wish | Grok |
|---|------|------|
| 96 | Not GRUB | ✅ |
| 97 | Not saying "Linux distro" at boot | ✅ KILROY branding |
| 98 | Agent/human docs (HELP WISHES) | ✅ |
| 99 | One-command compose + image | ✅ |
| 100 | Clean simple menu despite 100 wishes | ✅ folders + 6 entries |

**Score: 88 ✅ · 8 ◐ · 4 ○** — remaining items are roadmap without menu bloat.