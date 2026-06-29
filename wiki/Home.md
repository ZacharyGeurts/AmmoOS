# AmmoOS — Field Operating System

**[→ GitHub: ZacharyGeurts/AmmoOS](https://github.com/ZacharyGeurts/AmmoOS)** · [Manual](https://zacharygeurts.github.io/AmmoOS/) · [Stack hub](https://zacharygeurts.github.io/ZacharyGeurts/stack.html) · [Release v2.0.0-beta3](https://github.com/ZacharyGeurts/AmmoOS/releases/tag/v2.0.0-beta3)

**AmmoOS 2.0.0-beta3** — field OS on loopback `127.0.0.1`. Queen Browser shell, NEXUS C2, KILROY kernel, ZNetwork pipe. All stack components ship inside the AmmoOS tree.

> **TL;DR:** `git clone https://github.com/ZacharyGeurts/AmmoOS.git` → `./scripts/wire-stack.sh` → `sudo ./install-all.sh` → **http://127.0.0.1:9477/field**

---

## What it does

AmmoOS is the sovereign field operating system — not a traditional desktop replacement:

1. **Scores** live connections on 10 axes (gatekeeper).
2. **You decide** — Trust forever · Stop this site · KILL when corroborated.
3. **Publishes** everything to loopback panel (`:9477`) — no cloud required.
4. **Reloads** field tech on every reboot (`nexus-boot-impl`).
5. **Mirrors** the incumbent OS — familiar menu, field startbar.
6. **Embeds** field OS inside Queen Browser Start tab.
7. **Freezes** the host OS on demand — sovereign clock witness on resume.

---

## Quick install

```bash
git clone https://github.com/ZacharyGeurts/AmmoOS.git
cd AmmoOS
git checkout v2.0.0-beta3
./scripts/wire-stack.sh
sudo ./install-all.sh
```

Full guide → **[Installers](Installers)** · **[AmmoOS Beta 3](AmmoOS-Beta3)**

---

## Live surfaces

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:9477/field | **Host desktop** — apps + startbar |
| http://127.0.0.1:9477/command | **Field command** — C2 threat panel |
| http://127.0.0.1:9481/world/browser.html | **Queen Browser** — secured shell |
| http://127.0.0.1:9477/underlay-f9 | **Tristate installer** — Underlay F9 |

---

## Stack siblings

Component repos publish **redirect hubs** on GitHub Pages — all link back to AmmoOS code and manual:

| Component | Pages hub | Manual in AmmoOS |
|-----------|-----------|------------------|
| Queen | [Queen](https://zacharygeurts.github.io/Queen/) | [Queen Browser](https://zacharygeurts.github.io/AmmoOS/queen-browser.html) |
| Grok16 | [Grok16](https://zacharygeurts.github.io/Grok16/) | [Combinatronic](https://zacharygeurts.github.io/AmmoOS/combinatronic.html) |
| KILROY | [KILROY](https://zacharygeurts.github.io/KILROY/) | [Architecture](https://zacharygeurts.github.io/AmmoOS/architecture.html) |
| ZNetwork | [ZNetwork](https://zacharygeurts.github.io/ZNetwork/) | [Field I/O](https://zacharygeurts.github.io/AmmoOS/io.html) |

**[→ GitHub: ZacharyGeurts/AmmoOS](https://github.com/ZacharyGeurts/AmmoOS)**