# Welcome to NEXUS-Shield

**NEXUS ∞** is a quiet network bodyguard for Linux. It watches connections, spots weird behavior, and lets **you** decide what to trust — without killing your internet over a false alarm.

> **TL;DR:** Install once, then run `./nexus.sh` or click the desktop icon. Everything else is in the web panel. **v2.1:** click any **?** for plain-English help on every button.

---

## What does it actually do?

Think of NEXUS as a smart bouncer for outbound traffic:

1. **Watches** live connections (which app, which IP, which port).
2. **Scores** each one — "probably you browsing" vs "might be exfil or theft."
3. **Asks you** before blocking anything important. CDNs and normal browser traffic stay safe by default.
4. **Remembers** when you click **Authorize** — that peer is trusted forever (stored in Hostess7 field memory).
5. **Runs silently** — capped CPU, no popups, whitelisted consumer apps.

No bloated antivirus suite. Pure heuristics: file integrity, entropy, process behavior, privacy guard, firewall, and a connection gatekeeper.

---

## Quick start

```bash
git clone https://github.com/ZacharyGeurts/NEXUS-Shield.git
cd NEXUS-Shield
sudo ./stealth_install.sh
./nexus.sh
```

Your browser opens `https://127.0.0.1:9477/`.

---

## The three panel tabs

| Tab | For… |
|-----|------|
| **[Monitor](Panel-Guide#monitor-tab)** | Live connections, authorize/block, active threats |
| **[Settings](Panel-Guide#settings-tab)** | All toggles, adblock lists, paranoia history |
| **[Logs](Panel-Guide#logs-tab)** | Alert and vigil log tails |

Full walkthrough → **[Panel Guide](Panel-Guide)**

---

## When something looks scary

| Situation | What to do |
|-----------|------------|
| Browser/CDN flagged | Click **Authorize** — permanent trust |
| Real harm candidate | Click **Block harm** — outbound block for that IP |
| NEXUS was killed | Red banner → review forensics → pick restart option |
| Too many alerts | Settings → turn down paranoia auto-block (default is log-only) |

NEXUS is designed **OFF-first** for blocking. Detection and logging always run; crushing traffic is your choice.

---

## Learn more

| Guide | Topic |
|-------|-------|
| [Panel Guide](Panel-Guide) | Screenshots + plain-English tour |
| [Linux Installation](Linux-Installation) | Install, verify, uninstall |
| [Configuration](Configuration) | Panel settings vs config files |
| [Architecture](Architecture) | How modules connect |
| [Ultra-Stealth](Ultra-Stealth) | CPU limits, event-driven design |
| [Self-Defense](Self-Defense) | Signed manifest |

---

## Handy commands

```bash
./nexus.sh          # open panel
nexus status        # health
nexus verify        # integrity check
nexus alerts        # recent log lines
nexus test          # run tests
```

---

## License

| Project | License | Free like MIT? |
|---------|---------|----------------|
| **NEXUS-Shield** (this repo) | [MIT](https://github.com/ZacharyGeurts/NEXUS-Shield/blob/main/LICENSE) | Yes |
| **AMOURANTHRTX** (Field Die) | [GPL v3 or commercial](https://github.com/ZacharyGeurts/AMOURANTHRTX/blob/main/LICENSE) | **No** |

NEXUS-Shield is MIT — free to use with attribution. AMOURANTHRTX is a **separate product**: dual-licensed under **GPL v3** (copyleft) or **commercial** (3% profit share). That technology is **not MIT-free**.

Full breakdown → **[Licensing](Licensing)**

## Related

- [AMOURANTHRTX](https://github.com/ZacharyGeurts/AMOURANTHRTX) — Field Die runtime (GPL v3 or commercial — not MIT)
- [GitHub README](https://github.com/ZacharyGeurts/NEXUS-Shield#readme) — screenshots and feature summary