# NEXUS-Shield v2.0 — Connection Gatekeeper

**NEXUS ∞** by [AmouranthRTX](https://github.com/ZacharyGeurts/AMOURANTHRTX) — invisible, zero-trust behavioral security. Pure genius heuristics. No heavy AV agents.

## v2.0 highlights

- **Connection Gatekeeper** — 10-axis intent score per live connection (user browsing vs ephemeral search vs harm candidate)
- **Click to Authorize** — permanent trust stored in Hostess7 field memory (local + TEAM NVMe)
- **Click to Block** — harm candidates only; never auto-blocks your CDN/browser traffic
- **Panel auto-opens** on startup · **Start menu entry** + icon

## Quick launch

```bash
git clone https://github.com/ZacharyGeurts/NEXUS-Shield.git
cd NEXUS-Shield
chmod +x stealth_install.sh genius_shield.sh
sudo ./stealth_install.sh
```

## Goals

- **Non-intrusive** — `<5%` CPU, cgroup-limited, `Nice=19`, idle I/O; never breaks peripherals, network, or usability
- **Secure** — multi-layer behavioral + integrity + predictive correlation
- **AMOURANTHRTX field learnings** — silent daemon, whitelisted consumer devices/processes, user-just-use focus

## Modules

| Module | Role |
|--------|------|
| Shadow Reality | inotify + SHA256 tamper detection |
| Entropy Oracle | Shannon entropy on new files |
| Behavior Symphony | procfs chain scoring (whitelisted consumer apps) |
| Privacy Guard | sensitive-file view detection |
| Predictive Guard | correlates alerts to pre-tighten thresholds |
| Eternal Vigil | calm / alert / storm adaptive pacing |
| Self-Defense | signed manifest verified on daemon load |

## Quick start

**Legacy AV (deprecated, opt-in only):**
```bash
sudo NEXUS_LEGACY_AV=1 ./stealth_install.sh
```

**Windows (Admin):** `.\stealth.ps1`

**Tests:** `nexus test` or `./tests/run-tests.sh`

**Operator CLI:** `nexus status` · `nexus verify` · `nexus sign` · `nexus alerts`

## Documentation

📖 **[Live Wiki](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki)** · [Design doc](NEXUS-DESIGN-IMPROVEMENT.md)

| Page | Topic |
|------|-------|
| [Architecture](wiki/Architecture.md) | Module map, ultra-stealth |
| [Configuration](wiki/Configuration.md) | Granular toggles |
| [Ultra-Stealth](wiki/Ultra-Stealth.md) | cgroup, event-driven pacing |
| [Self-Defense](wiki/Self-Defense.md) | Script signing |
| [AMOURANTHRTX Integration](wiki/AMOURANTHRTX-Integration.md) | Device whitelist |

## Layout

```
lib/                 # Core modules + ultra-stealth + self-defense
config/              # nexus.conf + device-whitelist.conf
tests/               # Test suite
stealth_install.sh   # Default installer (genius-only)
genius_shield.sh     # Genius layer install + service
full_av_install.sh   # DEPRECATED legacy AV (opt-in)
```

ClamAV/rkhunter are **not** installed by default. Pure NEXUS genius heuristics only.

Part of the AmouranthRTX security ecosystem. Test in a VM before production deploy.
