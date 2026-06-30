# Grok compat engine

Grok ships a pinned **Limine 9.x-binary** tree under `boot/grok/vendor/limine/`.
Limine is free software used only as a boot substrate — same role as linux-7.1.1
for the kernel.

At image build time, Grok copies:

- `BOOTX64.EFI` → UEFI loader
- `limine-bios.sys` + CD stubs → BIOS path
- `grok.conf` → `limine.conf` (Limine config format)

The menu shows **Grok** branding via `interface_branding` and the Field theme.
End users do not need to know Limine unless hacking the compat layer.