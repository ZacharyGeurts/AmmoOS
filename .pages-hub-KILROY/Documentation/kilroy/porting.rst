Linux → KILROY porting
======================

All Field-native development happens in ``SG/KILROY/``. The compat substrate
(``compat/linux-7.1.1``) is the **full Linux 7.1.1 tree** — overlay target, not canonical.

KILROY 1.0 complete port
------------------------

See ``compat/LINUX_MANIFEST.md`` — all Linux subsystems stay; Field + identity overlay.

Port map
--------

See ``compat/PORT_MAP.md`` in the canonical repo for the full file mapping.

Pipeline
--------

1. ``kilroy-stage-compat.sh`` — pin complete linux-7.1.1 substrate
2. ``kilroy-sync-compat.sh`` — copy Field sources + apply identity
3. ``kilroy-apply-identity.sh`` — banners, UTS, Makefile, main.c, uts.h
4. ``kilroy-become-substrate.sh`` — full transform + verify
5. ``kilroy-port-complete.sh`` — audit full Linux + overlay

Config layers
-------------

* ``config/kilroy-identity.config`` — Field Die + LOCALVERSION
* ``config/kilroy-production.config`` — NVMe ext4 root (TEAM drive)
* ``arch/x86/configs/kilroy_field_defconfig`` — merged overlay fragment

Userspace
---------

* ``userspace/kilroy-status`` — ``/proc/kilroy_field`` CLI
* ``userspace/field-init`` — ramdisk PID1 stub
* ``rootfs/`` — production busybox root