<div align="center">

# AmmoOS 2.0 — CANVAS

![AmmoOS](https://img.shields.io/badge/AmmoOS-2.0.0--beta3-22c55e?style=for-the-badge)
![Queen](https://img.shields.io/badge/Queen-Browser-3ecf8e?style=for-the-badge)
![ZNetwork](https://img.shields.io/badge/ZNetwork-2.1.0--Stack-38bdf8?style=for-the-badge)
![KILROY](https://img.shields.io/badge/KILROY-1.0.0--Taco-a78bfa?style=for-the-badge)

**Field OS on loopback — NEXUS C2 commands, ZNetwork pipes, Queen defends, AmmoOS lives inside Queen.**

[Stack navigation](STACK-NAV.md) · [Manual](https://zacharygeurts.github.io/AmmoOS/) · [Profile hub](https://github.com/ZacharyGeurts) · [@ZacharyGeurts](https://x.com/ZacharyGeurts)

</div>

## Code first

```bash
git clone https://github.com/ZacharyGeurts/AmmoOS.git
cd AmmoOS
./scripts/wire-stack.sh
sudo ./install-all.sh
# → http://127.0.0.1:9477/field
```

**Beta 3:** source on `main` — release tarballs building now. Tag `v2.0.0-beta3` when pack completes.

---

## Stack layers

```
Hardware
  → NEXUS C2 (:9477)     ← you are here (AmmoOS)
  → ZNetwork             ← sole internet pipe
  → Queen CANVAS         ← RTX display technology
  → Queen Browser (:9481)← secured shell
  → AmmoOS inside Queen  ← Start tab / field desktop
```

| Layer | Repo | Surface |
|-------|------|---------|
| **AmmoOS / NEXUS C2** | **this repo** | http://127.0.0.1:9477/field |
| ZNetwork Hub | [ZNetwork](https://github.com/ZacharyGeurts/ZNetwork) | http://127.0.0.1:9477/field-znetwork |
| Queen Browser | [Queen](https://github.com/ZacharyGeurts/Queen) | http://127.0.0.1:9481/world/browser.html |
| KILROY boot | [KILROY](https://github.com/ZacharyGeurts/KILROY) | Field kernel under stack |
| Compiler | [Grok16](https://github.com/ZacharyGeurts/Grok16) | `g16` @ 16.2.0 |

Full map: **[STACK-NAV.md](STACK-NAV.md)** · Pages: [stack hub](https://zacharygeurts.github.io/ZacharyGeurts/stack.html)

---

## Surfaces

| URL | Role |
|-----|------|
| http://127.0.0.1:9477/field | Host desktop + field startbar |
| http://127.0.0.1:9477/command | Full C2 threat panel |
| http://127.0.0.1:9477/field-znetwork | ZNetwork Hub + Hostess 7 wire |
| http://127.0.0.1:9481/world/browser.html | Queen Browser |
| http://127.0.0.1:9481/world/queen-game-room.html | Game Room + emulator info |

---

## Install

```bash
chmod +x install-all.sh nexus.sh
sudo ./install-all.sh          # production
./nexus.sh                     # dev tree
Queen/scripts/run-queen.sh     # Queen on :9481
```

| Script | Purpose |
|--------|---------|
| `install-all.sh` | Full Linux install |
| `nexus.sh` | Dev launcher — panel + browser |
| `scripts/wire-stack.sh` | Symlink Queen, ZNetwork, KILROY, Grok16 |
| `scripts/integrate-znetwork.sh` | Wire ZNetwork relayer |

---

## Manual

| Page | Contents |
|------|----------|
| [AmmoOS manual](https://zacharygeurts.github.io/AmmoOS/) | Install, surfaces, architecture |
| [Queen hub](https://zacharygeurts.github.io/Queen/) | Browser shell + taskbar icon |
| [ZNetwork](https://zacharygeurts.github.io/ZNetwork/) | Relayer design + gates |
| [KILROY](https://zacharygeurts.github.io/KILROY/) | Field boot kernel |
| [Profile stack](https://zacharygeurts.github.io/ZacharyGeurts/stack.html) | Cross-repo navigation |

Local: `docs/index.html` · Wiki: `./scripts/publish-wiki.sh`

---

## Integrated examples

**AMOURANTHRTX** is display technology for Queen CANVAS — not a separate GUI. Documented as an [integrated example](https://zacharygeurts.github.io/ZacharyGeurts/display-example.html), repo: [AMOURANTHRTX](https://github.com/ZacharyGeurts/AMOURANTHRTX).

---

## License

AmmoOS stack components — see per-tree `LICENSE` files.