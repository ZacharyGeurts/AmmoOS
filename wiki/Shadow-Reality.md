# Shadow Reality

> *Mirrors files in RAM, detects tampering by diff.*

## Concept

Shadow Reality maintains a **shadow hash baseline** of critical system and user files. When the live file changes, NEXUS compares the new on-disk content against the shadow. Unexpected diffs trigger an alert — even if the attacker never touched the shadow store.

## Implementation ✅

| Layer | Tool | Role |
|-------|------|------|
| Hot shadow | `lib/shadow-reality.sh` + inotify | Real-time diff on watched paths |
| Alert | syslog + `/var/log/nexus-alerts.log` | Operator visibility only |

### Watch list (default)

```
/etc/passwd /etc/shadow /etc/gshadow /etc/sudoers
/etc/crontab /etc/ssh/sshd_config
~/.ssh/authorized_keys  ~/.bashrc
/usr/local/bin/*
```

### Diff algorithm

1. On first sight: store `sha256(file)` in `/var/lib/nexus-shield/shadow/`
2. On `IN_MODIFY` / `IN_CREATE`: re-hash, compare
3. If diff → log `SHADOW_REALITY_ALERT`

## Operator commands

```bash
nexus shadow init          # build baseline
nexus shadow verify        # one-shot diff report
sudo systemctl status nexus-genius.service
```

## Tuning

- High-churn paths (`/tmp`, `~/.cache`) are excluded automatically
- Pair with Entropy Oracle so new high-entropy files get double scrutiny