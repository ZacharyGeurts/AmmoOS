# Redata Pipeline — Lossless Truth to Sovereign Brain

**Field Technology v5 · core technical foundation**

Wiki quick reference — full prose in [Chapter 2](../docs/chapters/02-fields-pixels-packets.html#redata-pipeline) and [read-first gate](../docs/read-first.html).

---

## One sentence

**Redata** keeps every Mayer beat lossless in `seg-*.json`, gates imaging with a truth filter, and packs a verifiable ZAC7 monolith while Hostess 7 stays sovereign over `cache/fieldstorage/brain/sdf/`.

---

## Problem solved

| Surface | Role | Field Technology v5 size |
|---------|------|------------------------|
| PDF | Print / offline | ~8.8 MiB |
| Web | Full reader | ~17.5 MiB |
| Text | Smallest export | ~762 KiB |
| ZAC7 | Sovereign transport + brain | ~1.7 MiB (~19% of PDF) |

Redata prevents any surface from substituting for lossless brain storage.

---

## Three doctrines

| Doctrine | Anchor | Label |
|----------|--------|-------|
| **Lossless always** | `segments/seg-*.json` | Implemented |
| **Imaging is not the codec** | `plates/*.human.pgm` | Metaphor |
| **Truth before plates stick** | `truth_filter.jsonl` | Implemented |

---

## Ownership

- **Hostess 7** — owns `cache/fieldstorage/brain/sdf/`
- **Queen** — orchestrates forge, panel, ZAC restore (does not seize storage)
- **Field Primer** — sibling surfaces (web, PDF); source in `content/chapters/`

**Comfort rule:** Queen is the browser shell; Hostess keeps self data storage.

---

## End-to-end flow

```
content/chapters → Mayer segment → truth filter → redata artifacts → ZAC7 → verify → live brain
```

---

## Live status (refresh with verify commands)

Run:

```bash
./Hostess7.sh sdf-verify-redata
python3 NewLatest/Textbook/build-field-technology-zac.py --verify-only
python3 NewLatest/Queen/lib/queen-hostess-brain.py json
```

---

## Commands

```bash
export SG_ROOT=/path/to/SG
./Hostess7.sh queen-teach-redata
./Hostess7.sh sdf-verify-redata
python3 NewLatest/Queen/lib/queen-hostess-brain.py ingest-textbook
python3 NewLatest/Textbook/build-field-technology-zac.py --verify-only
```

---

## Key paths

| What | Path |
|------|------|
| ZAC monolith | `NewLatest/Textbook/field-technology-v5.zac` |
| Size comparison | `NewLatest/Textbook/size-comparison.json` |
| Live brain | `Hostess7/cache/fieldstorage/brain/sdf/` |
| Office notes | `SG/comments.md` |
| GrokHeavy brief | `Desktop/grokheavy-redata.md` |

---

## Doctrine pin

> Imaging is not the codec. SDF plates = recall topology. Lossless bytes = segment JSON + ZAC. Hostess owns the brain; Queen holds the gates.