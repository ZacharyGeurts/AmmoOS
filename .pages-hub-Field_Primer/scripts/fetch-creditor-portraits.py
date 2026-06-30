#!/usr/bin/env python3
"""Download creditor portraits via Wikimedia Special:FilePath; generate tributes if needed."""
from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/data/creditors-manifest.json"
OUT = ROOT / "assets/images/v4/creditors"
OUT_DOCS = ROOT / "docs/assets/images/v4/creditors"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

WIKI_FILES = {
    "maxwell": "James_Clerk_Maxwell.jpg",
    "clausius-boltzmann": "Boltzmann2.jpg",
    "landauer": "Rolf_Landauer.jpg",
    "shannon": "Claude_Shannon.jpg",
    "tesla": "N.Tesla.JPG",
    "cfl": "Richard_Courant.jpg",
    "von-neumann": "JohnvonNeumann-LosAlamos.gif",
    "turing": "Alan_Turing_Aged_16.jpg",
}


def load_font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wiki_url(filename: str) -> str:
    enc = urllib.parse.quote(filename.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width=800"


def download(url: str, dest: Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FieldPrimer/4.0 (educational; github.com/ZacharyGeurts/Field_Primer)"})
        with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as resp:
            data = resp.read(8_000_000)
        dest.write_bytes(data)
        im = Image.open(dest).convert("RGB")
        w = 800
        h = min(1000, int(w * im.height / im.width))
        im = im.resize((w, h), Image.Resampling.LANCZOS)
        im.save(dest, "JPEG", quality=92)
        return True
    except Exception as e:
        print(f"skip {url}: {e}")
        return False


def generated_tribute(slug: str, name: str, accent: tuple[int, int, int]) -> Image.Image:
    size = (800, 1000)
    img = Image.new("RGB", size, (8, 14, 28))
    draw = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / size[1]
        draw.line([(0, y), (size[0], y)], fill=(int(8 + 20 * t), int(14 + 30 * t), int(28 + 50 * t)))
    cx, cy = size[0] // 2, size[1] // 2 - 40
    for r in range(320, 80, -40):
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=accent, width=2)
    draw.ellipse((cx - 100, cy - 100, cx + 100, cy + 100), fill=accent)
    draw.ellipse((cx - 70, cy - 70, cx + 70, cy + 70), fill=(240, 208, 96))
    title = load_font(FONT_BOLD, 40)
    sub = load_font(FONT_REG, 20)
    bbox = title.getbbox(name)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy + 150), name, font=title, fill=(232, 242, 255))
    draw.text((cx - 130, cy + 210), "With love · Field Technology v4", font=sub, fill=(138, 164, 200))
    return img


ACCENT_MAP = {"phi": (56, 189, 248), "thermo": (245, 158, 11), "flow": (167, 139, 250), "gold": (240, 208, 96)}


def save_im(im: Image.Image, dest_name: str) -> None:
    for folder in (OUT, OUT_DOCS):
        im.save(folder / dest_name, "JPEG", quality=92)


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for folder in (OUT, OUT_DOCS):
        folder.mkdir(parents=True, exist_ok=True)

    for c in data["creditors"]:
        slug = c["slug"]
        dest_name = f"{slug}.jpg"
        accent = ACCENT_MAP.get(c.get("accent", "phi"), (56, 189, 248))
        ok = False

        if c["portrait_url"] != "generated":
            if slug in WIKI_FILES:
                time.sleep(2.0)
                dest = OUT / dest_name
                for fname in [WIKI_FILES[slug], WIKI_FILES[slug].replace(".jpg", ".png")]:
                    ok = download(wiki_url(fname), dest)
                    if ok:
                        break
                if ok:
                    im = Image.open(dest).convert("RGB")
                    save_im(im, dest_name)
                    print(f"wiki {dest_name}")
            if not ok and c["portrait_url"].startswith("http"):
                time.sleep(1.2)
                dest = OUT / dest_name
                ok = download(c["portrait_url"], dest)
                if ok:
                    im = Image.open(dest).convert("RGB")
                    save_im(im, dest_name)
                    print(f"downloaded {dest_name}")

        if not ok:
            im = generated_tribute(slug, c["name"], accent)
            save_im(im, dest_name)
            print(f"generated {dest_name}")


if __name__ == "__main__":
    main()