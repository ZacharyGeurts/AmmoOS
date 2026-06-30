# Toolkits

Web: [toolkits.html](https://zacharygeurts.github.io/Grok16/toolkits.html)

Grok16 1.0 carries rebuilt toolkits in-tree. Manifest: `data/grok16-toolkits.json`.

## GPY-16 (built-in)

| | |
|---|---|
| Tree | `python/` (GrokVM) |
| Driver | `bin/gpy-16` |
| Discern | `g16 script.py` auto-routes |

## Field binutils

```bash
./scripts/grok16-binutils.sh bootstrap
./scripts/grok16-binutils.sh install
./scripts/grok16-binutils.sh verify
```

Tools: `g16-as`, `g16-ld`, `g16-objdump`, `g16-ar`, `g16-nm`, …

## Languages

```bash
./scripts/grok16-languages.sh install
./scripts/grok16-languages.sh discern
./scripts/grok16-languages.sh hostess-gate
```

Rust/Go/Zig and other drivers use `g16-ld` where applicable.