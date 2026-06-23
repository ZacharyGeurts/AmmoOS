# Ultra-Stealth Mode

> *<5% CPU, cgroup isolation, event-driven — invisible to consumers.*

## Mechanisms

| Control | Implementation |
|---------|----------------|
| CPU cap | systemd `CPUQuota=5%` + cgroup v2 `cpu.max` |
| I/O priority | `IOSchedulingClass=idle` |
| Process priority | `Nice=19` + `ionice -c3` |
| File watches | inotify (Shadow Reality, Entropy Oracle) — **event-driven** |
| procfs scans | adaptive intervals: 30s calm → 2s storm |
| Supervisor loop | 300s maintenance only (no full-disk polling) |

## Adaptive polling

Behavior Symphony and Privacy Guard use **backoff in calm mode** and tighten only when Eternal Vigil or Predictive Guard escalates:

| Mode | Behavior poll | Privacy poll |
|------|---------------|--------------|
| Calm | 30s | 60s |
| Alert | 8s | 15s |
| Storm | 2s | 5s |

## Configuration

```bash
NEXUS_ULTRA_STEALTH=1
NEXUS_CPU_QUOTA_PCT=5
NEXUS_BEHAVIOR_POLL_CALM=30
NEXUS_PRIVACY_POLL_CALM=60
```

Edit `/usr/local/lib/nexus-shield/config/nexus.conf`, then `sudo systemctl restart nexus-genius.service`.

## Verify

```bash
nexus status
systemctl show nexus-genius.service -p CPUQuotaPerSecUSec,MemoryMax,Nice
```