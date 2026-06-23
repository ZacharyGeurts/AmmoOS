# NEXUS-Shield Improvement Design Doc

## Goals ✅

- **Non-intrusive:** <5% CPU, invisible, no breaks to peripherals/network/usability
- **Secure:** Multi-layer behavioral + integrity + predictive
- **Integrate AMOURANTHRTX field learnings:** silent daemon, whitelist common devices, user-just-use focus

## Key Improvements ✅

| # | Improvement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | Ultra-stealth mode | ✅ | `lib/ultra-stealth.sh`, cgroup, Nice=19, inotify event-driven |
| 2 | Custom only (deprecate ClamAV/rkhunter default) | ✅ | `stealth_install.sh` → `genius_shield.sh`; `NEXUS_LEGACY_AV=0` |
| 3 | Self-defense | ✅ | `lib/self-defense.sh`, `MANIFEST.sha256`, `nexus sign/verify` |
| 4 | Granular config | ✅ | `config/nexus.conf`, `device-whitelist.conf` |
| 5 | Test suite | ✅ | `tests/run-tests.sh`, `nexus test` |
| 6 | Wiki expansion | ✅ | Ultra-Stealth, Configuration, Self-Defense, AMOURANTHRTX pages |

## Default install

```bash
sudo ./stealth_install.sh
```

Genius-only. Ultra-stealth. Non-intrusive defaults enforced at install.

## Legacy opt-in

```bash
sudo NEXUS_LEGACY_AV=1 ./stealth_install.sh
```

Deprecated ClamAV/rkhunter stack.