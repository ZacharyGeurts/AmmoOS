#!/usr/bin/env python3
"""Generate NEXUS Field app icon — web browser window with globe."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets"
SIZES = (16, 22, 24, 32, 48, 64, 128, 256)


def render(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    s = float(size)
    pad = max(1.0, s * 0.08)
    rad = max(1, int(s * 0.05))

    # Rounded tile
    if size >= 32:
        draw.rounded_rectangle((pad, pad, s - pad, s - pad), radius=max(1, int(s * 0.16)), fill=(10, 16, 12, 255))
    else:
        draw.rectangle((pad, pad, s - pad, s - pad), fill=(10, 16, 12, 255))

    # Browser window frame
    wx0, wy0 = s * 0.14, s * 0.16
    wx1, wy1 = s * 0.86, s * 0.88
    if size >= 32:
        draw.rounded_rectangle((wx0, wy0, wx1, wy1), radius=rad, fill=(22, 38, 28, 255), outline=(196, 158, 62, 255), width=max(1, int(s * 0.02)))
    else:
        draw.rectangle((wx0, wy0, wx1, wy1), fill=(22, 38, 28, 255), outline=(196, 158, 62, 255), width=1)

    # Title bar
    ty1 = wy0 + s * 0.11
    draw.rectangle((wx0, wy0, wx1, ty1), fill=(14, 28, 20, 255))
    dot_r = max(1, int(s * 0.018))
    for i, col in enumerate(((220, 80, 70, 255), (230, 190, 60, 255), (70, 190, 90, 255))):
        cx = wx0 + s * (0.08 + i * 0.05)
        cy = wy0 + s * 0.055
        draw.ellipse((cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r), fill=col)

    # Address bar (between title bar bottom and content)
    if size >= 48:
        ax0, ay0 = wx0 + s * 0.06, ty1 + s * 0.015
        ax1, ay1 = wx1 - s * 0.06, ty1 + s * 0.09
        if ay1 - ay0 >= 3 and ax1 - ax0 >= 3:
            draw.rounded_rectangle((ax0, ay0, ax1, ay1), radius=2, fill=(32, 58, 42, 255))
            draw.rectangle((ax0 + s * 0.02, ay0 + s * 0.015, ax0 + s * 0.08, ay1 - s * 0.015), fill=(90, 200, 120, 220))

    # Content area + globe
    cx, cy = s * 0.5, s * 0.58
    globe_r = s * 0.17
    if size >= 24:
        draw.ellipse((cx - globe_r, cy - globe_r, cx + globe_r, cy + globe_r), fill=(28, 72, 52, 255), outline=(196, 158, 62, 255), width=max(1, int(s * 0.015)))
        # Meridians
        draw.arc((cx - globe_r * 0.85, cy - globe_r, cx + globe_r * 0.85, cy + globe_r), 270, 90, fill=(120, 220, 140, 200), width=max(1, int(s * 0.012)))
        draw.arc((cx - globe_r * 0.85, cy - globe_r, cx + globe_r * 0.85, cy + globe_r), 90, 270, fill=(120, 220, 140, 200), width=max(1, int(s * 0.012)))
        draw.line((cx - globe_r, cy, cx + globe_r, cy), fill=(120, 220, 140, 180), width=max(1, int(s * 0.01)))
        draw.ellipse((cx - globe_r, cy - globe_r * 0.35, cx + globe_r, cy + globe_r * 0.35), outline=(120, 220, 140, 160), width=max(1, int(s * 0.01)))

    return img


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    panel_assets = ROOT / "panel" / "assets"
    panel_assets.mkdir(parents=True, exist_ok=True)
    master = render(256)
    master.save(OUT_DIR / "nexus-field.png", optimize=True)
    master.save(panel_assets / "nexus-field.png", optimize=True)
    for sz in SIZES:
        render(sz).save(panel_assets / f"nexus-field-{sz}.png", optimize=True)
    for sz, name in ((64, "nexus-tray-us-64.png"), (32, "nexus-tray-us-32.png"), (24, "nexus-tray-us-24.png"), (22, "nexus-tray-us-22.png")):
        src = panel_assets / f"nexus-field-{sz}.png"
        if src.is_file():
            (panel_assets / name).write_bytes(src.read_bytes())
    print(f"wrote browser icon {OUT_DIR / 'nexus-field.png'}")


if __name__ == "__main__":
    main()