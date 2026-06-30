# Grok memtest entry (wish #83)

Place a Memtest86+ EFI binary here:

```
/boot/memtest/memtest86+.efi
```

Grok menu entry **Memtest (RAM check)** chainloads it when present. On the ESP after `grok-install.sh`, copy:

```bash
sudo mkdir -p /boot/efi/boot/memtest
sudo cp memtest86+.efi /boot/efi/boot/memtest/
```

Download from [memtest.org](https://www.memtest.org/) — use the EFI build for UEFI hosts.