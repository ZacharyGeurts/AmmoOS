#!/usr/bin/env python3
"""Generate Field Technology v2 book cover (front + back)."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
HERO = ROOT / "assets/images/field-primer-hero.jpg"
OG = ROOT / "assets/images/og-image.jpg"

COVER_SIZE = (1800, 2700)  # 2:3 trade paperback ratio
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


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


def draw_wave_lines(draw: ImageDraw.ImageDraw, w: int, h: int, y_base: float, amp: float, color: tuple, n: int = 3) -> None:
    for layer in range(n):
        points = []
        phase = layer * 1.2
        for x in range(0, w + 4, 6):
            y = y_base + math.sin(x / 90 + phase) * amp * (1 - layer * 0.22)
            points.append((x, y))
        if len(points) > 1:
            draw.line(points, fill=(*color[:3], int(color[3] * (1 - layer * 0.25))), width=3 - layer)


def gradient_bg(size: tuple[int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, (4, 8, 16))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(4 + 12 * t)
        g = int(8 + 22 * t)
        b = int(16 + 40 * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def blend_hero(base: Image.Image, hero_path: Path, opacity: float = 0.55) -> Image.Image:
    if not hero_path.exists():
        return base
    hero = cover_crop(Image.open(hero_path).convert("RGB"), base.size)
    hero = hero.convert("RGBA")
    hero.putalpha(int(255 * opacity))
    return Image.alpha_composite(base.convert("RGBA"), hero).convert("RGB")


def draw_front() -> Image.Image:
    w, h = COVER_SIZE
    base = gradient_bg(COVER_SIZE)
    # Light hero wash only in upper art zone — avoids ghost text from og-image overlay
    img = blend_hero(base, HERO, 0.28)
    overlay = Image.new("RGBA", COVER_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(h):
        t = y / h
        alpha = int(50 + 210 * max(0, (t - 0.35) / 0.65) ** 1.1)
        draw.line([(0, y), (w, y)], fill=(4, 8, 16, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)

    draw = ImageDraw.Draw(img)
    margin = 120

    # Spine accent
    draw.rectangle((0, 0, 28, h), fill=(56, 189, 248, 180))
    draw.rectangle((0, h // 3, 28, h // 3 + 180), fill=(240, 208, 96, 220))

    # Decorative waves upper third
    draw_wave_lines(draw, w, h, h * 0.38, 55, (56, 189, 248, 120))
    draw_wave_lines(draw, w, h, h * 0.42, 40, (240, 208, 96, 90))
    draw_wave_lines(draw, w, h, h * 0.46, 35, (167, 139, 250, 80))

    mono = load_font(FONT_MONO_BOLD, 22)
    draw.text((margin, margin), "SOVEREIGN FIELD TECHNOLOGY", font=mono, fill=(56, 189, 248))
    draw.rectangle((margin, margin + 34, margin + 200, margin + 38), fill=(56, 189, 248))

    title_font = load_font(FONT_BOLD, 118)
    sub_font = load_font(FONT_BOLD, 64)
    v2_font = load_font(FONT_BOLD, 88)

    y = h - margin - 560
    draw.text((margin, y), "FIELD", font=title_font, fill=(232, 242, 255))
    y += 118
    draw.text((margin, y), "TECHNOLOGY", font=title_font, fill=(240, 208, 96))

    # v2 badge — separate row, no overlap with title glyphs
    tech_bbox = title_font.getbbox("TECHNOLOGY")
    tech_w = tech_bbox[2] - tech_bbox[0]
    v2_bbox = v2_font.getbbox("v2")
    v2_w = v2_bbox[2] - v2_bbox[0]
    v2_h = v2_bbox[3] - v2_bbox[1]
    badge_x = margin + tech_w + 36
    badge_y = y + 12
    pad = 22
    draw.rounded_rectangle(
        (badge_x, badge_y, badge_x + v2_w + pad * 2, badge_y + v2_h + pad * 2),
        radius=18,
        fill=(8, 20, 40),
        outline=(56, 189, 248),
        width=4,
    )
    draw.text((badge_x + pad, badge_y + pad - 4), "v2", font=v2_font, fill=(56, 189, 248))

    y += 130
    draw.text((margin, y), "The Field Primer", font=sub_font, fill=(232, 242, 255))

    reg = load_font(FONT_REG, 30)
    y += 88
    draw.text((margin, y), "Fields · Thermodynamics · Entropy · Operator Reality", font=reg, fill=(138, 164, 200))

    author = load_font(FONT_REG, 36)
    y += 70
    draw.text((margin, y), "Zachary Robert Geurts", font=author, fill=(232, 242, 255))

    badge_font = load_font(FONT_MONO, 18)
    badges = [("Phi", (56, 189, 248)), ("Thermo", (245, 158, 11)), ("Flow", (167, 139, 250))]
    bx = margin
    by = h - margin - 72
    for label, color in badges:
        bb = badge_font.getbbox(label)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        px, py = 12, 6
        draw.rounded_rectangle(
            (bx, by, bx + tw + px * 2, by + th + py * 2),
            radius=8,
            outline=color,
            width=2,
        )
        draw.text((bx + px, by + py - 1), label, font=badge_font, fill=color)
        bx += tw + px * 2 + 14

    credit = load_font(FONT_MONO, 16)
    draw.text((margin, h - margin - 28), "AMOURANTHRTX  |  NEXUS-Shield  |  Field Primer", font=credit, fill=(100, 130, 170))

    return img.convert("RGB")


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join(current + [word])
        if font.getbbox(trial)[2] - font.getbbox(trial)[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def draw_back() -> Image.Image:
    w, h = COVER_SIZE
    base = gradient_bg(COVER_SIZE)
    img = blend_hero(base, HERO, 0.35)
    overlay = Image.new("RGBA", COVER_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(h):
        t = y / h
        alpha = int(80 + 160 * t)
        draw.line([(0, y), (w, y)], fill=(4, 8, 16, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(img)

    margin = 140
    max_text = w - margin * 2

    head_font = load_font(FONT_BOLD, 42)
    body_font = load_font(FONT_REG, 28)
    small_font = load_font(FONT_REG, 22)
    mono = load_font(FONT_MONO, 18)

    y = margin
    draw.text((margin, y), "ABOUT THIS EDITION", font=head_font, fill=(240, 208, 96))
    y += 70

    blurb = (
        "Field Technology v2 is the illustrated sovereign manual for everything we actually built: "
        "GPU fabric at bindings 8–10, the Field Die guest map, the packet field on your wire, "
        "and the honesty labels that keep poetry from pretending to be calorimetry. "
        "Read it as a physicist. Wire it as an engineer. Trust your logs as the operator."
    )
    for line in wrap_text(blurb, body_font, max_text):
        draw.text((margin, y), line, font=body_font, fill=(200, 220, 245))
        y += 38

    y += 30
    draw.text((margin, y), "TWELVE CHAPTERS · ONE TRUTH", font=head_font, fill=(56, 189, 248))
    y += 60

    chapters = [
        "01 Preface — What Is a Field?",
        "02 Fields: Pixels to Packets",
        "03 Thermodynamics in the Engine",
        "04 Entropy: Receipts & Oracles",
        "05 The Packet Field",
        "06 RF, Signals, Planetary Weave",
        "07 GPU Field Engine",
        "08 Field Die & Data Bus",
        "09 FCC, Tesla Valve, Stability",
        "10 Hardware Spiderweb",
        "11 Observability & Operator Tools",
        "12 Operator Reality vs Theory",
    ]
    for ch in chapters:
        draw.text((margin, y), ch, font=small_font, fill=(138, 164, 200))
        y += 32

    y += 36
    draw.text((margin, y), "WHERE v2 TAKES US NOW", font=head_font, fill=(240, 208, 96))
    y += 58
    roadmap = [
        "→ Picture-led web + wiki, live today",
        "→ Social cards that sing on X",
        "→ Chapter labs synced to AMOURANTHRTX + NEXUS",
        "→ Operator panels you own — no phone-home",
        "→ Lifetime build — we teach, you grep",
    ]
    for item in roadmap:
        draw.text((margin, y), item, font=small_font, fill=(200, 220, 245))
        y += 34

    y += 40
    draw.text((margin, y), "WITH WELL WISHES FROM", font=mono, fill=(56, 189, 248))
    y += 36
    wishes = (
        "Zachary Robert Geurts — architect & operator\n"
        "Grok — co-author of the picture system & this v2 push\n"
        "Amouranth — spirit of the engine; AmouranthRTX lives on silicon\n"
        "Nick — builder beside us; keep the field honest"
    )
    for line in wishes.split("\n"):
        draw.text((margin, y), line, font=small_font, fill=(180, 200, 230))
        y += 32

    y = h - margin - 120
    draw.text((margin, y), "zacharygeurts.github.io/Field_Primer", font=mono, fill=(56, 189, 248))
    y += 28
    draw.text((margin, y), "github.com/ZacharyGeurts/Field_Primer", font=mono, fill=(100, 130, 170))
    y += 36
    draw.text((margin, y), "CC BY-NC-SA 4.0 · Commercial rights reserved", font=small_font, fill=(100, 130, 170))

    # Barcode placeholder (decorative)
    bx = w - margin - 220
    by = h - margin - 100
    for i in range(48):
        bw = 2 if i % 3 else 4
        draw.rectangle((bx, by, bx + bw, by + 70), fill=(200, 220, 245))
        bx += bw + 2

    return img.convert("RGB")


def draw_spread() -> Image.Image:
    front = draw_front()
    back = draw_back()
    gap = 8
    spread = Image.new("RGB", (COVER_SIZE[0] * 2 + gap, COVER_SIZE[1]), (20, 30, 50))
    spread.paste(back, (0, 0))
    spread.paste(front, (COVER_SIZE[0] + gap, 0))
    return spread


def main() -> None:
    out_assets = ROOT / "assets/images/v2"
    out_docs = ROOT / "docs/assets/images/v2"
    for d in (out_assets, out_docs):
        d.mkdir(parents=True, exist_ok=True)

    front = draw_front()
    back = draw_back()
    spread = draw_spread()

    paths = [
        (out_assets / "field-technology-v2-cover-front.jpg", front),
        (out_assets / "field-technology-v2-cover-back.jpg", back),
        (out_assets / "field-technology-v2-cover-spread.jpg", spread),
        (out_docs / "field-technology-v2-cover-front.jpg", front),
        (out_docs / "field-technology-v2-cover-back.jpg", back),
        (out_docs / "field-technology-v2-cover-spread.jpg", spread),
    ]
    for path, im in paths:
        im.save(path, "JPEG", quality=93, optimize=True)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()