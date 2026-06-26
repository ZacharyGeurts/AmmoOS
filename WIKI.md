# NEXUS-Shield Wiki

**Live wiki:** https://github.com/ZacharyGeurts/NEXUS-Shield/wiki

**GitHub Pages manual (illustrated):** https://zacharygeurts.github.io/NEXUS-Shield/

---

## Pages (v10.4.0)

| Page | Topic |
|------|-------|
| [Home](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Home) | Overview |
| [Installers](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Installers) | Release tarballs + scripts |
| [Field I/O](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Field-IO) | API, state, diagrams |
| [Panel Guide](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Panel-Guide) | Tabs + screenshots |
| [Linux Installation](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Linux-Installation) | Install & verify |
| [Boot Implementation](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Boot-Implementation) | Reboot reload |
| [Underlay F9 Tristate](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Underlay-F9-Tristate) | 2026 installer |
| [Architecture](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Architecture) | Module map |
| [Configuration](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Configuration) | Config layers |
| [Self-Defense](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Self-Defense) | Manifest signing |
| [Licensing](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Licensing) | MIT vs GPL |

---

## Publish wiki

```bash
./scripts/publish-wiki.sh
```

Or manually:

```bash
git clone https://github.com/ZacharyGeurts/NEXUS-Shield.wiki.git
rsync -a --delete wiki/ NEXUS-Shield.wiki/
cd NEXUS-Shield.wiki && git add -A && git commit -m "wiki: v10.4.0 rewrite" && git push
```