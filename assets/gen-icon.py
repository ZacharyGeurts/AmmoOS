#!/usr/bin/env python3
"""Generate NEXUS-Shield 256x256 PNG icon (no external deps beyond zlib)."""
import math
import struct
import zlib
from pathlib import Path

W, H = 256, 256
out = Path(__file__).resolve().parent / "nexus-shield.png"


def _chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def _pixel(x: int, y: int) -> tuple[int, int, int, int]:
    cx, cy = W // 2, H // 2 + 6
    dx, dy = x - cx, y - cy
    dist = math.hypot(dx, dy)
    # Rounded shield silhouette
    shield_h = max(0.0, 1.0 - (abs(dx) / 96.0) ** 1.1 - (dy + 20) / 130.0)
    if shield_h <= 0 or dy > 95 or dy < -108:
        return (0, 0, 0, 0)
    edge = 1.0 - min(1.0, max(0.0, (shield_h - 0.92) / 0.08))
    if edge > 0.85:
        return (212, 175, 55, int(255 * min(1.0, (edge - 0.85) / 0.15)))

    t = max(0.0, min(1.0, shield_h))
    r = int(14 + t * 28 + abs(dx) * 0.08)
    g = int(20 + t * 45 + abs(dy) * 0.05)
    b = int(40 + t * 110)
    # Soft blue glow center
    glow = max(0.0, 1.0 - math.hypot(dx * 0.7, dy * 0.9) / 70.0)
    r = min(255, int(r + glow * 30))
    g = min(255, int(g + glow * 50))
    b = min(255, int(b + glow * 80))

    # N chevron
    nx = dx + 0
    if -62 < dy < 38 and -32 < nx < 32:
        stripe = int((dy + 62) / 14) % 2
        lane = int((nx + 32) / 16) % 2
        if stripe == lane:
            return (77, 155, 255, 255)

    # Inner gem
    if math.hypot(dx, dy - 8) < 22:
        return (255, 92, 122, int(200 + 55 * glow))

    return (r, g, b, 255)


raw = bytearray()
for y in range(H):
    raw.append(0)
    for x in range(W):
        r, g, b, a = _pixel(x, y)
        raw.extend((r, g, b, a))

compressed = zlib.compress(bytes(raw), 9)
png = b"\x89PNG\r\n\x1a\n"
png += _chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0))
png += _chunk(b"IDAT", compressed)
png += _chunk(b"IEND", b"")

out.write_bytes(png)
panel_out = out.parent.parent / "panel" / "assets" / "nexus-shield.png"
panel_out.parent.mkdir(parents=True, exist_ok=True)
panel_out.write_bytes(png)
print(f"OK {out} ({len(png)} bytes)")