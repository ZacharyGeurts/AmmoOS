# NEXUS-Shield Wiki

**NEXUS ∞** — invisible security by AmouranthRTX. Pure genius heuristics. User-just-use.

## Design goals

1. **Non-intrusive** — `<5%` CPU, no popups, no peripheral/network disruption
2. **Secure** — behavioral + integrity + predictive multi-layer defense
3. **AMOURANTHRTX field learnings** — silent daemon, device whitelist, zero friction

## Modules

| Module | Wiki |
|--------|------|
| Shadow Reality | [Shadow-Reality](Shadow-Reality) |
| Entropy Oracle | [Entropy-Oracle](Entropy-Oracle) |
| Behavior Symphony | [Behavior-Symphony](Behavior-Symphony) |
| Eternal Vigil | [Eternal-Vigil](Eternal-Vigil) |
| Privacy Guard | [Privacy-Guard](Privacy-Guard) |
| Predictive Guard | [Architecture](Architecture#predictive-guard) |
| Self-Defense | [Self-Defense](Self-Defense) |

## Install

```bash
sudo ./stealth_install.sh    # default — genius-only, ultra-stealth
sudo ./genius_shield.sh      # same stack, direct
nexus test                   # run test suite
```

## Guides

| Page | Topic |
|------|-------|
| [Architecture](Architecture) | How it fits together |
| [Ultra-Stealth](Ultra-Stealth) | cgroup, event-driven, CPU budget |
| [Configuration](Configuration) | Granular toggles |
| [Self-Defense](Self-Defense) | Signed script manifest |
| [AMOURANTHRTX Integration](AMOURANTHRTX-Integration) | Device/process whitelist |
| [Linux Installation](Linux-Installation) | Deploy + services |
| [Windows Installation](Windows-Installation) | Scheduled task |

## Quick commands

```bash
nexus status
nexus verify
nexus alerts
systemctl status nexus-genius.service
```

## Related

- [AMOURANTHRTX](https://github.com/ZacharyGeurts/AMOURANTHRTX) — Field Die runtime
- [Design doc](https://github.com/ZacharyGeurts/NEXUS-Shield/blob/main/NEXUS-DESIGN-IMPROVEMENT.md)