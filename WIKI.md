# NEXUS-Shield Wiki

**Live wiki:** https://github.com/ZacharyGeurts/NEXUS-Shield/wiki

## Pages

| Page | Topic |
|------|-------|
| [Home](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Home) | Friendly overview |
| [Panel Guide](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Panel-Guide) | Screenshots + every tab explained |
| [Linux Installation](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Linux-Installation) | Install & verify |
| [Configuration](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Configuration) | Panel settings vs config files |
| [Architecture](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Architecture) | Module map |
| [Ultra-Stealth](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Ultra-Stealth) | cgroup + event-driven |
| [Self-Defense](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Self-Defense) | Script signing |
| [AMOURANTHRTX Integration](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/AMOURANTHRTX-Integration) | Device whitelist |
| [Windows Installation](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Windows-Installation) | `stealth.ps1` |

## Publish wiki from repo

```bash
git clone https://github.com/ZacharyGeurts/NEXUS-Shield.wiki.git
cp -r ../NEXUS-Shield/wiki/*.md NEXUS-Shield.wiki/
cd NEXUS-Shield.wiki && git add -A && git commit -m "Sync wiki" && git push
```