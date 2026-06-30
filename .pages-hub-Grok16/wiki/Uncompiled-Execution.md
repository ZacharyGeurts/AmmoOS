# Uncompiled Execution

Web: [uncompiled.html](https://zacharygeurts.github.io/Grok16/uncompiled.html)

**Grok16 3.0** — dev runs at normal speed; compile is chamber-organized and **ahead**, not on every click.

## Doctrine

`data/field-exec-uncompiled-doctrine.json`

| Lane | Dev behavior | Speed (speed_demo @ 3s) |
|------|--------------|---------------------------|
| **Python** | True interpreter (`pythong` / CPython / gpy-16) | ~0.72–0.76M ops/s |
| **C / C++** | No line-by-line interpreter — chamber **compile ahead** | ~80–88M ops/s after plane cache |
| **CMake** | Configure + build once; bin reused | ~85.7M ops/s |

## Queen .launch — organized field (default)

1. **Inspect files** — walk chamber, map depth-0 fields, trim excess  
2. **No compile on launch** — interpreter for Python; BSP reuse for native  
3. **Staged plane** — copy from `data/bench/exec-plane/` when sources match (~0 ms)  
4. **Fallback** — Python entry when native plane not staged  
5. **Compile mode** — explicit only (`QUEEN_LAUNCH_COMPILE=1` or Queen Files Compile)  

Module: `Queen/lib/queen-launch-chamber.py`

## Not compiling C/C++

There is no C/C++ REPL. **Chamber organization** presents a bin-like run:

- Reuse staged binary from `data/bench/exec-plane/` (~0.2 ms copy)  
- Or compile once into plane cache (434 ms – 2.7 s first run)  
- Operator uses **Compile mode** only for release-day wave convert  

## Commands

```bash
# Organized field — inspect + run, no compile (default)
python3 Queen/lib/queen-launch-chamber.py run examples/speed-demo/speed-demo.launch

# Field map only
python3 Queen/lib/queen-launch-chamber.py project examples/speed-demo/speed-demo.launch

# Compile mode — singular plane wave-convert
QUEEN_LAUNCH_COMPILE=1 python3 Queen/lib/queen-launch-chamber.py run examples/speed-demo/speed-demo.launch
```

See [Speed Bench](Speed-Bench) for versioned compile + exec numbers.