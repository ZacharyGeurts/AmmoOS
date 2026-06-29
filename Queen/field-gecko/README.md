# Queen Field Gecko

Queen Browser engine backend for AmmoOS — **not** the operator's personal browser profile.

## What this is

- **Queen** is the product name users see everywhere (tabs, Start menu, taskbar).
- **Field Gecko** is the isolated engine profile under `field-gecko/profile/`.
- Legacy binaries may still be named `fieldfox` or `firefox` on disk — the shell is always Queen.

## Launch

```bash
./bin/launch-field-gecko.sh
```

Opens Queen with an isolated profile. Default home/search: DuckDuckGo.

## User guide

Operators migrating from Firefox should open:

`http://127.0.0.1:9481/world/queen-browser-guide.html`

## Bootstrap (optional)

```bash
./scripts/bootstrap-field-gecko.sh --tag FIREFOX_ESR_128_BASE
```

Builds a stripped gecko engine from Mozilla source (MPL 2.0). Queen branding applies in the AmmoOS shell — not in upstream Mozilla artwork.