# Windows + KILROY coexistence (Grok wish #89)

KILROY Field OS and Windows can share a GPT disk when Grok owns the EFI System Partition.

## Recommended layout

| Partition | Type | Contents |
|-----------|------|----------|
| ESP | FAT32 | Grok + `boot/kilroy/bzImage` + optional Windows bootloader |
| Microsoft reserved | MSR | Windows installer |
| KILROY_FIELD | ext4 | KILROY production root (`LABEL=KILROY_FIELD`) |
| Windows | NTFS | Windows C: |

## Boot flow

1. Firmware boots Grok (default entry **KILROY Field**).
2. To add Windows: copy `bootmgfw.efi` chain or use Limine `chainload` entry pointing at `\EFI\Microsoft\Boot\bootmgfw.efi`.
3. Keep **Grok security** entry strict on KILROY; Windows entry may use separate cmdline.

## Grok entry template (manual)

```
/Windows (chainload)
comment: Coexist — boot Windows Boot Manager from ESP
protocol: chainload
path: boot():/EFI/Microsoft/Boot/bootmgfw.efi
```

## Notes

- Disable Fast Boot in firmware for reliable menu.
- ReBAR/Above 4G affect GPU in both OSes — see `speedups/MANIFEST`.
- KILROY rootfs stays on ext4; Windows cannot read it without optional driver.