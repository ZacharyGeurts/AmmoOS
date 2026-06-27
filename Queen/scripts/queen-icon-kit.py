#!/usr/bin/env pythong
"""Queen icon kit — all taskbar / tray / desktop icons from local Amouranth branding."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

QUEEN = Path(__file__).resolve().parents[1]
NEXUS = QUEEN.parent
SOURCE = QUEEN / "world" / "assets" / "branding" / "amouranth-gentle.png"
PANEL_ASSETS = NEXUS / "panel" / "assets"
ASSETS = NEXUS / "assets"
BRANDING = QUEEN / "world" / "assets" / "branding"

DESKTOP_SIZES = (16, 22, 24, 32, 48, 64, 128, 256)
TRAY_SIZES = (22, 24, 32)
DARK_FILL = (2, 4, 3, 255)
DARK_EDGE = (26, 77, 50, 255)
EMERALD = (34, 197, 94, 255)
ROSE = (244, 114, 182, 255)


def _crop_face(img: Image.Image) -> Image.Image:
    rgba = img.convert("RGBA")
    w, h = rgba.size
    side = min(w, h)
    crop = max(8, int(side * 0.92))
    left = (w - crop) // 2
    top = max(0, int(h * 0.06))
    if top + crop > h:
        top = h - crop
    return rgba.crop((left, top, left + crop, top + crop))


def render_queen_icon(face: Image.Image, size: int, *, tray: bool = False) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    margin = max(1, size // 14) if tray else max(2, size // 16)
    inner = size - 2 * margin
    icon = _crop_face(face).resize((inner, inner), Image.Resampling.LANCZOS)
    if size <= 32:
        icon = icon.filter(ImageFilter.UnsharpMask(radius=0.6, percent=140, threshold=1))

    mask = Image.new("L", (inner, inner), 0)
    draw_m = ImageDraw.Draw(mask)
    radius = max(2, inner // 5)
    draw_m.rounded_rectangle((0, 0, inner - 1, inner - 1), radius=radius, fill=255)
    icon.putalpha(mask)

    draw = ImageDraw.Draw(canvas)
    bg = DARK_FILL if tray else (8, 16, 12, 255)
    draw.rounded_rectangle(
        (margin, margin, margin + inner - 1, margin + inner - 1),
        radius=radius,
        fill=bg,
        outline=DARK_EDGE,
        width=max(1, size // 32),
    )
    ring = max(1, size // 24)
    draw.rounded_rectangle(
        (margin - ring, margin - ring, margin + inner - 1 + ring, margin + inner - 1 + ring),
        radius=radius + ring,
        outline=EMERALD,
        width=ring,
    )
    if size >= 48 and not tray:
        draw.arc(
            (margin - ring * 2, margin - ring * 2, margin + inner + ring * 2, margin + inner + ring * 2),
            200, 340,
            fill=ROSE,
            width=max(1, ring),
        )
    canvas.paste(icon, (margin, margin), icon)
    return canvas


def _write(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True)


def install_hicolor(home: Path | None = None) -> None:
    home = home or Path(os.environ.get("HOME", "/home/default"))
    cache = home / ".local/share/icons/hicolor"
    for sz in DESKTOP_SIZES:
        src = PANEL_ASSETS / f"nexus-field-{sz}.png"
        if not src.is_file():
            continue
        for name in ("nexus-field.png", "queen-browser.png", "nexus-shield-panel.png"):
            dest = cache / f"{sz}x{sz}" / "apps" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(src.read_bytes())
    for px_dir in cache.glob("*x*"):
        if px_dir.is_dir() and (px_dir / "apps").is_dir():
            subprocess.run(["gtk-update-icon-cache", "-f", str(px_dir)], capture_output=True, timeout=8)


def build_all(*, force: bool = True) -> dict:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Queen branding source missing: {SOURCE}")
    face = Image.open(SOURCE)
    PANEL_ASSETS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    BRANDING.mkdir(parents=True, exist_ok=True)

    out: dict[str, list[str]] = {"desktop": [], "tray": [], "aliases": []}

    master = render_queen_icon(face, 256)
    for dest in (
        ASSETS / "nexus-field.png",
        PANEL_ASSETS / "nexus-field.png",
        PANEL_ASSETS / "nexus-shield.png",
        PANEL_ASSETS / "queen-browser.png",
        BRANDING / "queen-browser-256.png",
    ):
        _write(master, dest)
        out["desktop"].append(str(dest))

    for sz in DESKTOP_SIZES:
        img = render_queen_icon(face, sz)
        p = PANEL_ASSETS / f"nexus-field-{sz}.png"
        _write(img, p)
        out["desktop"].append(str(p))

    for sz in TRAY_SIZES:
        img = render_queen_icon(face, sz, tray=True)
        for base in ("queen-tray", "nexus-tray-us"):
            p = PANEL_ASSETS / f"{base}-{sz}.png"
            _write(img, p)
            out["tray"].append(str(p))
    for sz, names in ((64, ("queen-tray-64.png", "nexus-tray-us-64.png")), (128, ("queen-tray.png", "nexus-tray-us.png"))):
        img = render_queen_icon(face, sz, tray=True)
        for n in names:
            p = PANEL_ASSETS / n
            _write(img, p)
            out["tray"].append(str(p))

    _write(_crop_face(face).resize((38, 38), Image.Resampling.LANCZOS), PANEL_ASSETS / "amouranth-panel-avatar.png")
    _write(_crop_face(face).resize((38, 38), Image.Resampling.LANCZOS), PANEL_ASSETS / "amouranth-twitch-avatar.png")
    _write(render_queen_icon(face, 48), BRANDING / "queen-favicon-48.png")
    _write(render_queen_icon(face, 32, tray=True), SOURCE.parent / "queen-tray-source.png")

    install_hicolor()
    return {"ok": True, "source": str(SOURCE), **out, "count": len(out["desktop"]) + len(out["tray"])}


def main() -> int:
    import json

    try:
        doc = build_all()
        print(json.dumps(doc, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())