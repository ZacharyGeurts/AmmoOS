# NEXUS-Shield · Universal Protector

**v10.4.2** — Field C2 for Linux. Gatekeeper scoring, loopback panel, hardened boot-impl, painless field conversion, Underlay F9 Tristate installer.

> **TL;DR:** Download release → `sudo ./install-all.sh` → browser opens **http://127.0.0.1:9477/field** on every boot.

---

## What it does

NEXUS is a field command layer — not a traditional AV suite:

1. **Scores** live connections on 10 axes (gatekeeper).
2. **You decide** — Trust forever · Stop this site · KILL when corroborated.
3. **Publishes** everything to a loopback panel (`:9477`) — no cloud required.
4. **Reloads** field tech on every reboot (`nexus-boot-impl` — hardened, non-destructive).
5. **Converts** to field underlay via **Underlay F9** — painless, no surprise slowdowns.

---

## Quick install

```bash
tar -xzf nexus-shield-10.4.2-source.tar.gz
cd nexus-shield-10.4.2
sudo ./install-all.sh
```

Full guide → **[Installers](Installers)**

---

## Live surfaces

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:9477/field | Main C2 panel |
| http://127.0.0.1:9477/underlay-f9?sector=underlay | Tristate / Underlay F9 |
| http://127.0.0.1:9477/field#training | Hostess7 training tab |

---

## Documentation map

| Guide | Topic |
|-------|-------|
| **[Installers](Installers)** | Release tarballs, scripts, boot, troubleshoot |
| **[Field I/O](Field-IO)** | API, state files, diagrams |
| **[Field Switch Safety](Field-Switch-Safety)** | Painless conversion, no hotspots |
| **[Panel Guide](Panel-Guide)** | Every tab + screenshots |
| **[Linux Installation](Linux-Installation)** | systemd, verify, uninstall |
| **[Underlay F9 Tristate](Underlay-F9-Tristate)** | 2026 installer, F9 hotkey |
| **[Boot Implementation](Boot-Implementation)** | First install vs reboot refresh |
| **[Architecture](Architecture)** | Daemon modules |
| **[Configuration](Configuration)** | Panel vs config files |

**GitHub Pages manual** (illustrated): https://zacharygeurts.github.io/NEXUS-Shield/

---

## Handy commands

```bash
./nexus.sh                  # dev tree — panel + browser
nexus-install-gui.sh        # Tristate installer in browser
nexus status                # health
nexus trust <ip>            # trust forever
nexus verify                # manifest integrity
pythong lib/field-switch-safety.py evaluate --phase=commit
```

---

## License

| Project | License |
|---------|---------|
| **NEXUS-Shield** | [MIT](https://github.com/ZacharyGeurts/NEXUS-Shield/blob/main/LICENSE) |
| **AMOURANTHRTX** | GPL v3 or commercial — [separate repo](https://github.com/ZacharyGeurts/AMOURANTHRTX) |

→ **[Licensing](Licensing)**