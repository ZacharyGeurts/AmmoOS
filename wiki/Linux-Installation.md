# Linux Installation

Install once. Use forever with `./nexus.sh` or the desktop icon.

---

## Requirements

- Linux with systemd
- Root/sudo for install
- `curl`, Python 3 (installed automatically on Debian/Ubuntu via apt)

---

## Install (recommended)

```bash
git clone https://github.com/ZacharyGeurts/NEXUS-Shield.git
cd NEXUS-Shield
chmod +x stealth_install.sh nexus.sh
sudo ./stealth_install.sh
```

This installs:

| Piece | Where |
|-------|-------|
| Daemon + libs | `/usr/local/lib/nexus-shield` |
| CLI | `/usr/local/bin/nexus` |
| Launcher | `/usr/local/bin/nexus.sh` |
| State | `/var/lib/nexus-shield` |
| Service | `nexus-genius.service` |
| Desktop entry | **NEXUS-Shield** in app menu |
| Panel | `https://127.0.0.1:9477/` |

Packages pulled on Debian/Ubuntu: `inotify-tools`, `nftables`, `openssl`, `iproute2`, `tcpdump`.

---

## First run

```bash
./nexus.sh
```

Or click **NEXUS-Shield** in your application launcher.

The panel opens in your default browser. If the service wasn't running, the launcher starts it for you.

---

## Verify install

```bash
sudo systemctl is-active nexus-genius.service   # should print: active
nexus status
nexus verify
nexus test
```

`nexus verify` checks the signed manifest — if you edited libs, run `sudo nexus sign` then restart.

---

## Add yourself to the nexus group (optional)

Install adds your user to group `nexus` so you can read state files without sudo:

```bash
# log out/in, or:
sg nexus -c 'nexus status'
```

---

## Uninstall

```bash
sudo systemctl disable --now nexus-genius.service
sudo rm -f /etc/systemd/system/nexus-genius.service
sudo rm -f /usr/local/bin/nexus /usr/local/bin/nexus.sh
sudo rm -rf /usr/local/lib/nexus-shield /var/lib/nexus-shield
sudo rm -f /usr/share/applications/nexus-shield.desktop
```

---

## Direct install (same stack)

```bash
sudo ./genius_shield.sh
```

Same as `stealth_install.sh` on Linux — use whichever you prefer.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Panel won't open | `sudo systemctl start nexus-genius.service` then `./nexus.sh` |
| Browser TLS warning | Expected — self-signed localhost cert. Proceed once for 127.0.0.1 |
| Daemon won't start | `nexus verify` — manifest mismatch? `sudo nexus sign` |
| High CPU | `systemctl show nexus-genius` — confirm `CPUQuota=5%` |
| False behavior alert | Settings → check whitelist in `device-whitelist.conf` |
| "Broke internet" | Settings → ensure Paranoia auto-block and Firewall auto-block are OFF unless you want them |

---

## Next steps

- [Panel Guide](Panel-Guide) — what every screen means
- [Configuration](Configuration) — settings in the panel vs config files