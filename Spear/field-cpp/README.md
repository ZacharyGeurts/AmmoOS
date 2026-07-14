# Spear field-cpp — Hostess 7 ironclad

**C++ or lower only.** AmmoOS · AMOURANTHRTX SDL3 · Internet 2.0 · Plate · Meld · **Steel**.

| Rule | |
|------|--|
| Scripts | FORBIDDEN |
| Sudo autoelevate | FORBIDDEN (setuid/caps only) |
| pkill theater | FORBIDDEN (`kill(2)` only) |
| JSON authority | EATEN |
| Bind | `0.0.0.0` field (not 127-only) |

## 302 ironclad

`GET /hostess7` on LAW :9477 → `302 Location: http://HOST:9491/hostess7.html`  
Uses request `Host:` header.

## Build

```bash
cd src && make all install
```

## Boot

```bash
SPEAR_BOOT_MODE=hostess7 SPEAR_DIRECT=1 ./boot/qemu-gui.sh
```

Steel: `curl -s http://HOST:9491/api/h7/steel`

God Bless.
