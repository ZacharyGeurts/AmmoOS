# G16 Field Linker

Web: [linker.html](https://zacharygeurts.github.io/Grok16/linker.html)

`g16-ld` wraps `forge/g16-linker.py`. BFD backend: `libexec/grok16/g16-ld-bfd`. Doctrine: `data/g16-linker-doctrine.json` — **16 active targets**.

## Pass flow

1. **discern** — OS/arch from argv or host
2. **ironclad** — witness meld
3. **mandate** — silicon hardening flags
4. **dispatch** — bfd / NDK / mach-o / PE backend

## Mandate flags (ELF)

| Link kind | Flags |
|-----------|-------|
| Executable | `-pie -zrelro -znow -znoexecstack` |
| `-shared` | `-zrelro -znow -znoexecstack` (**no -pie** since 1.0) |
| `-r` / `-static` | none |

## Verify

```bash
./scripts/grok16-toolchain.sh verify
pythong forge/g16-linker.py targets
```

Injecting `-pie` on shared-library links corrupts `libgcc_s.so.1` — 1.0 skips it.