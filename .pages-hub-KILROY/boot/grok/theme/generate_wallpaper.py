#!/usr/bin/env pythong
"""Generate Grok Field boot wallpaper (24-bit BMP, no deps)."""
from __future__ import annotations

import math
import struct
import sys
from pathlib import Path

W, H = 1280, 720
OUT = Path(__file__).resolve().parent / "grok-field.bmp"


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def rgb(r: int, g: int, b: int) -> tuple[int, int, int]:
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


def field_color(x: int, y: int) -> tuple[int, int, int]:
    nx, ny = x / W, y / H
    # Deep field gradient: navy → teal → violet horizon
    base_r = lerp(8, 32, ny) + lerp(0, 24, math.sin(nx * 4.2) * 0.5 + 0.5)
    base_g = lerp(12, 48, ny) + lerp(0, 40, math.cos(ny * 5.1) * 0.5 + 0.5)
    base_b = lerp(28, 72, 1.0 - ny * 0.6)

    # Phi ring accents (golden ratio spacing)
    cx, cy = W * 0.72, H * 0.38
    dist = math.hypot(x - cx, y - cy)
    ring = math.exp(-((dist % 118) - 59) ** 2 / 900.0) * 0.35
    base_r += 180 * ring
    base_g += 120 * ring
    base_b += 40 * ring

    # Horizontal scan glow
    scan = math.exp(-((y - H * 0.62) ** 2) / (H * 0.08) ** 2) * 0.25
    base_g += 200 * scan
    base_b += 255 * scan

    # Subtle grid (field lattice)
    if (x % 64 < 2 or y % 64 < 2) and ny > 0.15:
        base_r += 12
        base_g += 28
        base_b += 48

    return rgb(int(base_r), int(base_g), int(base_b))


def write_bmp(path: Path) -> None:
    row_size = ((W * 3 + 3) // 4) * 4
    pixel_bytes = row_size * H
    header = struct.pack(
        "<2sIHHI",
        b"BM",
        54 + pixel_bytes,
        0,
        0,
        54,
    )
    dib = struct.pack(
        "<IiiHHIIiiII",
        40,
        W,
        H,
        1,
        24,
        0,
        pixel_bytes,
        2835,
        2835,
        0,
        0,
    )

    rows = []
    for y in range(H - 1, -1, -1):
        row = bytearray()
        for x in range(W):
            r, g, b = field_color(x, y)
            row.extend((b, g, r))
        row.extend(b"\x00" * (row_size - W * 3))
        rows.append(bytes(row))

    path.write_bytes(header + dib + b"".join(rows))
    print(f"[grok-theme] wrote {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    write_bmp(out)