# Architecture

NEXUS-Shield v2.0.2 — genius-only, connection gatekeeper, ultra-stealth.

---

## How you interact with it

```
You → ./nexus.sh or desktop icon
         ↓
    Browser panel (HTTPS localhost :9477)
         ↓
    Monitor / Settings / Logs
         ↓
    API → nft firewall, settings.override, Hostess7 trust memory
```

The daemon runs whether or not the panel is open. The panel is the control surface.

---

## Daemon stack

```
nexus-genius.service (CPUQuota=5%, Nice=19, MemoryMax=256M)
  └── nexus-daemon.sh
        ├── verify MANIFEST.sha256 (self-defense)
        ├── Connection Gatekeeper (10-axis intent, JSON state)
        ├── Packet Oracle (ss snapshots)
        ├── Threat Panel HTTP (local TLS)
        ├── Firewall Sentinel + Trust (nft + Hostess7 JSONL)
        ├── Shadow Reality (inotify) — event-driven
        ├── Entropy Oracle (inotify) — event-driven
        ├── Behavior Symphony (adaptive procfs)
        ├── Privacy Guard (adaptive fd scan)
        ├── Predictive Guard (alert correlation)
        ├── Paranoia + Shutdown Guard
        ├── Adblock Loader (filter lists → nft block_out)
        └── Eternal Vigil (calm / alert / storm)
```

---

## Data flow

```
  live TCP flows ──► Connection Gatekeeper ──► panel Monitor tab
  inotify events ──► Shadow / Entropy ──► threat vectors
  procfs snapshot  ──► Behavior Symphony (whitelisted comms skipped)
  /proc/fd scan    ──► Privacy Guard
  alert correlation──► Predictive Guard ──► Eternal Vigil tighten
                              │
                              ▼
                   /var/log/nexus-alerts.log
```

---

## Key paths

| Path | Purpose |
|------|---------|
| `/var/log/nexus-alerts.log` | Unified alerts |
| `/var/lib/nexus-shield/` | State, TLS, settings.override |
| `/var/lib/nexus-shield/connection-intent.json` | Gatekeeper scores |
| `/var/lib/nexus-shield/settings.override` | Panel toggles |
| `/usr/local/lib/nexus-shield/MANIFEST.sha256` | Self-defense signatures |
| `/usr/local/bin/nexus.sh` | User launcher |

---

## Consumer guarantee

- No desktop notifications (except shutdown modal in panel)
- Whitelisted consumer apps and USB/audio/display devices
- `<5%` CPU cgroup cap
- Event-driven file integrity — no hourly full-home scans
- Gatekeeper does **not** auto-block browser/CDN traffic

---

## Predictive Guard

Correlates recent module alerts. Score ≥ 6 pre-triggers Eternal Vigil **alert** mode before a full storm — tightening without visible UX changes.