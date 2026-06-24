#!/usr/bin/env python3
"""Dark-theme NEXUS tray icon — Amouranth face maxed at taskbar pixel size."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

# Standard Linux taskbar tray sizes (22–32 px). Render each from full-res source.
TRAY_PIXEL_SIZES = (22, 24, 32)

DARK_FILL = (8, 10, 18, 255)
DARK_EDGE = (12, 18, 32, 255)


def _face_source(install: Path) -> Path:
    for rel in (
        "panel/assets/amouranth-twitch-avatar.png",
        "panel/assets/nexus-tray-amouranth.png",
        "panel/assets/nexus-shield.png",
    ):
        p = install / rel
        if p.is_file() and p.stat().st_size > 0:
            return p
    return install / "panel" / "assets" / "amouranth-twitch-avatar.png"


def _face_crop(img: Image.Image) -> Image.Image:
    """Tight square crop biased upward so the face fills the tiny tray slot."""
    rgba = img.convert("RGBA")
    w, h = rgba.size
    side = min(w, h)
    zoom = 0.82
    crop_side = max(8, int(side * zoom))
    left = (w - crop_side) // 2
    top = max(0, (h - crop_side) // 2 - int(h * 0.06))
    if top + crop_side > h:
        top = h - crop_side
    return rgba.crop((left, top, left + crop_side, top + crop_side))


def render_dark_face_icon(face: Image.Image, size: int) -> Image.Image:
    """Tiny dark tray tile — face uses every pixel possible (1 px dark rim)."""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    margin = 1
    face_px = size - 2 * margin
    face_sq = _face_crop(face).resize((face_px, face_px), Image.Resampling.LANCZOS)
    if size <= 32:
        face_sq = face_sq.filter(ImageFilter.UnsharpMask(radius=0.5, percent=140, threshold=1))

    mask = Image.new("L", (face_px, face_px), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, face_px - 1, face_px - 1), fill=255)
    face_sq.putalpha(mask)

    draw = ImageDraw.Draw(canvas)
    draw.ellipse(
        (margin, margin, margin + face_px - 1, margin + face_px - 1),
        fill=DARK_FILL,
        outline=DARK_EDGE,
        width=1,
    )
    canvas.paste(face_sq, (margin, margin), face_sq)
    return canvas


def install_xdg_tray_icons(install: Path, home: Path | None = None) -> None:
    home = home or Path(os.environ.get("HOME", "/home/default"))
    assets = install / "panel" / "assets"
    cache_root = home / ".local/share/icons/hicolor"
    for px in TRAY_PIXEL_SIZES:
        src = assets / f"nexus-tray-amouranth-{px}.png"
        if not src.is_file():
            continue
        dest = cache_root / f"{px}x{px}" / "apps" / "nexus-shield-panel.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(src.read_bytes())
    for px_dir in cache_root.glob("*x*"):
        if px_dir.is_dir():
            subprocess.run(
                ["gtk-update-icon-cache", str(px_dir)],
                capture_output=True,
                timeout=8,
            )


def build_tray_icons(
    install: Path,
    state: Path,
    *,
    force: bool = False,
) -> Path:
    src = _face_source(install)
    icon = state / "nexus-tray.png"
    stamp_file = state / "nexus-tray-icon.stamp"
    tag = (
        f"dark-v3-maxface:{src}:{src.stat().st_mtime_ns}:{src.stat().st_size}"
        if src.is_file()
        else "dark-v3-maxface:missing"
    )
    state.mkdir(parents=True, exist_ok=True)
    assets = install / "panel" / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    if (
        not force
        and icon.is_file()
        and icon.stat().st_size > 0
        and stamp_file.is_file()
        and stamp_file.read_text(encoding="utf-8", errors="replace").strip() == tag
    ):
        return icon

    if not src.is_file():
        raise FileNotFoundError(f"face source missing: {src}")

    face = Image.open(src)
    rendered: dict[int, Image.Image] = {}
    for px in TRAY_PIXEL_SIZES:
        rendered[px] = render_dark_face_icon(face, px)
        rendered[px].save(assets / f"nexus-tray-amouranth-{px}.png", format="PNG")
    for px in (64, 128):
        render_dark_face_icon(face, px).save(
            assets / ("nexus-tray-amouranth.png" if px == 128 else "nexus-tray-amouranth-64.png"),
            format="PNG",
        )

    # Runtime tray file at max taskbar resolution (32 px).
    rendered[max(TRAY_PIXEL_SIZES)].save(icon, format="PNG")
    install_xdg_tray_icons(install)
    stamp_file.write_text(tag + "\n", encoding="utf-8")
    return icon


def main() -> int:
    install = Path(os.environ.get("NEXUS_INSTALL_ROOT", Path(__file__).resolve().parent.parent))
    state = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
    force = os.environ.get("NEXUS_TRAY_ICON_REFRESH", "0") == "1" or "--force" in sys.argv
    try:
        out = build_tray_icons(install, state, force=force)
        print(out)
        return 0
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())