# Panel Guide

The NEXUS panel is your entire control surface. No config-file spelunking required.

**Open it:** `./nexus.sh` or the **NEXUS-Shield** desktop icon → `https://127.0.0.1:9477/`

---

## Monitor tab

![Monitor tab](https://raw.githubusercontent.com/ZacharyGeurts/NEXUS-Shield/main/docs/screenshots/panel-monitor.png)

### Connection Gatekeeper (left side)

Every live TCP flow gets a **verdict** and a **10-axis score**:

| Verdict | Meaning |
|---------|---------|
| `USER_OK` | Looks like normal you — browser, media, trusted process |
| `EPHEMERAL` | Short-lived / search-like traffic |
| `SUSPICIOUS` | Worth a glance, not auto-blocked |
| `HARM_CANDIDATE` | High harm-axis score — **you** decide to block |

**Axes explained (plain English):**

- **User browser / Media stream** — signals everyday use
- **Search / ephemeral** — quick lookups, not sustained abuse
- **Bandwidth abuse / Stream theft** — heavy or sketchy data movement
- **Beacon pattern** — repetitive callback behavior
- **Process trust** — is the app on the whitelist?
- **Destination risk** — IP reputation class
- **Threat linked** — correlated with recent alerts
- **You authorized** — you already clicked trust

### Buttons on each connection

| Button | Effect |
|--------|--------|
| **Authorize** | Permanent trust. Written to firewall + Hostess7 JSONL (local + TEAM). Never auto-block this peer again. |
| **Block harm** | Only on harm candidates. Adds an outbound nft block for 24h. |

### Permanent authorizations (bottom left)

List of every IP you've trusted. **Revoke** removes trust if you change your mind.

### Threats (right side)

- **Correlation** — how many recent alerts overlap
- **Active threats** — vector name, severity, detail
- **Firewall / blocks** — nft sentinel status

---

## Settings tab

![Settings tab](https://raw.githubusercontent.com/ZacharyGeurts/NEXUS-Shield/main/docs/screenshots/panel-settings.png)

### Protection

| Toggle | Default | Plain English |
|--------|---------|---------------|
| Paranoia auto-block | OFF | Log everything first; enable to block after forensics |
| Firewall auto-block | OFF | Auto-block on threat *vectors* (not gatekeeper connections) |
| Autosanitize | OFF | Legacy auto-sanitize — prefer manual gatekeeper clicks |
| Shutdown guard | ON | Capture forensics if NEXUS is killed |

### Modules

Turn watchers on/off: gatekeeper, packet oracle, shadow reality, entropy oracle, behavior symphony, privacy guard, Hostess7 corroborate, auto-open panel on boot.

> Some module toggles save instantly but need a service restart to fully apply: `sudo systemctl restart nexus-genius.service`

### Adblock loader

1. Click **Load EasyList** / **EasyPrivacy** / **Fanboy** (or paste a custom URL).
2. Check **Enable adblock**.
3. Click **Apply to firewall** — resolves domains to IPs and blocks outbound via nft.

Sacred/trusted IPs are never blocked.

### Paranoia incidents & Autosanitize actions

Historical forensics and undo checkboxes live here — moved from old separate tabs so everything is one place.

---

## Logs tab

![Logs tab](https://raw.githubusercontent.com/ZacharyGeurts/NEXUS-Shield/main/docs/screenshots/panel-logs.png)

| Sub-tab | File |
|---------|------|
| Alerts | `/var/log/nexus-alerts.log` |
| Vigil | Eternal Vigil maintenance log |

Hit **Refresh** to pull the latest lines. Good first stop when something feels off.

---

## Shutdown modal (red banner)

If NEXUS was killed uncleanly, a banner and modal appear with:

- **Who killed it** (systemd, signal, process)
- **Remote peers at death** — pick which IP to block on restart
- **Review forensics** — jumps to Settings incidents
- **Block offender & restart** — recommended if you see a clear bad peer
- **Restart log-only** — no new blocks, just resume watching

Nothing happens until you click. Default safe path is review first.

---

## Deep links

Share or bookmark a specific tab:

- Monitor — `https://127.0.0.1:9477/#monitor`
- Settings — `https://127.0.0.1:9477/#settings`
- Logs — `https://127.0.0.1:9477/#logs`

Localhost only. TLS self-signed cert — your browser may ask you to trust it once.