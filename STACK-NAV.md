# AmmoOS Stack — navigation hub

**AmmoOS leads.** Everything else in this family exists to boot, pipe, render, or defend the field OS on `127.0.0.1`.

## Stack (bottom → top)

| Layer | Repo | Role | Loopback |
|-------|------|------|----------|
| Hardware | — | witness, no breaks | — |
| **NEXUS C2** | [AmmoOS](https://github.com/ZacharyGeurts/AmmoOS) | command, gates, host desktop | `:9477` |
| **ZNetwork** | [ZNetwork](https://github.com/ZacharyGeurts/ZNetwork) | sole internet pipe, relayer | loopback |
| **Queen CANVAS** | [Queen](https://github.com/ZacharyGeurts/Queen) | RTX display technology (not a GUI) | — |
| **Queen Browser** | [Queen](https://github.com/ZacharyGeurts/Queen) | secured shell, tabs, gates | `:9481` |
| **AmmoOS** | [AmmoOS](https://github.com/ZacharyGeurts/AmmoOS) | field OS **inside** Queen Start tab | `:9477/field` |

Doctrine: `data/field-stack-layer-doctrine.json`

## Start here

```bash
git clone https://github.com/ZacharyGeurts/AmmoOS.git
cd AmmoOS
./scripts/wire-stack.sh    # symlinks Queen, ZNetwork, KILROY, Grok16 siblings
sudo ./install-all.sh
```

| Surface | URL |
|---------|-----|
| Host desktop (C2) | http://127.0.0.1:9477/field |
| Field command | http://127.0.0.1:9477/command |
| ZNetwork Hub | http://127.0.0.1:9477/field-znetwork |
| Queen Browser | http://127.0.0.1:9481/world/browser.html |
| Game Room | http://127.0.0.1:9481/world/queen-game-room.html |

## Repo map

| Repo | Pages | What it is |
|------|-------|------------|
| **[AmmoOS](https://zacharygeurts.github.io/AmmoOS/)** | 📄 [manual](https://zacharygeurts.github.io/AmmoOS/) | **Leader** — field OS, NEXUS C2, install, stack doctrine |
| **[Queen](https://github.com/ZacharyGeurts/Queen)** | 📄 [hub](https://zacharygeurts.github.io/Queen/) | Browser shell + CANVAS renderer; AmmoOS lives inside |
| **[ZNetwork](https://zacharygeurts.github.io/ZNetwork/)** | 📄 [manual](https://zacharygeurts.github.io/ZNetwork/) | Smart relayer — 100% ingress/egress pipe |
| **[KILROY](https://zacharygeurts.github.io/KILROY/)** | 📄 [manual](https://zacharygeurts.github.io/KILROY/) | Field boot kernel (Linux-compatible, not Linux) |
| **[Grok16](https://zacharygeurts.github.io/Grok16/)** | 📄 [manual](https://zacharygeurts.github.io/Grok16/) | Sovereign `g16` compiler — pairs with AmmoOS stack |
| **[Final_Eye](https://zacharygeurts.github.io/Final_Eye/)** | 📄 [textbook](https://zacharygeurts.github.io/Final_Eye/) | Vision stack — ZOCRSM1, GVC1, operator textbook v1.3 |
| **[Final_Ear](https://zacharygeurts.github.io/Final_Ear/)** | 📄 [hub](https://zacharygeurts.github.io/Final_Ear/) | Audio truth filters — `sense=audio` field manual |
| **[Final_Mouth](https://zacharygeurts.github.io/Final_Mouth/)** | 📄 [hub](https://zacharygeurts.github.io/Final_Mouth/) | Speech stack — incorporated in AmmoOS tree |

## Sense trilogy

Eye · Ear · Mouth share Queen earball bridges and panel field-manual routes. Wire with `scripts/wire-stack.sh`.

## Profile hub

- GitHub: [@ZacharyGeurts](https://github.com/ZacharyGeurts)
- Pages: [zacharygeurts.github.io/ZacharyGeurts](https://zacharygeurts.github.io/ZacharyGeurts/)
- Stack diagram: [stack.html](https://zacharygeurts.github.io/ZacharyGeurts/stack.html)

## Integrated examples (not stack leaders)

These ship **inside** NewLatest but are documented separately:

| Example | Repo | Role |
|---------|------|------|
| Display technology | [AMOURANTHRTX](https://github.com/ZacharyGeurts/AMOURANTHRTX) | Queen CANVAS backend — SPIR-V RTX, not operator GUI |
| Compiler GUI | [AmmoCode](https://github.com/ZacharyGeurts/AmmoCode) | Grok16 field IDE |

See [display example page](https://zacharygeurts.github.io/ZacharyGeurts/display-example.html).

## Version line (beta 3)

| Component | Version |
|-----------|---------|
| AmmoOS | `2.0.0-beta3.1` |
| Queen | ships in AmmoOS tree + [Queen](https://github.com/ZacharyGeurts/Queen) hub |
| ZNetwork | `2.1.0` Stack |
| KILROY | `1.0.0-taco` |
| Grok16 | `5.2.0` |

*Navigate by layer — install AmmoOS once, wire siblings with `scripts/wire-stack.sh`.*