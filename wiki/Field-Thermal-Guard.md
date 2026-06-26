# Field Thermal Guard

**v10.4.3** — Landauer-aware work budgeting before any global redata. Quality job 1: bounded, observable, back-off capable.

---

## Why

Field layers that perform entropy management, peak folding, or phase decoupling do irreversible information processing. By Landauer's limit that produces heat (~kT ln 2 per bit erased). On real silicon this appears as elevated TDP and thermal throttling.

A naïve monolithic global redata (full canvas refresh in one blast) concentrates that work. **Incremental, budget-capped redata is required before hard-drive global refresh.**

---

## Diagram

![Field thermal guard](https://raw.githubusercontent.com/ZacharyGeurts/NEXUS-Shield/main/docs/images/field-thermal-guard.svg)

---

## Policy

| Guarantee | Detail |
|-----------|--------|
| Incremental only | Chunked region passes — never monolithic blast |
| Work budget | Rolling 1s window vs `NEXUS_FIELD_MAX_JOULES_PER_SEC` |
| Back-off | 5 ms yield when projected power exceeds budget |
| Observable | One-line log: `field thermal headroom X%` |
| Gatekeeper tie-in | Anomaly → stealth rate limit + budget tighten (0.75×) |
| Cold path | One atomic + timestamp check when idle |

---

## Modules

| Path | Role |
|------|------|
| `lib/field-thermal-guard.py` | Work estimator, headroom, anomaly, gatekeeper tighten |
| `lib/field-global-redata.py` | Chunked incremental redata (`boot-test`, `incremental`) |
| `data/field-thermal-guard-doctrine.json` | Landauer defaults + policy |
| `AMOURANTHRTX/.../FieldThermalGuard.hpp` | Engine-side mirror (Pipeline dispatch guard) |

---

## Config (`config/nexus.conf`)

```bash
NEXUS_FIELD_THERMAL_GUARD=1
NEXUS_FIELD_MAX_JOULES_PER_SEC=45
NEXUS_FIELD_JOULES_PER_OP=1.2e-9
NEXUS_FIELD_REDATA_CHUNK=8192
NEXUS_FIELD_GLOBAL_REDATA_INCREMENTAL=1
```

Policy file written at runtime: `field-thermal-guard-policy.env` (NEXUS-Shield underlay can tighten on anomaly).

---

## Boot path

On **first install** and **every refresh**, `nexus-boot-impl.sh` runs:

1. `field-thermal-guard.py evaluate` — init headroom + policy
2. `field-global-redata.py boot-test` — bounded 3-region incremental pass

Daemon vigil cycle calls `field-thermal-guard.py cycle` each tick.

---

## State files

| File | Role |
|------|------|
| `field-thermal-guard.json` | Panel publish — headroom, budget, anomaly |
| `field-thermal-guard-policy.env` | Tunables for AMOURANTHRTX / underlay |
| `field-thermal-anomaly.json` | hwmon + RAPL anomaly receipt |
| `field-thermal-rate-limit.json` | Gatekeeper stealth rate limit when active |
| `field-global-redata.json` | Last incremental redata receipt |

---

## Verify

```bash
NEXUS_INSTALL_ROOT=/path/to/tree NEXUS_STATE_DIR=/tmp/nexus-test \
  pythong lib/field-thermal-guard.py cycle

NEXUS_INSTALL_ROOT=/path/to/tree NEXUS_STATE_DIR=/tmp/nexus-test \
  pythong lib/field-global-redata.py boot-test
```

Expect `headroom_pct` in JSON and `field thermal headroom` in alerts log.

→ **[Boot Implementation](Boot-Implementation)** · **[Field I/O](Field-IO)** · **[SECURITY.md](https://github.com/ZacharyGeurts/NEXUS-Shield/blob/main/SECURITY.md)**