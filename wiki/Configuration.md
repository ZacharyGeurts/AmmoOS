# Configuration

Granular toggles in `config/nexus.conf`. Installed copy: `/usr/local/lib/nexus-shield/config/nexus.conf`.

## Ultra-stealth

| Toggle | Default | Purpose |
|--------|---------|---------|
| `NEXUS_ULTRA_STEALTH` | `1` | cgroup + adaptive pacing |
| `NEXUS_CPU_QUOTA_PCT` | `5` | max CPU percent |
| `NEXUS_SELF_DEFENSE` | `1` | verify MANIFEST on load |
| `NEXUS_PREDICTIVE` | `1` | correlate alerts pre-tighten |

## Legacy AV (deprecated)

| Toggle | Default | Purpose |
|--------|---------|---------|
| `NEXUS_LEGACY_AV` | `0` | ClamAV/rkhunter opt-in only |

Set at install: `sudo NEXUS_LEGACY_AV=1 ./stealth_install.sh`

## Module toggles

| Toggle | Default |
|--------|---------|
| `NEXUS_SHADOW_WATCH` | `1` |
| `NEXUS_ENTROPY_WATCH` | `1` |
| `NEXUS_BEHAVIOR_WATCH` | `1` |
| `NEXUS_PRIVACY_GUARD` | `1` |

## Polling cadence

| Setting | Calm default |
|---------|--------------|
| `NEXUS_BEHAVIOR_POLL_CALM` | 30 |
| `NEXUS_PRIVACY_POLL_CALM` | 60 |
| `NEXUS_VIGIL_MAINTAIN_INTERVAL` | 300 |

## Device whitelist

Extend consumer-safe processes in `config/device-whitelist.conf`:

```bash
NEXUS_DEVICE_WHITELIST_COMM+=(
  my-custom-app
)
```

## Apply changes

```bash
sudo nexus sign          # re-sign after lib edits
sudo systemctl restart nexus-genius.service
```