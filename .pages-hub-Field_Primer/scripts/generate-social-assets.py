#!/usr/bin/env python3
"""Generate OG image, GitHub social preview, and favicon for Field Primer."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
HERO = ROOT / "assets/images/field-primer-hero.jpg"
SOCIAL_BASE = (
    Path.home()
    / ".grok/sessions/%2Fhome%2Fdefault%2FDesktop%2FSG"
    / "019ef94c-ca1b-7753-8072-a3a7582b7f87/images/13.jpg"
)

OG_SIZE = (1200, 630)
GH_SIZE = (1280, 640)
FAV_SIZE = (180, 180)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def cover_crop(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    resized = img.resize((int(src_w * scale), int(src_h * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def draw_social_card(size: tuple[int, int]) -> Image.Image:
    base_path = SOCIAL_BASE if SOCIAL_BASE.exists() else HERO
    img = Image.open(base_path).convert("RGB")
    img = cover_crop(img, size)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    w, h = size
    for y in range(h):
        t = y / h
        alpha = int(40 + 180 * max(0, (t - 0.35) / 0.65) ** 1.4)
        draw.line([(0, y), (w, y)], fill=(4, 8, 16, alpha))

    img = Image.alpha_composite(img.convert("RGBA"), overlay)

    draw = ImageDraw.Draw(img)
    title_font = load_font(FONT_BOLD, 72 if w >= 1200 else 64)
    sub_font = load_font(FONT_REG, 28 if w >= 1200 else 24)
    badge_font = load_font(FONT_MONO, 20)
    credit_font = load_font(FONT_REG, 18)

    margin = 56
    y = h - margin

    credit = "zacharygeurts.github.io/Field_Primer"
    draw.text((margin, y - 28), credit, font=credit_font, fill=(138, 164, 200, 255))

    badges = [
        ("Φ Phi", (56, 189, 248)),
        ("Thermo", (245, 158, 11)),
        ("Flow", (167, 139, 250)),
    ]
    bx = margin
    by = y - 88
    for label, color in badges:
        bbox = badge_font.getbbox(label)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad_x, pad_y = 14, 8
        draw.rounded_rectangle(
            (bx, by, bx + tw + pad_x * 2, by + th + pad_y * 2),
            radius=10,
            fill=(*color, 38),
            outline=(*color, 200),
            width=2,
        )
        draw.text((bx + pad_x, by + pad_y - 2), label, font=badge_font, fill=(*color, 255))
        bx += tw + pad_x * 2 + 16

    subtitle = "Fields · Thermodynamics · Entropy · Operator Reality"
    sub_bbox = sub_font.getbbox(subtitle)
    sub_h = sub_bbox[3] - sub_bbox[1]
    y -= 88 + sub_h + 18
    draw.text((margin, y), subtitle, font=sub_font, fill=(232, 242, 255, 230))

    title = "THE FIELD PRIMER"
    title_bbox = title_font.getbbox(title)
    title_h = title_bbox[3] - title_bbox[1]
    y -= title_h + 10
    draw.text((margin, y), title, font=title_font, fill=(240, 208, 96, 255))

    eyebrow = "SOVEREIGN FIELD TECHNOLOGY MANUAL"
    eye_font = load_font(FONT_MONO, 16)
    y -= 30
    draw.text((margin, y), eyebrow, font=eye_font, fill=(56, 189, 248, 220))

    # Accent line
    draw.rectangle((margin, y - 18, margin + 120, y - 14), fill=(56, 189, 248, 255))

    return img.convert("RGB")


def draw_favicon() -> Image.Image:
    img = Image.open(HERO).convert("RGB")
    img = cover_crop(img, FAV_SIZE)
    overlay = Image.new("RGBA", FAV_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(FAV_SIZE[1]):
        t = y / FAV_SIZE[1]
        alpha = int(60 + 140 * t)
        draw.line([(0, y), (FAV_SIZE[0], y)], fill=(4, 8, 16, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(img)
    font = load_font(FONT_BOLD, 52)
    text = "Φ"
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (FAV_SIZE[0] - tw) // 2 - bbox[0]
    y = (FAV_SIZE[1] - th) // 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=(56, 189, 248, 255))
    return img.convert("RGB")


def main() -> None:
    og = draw_social_card(OG_SIZE)
    gh = draw_social_card(GH_SIZE)
    fav = draw_favicon()

    out_dirs = [
        ROOT / "assets/images",
        ROOT / "docs/assets/images",
        ROOT / ".github",
        ROOT / "docs",
    ]
    for d in out_dirs:
        d.mkdir(parents=True, exist_ok=True)

    og_path_assets = ROOT / "assets/images/og-image.jpg"
    og_path_docs = ROOT / "docs/assets/images/og-image.jpg"
    og.save(og_path_assets, "JPEG", quality=92, optimize=True)
    og.save(og_path_docs, "JPEG", quality=92, optimize=True)

    gh_path = ROOT / ".github/social-preview.png"
    gh.save(gh_path, "PNG", optimize=True)

    fav_path = ROOT / "docs/apple-touch-icon.png"
    fav.save(fav_path, "PNG", optimize=True)

    # 32px favicon
    fav32 = fav.resize((32, 32), Image.Resampling.LANCZOS)
    fav32.save(ROOT / "docs/favicon.png", "PNG", optimize=True)

    print(f"wrote {og_path_assets}")
    print(f"wrote {og_path_docs}")
    print(f"wrote {gh_path}")
    print(f"wrote {fav_path}")
    print(f"wrote docs/favicon.png")


if __name__ == "__main__":
    main()