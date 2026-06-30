KILROY 1.0 and the full Linux tree
===================================

KILROY Field OS **1.0** includes **all of Linux 7.1.1** as the compat substrate.
We do not maintain a partial kernel — we maintain a **complete** Linux tree plus a
Field-native overlay.

What you get
------------

* **100% Linux drivers and subsystems** — block, net, mm, fs, DRM, NVMe, …
* **Field Die** at the syscall boundary — ``kernel/rtx/``
* **KILROY identity** — banners, ``uname``, ``NAME = Field``, Grok boot
* **Linux-compatible ABI** — unmodified POSIX/glibc binary passthrough

Canonical vs substrate
----------------------

* Edit Field code in ``SG/KILROY/`` only.
* ``compat/linux-7.1.1`` is the pinned Linux tree + synced overlay.
* See ``LINUX_MANIFEST.md`` and ``PORT_MAP.md`` for the full map.

Build
-----

::

  ./scripts/kilroy-become-substrate.sh
  ./scripts/kilroy-port-complete.sh
  ./scripts/build-kilroy.sh

Output: ``build/bzImage`` with ``LOCALVERSION=-kilroy`` — **KILROY 1.0**, not "Linux".