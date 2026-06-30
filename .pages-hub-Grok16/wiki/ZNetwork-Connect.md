# ZNetwork — connect everyone securely?

Doctrine: `data/grok16-znetwork-field-wire-doctrine.json`

**Short verdict:** Yes **in layers**, not as one open directory today. Security-first; wire-speed when **both ends are field computers**; identity without cellphone is **possible** with sovereign receipts + invites — not with a public name→address phone book.

## Field expansion down the wire

```
[Field computer A]  →  convert at egress  →  sealed field-io packet  →  wire  →  deconvert at ingress  →  [Field computer B]
```

- **Egress:** `field-io-packet.py` — one amplitude collapsed; only signed envelopes leave the machine. **Never ship raw field files on the wire.**
- **Transit:** HMAC-sealed `field-io-packet/v1`, 64 KB chunks; TLS 1.3 on untrusted hops.
- **Ingress:** Sovereign time + gatekeeper IFF + depth-0 join onto local **2D platform**.

When **both** peers run field computers (Grok16 prefix + ZNetwork), they talk as **belt peers** — no OS field-on-field stack. If one peer rests on an existing field, **defield first** (AmmoCode rule).

## Name + address without cellphone

What you asked for:

| Want | Approach |
|------|----------|
| Type name | **Display label only** — not root of trust |
| Type address | **Wire-point token** — opaque HMAC rotation, not plaintext street/IP in cloud |
| Auto-update | **Sovereign receipt** seals each publish; friends sync when both online |
| No phone | LAN beacon, invite URL, USB sovereign key file — **no SMS OTP root** |

What we **reject:**

- Central searchable directory (theft magnet)
- Anonymous open WAN scan
- Storing plaintext home addresses in shared JSON

AmmoCode mesh: polite LAN discovery, friend/block lists, MITM beacon pins — `ammocode-network-doctrine.json`.

## Anti-fake accounts

No username registry. Trust comes from:

- **Truth gate** — ironclad + field_sanity + g1id + voltage (all green)
- **Connection gatekeeper** — 10-axis IFF per flow
- **Threat rating** — block below 25; open network needs ≥60 or friend
- **Manual invite** or pinned LAN beacon

Sybil floods fail the gatekeeper, not a CAPTCHA.

## Anti address theft

- Friends/blocks: **local** `network-lists.json` only
- Wire-points: **opaque tokens**, not raw IPs in a public DB
- Tunnel connect: **beacon_pin** + `verify_beacon` before `tunnel_connect`
- Receipt ledger: append-only local jsonl — no PII export

## Throughput vs safety

| Path | Speed | Safety |
|------|-------|--------|
| Field-to-field (both field PCs) | Wire-limited | Depth 0 + sealed envelopes |
| WebSocket collab :9556 | Fast | Invite-only |
| HTTP tunnel fallback | ~32 KB/s class | Firewall escape; pinned beacons |
| ZNetwork ACTIVE | OS handoff | **Blocked** until human review |

Sustained wire load: use **`field_physics`**, token-bucket per peer — not `field_opt` heat debt.

## ZNetwork modes today

| Mode | Behavior |
|------|----------|
| `REVIEW_ONLY` | **Default** — plan JSON, zero mutation |
| `SHADOW` | Read-only taps + receipts |
| `ACTIVE` | Needs checklist + `ZNETWORK_REVIEW_APPROVED=1` |

AmmoCode: **attach-only** if ZNetwork already running — never double-field.

## Safety concerns (continue watching)

1. **Field files on wire** — heats both ends → envelopes only
2. **Central directory** — scrape target → no central DB
3. **Fake operators** — Sybil → truth_gate + no open WAN
4. **Thermal on max bandwidth** — sustained `field_opt` → use `field_physics`
5. **ACTIVE before review** — OS handoff risk → REVIEW_ONLY default
6. **MITM on open net** — tunnel without pin → beacon_pin required