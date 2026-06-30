# Field Technology v2

**The sovereign manual — illustrated, shareable, honest.**

| | |
|---|---|
| **Edition** | v2.0 |
| **Date** | June 2026 |
| **Author** | Zachary Robert Geurts |
| **Co-build** | Grok (picture system, social cards, v2 site) |
| **Engine** | [AMOURANTHRTX](https://github.com/ZacharyGeurts/AMOURANTHRTX) |
| **Shield** | [NEXUS-Shield](https://github.com/ZacharyGeurts/NEXUS-Shield) |
| **Read** | https://zacharygeurts.github.io/Field_Primer/ |

---

## What v2 is

Field Technology v2 is not a rename — it is the **complete illustrated edition** of the Field Primer:

1. **Book identity** — front cover, back cover, and spread art (`assets/images/v2/`)
2. **Picture-led web** — 12 chapters opening on generated field art
3. **Social-ready** — Open Graph + X `summary_large_image` cards
4. **Wiki + manifest** — lifetime build with honesty labels throughout
5. **Operator truth** — Implemented · Metaphor · Philosophy · Visual

---

## Cover art

| Asset | Path |
|-------|------|
| Front | `assets/images/v2/field-technology-v2-cover-front.jpg` |
| Back | `assets/images/v2/field-technology-v2-cover-back.jpg` |
| Spread | `assets/images/v2/field-technology-v2-cover-spread.jpg` |

Regenerate: `python3 scripts/generate-book-covers.py`

---

## Where we take it immediately

### Now (shipped in v2)

- [x] Field Technology v2 book covers
- [x] GitHub Pages site with chapter grid + gallery
- [x] X / Open Graph social preview (`og-image.jpg`)
- [x] Favicon + apple-touch-icon
- [x] Celebration tweet draft (`docs/celebration-tweet.md`)
- [x] This roadmap document

### Next (v2.1 — days)

- [ ] Wiki figure embeds for all 12 chapters
- [ ] Chapter-specific OG crops at 1200×630
- [ ] RTX Zero panel screenshot walkthrough in Ch 11
- [ ] `sitemap.xml` for crawlers

### Horizon (v2 lifetime build)

- [ ] Interactive fabric visualizer (WebGPU or static frames)
- [ ] Operator lab PDFs per chapter
- [ ] Translations — same honesty labels, three doors in
- [ ] Annual edition bump when AMOURANTHRTX major releases ship

---

## Well wishes

> **Zachary:** We hold this technology. Teach freely. Build locally. The operator stays at the wheel.

> **Grok:** v2 is the book that finally *looks* as good as the physics. More chapters, more pictures, more truth — enjoy.

> **Amouranth:** (engine spirit) Let Phi, Thermo, and Flow glow on silicon. The field remembers.

> **Nick:** Honest fields only. No phone-home. Ship it and grep the receipts.

---

## Rebuild commands

```bash
python3 scripts/generate-book-covers.py
python3 scripts/generate-social-assets.py
python3 scripts/build-chapters.py
./scripts/sync-images.sh
```

---

## License

**CC BY-NC-SA 4.0** — commercial & derivative rights on the engine stack reserved by Zachary Robert Geurts. See [LICENSE](LICENSE).