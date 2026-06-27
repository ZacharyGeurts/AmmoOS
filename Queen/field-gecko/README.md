# Queen Field Gecko

Queen Browser gecko backend for AmmoOS — **not** the operator's personal Firefox profile.

## Doctrine

- **Queen Webbrowser** (`/world/browser.html`) is the stable tabbed shell.
- **No comp shader boot** — `QUEEN_WEB_SHELL=1`, `QUEEN_SKIP_RTX_BOOT=1`.
- **No OS browser fallback** — `QUEEN_NO_OS_BROWSER=1` uses this launcher only.
- Stripped for AI operators: telemetry off, loopback-first, g16 toolchain path in manifest.

## Ship now (legal, no fork required)

Uses system `firefox` with an **isolated Queen profile** under `field-gecko/profile/`:

```bash
./bin/launch-field-gecko.sh
```

## Build later (MPL 2.0 source path)

```bash
./scripts/bootstrap-field-gecko.sh --tag FIREFOX_ESR_128_BASE
# Configure with g16 when engine tree is wired — see manifest.json
```