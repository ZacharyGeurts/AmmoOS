#!/usr/bin/env pythong
"""Generate Grok theme wallpapers (24-bit BMP, no deps)."""
from __future__ import annotations

import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H = 1280, 720

THEMES = {
    "field": {
        "base": (8, 12, 28),
        "mid": (0, 80, 120),
        "hi": (180, 100, 40),
        "scan": (0, 200, 255),
        "grid": (12, 28, 48),
    },
    "midnight": {
        "base": (0, 0, 0),
        "mid": (20, 20, 30),
        "hi": (60, 60, 80),
        "scan": (50, 200, 200),
        "grid": (30, 30, 40),
    },
    "dawn": {
        "base": (26, 16, 32),
        "mid": (120, 60, 40),
        "hi": (220, 140, 60),
        "scan": (255, 200, 120),
        "grid": (40, 30, 35),
    },
    "mono": {
        "base": (16, 16, 16),
        "mid": (64, 64, 64),
        "hi": (140, 140, 140),
        "scan": (200, 200, 200),
        "grid": (48, 48, 48),
    },
}


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def rgb(r: int, g: int, b: int) -> tuple[int, int, int]:
    return (max(0, min(255, int(r))), max(0, min(255, int(g))), max(0, min(255, int(b))))


def color_at(theme: str, x: int, y: int) -> tuple[int, int, int]:
    t = THEMES[theme]
    br, bg, bb = t["base"]
    mr, mg, mb = t["mid"]
    hr, hg, hb = t["hi"]
    nx, ny = x / W, y / H

    r = lerp(br, hr, ny) + lerp(0, mr, math.sin(nx * 4.2) * 0.5 + 0.5)
    g = lerp(bg, hg, ny * 0.8) + lerp(0, mg, math.cos(ny * 5.1) * 0.5 + 0.5)
    b = lerp(bb, hb, 1.0 - ny * 0.5)

    if theme == "field":
        cx, cy = W * 0.72, H * 0.38
        dist = math.hypot(x - cx, y - cy)
        ring = math.exp(-((dist % 118) - 59) ** 2 / 900.0) * 0.35
        r += 180 * ring
        g += 120 * ring
        b += 40 * ring

    sr, sg, sb = t["scan"]
    scan = math.exp(-((y - H * 0.62) ** 2) / (H * 0.08) ** 2) * 0.22
    r += sr * scan
    g += sg * scan
    b += sb * scan

    gr, gg, gb = t["grid"]
    if (x % 64 < 2 or y % 64 < 2) and ny > 0.12:
        r += gr
        g += gg
        b += gb

    return rgb(r, g, b)


def write_bmp(path: Path, theme: str) -> None:
    row_size = ((W * 3 + 3) // 4) * 4
    pixel_bytes = row_size * H
    header = struct.pack("<2sIHHI", b"BM", 54 + pixel_bytes, 0, 0, 54)
    dib = struct.pack(
        "<IiiHHIIiiII", 40, W, H, 1, 24, 0, pixel_bytes, 2835, 2835, 0, 0,
    )
    rows = []
    for y in range(H - 1, -1, -1):
        row = bytearray()
        for x in range(W):
            r, g, b = color_at(theme, x, y)
            row.extend((b, g, r))
        row.extend(b"\x00" * (row_size - W * 3))
        rows.append(bytes(row))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + dib + b"".join(rows))


def main() -> None:
    for name in THEMES:
        out = ROOT / "themes" / name / "wallpaper.bmp"
        write_bmp(out, name)
        print(f"[grok-theme] {name} -> {out} ({out.stat().st_size} bytes)")
    # Legacy path
    legacy = ROOT / "theme" / "grok-field.bmp"
    write_bmp(legacy, "field")
    print(f"[grok-theme] legacy -> {legacy}")


if __name__ == "__main__":
    main()