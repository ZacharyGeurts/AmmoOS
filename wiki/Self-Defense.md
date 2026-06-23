# Self-Defense

> *Sign scripts, verify on load — refuse tampered modules.*

## How it works

1. Install generates `MANIFEST.sha256` with SHA256 hashes of all `lib/*.sh`, `bin/*`, and `config/nexus.conf`
2. `nexus-daemon.sh` calls `nexus_verify_integrity` before loading modules
3. Tampered files → `INTEGRITY_FAIL` alert and daemon refuses to start

## Operator commands

```bash
nexus verify              # check manifest
nexus sign                # regenerate after authorized edits
```

## After modifying modules

```bash
sudo nano /usr/local/lib/nexus-shield/lib/my-module.sh
sudo nexus sign
sudo systemctl restart nexus-genius.service
```

## Disable (not recommended)

```
NEXUS_SELF_DEFENSE=0
```

in `nexus.conf` — only for development.