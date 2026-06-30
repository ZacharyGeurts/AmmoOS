#!/usr/bin/env python3
"""Generate serious math/science textbook figures — Textbook of 2026."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_ASSETS = ROOT / "assets/images/v3/science"
OUT_DOCS = ROOT / "docs/assets/images/v3/science"
HERO_LEGACY = ROOT / "assets/images/field-primer-hero.jpg"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

BG = (8, 14, 28)
GRID = (40, 60, 100)
TEXT = (220, 232, 248)
MUTED = (120, 145, 180)
PHI_C = (56, 189, 248)
THERMO_C = (245, 158, 11)
FLOW_C = (167, 139, 250)
GOLD = (240, 208, 96)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def heat_color(t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    if t < 0.33:
        u = t / 0.33
        return (int(lerp(20, 30, u)), int(lerp(40, 100, u)), int(lerp(80, 200, u)))
    if t < 0.66:
        u = (t - 0.33) / 0.33
        return (int(lerp(30, 200, u)), int(lerp(100, 180, u)), int(lerp(200, 80, u)))
    u = (t - 0.66) / 0.34
    return (int(lerp(200, 240, u)), int(lerp(180, 200, u)), int(lerp(80, 60, u)))


def draw_grid(draw: ImageDraw.ImageDraw, w: int, h: int, ox: int, oy: int, pw: int, ph: int, step: int = 40) -> None:
    for x in range(ox, ox + pw + 1, step):
        draw.line([(x, oy), (x, oy + ph)], fill=GRID, width=1)
    for y in range(oy, oy + ph + 1, step):
        draw.line([(ox, y), (ox + pw, y)], fill=GRID, width=1)
    draw.rectangle((ox, oy, ox + pw, oy + ph), outline=MUTED, width=2)
    draw.line([(ox, oy + ph), (ox + pw, oy + ph)], fill=TEXT, width=2)
    draw.line([(ox, oy), (ox, oy + ph)], fill=TEXT, width=2)


def scalar_field_panel(size: tuple[int, int], title: str, formula: str) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(img)
    draw.text((48, 36), title, font=font(FONT_BOLD, 36), fill=TEXT)
    draw.text((48, 82), formula, font=font(FONT_MONO, 22), fill=PHI_C)

    ox, oy, pw, ph = 48, 130, w - 220, h - 200
    nx, ny = 120, 80
    for j in range(ny):
        for i in range(nx):
            x = i / nx * 4 * math.pi
            y = j / ny * 3 * math.pi
            val = math.sin(x) * math.cos(y) * 0.5 + math.sin(x * 0.5 + y * 0.7) * 0.3
            t = (val + 1) / 2
            px = ox + int(i / nx * pw)
            py = oy + int(j / ny * ph)
            pw_cell = max(2, pw // nx + 1)
            ph_cell = max(2, ph // ny + 1)
            draw.rectangle((px, py, px + pw_cell, py + ph_cell), fill=heat_color(t))

    draw_grid(draw, w, h, ox, oy, pw, ph)
    draw.text((ox + pw // 2 - 10, oy + ph + 12), "x", font=font(FONT_REG, 18), fill=MUTED)
    draw.text((ox - 28, oy + ph // 2), "y", font=font(FONT_REG, 18), fill=MUTED)

    # colorbar
    cbx = w - 120
    for j in range(ph):
        t = 1 - j / ph
        draw.line([(cbx, oy + j), (cbx + 24, oy + j)], fill=heat_color(t))
    draw.rectangle((cbx, oy, cbx + 24, oy + ph), outline=MUTED)
    draw.text((cbx - 8, oy - 22), "1.0", font=font(FONT_MONO, 14), fill=MUTED)
    draw.text((cbx - 8, oy + ph - 8), "0.0", font=font(FONT_MONO, 14), fill=MUTED)
    draw.text((cbx + 32, oy + ph // 2 - 20), "Φ", font=font(FONT_BOLD, 20), fill=PHI_C)
    return img


def triple_channel_plot(size: tuple[int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(img)
    draw.text((48, 36), "Coupled fabric channels", font=font(FONT_BOLD, 34), fill=TEXT)
    draw.text((48, 78), "Bindings 8 · 9 · 10  |  R32G32B32A32", font=font(FONT_MONO, 18), fill=MUTED)

    panels = [("Φ Phi", PHI_C), ("Thermo", THERMO_C), ("Flow", FLOW_C)]
    pw = (w - 120) // 3 - 16
    ph = h - 180
    ox0, oy = 48, 120
    for idx, (label, color) in enumerate(panels):
        ox = ox0 + idx * (pw + 24)
        draw.rectangle((ox, oy, ox + pw, oy + ph), outline=color, width=2)
        points = []
        for i in range(pw):
            x = i / pw * 6 * math.pi
            y = oy + ph // 2 + math.sin(x + idx) * (ph * 0.32) * math.exp(-0.08 * (i % 80))
            points.append((ox + i, y))
        if len(points) > 1:
            draw.line(points, fill=color, width=3)
        draw.text((ox + 12, oy + 12), label, font=font(FONT_BOLD, 20), fill=color)
    draw.text((48, h - 48), "∂Φ/∂t = D∇²Φ + f(Φ,T,F)   ·   CFL guarded on host", font=font(FONT_MONO, 16), fill=MUTED)
    return img


def textbook_hero(size: tuple[int, int]) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(img)
    # subtle coordinate grid full bleed
    for x in range(0, w, 48):
        draw.line([(x, 0), (x, h)], fill=(16, 26, 44))
    for y in range(0, h, 48):
        draw.line([(0, y), (w, y)], fill=(16, 26, 44))

    # field lines
    for k in range(12):
        pts = []
        phase = k * 0.5
        for i in range(0, w, 8):
            t = i / w
            y = int(h * 0.35 + math.sin(t * 8 + phase) * h * 0.22 + math.sin(t * 3) * h * 0.08)
            pts.append((i, y))
        col = PHI_C if k % 3 == 0 else THERMO_C if k % 3 == 1 else FLOW_C
        draw.line(pts, fill=(*col, 80) if isinstance(col, tuple) else col, width=2)

    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(h):
        t = y / h
        od.line([(0, y), (w, y)], fill=(8, 14, 28, int(40 + 200 * t)))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.text((64, h - 120), "Field Technology · Textbook of 2026", font=font(FONT_MONO_BOLD, 20), fill=GOLD)
    return img


def write_all() -> None:
    for d in (OUT_ASSETS, OUT_DOCS):
        d.mkdir(parents=True, exist_ok=True)

    figures = {
        "textbook-hero.jpg": textbook_hero((1920, 1080)),
        "ch01-scalar-field.jpg": scalar_field_panel((1600, 1000), "Chapter 1 — Scalar field over R²", "Φ(x,y,t) — continuous state at every point"),
        "ch03-energy-transfer.jpg": triple_channel_plot((1600, 900)),
        "fabric-schematic.jpg": triple_channel_plot((1400, 800)),
    }
    for name, im in figures.items():
        for folder in (OUT_ASSETS, OUT_DOCS):
            im.save(folder / name, "JPEG", quality=92, optimize=True)
            print(f"wrote {folder / name}")


if __name__ == "__main__":
    write_all()