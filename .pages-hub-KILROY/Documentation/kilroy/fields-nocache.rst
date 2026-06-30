CACHE and DIRECT fields (layout v9)
====================================

KILROY Field OS layout **v9** adds two slots beyond TIME/RAM/THERMO/CONTEXT/CPU/FLOW:

* **Slot 6 — CACHE** — shed legacy Linux cache retention under RAM pressure
* **Slot 7 — DIRECT** — track field-direct vs cache-coupled memory maps

Philosophy
----------

We are **beyond caching** for Field hot paths. The Linux page cache remains for
ABI compatibility (POSIX read/write/mmap on files), but the Field Die:

1. **Sheds retention** — amortized ``lru_add_drain()`` + ``drop_slab()`` when RAM
   field pressure crosses 650000 micro (65% of unity scale).
2. **Prefers direct coherence** — anonymous ``mmap`` paths are counted as
   field-direct; file-backed maps remain cache-coupled for Linux compat.

Build
-----

Enable in ``arch/x86/configs/kilroy_field_defconfig`` or identity fragment::

  CONFIG_RTX_FIELD_CACHE_SLOT=y
  CONFIG_RTX_FIELD_DIRECT_SLOT=y

Optional nocache substrate tuning (``config/kilroy-nocache.config``)::

  CONFIG_TRANSPARENT_HUGEPAGE=n
  CONFIG_NUMA_BALANCING=n
  CONFIG_SLUB_TINY=y

Telemetry
---------

``/proc/kilroy_field/cache``::

  shed_count, bypass_ops, slab_drops, lru_drains
  retention_micro, pressure_micro

``/proc/kilroy_field/direct``::

  direct_maps, direct_bytes, cached_maps
  coherence_ops, direct_ratio_micro

``/proc/kilroy_field/status`` includes ``slot6_cache`` and ``slot7_direct`` summaries.

Userspace::

  kilroy-status cache
  kilroy-status direct

Shed policy
-----------

CACHE field ticks on memory syscalls (read/write/mmap/munmap/brk/mprotect).
When syscall generation hits the shed mask **and** pressure ≥ threshold **and**
at least 5 seconds since last shed, the Field Die drains LRU and drops slabs.

This yields measurable gains on RAM-heavy workloads without breaking Linux file I/O.