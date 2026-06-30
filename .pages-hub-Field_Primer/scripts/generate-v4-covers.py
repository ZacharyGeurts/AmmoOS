#!/usr/bin/env python3
"""Field Technology v4 OG + social card (v3 cover art, v4 copy)."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OG_SIZE = (1200, 630)
COVER_FRONT = ROOT / "assets/images/v3/field-technology-v3-cover-front.jpg"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def load_font(path: str, size: int):
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
    for k in range(6):
        pts = []
        for i in range(0, w, 10):
            pts.append((i, int(h * 0.35 + math.sin(i / 80 + k) * h * 0.12)))
        draw.line(pts, fill=(167, 139, 250) if k % 2 else (56, 189, 248), width=2)
    return img


def draw_og() -> Image.Image:
    w, h = OG_SIZE
    img = science_bg(OG_SIZE).convert("RGBA")
    panel_w = 620
    overlay = Image.new("RGBA", OG_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x in range(panel_w):
        t = x / panel_w
        draw.line([(x, 0), (x, h)], fill=(8, 14, 28, int(220 - 80 * t)))
    img = Image.alpha_composite(img, overlay)
    if COVER_FRONT.exists():
        cover = cover_crop(Image.open(COVER_FRONT).convert("RGB"), (w - panel_w + 40, h))
        img.paste(cover, (panel_w - 40, 0))
        fade = Image.new("RGBA", OG_SIZE, (0, 0, 0, 0))
        fdraw = ImageDraw.Draw(fade)
        for x in range(panel_w - 40, panel_w + 120):
            t = (x - (panel_w - 40)) / 160
            fdraw.line([(x, 0), (x, h)], fill=(8, 14, 28, int(255 * min(1, t))))
        img = Image.alpha_composite(img, fade)
    draw = ImageDraw.Draw(img)
    m = 48
    draw.text((m, m), "FIELD TECHNOLOGY v4", font=load_font(FONT_BOLD, 42), fill=(240, 208, 96))
    draw.text((m, m + 50), "Textbook of 2026", font=load_font(FONT_REG, 22), fill=(200, 220, 245))
    draw.text((m, m + 84), "18 chapters · Creditors · Us & God", font=load_font(FONT_REG, 17), fill=(167, 180, 210))
    draw.text((m, m + 118), "Reality is 3D · Time is linear", font=load_font(FONT_MATH, 15), fill=(56, 189, 248))
    draw.text((m, m + 142), "Energy can be moved", font=load_font(FONT_MATH, 15), fill=(56, 189, 248))
    draw.text((m, h - m - 28), "zacharygeurts.github.io/Field_Primer", font=load_font(FONT_MATH, 15), fill=(138, 164, 200))
    return img.convert("RGB")


def main() -> None:
    og = draw_og()
    og.save(ROOT / "assets/images/og-image.jpg", "JPEG", quality=92, optimize=True)
    og.save(ROOT / "docs/assets/images/og-image.jpg", "JPEG", quality=92, optimize=True)
    og.save(ROOT / ".github/social-preview.png", "PNG", optimize=True)
    print("v4 og written")


if __name__ == "__main__":
    main()