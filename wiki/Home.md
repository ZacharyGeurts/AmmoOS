# NEXUS-Shield · Universal Protector

**g16 1.0** — Host desktop landing, Queen Browser OS inside, field C2, host freeze, Underlay F9 Tristate installer.

> **TL;DR:** Clone repo → `sudo ./install-all.sh` → browser opens **http://127.0.0.1:9477/field** (host desktop) on every boot.

---

## What it does

NEXUS is a field command layer — not a traditional AV suite:

1. **Scores** live connections on 10 axes (gatekeeper).
2. **You decide** — Trust forever · Stop this site · KILL when corroborated.
3. **Publishes** everything to a loopback panel (`:9477`) — no cloud required.
4. **Reloads** field tech on every reboot (`nexus-boot-impl` — hardened, non-destructive).
5. **Mirrors** the incumbent OS on first page — all apps, familiar menu, field startbar.
6. **Embeds** field OS inside Queen Browser Start tab — drop/rise underlay beneath host.
7. **Freezes** the host OS on demand — memory lock, sovereign clock witness on resume.

---

## Quick install

```bash
git clone https://github.com/ZacharyGeurts/NEXUS-Shield.git
cd NEXUS-Shield
sudo ./install-all.sh
```

Full guide → **[Installers](Installers)**

---

## Live surfaces

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:9477/field | **Host desktop** — apps + startbar (first page) |
| http://127.0.0.1:9477/command | **Field command** — full C2 threat panel |
| http://127.0.0.1:9481/world/browser.html | **Queen Browser** — OS inside Start tab |
| http://127.0.0.1:9477/underlay-f9?sector=underlay | Tristate / Underlay F9 |
| http://127.0.0.1:9477/command#training | Hostess7 training tab |

---

## Documentation map

| Guide | Topic |
|-------|-------|
| **[Installers](Installers)** | Release tarballs, scripts, boot, troubleshoot |
| **[Host Desktop](Host-Desktop)** | First page, startbar, app mirror |
| **[Queen Browser](Queen-Browser)** | Browser chrome, OS inside, drop/rise |
| **[Host Freeze](Host-Freeze)** | Soft/mem/disk freeze, sovereign resume |
| **[Field I/O](Field-IO)** | API, state files, diagrams |
| **[Field Switch Safety](Field-Switch-Safety)** | Painless conversion, no hotspots |
| **[Field Thermal Guard](Field-Thermal-Guard)** | Landauer budget, incremental redata |
| **[Panel Guide](Panel-Guide)** | Command deck tabs + screenshots |
| **[Linux Installation](Linux-Installation)** | systemd, verify, uninstall |
| **[Underlay F9 Tristate](Underlay-F9-Tristate)** | 2026 installer, F9 hotkey |
| **[Boot Implementation](Boot-Implementation)** | First install vs reboot refresh |
| **[Architecture](Architecture)** | Daemon modules |
| **[Configuration](Configuration)** | Panel vs config files |

**GitHub Pages manual** (illustrated): https://zacharygeurts.github.io/NEXUS-Shield/

---

## Handy commands

```bash
./nexus.sh                  # dev tree — host desktop + browser
Queen/scripts/run-queen.sh  # Queen Browser on :9481
nexus-install-gui.sh        # Tristate installer in browser
nexus status                # health
nexus trust <ip>            # trust forever
nexus verify                # manifest integrity
```

---

## License

| Project | License |
|---------|---------|
| **NEXUS-Shield** | [MIT](https://github.com/ZacharyGeurts/NEXUS-Shield/blob/main/LICENSE) |
| **AMOURANTHRTX** | GPL v3 or commercial — [separate repo](https://github.com/ZacharyGeurts/AMOURANTHRTX) |

→ **[Licensing](Licensing)**