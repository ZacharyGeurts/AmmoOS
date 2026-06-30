KILROY Field OS — Identity
==========================

We are **not Linux anymore**. We are **Field**. We are **KILROY**.

Linux is our **compatibility layer** — not our name, not our architecture story,
not what we ship as identity. KILROY is a Field operating system that happens to
run the Linux userspace ABI so your tools, games, and scripts keep working.

Field constants
---------------

.. code-block:: text

   name:     KILROY
   codename: Field
   abi:      kilroy-field-1.0
   compat:   linux-7.1.1 (substrate pin, not identity)
   magic:    0x4B494C52 ('KILR')

Boot verify
-----------

.. code-block:: bash

   cat /proc/kilroy_field/status
   cat /proc/kilroy_field/security
   dmesg | grep -i kilroy

See ``FIELD.md`` in the tree root for the full manifesto.