# Windows Installation

## Status ✅

`stealth.ps1` deploys invisible background protection via a hidden scheduled task.

## Requirements

- Windows 10/11
- PowerShell 5.1+
- Run as **Administrator**

## Install

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\stealth.ps1
```

No UI appears. Protection starts immediately and at every boot.

## What it deploys

| Component | Location |
|-----------|----------|
| Watch script | `%ProgramData%\NEXUS\nexus-watch.ps1` |
| Shadow hashes | `%ProgramData%\NEXUS\shadow\` |
| Alert log | `%ProgramData%\NEXUS\nexus-alerts.log` |
| Scheduled task | `NEXUS-Shield` (hidden, highest privilege) |

## Modules on Windows

| Module | Implementation |
|--------|----------------|
| Shadow Reality | SHA256 baseline on hosts, authorized_keys |
| Entropy Oracle | Shannon H on Desktop/Downloads files |
| Behavior Symphony | Process path/name scoring |
| Privacy Guard | Suspicious access near SSH keys |
| Eternal Vigil | 5-minute loop (calm interval) |

## Verify

```powershell
Get-ScheduledTask -TaskName 'NEXUS-Shield'
Get-Content "$env:ProgramData\NEXUS\nexus-alerts.log" -Tail 20
```

## Uninstall

```powershell
Unregister-ScheduledTask -TaskName 'NEXUS-Shield' -Confirm:$false
Remove-Item -Recurse -Force "$env:ProgramData\NEXUS"
```

## Security note

Always review PowerShell scripts before running as Administrator. NEXUS-Shield is open source — read every line first.