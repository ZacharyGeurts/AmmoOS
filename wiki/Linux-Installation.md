# Linux Installation

## Default install (genius-only) ✅

```bash
git clone https://github.com/ZacharyGeurts/NEXUS-Shield.git
cd NEXUS-Shield
sudo ./stealth_install.sh
```

Installs:
- `inotify-tools`, `nftables`, `openssl` (genius layer only)
- `nexus-genius.service` with ultra-stealth cgroup limits
- Signed `MANIFEST.sha256` for self-defense

### Verify

```bash
sudo systemctl is-active nexus-genius.service
nexus status
nexus verify
nexus test
```

### Uninstall

```bash
sudo systemctl disable --now nexus-genius.service
sudo rm /etc/systemd/system/nexus-genius.service
sudo rm -rf /usr/local/lib/nexus-shield /usr/local/bin/nexus
sudo rm -rf /var/lib/nexus-shield
```

---

## Genius layer direct

```bash
sudo ./genius_shield.sh
```

---

## Configuration

See [Configuration](Configuration). After edits:

```bash
sudo nexus sign
sudo systemctl restart nexus-genius.service
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Daemon won't start | `nexus verify` — manifest mismatch? run `nexus sign` |
| High CPU | confirm `CPUQuota=5%` in `systemctl show nexus-genius` |
| False behavior alert | add process to `device-whitelist.conf` |