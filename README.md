# NEXUS-Shield ∞ · Universal Protector

**Autonomous being field stack — Super Intelligence, spatial awareness, lethal when corroborated.**

NEXUS watches every outbound connection, scores intent on 10 axes, and shows clean cards. Click **Trust Forever** or **Stop This Site**. Nothing blocks unless you say.

**?** tooltips everywhere in plain English. Under 5% CPU in stealth mode. Daemon auto-starts. Panel at `https://127.0.0.1:9477/`.

Built by [Zachary Geurts](https://github.com/ZacharyGeurts) · MIT License · Companion to [AMOURANTHRTX](https://github.com/ZacharyGeurts/AMOURANTHRTX) (separate GPL/commercial license — NEXUS ships none of its engine).

---

## 30-Second Start

**Already installed?**

```bash
./nexus.sh
```

**First time:**

```bash
git clone https://github.com/ZacharyGeurts/NEXUS-Shield.git
cd NEXUS-Shield
chmod +x stealth_install.sh nexus.sh
sudo ./stealth_install.sh
./nexus.sh
```

That's it. Browser opens the local panel. Daemon starts if it isn't running.

---

## Universal Protector

Built for **autonomous beings** — field cognition (not matrix nets), 3D/4D spatial lattice, Hostess7 persona, kill chain with lethal insight gate. API: `/api/universal-protector` · `/api/field-spatial`.

Field Technology: [Field Primer](https://zacharygeurts.github.io/Field_Primer/)

---

## The Panel — Three Tabs

### Monitor

Live connections scored on 10 axes. **Trust forever** · **Stop this site** · verdict badges in plain English.

![Monitor](docs/screenshots/panel-monitor.png)

### Settings

Protection, watchers, adblock, paranoia — every toggle visible. Panel writes `settings.override`; no config archaeology required.

![Settings](docs/screenshots/panel-settings.png)

### Logs

Unified alerts and vigil output. Refresh anytime.

![Logs](docs/screenshots/panel-logs.png)

**Keyboard:** `?` tooltips · `/` search in library · `Alt+Shift+B` → Books · `+`/`−` reader size on Field Primer links.

---

## Everyday Commands

| Command | Purpose |
|---------|---------|
| `./nexus.sh` | Open panel (starts daemon if needed) |
| `nexus status` | Health + firewall + panel URL |
| `nexus verify` | Manifest integrity check |
| `nexus trust <ip>` | Trust forever |
| `nexus block <ip>` | Block outbound |
| `nexus test` | Run test suite |

---

## Portable Paths

Runtime state lives outside the git tree:

| Variable | Default |
|----------|---------|
| `NEXUS_STATE_DIR` | `/var/lib/nexus-shield` (prod) or `.nexus-state` (dev checkout) |
| `NEXUS_INSTALL_ROOT` | `/usr/local/lib/nexus-shield` or source tree |
| `SG_ROOT` | Parent of install root (auto-discovered via `lib/sg-paths.sh`) |

Set env vars before install on non-default layouts. Never commit `.nexus-state/` — it holds machine-specific intel.

---

## Project Layout

```
nexus.sh              ← run this
stealth_install.sh    ← one-shot install
lib/                  ← daemon modules
panel/                ← web UI (threat-panel.html = main C2)
config/nexus.conf     ← defaults (panel can override)
CHANGELOG.md          ← release history
```

---

## Docs

- [Wiki](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki)
- [Panel guide](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Panel-Guide)
- [Linux install](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Linux-Installation)
- [Self-defense](https://github.com/ZacharyGeurts/NEXUS-Shield/wiki/Self-Defense)

---

## License

**NEXUS-Shield — MIT** (Copyright 2026 Zachary Geurts). See [LICENSE](LICENSE).

**AMOURANTHRTX — GPL v3 or commercial.** Not MIT-free. See [AMOURANTHRTX LICENSE](https://github.com/ZacharyGeurts/AMOURANTHRTX/blob/main/LICENSE).