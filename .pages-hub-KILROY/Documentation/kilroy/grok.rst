Grok Bootloader
===============

KILROY ships **Grok** as the field-native boot manager. GRUB is deprecated.

Features
--------

- Intuitive menu (↑↓ Enter · **E** edit in place)
- Four themes: field, midnight, dawn, mono
- Mandatory BIOS security manifest + ``grok-firmware-audit.sh``
- Speedup hints (ReBAR, Above 4G, NVMe)
- 100 documented wishes — clean menu

Kernel handoff
--------------

Grok passes kernel cmdline tags consumed by the Field Die:

- ``grok.security=strict`` — default production path
- ``grok.security=waived`` — explicit insecure opt-in (logs alert)
- ``kilroy.field=1`` — Grok chain marker

Telemetry: ``/proc/kilroy_field/boot`` and ``/proc/kilroy_field/security``

Build
-----

.. code-block:: bash

   ./scripts/grok-compose.sh
   ./scripts/grok-mkimage.sh

Canonical source: ``SG/KILROY/boot/grok/`` — see ``GROK.md`` and ``WISHES.md``.