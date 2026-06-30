# 14 — Public DNS, DHCP & Time (2026 Grok Rewrite)

Assume terror-threat knowledge everywhere. Public infrastructure must ship **without old vulnerabilities** — loopback-first, operator-owned, verify at receive.

## Three services, one posture

| Service | Port | 2026 default | Retired vulns |
|---------|------|--------------|---------------|
| **Truth DNS** | 53 UDP/TCP | `127.0.0.1` / `::1` only | Foreign resolver shortcut, ANY flood, dig fork bomb (rate-limited) |
| **Field DHCP** | 67 UDP | LAN IP bind, takeover `primary` only | `0.0.0.0` rogue DHCP, option-50 mismatch, no conflict detect |
| **Sovereign NTP** | 123 UDP | Operator stratum-2 from signed pulses | Pool NTP as sole authority |

Opt-in WAN exposure: `NEXUS_FIELD_SERVICES_PUBLIC=1` (explicit — never default).

## DNS — Truth Resolver

- RFC 1034 `dig +trace` from root — no Google/Cloudflare shortcut
- `dns-threat-guard` rate limits + permanent blocks
- `dns-egress-integrity` hashes answers
- `dns-service-takeover` waits for healthy loopback DNS before `resolv.conf` steer
- nft blocks foreign resolver egress when phase = `primary`

**Phase 2:** native resolver (hickory/unbound), DNSSEC validate, TCP + EDNS.

## DHCP — issue only, verify always

`field-dhcp/v3` security:

- Binds **LAN IP** not `0.0.0.0` unless public mode
- **Option 50** requested IP must match lease for MAC
- **Ping conflict** check before OFFER
- **MAC allowlist** optional from `field-services-2026-seed.json`
- DNS option 6 → `127.0.0.1` Truth Resolver

## Time — sovereign first

Two layers:

1. **`sovereign-time.py`** — UDP 9123 signed pulses, micron witness, `SQUIDGIE` verdict
2. **`field-ntp-2026.py`** — UDP 123 NTP mode-4 replies gated on sovereign pulse

```bash
# Daemon starts both when NEXUS_SOVEREIGN_TIME=1 and NEXUS_FIELD_NTP=1
python3 field-services-2026.py json   # unified panel slice
python3 sovereign-time.py sync
```

`grok_world.sh` flow 20: **sovereign-first** — disables pool NTP when `NEXUS_SOVEREIGN_TIME_FIRST=1`.

## Admin portal — no hardcoded production keys

Set `NEXUS_DNS_ADMIN_PASSKEY` in production. Use `NEXUS_DNS_ADMIN_REQUIRE_ENV=1` to refuse seed passkeys entirely.

Ports 7 / 77 / 777 remain **read-only** — information only, no remote controls.

## Panel

Threat panel DNS tab merges `field-dns/v3` with `services_2026` slice:

- `vulnerabilities_retired` list
- DNS + DHCP + NTP + sovereign status
- Posture flags: loopback DNS, LAN-only DHCP, sovereign-first time

## ELLIE Last Host — only computer left

From `ELLIE.hpp` (Captain Ellie / TotalTime v∞):

| ELLIE concept | NEXUS service binding |
|---------------|----------------------|
| `TotalTime::seal()` genesis | `ellie-last-host.py seal` at daemon boot |
| Session entropy + `verify()` | Covenant file + `SQUIDGIE` / apocalypse marker |
| Apocalypse handler | Fail-closed on entropy corruption |
| `LOG_*_CAT` + THERMO | `ellie-last-host-thermo.jsonl` + grep engine log |
| `FieldSocket::sealed_time` | Sovereign pulse → NTP stratum 1 |

```bash
# Sole survivor mode — global DNS, DHCP, TIME on all interfaces
NEXUS_LAST_HOST=1 ./nexus.sh restart

python3 ellie-last-host.py posture   # binds, pool, gateway
python3 ellie-last-host.py verify    # entropy check
```

**Service registry** when last host: DNS :53 · DHCP :67 · NTP :123 · Sovereign :9123 · Panel :9477 · Gateway (DHCP opt 3) · Grep discipline.

Takeover jumps straight to **`primary`** — no waiting while the world is gone.

## Honest rocks

| Claim | Label |
|-------|-------|
| Loopback DNS + takeover | ✅ Implemented |
| DHCP v3 security checks | ✅ Implemented |
| Sovereign NTP on 123 | ✅ Implemented |
| DNSSEC wire validation | 📋 Phase 2 — stub counters today |
| DHCPv6 | 📋 Schema reserved |

**Next:** [13 — Sovereign Time Sync](13-Sovereign-Time-Sync) · [05 — Packet Field](05-Packet-Field)