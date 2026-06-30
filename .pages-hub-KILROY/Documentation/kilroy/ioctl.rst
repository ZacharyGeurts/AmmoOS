/dev/kilroy_field ioctl ABI
============================

Device node: ``/dev/kilroy_field`` (misc char, ``CONFIG_RTX_FIELD_CHARDEV``).

Magic: ``'K'`` · ABI string: ``kilroy-field-1.0`` · Layout: **v9**

Core ioctls
-----------

- ``KILROY_IOC_ACTIVATE`` / ``DEACTIVATE``
- ``KILROY_IOC_GET_ABI`` — 32-byte ABI string
- ``KILROY_IOC_GET_STATE`` — full ``struct kilroy_field_state``
- ``KILROY_IOC_SET_THERMO`` / ``SET_FCC`` — push physics (micro/submicro)
- ``KILROY_IOC_GET_SLOTS`` / ``GET_POWER`` / ``GET_CPU`` / ``GET_RAM``

Layout v9 extensions
--------------------

- ``KILROY_IOC_GET_CACHE`` — ``struct kilroy_field_cache``
- ``KILROY_IOC_GET_DIRECT`` — ``struct kilroy_field_direct``
- ``KILROY_IOC_GET_FLOW`` — ``struct kilroy_field_flow``

UAPI header: ``include/uapi/kilroy/rtx_field.h``

Userspace bridge: ``userspace/field-kilroy/`` (FieldKilroy canonical copy).

Proc remains the portable fallback: ``/proc/kilroy_field/{thermo,fcc,...}``