# 13 — Sovereign Time Sync (Terror-Threat Posture)

Assume adversaries know field literacy. Assume pool NTP, remote RTC, and silicon clocks can be **squidgied** — nudged just enough to desync logs, GPS sub-micron nodes, and thermo receipts without tripping naive alarms.

## Three clocks, three jobs

| Clock | Role | Trust |
|-------|------|-------|
| **Monotonic** (`CLOCK_MONOTONIC`) | Ordering — ticks never go backward | Host kernel |
| **Realtime** (`CLOCK_REALTIME`) | Wall labels for grep and correlation | **Your timeserver only** |
| **Sysfs freq witness** | Spiderweb Puny tier — MHz table per core | Read-only hardware |

Entropy cannot be reversed; neither can honest time. You **seal forward** and **verify at receive**.

## Engine spine (AMOURANTHRTX)

`TotalTime::seal()` in `ELLIE.hpp` locks session genesis into `FieldSocket::sealed_time`. Frame-rate jitter cannot rewrite physics time. That is **session-local** monotonic discipline.

Sovereign sync extends the same posture **across hosts**: operator-owned pulses, signed receipts, receiver double-check.

## Operator timeserver

Run your own pulse source — do not let the internet set your epoch alone.

```bash
# Operator node (LAN bind only by default)
NEXUS_SOVEREIGN_TIME_BIND=127.0.0.1 python3 sovereign-time.py serve

# Issue one signed pulse locally
python3 sovereign-time.py pulse
```

Each pulse carries: `mono_ns`, `realtime_ns`, `micron_witness` (monotonic instant hashed with sysfs `scaling_cur_freq`), HMAC signature.

Disable gradient chaos from many NTP sources (`grok_world.sh` flow 20: single source). Under terror threat: **your** source wins.

## Receiver verify — did we get squidgied?

Every receiving end pulls a pulse and checks:

1. **Signature** — HMAC from operator key in `NEXUS_STATE_DIR`
2. **Monotonic never backward** — compared to previous pulse
3. **Realtime vs monotonic skew** — within `NEXUS_TIME_MAX_SKEW_MS` (default 50 ms)
4. **Freq fingerprint jump** — `freq_sum_khz` delta without thermal story → `SQUIDGIE`
5. **Micron witness flip** — witness changes in &lt;50 ms wall window → tamper

```bash
python3 sovereign-time.py sync 127.0.0.1 9123
```

Verdict: `USER_OK` or **`SQUIDGIE`**. Grep receipts:

```bash
grep SQUIDGIE /var/lib/nexus-shield/sovereign-time-receipts.jsonl
```

## Coupling to sub-micron stack

| Layer | Time binding |
|-------|----------------|
| **Precision GPS** (`gps-precision.py`) | Sub-micron ENU nodes need stable UTC labels |
| **Spiderweb Adept** | `SimulateSubMicron` + sysfs clocks — freq witness |
| **ThermoAccountant** | `entropyThisFrame` is the receipt that time ran forward |
| **NEXUS panel** | Correlate sovereign-time status with threat spiderweb |

If GPS says nanometers but clocks disagree at receive, **trust the triple verify**, not the prettiest map dot.

## Honest rocks

| Claim | Label |
|-------|-------|
| UDP signed pulses on localhost | ✅ Implemented (`sovereign-time.py`) |
| Tamper abort like `TotalTime::verify()` abort | 🎭 Posture on NEXUS side; engine abort is C++ |
| Sub-micron SEM from clock sync | 🎭 Correlation discipline — not electron microscopy |

**Next:** [Home](Home) · [11 — Observability](11-Observability-Operator-Tools)