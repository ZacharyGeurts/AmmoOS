# 02 — Fields: From Pixels to Packets

## Scalar, vector, telemetry

| Type | Example in stack |
|------|------------------|
| **Scalar field** | Thermo — one heat value per texel |
| **Vector field** | Flow `.gb` — gradient components per texel |
| **Telemetry field** | `data_bus[64]` — 64 packed words per dispatch |

## GPU fabric path

```
RayCanvas::createAnalogFieldFabric()
  → fieldPhi, fieldThermo, fieldFlow (storage images)
  → CANVAS.comp / energy.comp / x86.comp evolve each dispatch
  → Pipeline::updateHardwareFromAnalogFields() mirrors averages to hardwareFabric
```

The host **never** runs a CPU-side PDE solver on the fabric.

## Field Die path

```
FieldX86Die SSBO (binding 1)
  → 64 MiB guest linear map
  → VGA text at guest 0xB8000
  → C: mirror at 0x01000000
  → x86.comp interprets guest instructions on GPU
```

Guest RAM is where DOS lives. `data_bus` is the **dashboard** the shader reads.

## Packet field path (NEXUS)

```
ss / connection-intent / DPI sample
  → gatekeeper scoring
  → threat-panel.json publish
  → panel :9477 + field jsonl archive
```

## Integration diagram (conceptual)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Phi/Thermo │     │  Field Die   │     │ Packet field│
│  Flow GPU   │     │  guest RAM   │     │  local net  │
└──────┬──────┘     └──────┬───────┘     └──────┬──────┘
       │                   │                    │
       └─────────── data_bus[64] ───────────────┘
                         │
                    Operator panel
```

**Next:** [03 — Thermodynamics](03-Thermodynamics-In-The-Engine)