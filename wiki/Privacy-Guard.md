# Privacy Guard

> *Prevents hostile viewing of sensitive files without disrupting normal use.*

## Concept

Privacy Guard complements Shadow Reality (tampering) with **viewing detection**. It scans `/proc/*/fd` for non-privileged processes that have opened sensitive paths — SSH keys, shadow databases, sudoers — and hardens default permissions on those files.

## What it protects

| Path | Threat |
|------|--------|
| `/etc/shadow`, `/etc/gshadow` | Credential theft |
| `/etc/sudoers` | Privilege escalation recon |
| `~/.ssh/authorized_keys` | Backdoor injection / key theft |
| `~/.bash_history` | Credential harvesting |

## Implementation

| Layer | Mechanism |
|-------|-----------|
| **Hardening** | `chmod 600` on shadow files, `700` on `.ssh` dirs |
| **Detection** | Poll `/proc/[pid]/fd` symlinks every 5s |
| **Allowlist** | root, `sshd`, `sudo`, `systemd`, `aide`, `clamscan` |
| **Alert** | `PRIVACY_GUARD_ALERT` → `/var/log/nexus-alerts.log` |

## Consumer impact

- **None visible** — no prompts, no blocked apps for legitimate users
- Shells and editors owned by the user can still read their own files
- Alerts fire when an **unexpected process** opens a sensitive system path

## Configuration

In `config/nexus.conf`:

```
NEXUS_PRIVACY_GUARD=1
```

Disable with `0` and restart `nexus-genius.service`.

## Windows

`stealth.ps1` registers a hidden scheduled task that monitors suspicious process access patterns around `authorized_keys` and logs to `%ProgramData%\NEXUS\nexus-alerts.log`.

## Operator commands

```bash
nexus alerts | grep privacy-guard
sudo journalctl -t nexus-privacy-guard
```