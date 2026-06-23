#!/usr/bin/env python3
"""Generate NEXUS-Shield 256x256 PNG icon (no external deps beyond zlib)."""
import struct
import zlib
from pathlib import Path

W, H = 256, 256
out = Path(__file__).resolve().parent / "nexus-shield.png"


def _chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def _pixel(x: int, y: int) -> tuple[int, int, int, int]:
    cx, cy = W // 2, H // 2
    dx, dy = x - cx, y - cy
    dist = (dx * dx + dy * dy) ** 0.5
    # shield shape
    if dist > 118:
        return (0, 0, 0, 0)
    if dist > 108:
        return (201, 162, 39, 255)  # gold ring
    # gradient core
    t = max(0, min(1, 1 - dist / 108))
    r = int(11 + t * 20)
    g = int(13 + t * 30)
    b = int(18 + t * 80)
    # N chevron
    if abs(dx) < 28 and -70 < dy < 50:
        lane = (dx + 28) // 14
        if (dy + 70) // 20 % 2 == lane % 2:
            return (61, 139, 253, 255)
    # inner hex
    if dist < 42 and abs(dy) < 20:
        return (255, 77, 109, 220)
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
print(f"OK {out} ({len(png)} bytes)")