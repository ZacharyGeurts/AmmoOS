# Architecture

Web: [architecture.html](https://zacharygeurts.github.io/Grok16/architecture.html)

## Stack (1.0)

```
vendor/gcc (gcc-15, BASE-VER 16.2.0)
    → build/gcc (host + self-host)
    → bin/g16 (unified driver)
    → libexec/grok16/{g16-cc,g16-cxx,g16-ld-bfd}
```

## Forge tools

| Tool | Role |
|------|------|
| `gcc_fetch` | Clone upstream GCC |
| `gcc_configure` | Host configure |
| `gcc_build` | Host build + install |
| `gcc_rebuild` | Self-host with g16 |
| `linker_install` | g16-ld wrapper + BFD backend |

## Unified driver

- `g16` — discern C/C++/Python/ASM + delegate
- `g++16` — symlink to `g16`
- Backends in `libexec/grok16/` (not moved — cc1 paths stay valid)

## Key paths

| Var | Default |
|-----|---------|
| `GROK16_ROOT` | repo root |
| `G16_PREFIX` | install prefix (= root in dev) |
| `GROK16_GCC_SRC` | `vendor/gcc` |
| `GROK16_GCC_BUILD` | `build/gcc` |

Self-host stamp: `SELFHOST.json`