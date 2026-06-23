# Configuration

**You don't need to edit config files.** Open the panel → **Settings** tab.

Every checkbox writes to `/var/lib/nexus-shield/settings.override`, which overrides defaults from `config/nexus.conf` on the next daemon read.

---

## Panel settings (recommended)

| Setting | Default | What it does |
|---------|---------|--------------|
| Paranoia auto-block | OFF | Block after logging forensics |
| Firewall auto-block | OFF | Auto-block threat vectors |
| Autosanitize | OFF | Legacy auto-sanitize |
| Shutdown guard | ON | Forensics on unclean kill |
| Connection gatekeeper | ON | 10-axis connection scoring |
| Packet oracle | ON | Connection snapshots for panel |
| Shadow / Entropy / Behavior / Privacy | ON | File & process watchers |
| Hostess7 corroborate | ON | Field memory cross-check |
| Auto-open panel on boot | ON | Once per day when daemon starts |
| Adblock | OFF | Filter-list domain blocking |

See [Panel Guide](Panel-Guide#settings-tab) for adblock loader steps.

---

## Config file (advanced)

Installed copy: `/usr/local/lib/nexus-shield/config/nexus.conf`

Use this for defaults on fresh install or automation — not day-to-day tuning.

### Ultra-stealth

| Toggle | Default | Purpose |
|--------|---------|---------|
| `NEXUS_ULTRA_STEALTH` | `1` | cgroup + adaptive pacing |
| `NEXUS_CPU_QUOTA_PCT` | `5` | max CPU percent |
| `NEXUS_SELF_DEFENSE` | `1` | verify MANIFEST on load |
| `NEXUS_PREDICTIVE` | `1` | correlate alerts pre-tighten |

### Polling cadence

| Setting | Calm default |
|---------|--------------|
| `NEXUS_BEHAVIOR_POLL_CALM` | 30 |
| `NEXUS_PRIVACY_POLL_CALM` | 60 |
| `NEXUS_VIGIL_MAINTAIN_INTERVAL` | 300 |

---

## Device whitelist

Consumer-safe apps live in `config/device-whitelist.conf`:

```bash
NEXUS_DEVICE_WHITELIST_COMM+=(
  my-custom-app
)
```

After edits:

```bash
sudo nexus sign
sudo systemctl restart nexus-genius.service
```

---

## Apply file-based changes

```bash
sudo nexus sign          # re-sign after lib/ edits
sudo systemctl restart nexus-genius.service
```

Panel-only changes apply immediately for paranoia/autosanitize/adblock; module restarts may need the service bounce above.