# NEXUS-Shield

**g16 1.0** — Host desktop landing, Queen Browser OS inside, field C2 command deck, host freeze, Underlay F9 Tristate installer.

## What's new in g16 1.0

| Surface | URL | Role |
|---------|-----|------|
| **Host desktop** (first page) | http://127.0.0.1:9477/field | Mirror incumbent OS apps + field startbar |
| **Field command** (full C2) | http://127.0.0.1:9477/command | Threat panel — Monitor, Training, Intel, System |
| **Queen Browser** | http://127.0.0.1:9481/world/browser.html | Browser chrome with field OS inside Start tab |
| **Underlay F9** | http://127.0.0.1:9477/underlay-f9?sector=underlay | 2026 Tristate installer |

**Drop / Rise** — Queen shell calls `/api/field-underlay-surface` to drop the field underlay beneath the host desktop or rise the field OS slice.

**Host freeze** — `/api/field-host-freeze` soft (cgroup), mem (S3), or disk (hibernate) modes; sovereign gap witness on resume.

## Thermodynamic Foundations • Honoring Rolf Landauer

[Landauer Tribute — Field Primer](https://zacharygeurts.github.io/Field_Primer/creditors/landauer.html)

> E_min = k_B T ln 2 — the theoretical floor behind ThermoAccountant's proxy ledger.

> Landauer taught tenderness toward bits.

> To erase in haste without accounting is to spend another's clarity.

> Irreversibility reminds us: some truths, once spoken, cannot be unspoken without heat.

In NEXUS-Shield and Field layer: **All global redata is incremental, budget-capped, and guarded** — we practice the tenderness he taught. Thermal headroom enforced. Quality job 1. No damage. No haste.

---

## Install

```bash
git clone https://github.com/ZacharyGeurts/NEXUS-Shield.git
cd NEXUS-Shield
chmod +x install-all.sh genius_shield.sh nexus.sh nexus-install-gui.sh
sudo ./install-all.sh
```

Browser opens **http://127.0.0.1:9477/field** (host desktop) on start. Full C2 at **/command**.

**Installer guide:** [INSTALL-README.md](INSTALL-README.md)

| Script | Purpose |
|--------|---------|
| `install-all.sh` | One approval — full Linux install |
| `genius_shield.sh` | Deploy to `/usr/local/lib/nexus-shield` + systemd |
| `nexus-install-gui.sh` | Open Tristate / Underlay F9 installer |
| `nexus.sh` | Dev tree — panel + browser |
| `Queen/scripts/run-queen.sh` | Queen Browser on `:9481` |

---

## Manual (GitHub Pages)

| Page | Contents |
|------|----------|
| [Manual index](https://zacharygeurts.github.io/NEXUS-Shield/) | Overview + architecture diagram |
| [Field I/O](https://zacharygeurts.github.io/NEXUS-Shield/io.html) | API, state files, boot markers **with diagrams** |
| [Getting Started](https://zacharygeurts.github.io/NEXUS-Shield/getting-started.html) | Install flow + panel screenshot |

Local preview: open `docs/index.html` in a browser (images in `docs/images/`).

**Wiki:** https://github.com/ZacharyGeurts/NEXUS-Shield/wiki (sync via `./scripts/publish-wiki.sh`)

---

## Everyday commands

```bash
./nexus.sh                 # open host desktop (dev tree)
nexus status               # health + URL
nexus trust <ip>           # trust forever
nexus verify               # manifest integrity
nexus-install-gui.sh       # Tristate installer in browser
```

---

## Architecture

<p align="center">
  <img src="docs/images/io-architecture.svg" alt="NEXUS architecture I/O" width="640" />
</p>

```
Host browser
  ├─ :9477/field        → field-desktop.html (apps + startbar)
  ├─ :9477/command      → threat-panel.html (full C2)
  └─ :9481/world/browser.html → Queen chrome → Start tab embeds /field
        ↕ /api/field-underlay-surface (drop / rise)
Panel HTTP :9477 ↔ nexus-genius.service ↔ /var/lib/nexus-shield ↔ nftables perimeter
```

See [Field I/O manual](docs/io.html) for boot flow, API tables, and state file map (all illustrated).

---

## Project layout

```
install-all.sh          ← main installer
INSTALL-README.md       ← installer guide (read this for deploy)
nexus.sh                ← field dev launcher
lib/                    ← daemon modules (field-host-desktop, field-host-freeze, …)
panel/                  ← web UI (field-desktop.html, threat-panel.html)
Queen/                  ← Queen Browser OS inside
docs/                   ← GitHub Pages manual + images
wiki/                   ← GitHub wiki source
config/nexus.conf       ← defaults
```

---

## License

**NEXUS-Shield — MIT** · [LICENSE](LICENSE)

**AMOURANTHRTX — GPL v3 or commercial** (separate repo, not MIT-free)