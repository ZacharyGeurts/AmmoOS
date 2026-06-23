# Eternal Vigil

> *Background loop with adaptive thresholds.*

## Concept

Eternal Vigil is the **watchdog heartbeat** of NEXUS-Shield. It never stops. It adjusts how aggressively other modules scan based on recent activity.

## Shipped service

### `nexus-genius.service`

```
nexus-genius.service
  └── /usr/local/lib/nexus-shield/lib/nexus-daemon.sh
        ├── Shadow Reality (inotify)
        ├── Entropy Oracle (inotify)
        ├── Behavior Symphony (procfs)
        ├── Privacy Guard (fd scan)
        ├── Connection Gatekeeper (intent scoring)
        └── Threat Panel (HTTPS localhost)
```

Runs at `Nice=19` with idle I/O scheduling — invisible to consumers.

## Adaptive thresholds ✅

| State | Scan interval | Entropy threshold | Behavior sensitivity |
|-------|---------------|-------------------|--------------------|
| **Calm** | 3600s | 7.4 | 50 |
| **Alert** (any module fired) | 900s | 6.8 | 50 |
| **Storm** (3+ alerts in 10m) | 300s | 6.5 | 40 |

Calm state returns after 24h without alerts.

## Commands

```bash
sudo systemctl status nexus-genius.service
nexus status
tail -f /var/log/nexus-alerts.log
```

## Logs

| File | Content |
|------|---------|
| `/var/log/nexus-alerts.log` | Unified alert stream (all modules) |
| `journalctl -u nexus-genius` | Genius layer service output |