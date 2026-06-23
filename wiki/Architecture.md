# Architecture

NEXUS-Shield v1.1 — **genius-only default**, ultra-stealth, self-defended.

## Tiers

### Default — Genius layer (`stealth_install.sh`) ✅

Pure NEXUS heuristics. Dependency: `inotify-tools` only.

```
nexus-genius.service (CPUQuota=5%, Nice=19, MemoryMax=128M)
  └── nexus-daemon.sh
        ├── verify MANIFEST.sha256 (self-defense)
        ├── Shadow Reality (inotify) — event-driven
        ├── Entropy Oracle (inotify) — event-driven
        ├── Behavior Symphony (adaptive procfs)
        ├── Privacy Guard (adaptive fd scan)
        ├── Predictive Guard (alert correlation)
        └── Eternal Vigil (calm/alert/storm)
```

### Deprecated — Legacy AV (`NEXUS_LEGACY_AV=1`) ⚠️

ClamAV + rkhunter + AIDE. Opt-in only. Genius layer still runs as primary.

---

## Module map

```
  inotify file event ──► Shadow Reality / Entropy Oracle
  procfs snapshot    ──► Behavior Symphony (whitelisted comms skipped)
  /proc/fd scan      ──► Privacy Guard (device paths skipped)
  alert correlation  ──► Predictive Guard ──► Eternal Vigil tighten
                              │
                              ▼
                   /var/log/nexus-alerts.log
```

## Predictive Guard

Correlates recent module alerts. Score ≥ 6 pre-triggers Eternal Vigil **alert** mode before a full storm — predictive tightening without consumer-visible changes.

## Data paths

| Path | Purpose |
|------|---------|
| `/var/log/nexus-alerts.log` | Unified alerts (600) |
| `/var/lib/nexus-shield/` | State, shadow hashes (700) |
| `/usr/local/lib/nexus-shield/MANIFEST.sha256` | Self-defense signatures |
| `/usr/local/lib/nexus-shield/config/` | Runtime toggles |

## Consumer guarantee

- No desktop notifications
- Whitelisted consumer apps and USB/audio/display devices
- `<5%` CPU cgroup cap
- Event-driven file integrity — no hourly full-home scans in default mode