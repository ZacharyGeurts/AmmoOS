# Queen Browser

**g16 1.0** — Full browser chrome at `http://127.0.0.1:9481/world/browser.html` with field OS inside the Start tab.

---

## Architecture

```
Queen :9481/world/browser.html  (chrome — tabs, nav, drop/rise)
  └─ Start tab iframe → http://127.0.0.1:9477/field  (host desktop)
       └─ launches apps in Queen tabs when embedded
```

Full C2 remains at `http://127.0.0.1:9477/command` — reachable from host desktop pinned apps or Queen nav.

---

## Drop / Rise

Queen shell buttons call the panel underlay surface API:

```bash
curl -s http://127.0.0.1:9477/api/field-underlay-surface | jq .
```

| Control | Effect |
|---------|--------|
| **Drop ⬇** | Field underlay sinks beneath host desktop |
| **Rise ⬆** | Field OS slice rises to foreground |

Handler: `lib/field-underlay-surface.py` · Shell: `Queen/world/queen-browser-shell.js`

---

## Launch

```bash
Queen/scripts/run-queen.sh
```

Defaults: `QUEEN_BROWSER_START` and `QUEEN_BROWSER_HOME` → `/field` on panel `:9477`.

→ **[Host Desktop](Host-Desktop)** · **[Underlay F9 Tristate](Underlay-F9-Tristate)**