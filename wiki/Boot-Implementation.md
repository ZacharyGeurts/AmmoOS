# Boot Implementation

Every **startup and reboot** reloads field tech before the normal daemon loop. **First install** runs a heavier path once.

---

## Flow

![Boot I/O](https://raw.githubusercontent.com/ZacharyGeurts/NEXUS-Shield/main/docs/images/io-boot-flow.svg)

1. **systemd** `ExecStartPre` → `scripts/nexus-boot-impl.sh`
2. **First install** (`first-boot.complete` missing): wire-stack, migrate state, sign manifest, sense meld
3. **Every boot** (refresh): re-wire, export paths, front-hook, verify, meld
4. **Daemon** starts watchers + panel
5. **Browser** opens `/field` once per `boot_id`

---

## Scripts

| Path | Role |
|------|------|
| `lib/nexus-boot-impl.sh` | Core first vs refresh logic |
| `scripts/nexus-boot-impl.sh` | Standalone entry (ExecStartPre) |

Hooked from: `nexus-daemon.sh`, `nexus.sh`, `genius_shield.sh` (first install).

---

## Markers (`NEXUS_STATE_DIR`)

```
first-boot.complete    # written after first full impl
boot-impl.last         # mode=first|refresh, version, ts
boot-impl.log          # wire-stack output
panel-launched.boot    # kernel boot_id — browser once per reboot
```

---

## Force full re-impl

```bash
sudo rm /var/lib/nexus-shield/first-boot.complete
sudo systemctl restart nexus-genius.service
```

Or one-shot: `NEXUS_BOOT_FORCE_FIRST=1 bash scripts/nexus-boot-impl.sh`

---

## Disable

Set `NEXUS_BOOT_IMPL=0` in `config/nexus.conf` or `settings.override`.