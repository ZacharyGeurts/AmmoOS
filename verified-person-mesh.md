# Verified Person Mesh + FieldClaim System

## Overview

The sovereign identity system for AmmoOS / Field / KILROY stack replaces passwords with cryptographic, device-bound, human-verified claims.

- **Passwordless forever**: No passwords. Auth uses attested device (G1ID + KILROY-firmware + field1) bound to verified person.
- **Name + Address only**: User provides only Name and Address inside AmmoOS (via `bin/ammoos-setup-identity`) to activate the feature.
- **Everyone knows everyone (transparency)**: Every machine publishes its base identity and verified people at basest levels (G1ID, device, person, claims). Other machines discover, verify, and merge via mesh (field-dns, znetwork, direct, public-identity/ on drive).
- **Network on boot**: Auto-connect if available (MACs, IPv4, IPv6 captured). Picker for multiple (wifi/ethernet/etc) if interactive. Each machine is full server (own DNS+DHCP from storage). Network fingerprints bound to identity for Bad Actor propagation.
- **Anti-fake at enrollment**: Geo cross-check (claimed address vs current/proposed GPS/device location) + device uniqueness + botnet heuristics. Only at registration time.
- **FieldClaim format**: Portable verifiable credential for websites and peers.

Security model: **Transparency + crypto + device roots + human binding + enrollment gates + mesh propagation**. Not obscurity. Bad actors already publish lists — we do it better with verification.

## Core Components

- `lib/verified-person-tracker.py` + `.sh`: Tracker, enrollment, publication, discovery, merge, revocation.
- `lib/field-claim.py` + `.sh`: Issue/verify FieldClaims, publish machine identity.
- `scripts/ammoos-setup-identity.sh` (and bin/ symlink): Minimal UI entry (Name + Address only).
- `lib/field-coexist-network.sh`: Boot-time net connect + picker.
- Public artifacts (auto-written):
  - `~/.field-state/public-identity/verified-people-pub.json`
  - `machine-base-identity.json`
  - Mirrored to HOSTESS7_TEAM/fieldstorage for drive visibility.
- Mesh: `get_base_machine_identity()`, `publish_shared_tracker()`, `merge_peer_identity()`, `discover_peers()`.

## Enrollment (Name + Address Only)

Run inside AmmoOS (terminal, desktop launcher, Queen surface):

```bash
bin/ammoos-setup-identity
# Prompts ONLY for:
#   Your Name
#   Your Address
```

- Device auto-bound via G1ID / field-unified-device / hardware probe.
- If net: location validation runs.
- Publishes identity + claim for mesh.
- See `scripts/passwordless-enroll.sh --force` for advanced.

## FieldClaim Format (for websites & peers)

```json
{
  "schema": "field-claim/v1",
  "type": "verified-person-device",
  "person": { "id": "vp_...", "name": "...", "address_hash": "..." },
  "device": { "g1id": {...}, "machine_id": "..." },
  "enrollment": {
    "name_and_address_known": true,
    "geo_validated_at_registration": true/false,
    "bot_risk_at_registration": "low",
    "registration_flags": []
  },
  "claims": ["human_verified", "device_bound_to_person", "passwordless", "data_sovereign_only", "registration_location_checked"],
  "attestation": { "device_sig": "...", "person_binding": "...", "firmware_root": "KILROY-firmware-1.0" },
  "registry_anchor": "..."
}
```

Websites/peers call `verify_claim(claim, pub_tracker)`.

## Revocation & Bad Actors (Propagation)

Revocation is critical. Bad actors are marked and **propagated** as "Bad Actor" with threat metadata so the entire mesh and downstream systems (threat panels, kill/re-kill, attack-kit) can act.

### Marking a Bad Actor

```bash
python3 lib/verified-person-tracker.py revoke <person_id> \
  --reason "Bad Actor" \
  --threat_level 90 \
  --kill_position "rekill" \
  --source "mesh"   # or "operator", "peer", "threat-panel"
```

Or via script:

```bash
bash lib/verified-person-tracker.sh revoke <id> "Bad Actor" 90 "rekill"
```

Effects:
- Person record updated: `status: "Bad Actor"`, `threat_level`, `kill_position: "rekill" | "kill"`, `revoked_at`, `revocation_reason`.
- `verified: false`, `passwordless_ready: false`.
- Added to local revocation ledger.
- Next publish: included in `verified-people-pub.json` under `"revocations"`.

### Propagation Through Systems

- **Mesh Discovery/Merge** (`discover_peers`, `merge_peer_identity`):
  - Peers publish revocations.
  - On merge: if a peer reports higher threat or "Bad Actor", local status is updated (escalate threat_level, set kill_position).
  - Bad status spreads automatically when machines talk (field-dns, znetwork, direct fetch of public-identity/).

- **On Boot + Net Connect**:
  - `field_coexist_connect_on_boot` + startup scripts trigger `discover_peers` + revocation sync if network present.
  - Revocations from mesh are merged before full surfaces come up.

- **FieldClaim Verification**:
  - `verify_claim` returns `{"ok": false, "revoked": true, "status": "Bad Actor", "threat_level": 90, "kill_position": "rekill", ...}`
  - Websites/peers must refuse or escalate.

- **Downstream Systems** (propagation targets):
  - **threat-panel.json / threat-panel-http.py**: Bad Actor entries with threat_level are injected (see `nexus_threat_panel_publish`).
  - **kill-rekill-registry.json** (via `field-attack-kit.py`): If threat_level >= threshold or kill_position == "rekill", registered for `every_kill_rekill`, `boot_rekill`, `auto_rekill`, `rekill_target`.
  - **field-attack-kit.py**: `rekill_target(ip_or_device, "BAD_ACTOR", severity)`, `register_kill_for_rekill`.
  - **kill-detect.py / host-identity.py**: Same-host re-validation can trigger re-kill for bad bound devices.
  - **human-registry.py / existence-identity.py**: Marked with `category_primary: "Bad Actor"`, low confidence, tags.
  - **znetwork / field-dns**: Bad identities can be DNS-poisoned or connection-blocked at gatekeeper.
  - **mesh peers**: Other machines see the revocation in pub and refuse claims / isolate device.

### Threat Levels & Kill Positions

- **threat_level**: 0-100 (numeric). 
  - < 30: watch
  - 30-70: elevated
  - >70: critical (triggers re-kill paths)
- **kill_position**: "kill" (one-time interdict) or "rekill" (every re-appearance gets re-kill, per `every_kill_rekill` rule).
- **status**: "Bad Actor" (primary label for propagation).
- Source of revocation is recorded for audit (prevents spoofed revocations without high mesh consensus).

Example in pub tracker:
```json
"revocations": {
  "vp_bad123": {
    "status": "Bad Actor",
    "threat_level": 95,
    "kill_position": "rekill",
    "reason": "Coordinated sybil + hostile C2",
    "revoked_at": "2026-...",
    "sources": ["mesh", "threat-panel"]
  }
}
```

### Manual / Operator Revocation

Inside AmmoOS (after net):
```bash
python3 lib/verified-person-tracker.py revoke <id> "Bad Actor" 100 "rekill"
# Then force re-publish
bash lib/field-claim.sh publish-identity
python3 lib/verified-person-tracker.py discover-peers
```

High-threat revocations can trigger immediate `nexus_field_attack_rekill_cycle`.

## Boot & Network Flow (with MAC/IPv4/IPv6)

Networking is part of the boot process. We capture MACs, IPv4 and IPv6 because every machine is a full-fledged server (own DNS + DHCP) thanks to the storage (field1 + fieldstorage on whole drive).

- Network fingerprint (MACs, IPs) collected early via `_collect_network_fingerprint()`.
- Bound to device/person at enrollment (only Name+Address from user).
- Bad Actor revocations carry network ids → local DNS/DHCP (served from our storage) blocks bad MACs/IPs.
- Propagation: mesh peers share network info of bad actors for cross-machine blocking.

Flow (KILROY gets any device online):
1. Early net connect + MAC/IPv4/IPv6 fingerprint.
2. NEXUS C2 / znetwork.
3. KILROY-firmware + universal network drivers (any hardware).
4. **Simple Network connector UI** (after NEXUS C2 then KILROY): picker, guarantee 127.0.0.1 DNS/DHCP (fallback for old tables), share tables with peer AmmoOS via mesh.
5. User enters AmmoOS → `bin/ammoos-setup-identity` (Name + Address only).
6. Full mesh with network-bound identities + revocation propagation.

Local 127.0.0.1 DNS/DHCP always works from our storage. Stale upstream? Use local + peer-shared tables.

## Full Server per Machine (DNS/DHCP) — Hardened & Officiated

Because we have the storage:
- Each machine runs its own authoritative DNS (field-dns.py, truthful, blocks bad-actor domains/MACs/IPs).
- Each machine runs its own DHCP (field-dhcp.py, leases only to non-bad MACs, points to our DNS).
- Data lives in fieldstorage / nexus-state on the drive.
- Revocations from "everyone knows everyone" are loaded and enforced locally.
- No reliance on external DNS/DHCP.

**Harden & Officiate (no local intervention, 100% secure and up to code):**
- /etc/resolv.conf chattr +i immutable after 127.0.0.1.
- systemd-resolved masked + DNSStubListener=no.
- Official ICANN/IANA root hints (via KILROY-firmware curation).
- Strict DNSSEC validation ("strict").
- RFCs: 1035, 4033 (DNSSEC), 6761 (local), 9520, etc.
- officiate() functions called post NEXUS C2 + KILROY in network-connector-ui.sh and boot.
- 127.0.0.1 always, old tables → local fallback + mesh table share (signed by identity).
- Bad Actor MAC/IP blocks enforced in DHCP (no lease) and DNS.
- nft blocks, rate limits, immutable state files.

We are sovereign full servers — hardened, ICANN-rooted where applicable, zero local tampering.

## Website Integration

Any weebsite:

1. Receive FieldClaim (header, body, or protocol).
2. Fetch latest pub tracker from the claimed person's machine or trusted mesh anchor.
3. Call `verify_claim(claim, tracker)`.
4. If `revoked` or `status == "Bad Actor"` or low `geo_match` at enrollment → reject or flag with threat details.

Example (Python):
```python
from lib.field_claim import verify_claim
result = verify_claim(received_claim, pub_tracker)
if not result["ok"] or result.get("revoked"):
    print("Bad Actor threat:", result.get("threat_level"), result.get("kill_position"))
```

## Security Notes

- Revocation is mesh-propagated but local-first (operator can always force).
- Geo/device checks only at enrollment (runtime is pure crypto + claim).
- Transparency makes bad actors visible and costly.
- Integrates with full stack kill/re-kill/threat systems for automated response.

## Files & Commands

See:
- `bin/ammoos-setup-identity`
- `lib/verified-person-tracker.py` (revoke, publish, merge, discover)
- `lib/field-claim.py` (publish_machine_identity, verify)
- `scripts/field-qemu-visible.sh` + `launch-field-qemu.sh` (auto on visible boot)
- `public-identity/` on state + drive.

For full revocation propagation: ensure net on boot + run discover periodically (wired in startup).

This system makes fake people expensive and bad actors self-documenting + actionable across the mesh.