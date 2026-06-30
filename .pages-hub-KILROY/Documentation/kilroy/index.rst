KILROY Field OS
===============

This tree is the **KILROY compat substrate** (linux-7.1.1 lineage) with native
Field Die overlay. We are Field. We are Linux-compatible. We are not Linux.

**KILROY 1.0** ships the **full Linux 7.1.1 tree** plus Field overlay — see :doc:`linux-substrate`.

* :doc:`overview` — identity manifesto
* :doc:`linux-substrate` — complete Linux pin + overlay model
* :doc:`grok` — Grok bootloader (replaces GRUB)
* :doc:`fields-nocache` — CACHE + DIRECT fields (layout v9, beyond legacy caching)
* :doc:`ioctl` — ``/dev/kilroy_field`` ABI for FieldKilroy userspace
* Field telemetry: ``/proc/kilroy_field/`` (status, boot, security, cache, direct, …)
* Canonical edits: ``SG/KILROY/`` then ``kilroy-become-substrate.sh``