# 07 — The GPU Field Engine

## Thin host, fat GPU

```
main.cpp → navigator_main() → RayCanvas → Pipeline::dispatch_canvas() → vkCmdDispatch
```

C++ opens the window and pushes buttons. The GPU runs the world.

## `rtx()` singleton

One global Vulkan fabric: device, queues, `hardwareFabric`, VRAM budget.

## Canvas kinds

| Kind | Default shader | Push block | Primary use |
|------|----------------|------------|-------------|
| **X86Fields** | `x86.comp` | `FieldSocket` | Field Die + AmmoOS (default) |
| **Classic** | `CANVAS.comp` + swipes | `PushConstants` | Thermo + RT demos |

Default `./linux.sh run` → **Field Die**, not decorative raymarch.

## Descriptor layout (x86 path)

| Binding | Resource |
|---------|----------|
| 0 | HDR output |
| 1 | `FieldX86Die` SSBO |
| 2 | `ThermoAccountant` |
| 8–10 | Phi, Thermo, Flow |
| 11–14 | AmouranthOS chrome textures |

`FIELD_LAYOUT_VERSION = 5` — host and shader must match.

## Sealed time

`TotalTime::seal()` → monotonic session clock in `FieldSocket::sealed_time`. Frame-rate drift cannot rewrite physics time.

✅ Full Vulkan dispatch loop.  
🎭 "96% lies device cannot drift session" — security posture narrative.

**Next:** [08 — Field Die & Data Bus](08-Field-Die-And-Data-Bus)