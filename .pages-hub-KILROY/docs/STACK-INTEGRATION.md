# KILROY stack integration (v2 — 2026-06-30)

KILROY is the **PC core** — syscall truth, network lane (ZNetwork absorbed), loopback authority.

## Stack layers (rewritten)

| Order | Layer | Role |
|-------|-------|------|
| 0 | Hardware | Witness — no breaks |
| 1 | NEXUS C2 | Command panel — absorbed into KILROY at runtime |
| 2 | **KILROY** | PC core — ZNetwork absorbed, defense, loopback `127.0.0.1` |
| 3 | **AmmoOS** | Field OS desktop — **AMOURANTHRTX** display backend |
| 4 | **Queen** | Standalone secured browser — `:9481`, not an AmmoOS container |

Doctrine: `AmmoOS/data/field-stack-layer-doctrine.json` (v2)

## Load OS

```bash
cd SG/NewLatest
./scripts/kilroy-load-os.sh
```

Boot order: KILROY core → field stack → AmmoOS desktop (`/field`) → Queen on demand.

## Surfaces

| Surface | URL |
|---------|-----|
| AmmoOS desktop | `http://127.0.0.1:9477/field` |
| Queen Browser | `http://127.0.0.1:9481/world/browser.html` |
| KILROY API | `http://127.0.0.1:9481/api/kilroy` |
| Load OS action | `POST /api/kilroy` `{"action":"load_os"}` |
| Field proc | `/proc/kilroy_field/*` |

## Pairing

- **Grok16 5.2.0**
- **AmmoOS 2.0.0-beta3.1**
- **KILROY 1.1.0 Sanctuary**