# Picture System

Field Primer is designed **around images** — each chapter opens on generated art paired with expanded smart text.

## Where images live

| Path | Purpose |
|------|---------|
| `assets/images/` | Source of truth (repo root) |
| `docs/assets/images/` | GitHub Pages copy |
| `docs/data/image-manifest.json` | Chapter ↔ image mapping |

## Chapter openers

| Ch | Image |
|----|-------|
| 01 | `chapters/ch01-preface.jpg` |
| 02–03 | `fabric-triple.jpg` |
| 04 | `entropy-chapter.jpg` |
| 05 | `packet-field.jpg` |
| 06 | `chapters/ch06-planetary-weave.jpg` |
| 07 | `chapters/ch07-gpu-engine.jpg` |
| 08 | `field-die.jpg` |
| 09 | `chapters/ch09-tesla-valve.jpg` |
| 10 | `chapters/ch10-spiderweb.jpg` |
| 11 | `chapters/ch11-observability.jpg` |
| 12 | `chapters/ch12-honesty.jpg` |

## Web reading

- **Illustrated chapters:** https://zacharygeurts.github.io/Field_Primer/chapters/01-preface.html
- **Gallery:** https://zacharygeurts.github.io/Field_Primer/gallery.html

## Regenerate pipeline

```bash
# After adding images to assets/images/
./scripts/sync-images.sh
python3 scripts/build-chapters.py
```

## Honesty rule for figures

All generated art is **teaching metaphor** unless labeled **Implemented** in prose. Pair every figure with Chapter 12 labels: Implemented · Metaphor · Philosophy · Visual.