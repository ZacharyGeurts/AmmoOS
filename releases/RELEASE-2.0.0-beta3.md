# AmmoOS 2.0.0-beta3

**Tag:** `v2.0.0-beta3` · **Repo:** [ZacharyGeurts/AmmoOS](https://github.com/ZacharyGeurts/AmmoOS) · **Lineage:** `NewLatest` canonical

## Status: building now

Source is pushed to `main` — **release tarballs and GitHub Pages manual are not published yet.** We are actively building beta 3 artifacts; watch this repo for `v2.0.0-beta3` assets when the pack pipeline completes.

## What landed in source (beta 3)

- **SG → NewLatest consolidation** — stack siblings absorbed into one canonical tree; `SG/` is `NewLatest` + runtime state only
- **ZNetwork Hub** — NEXUS C2 page at `/field-znetwork` with stack layers, Queen Browser + AmmoOS links, live relayer posture
- **Hostess 7 ↔ ZNetwork** — Super Intelligence wire; local communication profile from [x.com/ZacharyGeurts](https://x.com/ZacharyGeurts); Queen sole egress through ZNetwork relayer
- **Emulator system info** — each Game Room system has device visual + CHIPS catalog stack (`/world/queen-system-info.html`)
- **CHIPS catalog deep links** — `?stack=` platform stack views

## Stack (unchanged doctrine)

Hardware → **NEXUS C2** → **ZNetwork** → Queen CANVAS → **Queen Browser** → **AmmoOS** inside Queen on `127.0.0.1`.

## Surfaces

| URL | Role |
|-----|------|
| http://127.0.0.1:9477/field | NEXUS C2 host desktop |
| http://127.0.0.1:9477/field-znetwork | ZNetwork Hub + Hostess 7 wire |
| http://127.0.0.1:9481/world/browser.html | Queen Browser |
| http://127.0.0.1:9481/world/queen-game-room.html | Game Room |
| http://127.0.0.1:9481/world/queen-system-info.html?system=nes | Emulator info + CHIPS |

## Install (from git — until tarballs ship)

```bash
git clone https://github.com/ZacharyGeurts/AmmoOS.git
cd AmmoOS
git checkout v2.0.0-beta3   # or main
./scripts/wire-stack.sh
sudo ./install-all.sh
```

**Note:** Large stack siblings (Grok16, Final_Eye, …) wire via `scripts/wire-stack.sh` from your local tree or future release bundles.