#!/usr/bin/env pythong
"""Dark-theme NEXUS tray icon — US field (Statue of Liberty) at taskbar pixel size."""
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
ICON_BASENAME = "nexus-tray-us"


def _us_source(install: Path) -> Path:
    for rel in (
        "panel/assets/nexus-tray-us-source.jpg",
        "panel/assets/nexus-tray-us-source.png",
        f"panel/assets/{ICON_BASENAME}.png",
        "panel/assets/nexus-shield.png",
    ):
        p = install / rel
        if p.is_file() and p.stat().st_size > 0:
            return p
    return install / "panel" / "assets" / "nexus-tray-us-source.jpg"


def _us_crop(img: Image.Image) -> Image.Image:
    """Square crop on crown and face — biased upward for the portrait source."""
    rgba = img.convert("RGBA")
    w, h = rgba.size
    side = min(w, h)
    zoom = 0.88
    crop_side = max(8, int(side * zoom))
    left = (w - crop_side) // 2
    top = max(0, int(h * 0.02))
    if top + crop_side > h:
        top = h - crop_side
    return rgba.crop((left, top, left + crop_side, top + crop_side))


def render_dark_us_icon(face: Image.Image, size: int) -> Image.Image:
    """Tiny dark tray tile — statue head fills the slot (1 px dark rim)."""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    margin = 1
    icon_px = size - 2 * margin
    icon_sq = _us_crop(face).resize((icon_px, icon_px), Image.Resampling.LANCZOS)
    if size <= 32:
        icon_sq = icon_sq.filter(ImageFilter.UnsharpMask(radius=0.5, percent=150, threshold=1))

    mask = Image.new("L", (icon_px, icon_px), 0)
    draw_mask = ImageDraw.Draw(mask)
    radius = max(2, icon_px // 6)
    draw_mask.rounded_rectangle((0, 0, icon_px - 1, icon_px - 1), radius=radius, fill=255)
    icon_sq.putalpha(mask)

    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (margin, margin, margin + icon_px - 1, margin + icon_px - 1),
        radius=radius,
        fill=DARK_FILL,
        outline=DARK_EDGE,
        width=1,
    )
    canvas.paste(icon_sq, (margin, margin), icon_sq)
    return canvas


def install_xdg_tray_icons(install: Path, home: Path | None = None) -> None:
    home = home or Path(os.environ.get("HOME", "/home/default"))
    assets = install / "panel" / "assets"
    cache_root = home / ".local/share/icons/hicolor"
    for px in TRAY_PIXEL_SIZES:
        src = assets / f"{ICON_BASENAME}-{px}.png"
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
    src = _us_source(install)
    icon = state / "nexus-tray.png"
    stamp_file = state / "nexus-tray-icon.stamp"
    tag = (
        f"dark-v4-us:{src}:{src.stat().st_mtime_ns}:{src.stat().st_size}"
        if src.is_file()
        else "dark-v4-us:missing"
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
        raise FileNotFoundError(f"US tray source missing: {src}")

    statue = Image.open(src)
    rendered: dict[int, Image.Image] = {}
    for px in TRAY_PIXEL_SIZES:
        rendered[px] = render_dark_us_icon(statue, px)
        rendered[px].save(assets / f"{ICON_BASENAME}-{px}.png", format="PNG")
    for px in (64, 128):
        render_dark_us_icon(statue, px).save(
            assets / (f"{ICON_BASENAME}.png" if px == 128 else f"{ICON_BASENAME}-64.png"),
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