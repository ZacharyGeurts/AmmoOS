#!/usr/bin/env python3
"""Field Technology v3 — textbook 2026 covers and OG (no meme assets)."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCIENCE = ROOT / "assets/images/v3/science/textbook-hero.jpg"
HERO = ROOT / "assets/images/field-primer-hero.jpg"
FABRIC = ROOT / "assets/images/fabric-triple.jpg"

COVER_SIZE = (1800, 2700)
OG_SIZE = (1200, 630)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FONT_MATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

AXIOMS = ("Reality is 3D.", "Time is linear.", "Energy can be moved.")


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def cover_crop(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    resized = img.resize((int(sw * scale), int(sh * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - tw) // 2
    top = (resized.height - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def science_bg(size: tuple[int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, (8, 14, 28))
    draw = ImageDraw.Draw(img)
    for x in range(0, w, 36):
        draw.line([(x, 0), (x, h)], fill=(18, 30, 52))
    for y in range(0, h, 36):
        draw.line([(0, y), (w, y)], fill=(18, 30, 52))
    for k in range(8):
        pts = []
        for i in range(0, w, 10):
            t = i / w
            y = int(h * 0.3 + math.sin(t * 10 + k) * h * 0.15)
            pts.append((i, y))
        draw.line(pts, fill=(56, 189, 248) if k % 2 == 0 else (167, 139, 250), width=2)
    src = SCIENCE if SCIENCE.exists() else HERO
    if src.exists():
        layer = cover_crop(Image.open(src).convert("RGB"), size).convert("RGBA")
        layer.putalpha(90)
        img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return img


def wrap(text: str, fnt: ImageFont.FreeTypeFont, width: int) -> list[str]:
    words, lines, cur = text.split(), [], []
    for word in words:
        trial = " ".join(cur + [word])
        if fnt.getbbox(trial)[2] - fnt.getbbox(trial)[0] <= width:
            cur.append(word)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [word]
    if cur:
        lines.append(" ".join(cur))
    return lines


def draw_front() -> Image.Image:
    w, h = COVER_SIZE
    img = science_bg(COVER_SIZE)
    overlay = Image.new("RGBA", COVER_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(h):
        t = y / h
        draw.line([(0, y), (w, y)], fill=(8, 14, 28, int(50 + 210 * max(0, (t - 0.35) / 0.65))))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(img)
    margin = 120
    draw.rectangle((0, 0, 24, h), fill=(56, 189, 248))

    mono = load_font(FONT_MONO, 20)
    draw.text((margin, margin), "TEXTBOOK OF 2026", font=mono, fill=(56, 189, 248))
    draw.text((margin, margin + 32), "SOVEREIGN FIELD TECHNOLOGY", font=mono, fill=(138, 164, 200))

    ax = load_font(FONT_MATH, 20)
    y = margin + 80
    for axiom in AXIOMS:
        draw.text((margin, y), axiom, font=ax, fill=(240, 208, 96))
        y += 32

    title = load_font(FONT_BOLD, 100)
    y = h - margin - 520
    draw.text((margin, y), "FIELD", font=title, fill=(232, 242, 255))
    y += 100
    draw.text((margin, y), "TECHNOLOGY", font=title, fill=(240, 208, 96))
    v3 = load_font(FONT_BOLD, 80)
    tw = title.getbbox("TECHNOLOGY")[2] - title.getbbox("TECHNOLOGY")[0]
    vx = margin + tw + 28
    draw.rounded_rectangle((vx, y + 6, vx + 120, y + 96), radius=14, outline=(167, 139, 250), width=3)
    draw.text((vx + 22, y + 12), "v3", font=v3, fill=(167, 139, 250))

    sub = load_font(FONT_REG, 30)
    y += 120
    draw.text((margin, y), "Mathematics · Thermodynamics · Operator Science", font=sub, fill=(200, 220, 245))
    y += 48
    draw.text((margin, y), "Zachary Robert Geurts", font=load_font(FONT_REG, 34), fill=(232, 242, 255))

    eq = load_font(FONT_MATH, 18)
    draw.text((margin, h - margin - 56), "∇²Φ  ·  ∂S/∂t  ·  H = −Σ pᵢ log₂ pᵢ", font=eq, fill=(100, 130, 170))
    draw.text((margin, h - margin - 28), "AMOURANTHRTX  |  NEXUS-Shield  |  Field Primer", font=eq, fill=(100, 130, 170))
    return img.convert("RGB")


def draw_back() -> Image.Image:
    w, h = COVER_SIZE
    img = science_bg(COVER_SIZE)
    overlay = Image.new("RGBA", COVER_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(h):
        draw.line([(0, y), (w, y)], fill=(8, 14, 28, int(100 + 150 * y / h)))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(img)
    margin = 140
    max_w = w - margin * 2
    head = load_font(FONT_BOLD, 38)
    body = load_font(FONT_REG, 24)
    small = load_font(FONT_REG, 20)
    mono = load_font(FONT_MATH, 17)
    y = margin

    draw.text((margin, y), "TEXTBOOK OF 2026", font=head, fill=(240, 208, 96))
    y += 56
    for line in wrap(
        "Serious mathematics and science for operators, physicists, and engineers. "
        "Continuous fields on GPU storage images, die-resident state, and local network telemetry — "
        "with honesty labels on every claim.",
        body,
        max_w,
    ):
        draw.text((margin, y), line, font=body, fill=(200, 220, 245))
        y += 32
    y += 20
    draw.text((margin, y), "THREE AXIOMS", font=head, fill=(56, 189, 248))
    y += 48
    for ax in AXIOMS:
        draw.text((margin, y), ax, font=mono, fill=(200, 220, 245))
        y += 30
    y += 20
    draw.text((margin, y), "THE ROCKS", font=head, fill=(245, 158, 11))
    y += 46
    rocks = [
        "Packet field: local sockets + heuristics only",
        "Landauer in-engine: proxy integral, not calorimetry",
        "Planetary RF weave: visual shader layer",
        "Poetic names: labeled Metaphor or Visual",
    ]
    for rock in rocks:
        draw.text((margin, y), f"• {rock}", font=small, fill=(138, 164, 200))
        y += 28
    y += 24
    draw.text((margin, y), "RESEARCHERS WHO PROMPTED US", font=head, fill=(167, 139, 250))
    y += 46
    credits = [
        "Maxwell · Landauer · Shannon · CFL · Boltzmann",
        "Zachary Robert Geurts · Grok (xAI) · Nick",
        "Full: github.com/ZacharyGeurts/Field_Primer",
        "RESEARCH-CREDITS.md",
    ]
    for c in credits:
        draw.text((margin, y), c, font=small, fill=(180, 200, 230))
        y += 26
    y += 12
    draw.text((margin, y), "TWELVE CHAPTERS", font=head, fill=(56, 189, 248))
    y += 44
    for i in range(1, 13):
        draw.text((margin, y), f"{i:02d}  See web edition for full map", font=small, fill=(120, 145, 180))
        y += 22
        if i == 4:
            break
    draw.text((margin, y), "…  zacharygeurts.github.io/Field_Primer", font=mono, fill=(56, 189, 248))
    y = h - margin - 60
    draw.text((margin, y), "CC BY-NC-SA 4.0", font=small, fill=(100, 130, 170))
    return img.convert("RGB")


def draw_og() -> Image.Image:
    w, h = OG_SIZE
    img = science_bg(OG_SIZE)
    overlay = Image.new("RGBA", OG_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(h):
        t = y / h
        draw.line([(0, y), (w, y)], fill=(8, 14, 28, int(60 + 170 * max(0, (t - 0.3) / 0.7))))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(img)
    m = 56
    draw.text((m, m), "FIELD TECHNOLOGY v3", font=load_font(FONT_BOLD, 48), fill=(240, 208, 96))
    draw.text((m, m + 58), "Textbook of 2026 — Math · Science · Operator Truth", font=load_font(FONT_REG, 20), fill=(200, 220, 245))
    draw.text((m, m + 92), "Reality is 3D  ·  Time is linear  ·  Energy can be moved", font=load_font(FONT_MATH, 18), fill=(56, 189, 248))
    draw.text((m, h - m - 32), "zacharygeurts.github.io/Field_Primer", font=load_font(FONT_MONO, 16), fill=(138, 164, 200))
    return img.convert("RGB")


def main() -> None:
    front, back, og = draw_front(), draw_back(), draw_og()
    spread = Image.new("RGB", (COVER_SIZE[0] * 2 + 8, COVER_SIZE[1]), (12, 20, 36))
    spread.paste(back, (0, 0))
    spread.paste(front, (COVER_SIZE[0] + 8, 0))
    for folder in (ROOT / "assets/images/v3", ROOT / "docs/assets/images/v3"):
        folder.mkdir(parents=True, exist_ok=True)
        for name, im in [
            ("field-technology-v3-cover-front.jpg", front),
            ("field-technology-v3-cover-back.jpg", back),
            ("field-technology-v3-cover-spread.jpg", spread),
        ]:
            im.save(folder / name, "JPEG", quality=93, optimize=True)
    og.save(ROOT / "assets/images/og-image.jpg", "JPEG", quality=92, optimize=True)
    og.save(ROOT / "docs/assets/images/og-image.jpg", "JPEG", quality=92, optimize=True)
    og.save(ROOT / ".github/social-preview.png", "PNG", optimize=True)
    # hero for site
    hero = science_bg((1920, 1080))
    hero.save(ROOT / "assets/images/v3/science/textbook-hero.jpg", "JPEG", quality=92, optimize=True)
    hero.save(ROOT / "docs/assets/images/v3/science/textbook-hero.jpg", "JPEG", quality=92, optimize=True)
    print("textbook 2026 covers + og written")


if __name__ == "__main__":
    main()