# NEXUS-Shield v2.0.2 — Connection Gatekeeper

**NEXUS ∞** by [AmouranthRTX](https://github.com/ZacharyGeurts/AMOURANTHRTX) — invisible, zero-trust behavioral security. Pure genius heuristics. No heavy AV agents.

## Use it

After install, that's all you need:

```bash
./nexus.sh
```

Or click **NEXUS-Shield** in your app menu / desktop icon.

The web panel opens at `https://127.0.0.1:9477/` — monitor connections, authorize trust, block harm, and flip every setting (adblock loaders, paranoia, modules) from **Settings**. No config file editing.

## Install once

```bash
git clone https://github.com/ZacharyGeurts/NEXUS-Shield.git
cd NEXUS-Shield
chmod +x stealth_install.sh genius_shield.sh nexus.sh
sudo ./stealth_install.sh
```

## v2.0.2

- **Simple launcher** — `./nexus.sh` or desktop icon; daemon starts automatically
- **Settings tab** — all toggles, adblock list loaders, paranoia & autosanitize in one place
- **Monitor | Settings | Logs** — trimmed panel navigation

## v2.0 highlights

- **Connection Gatekeeper** — 10-axis intent score per live connection
- **Click to Authorize** — permanent trust in Hostess7 field memory
- **Click to Block** — harm candidates only; never auto-blocks CDN/browser traffic

## Goals

- **Non-intrusive** — `<5%` CPU, cgroup-limited, `Nice=19`
- **Secure** — multi-layer behavioral + integrity + predictive correlation
- **AMOURANTHRTX field learnings** — silent daemon, whitelisted consumer apps

## Modules

| Module | Role |
|--------|------|
| Shadow Reality | inotify + SHA256 tamper detection |
| Entropy Oracle | Shannon entropy on new files |
| Behavior Symphony | procfs chain scoring |
| Privacy Guard | sensitive-file view detection |
| Predictive Guard | correlates alerts to pre-tighten thresholds |
| Eternal Vigil | calm / alert / storm adaptive pacing |
| Self-Defense | signed manifest verified on daemon load |

## Operator CLI

`nexus status` · `nexus verify` · `nexus sign` · `nexus alerts`

**Tests:** `nexus test` or `./tests/run-tests.sh`

## Layout

```
stealth_install.sh   # one-shot install
genius_shield.sh     # Genius layer install + service
nexus.sh             # open panel (starts daemon if needed)
lib/                 # daemon modules
panel/               # threat panel UI
config/nexus.conf    # defaults (overridden by panel Settings)
```