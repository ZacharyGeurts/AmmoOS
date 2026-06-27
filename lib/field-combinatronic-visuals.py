#!/usr/bin/env pythong
"""Combinatronic visuals — precise chip macro renders, Explaining X book covers, H7 manuals."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import random
import re
import sys
import time
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", Path(__file__).resolve().parents[1]))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", INSTALL / ".nexus-state"))
QUEEN = INSTALL / "Queen"
CATALOG = INSTALL / "data" / "field-combinatronic-chip-catalog.json"
SEED = INSTALL / "data" / "field-program-combinatronic-seed.json"
DOCTRINE = INSTALL / "data" / "field-combinatronic-visuals-doctrine.json"
MANIFEST = INSTALL / "data" / "field-combinatronic-visuals-manifest.json"
REGISTRY = INSTALL / "data" / "field-combinatronic-visuals-registry.json"
ASSETS = INSTALL / "data" / "combinatronic-visuals"
CHIPS_DIR = ASSETS / "chips"
BOOKS_DIR = ASSETS / "books"
WORLD_ASSETS = QUEEN / "world" / "assets" / "combinatronic"
LIBRARY_SHELF = INSTALL / "library" / "dewey" / "000-computer-science"
PANEL = STATE / "field-combinatronic-visuals-panel.json"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
H7_MAGICS = (b"H7B\x01", b"H7B\x02")
H7C_MAGICS = (b"H7C\x01", b"H7C\x02")

LANG_LABELS: dict[str, str] = {
    "c": "C",
    "cxx": "C++",
    "python": "Python",
    "rust": "Rust",
    "go": "Go",
    "zig": "Zig",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "java": "Java",
    "sql": "SQL",
    "shell": "Shell",
    "asm": "Assembly",
    "fortran": "Fortran",
    "haskell": "Haskell",
    "lisp": "Lisp",
    "ruby": "Ruby",
    "php": "PHP",
    "lua": "Lua",
    "csharp": "C#",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "cobol": "COBOL",
    "prolog": "Prolog",
    "verilog": "Verilog",
    "ada": "Ada",
    "objc": "Objective-C",
    "d": "D",
    "elixir": "Elixir",
    "erlang": "Erlang",
    "scala": "Scala",
    "perl": "Perl",
    "r": "R",
    "julia": "Julia",
    "ocaml": "OCaml",
    "clojure": "Clojure",
    "matlab": "MATLAB",
    "nim": "Nim",
    "dart": "Dart",
    "field": "Field",
    "ammolang": "AmmoLang",
    "basic": "BASIC",
    "qbasic": "QBasic",
    "quickbasic": "QuickBASIC",
    "freebasic": "FreeBASIC",
    "pascal": "Pascal",
    "turbo_pascal": "Turbo Pascal",
    "delphi": "Delphi",
    "modula2": "Modula-2",
    "smalltalk": "Smalltalk",
    "forth": "Forth",
    "apl": "APL",
    "visual_basic": "Visual Basic",
    "vba": "VBA",
    "algol": "Algol",
    "snobol": "SNOBOL",
    "cobol_copy": "COBOL COPY",
}

LANG_ACCENT: dict[str, tuple[int, int, int]] = {
    "python": (55, 118, 171),
    "rust": (222, 99, 52),
    "go": (0, 173, 216),
    "javascript": (247, 223, 30),
    "typescript": (49, 120, 198),
    "c": (85, 85, 85),
    "cxx": (0, 90, 156),
    "java": (237, 139, 0),
    "ruby": (204, 52, 45),
    "qbasic": (0, 128, 0),
    "pascal": (0, 64, 128),
    "turbo_pascal": (0, 48, 96),
    "basic": (0, 128, 128),
    "ammolang": (96, 32, 128),
}


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _save(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(INSTALL.resolve()))
    except ValueError:
        return str(path)


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _chip_ids() -> list[str]:
    catalog = _load(CATALOG, {})
    return [str(c["id"]) for c in catalog.get("chips") or [] if c.get("id")]


def _lang_ids() -> list[str]:
    seed = _load(SEED, {})
    return sorted((seed.get("language_packs") or {}).keys())


def _expected_file_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for chip_id in _chip_ids():
        rows.append(
            {
                "pattern": "chip_png",
                "chip_id": chip_id,
                "path": _rel(CHIPS_DIR / f"{chip_id}.png"),
                "repair_cmd": f"chip {chip_id}",
            }
        )
        rows.append(
            {
                "pattern": "chip_mirror",
                "chip_id": chip_id,
                "path": _rel(WORLD_ASSETS / "chips" / f"{chip_id}.png"),
                "repair_cmd": "repair mirror",
                "mirror_of": _rel(CHIPS_DIR / f"{chip_id}.png"),
            }
        )
    for lang_id in _lang_ids():
        book_id = f"explaining_{lang_id}"
        rows.append(
            {
                "pattern": "book_cover",
                "lang_id": lang_id,
                "path": _rel(BOOKS_DIR / f"{lang_id}.png"),
                "repair_cmd": f"book {lang_id}",
            }
        )
        rows.append(
            {
                "pattern": "book_mirror",
                "lang_id": lang_id,
                "path": _rel(WORLD_ASSETS / "books" / f"{lang_id}.png"),
                "repair_cmd": "repair mirror",
                "mirror_of": _rel(BOOKS_DIR / f"{lang_id}.png"),
            }
        )
        rows.append(
            {
                "pattern": "h7_manual",
                "lang_id": lang_id,
                "path": _rel(LIBRARY_SHELF / book_id / f"{book_id}.h7c"),
                "repair_cmd": f"book {lang_id}",
            }
        )
        rows.append(
            {
                "pattern": "book_json",
                "lang_id": lang_id,
                "path": _rel(LIBRARY_SHELF / book_id / "book.json"),
                "repair_cmd": f"book {lang_id}",
            }
        )
    rows.extend(
        [
            {"pattern": "manifest", "path": _rel(MANIFEST), "repair_cmd": "generate"},
            {"pattern": "registry", "path": _rel(REGISTRY), "repair_cmd": "registry"},
            {"pattern": "panel", "path": "field-combinatronic-visuals-panel.json", "root": "state", "repair_cmd": "manifest"},
            {"pattern": "chip_catalog", "path": _rel(CATALOG), "role": "source"},
            {"pattern": "program_seed", "path": _rel(SEED), "role": "source"},
            {"pattern": "doctrine", "path": _rel(DOCTRINE), "role": "source"},
            {"pattern": "generator", "path": _rel(Path(__file__)), "role": "source"},
            {"pattern": "h7_packer", "path": "Hostess7/scripts/field_h7_book.py", "role": "source"},
        ]
    )
    return rows


def _resolve_row_path(row: dict[str, Any]) -> Path:
    if row.get("root") == "state":
        return STATE / Path(row["path"]).name
    return INSTALL / row["path"]


def _verify_png(path: Path, *, min_bytes: int = 3000) -> dict[str, Any]:
    if not path.is_file():
        return {"ok": False, "status": "missing"}
    try:
        data = path.read_bytes()
    except OSError as exc:
        return {"ok": False, "status": "unreadable", "error": str(exc)}
    if len(data) < min_bytes:
        return {"ok": False, "status": "truncated", "bytes": len(data)}
    if not data.startswith(PNG_MAGIC):
        return {"ok": False, "status": "bad_magic", "bytes": len(data)}
    return {"ok": True, "status": "ok", "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _h7c_module():
    path = INSTALL / "lib" / "field-h7c-compression.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("field_h7c_compression", path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _verify_h7(path: Path) -> dict[str, Any]:
    """Verify Dewey manual — H7c primary; legacy H7 converts on open."""
    if not path.is_file():
        return {"ok": False, "status": "missing"}
    if path.suffix.lower() == ".h7":
        dewey = _import_mod("field_dewey_vis", "field-dewey-library.py")
        if dewey and hasattr(dewey, "ensure_h7c_path"):
            path = dewey.ensure_h7c_path(path)
    try:
        data = path.read_bytes()
    except OSError as exc:
        return {"ok": False, "status": "unreadable", "error": str(exc)}
    if data[:4] in H7C_MAGICS:
        mod = _h7c_module()
        if not mod:
            return {"ok": False, "status": "no_h7c_module", "bytes": len(data)}
        try:
            header, text, _stats = mod.decompress_h7c(data, verify=True)
        except Exception as exc:
            return {"ok": False, "status": "corrupt", "error": str(exc), "bytes": len(data)}
        return {
            "ok": True,
            "status": "ok",
            "format": "h7c",
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "char_count": header.get("char_count") or len(text),
            "line_count": header.get("line_count"),
            "title": header.get("title"),
        }
    if data[:4] not in H7_MAGICS:
        return {"ok": False, "status": "bad_magic", "bytes": len(data)}
    mod = _h7_module()
    if not mod:
        return {"ok": False, "status": "no_h7_module", "bytes": len(data)}
    try:
        header, text = mod.unpack_h7(data, verify=True)
    except Exception as exc:
        return {"ok": False, "status": "corrupt", "error": str(exc), "bytes": len(data)}
    return {
        "ok": True,
        "status": "ok",
        "format": "h7",
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "char_count": header.get("char_count"),
        "line_count": header.get("line_count"),
        "title": header.get("title"),
    }


def _verify_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"ok": False, "status": "missing"}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "status": "corrupt", "error": str(exc)}
    return {"ok": True, "status": "ok", "bytes": path.stat().st_size, "sha256": _sha256_file(path), "schema": doc.get("schema")}


def _verify_row(row: dict[str, Any]) -> dict[str, Any]:
    path = _resolve_row_path(row)
    pattern = row.get("pattern", "")
    if pattern in ("chip_png", "book_cover", "chip_mirror", "book_mirror"):
        min_b = 8000 if "chip" in pattern else 3000
        check = _verify_png(path, min_bytes=min_b)
    elif pattern == "h7_manual":
        check = _verify_h7(path)
    elif pattern in ("book_json", "manifest", "registry", "chip_catalog", "program_seed", "doctrine"):
        check = _verify_json(path)
    elif pattern == "panel":
        check = _verify_json(path) if path.is_file() else {"ok": False, "status": "missing"}
    elif pattern == "generator":
        check = {"ok": path.is_file(), "status": "ok" if path.is_file() else "missing", "sha256": _sha256_file(path)}
    elif pattern == "h7_packer":
        p = INSTALL / row["path"]
        check = {"ok": p.is_file(), "status": "ok" if p.is_file() else "missing", "sha256": _sha256_file(p)}
    else:
        check = {"ok": path.is_file(), "status": "ok" if path.is_file() else "missing"}
    return {**row, "abs_path": str(path), "verify": check}


def inventory() -> dict[str, Any]:
    rows = [_verify_row(r) for r in _expected_file_rows()]
    required = [r for r in rows if r.get("pattern") != "panel"]
    ok = sum(1 for r in required if r.get("verify", {}).get("ok"))
    broken = [r for r in required if not r.get("verify", {}).get("ok")]
    return {
        "schema": "field-combinatronic-visuals-inventory/v1",
        "generated": _now(),
        "install_root": str(INSTALL),
        "state_dir": str(STATE),
        "total": len(rows),
        "required": len(required),
        "ok": ok,
        "broken": len(broken),
        "complete": len(broken) == 0,
        "rows": rows,
        "broken_rows": broken,
        "doctrine": _rel(DOCTRINE),
    }


def verify_all() -> dict[str, Any]:
    inv = inventory()
    return {
        "schema": "field-combinatronic-visuals-verify/v1",
        "ok": inv["complete"],
        "generated": inv["generated"],
        "total": inv["total"],
        "broken": inv["broken"],
        "broken_paths": [r["path"] for r in inv["broken_rows"]],
    }


def repair_mirror() -> dict[str, Any]:
    fixed: list[str] = []
    errors: list[dict[str, Any]] = []
    for chip_id in _chip_ids():
        src = CHIPS_DIR / f"{chip_id}.png"
        if not src.is_file():
            errors.append({"path": _rel(src), "error": "source_missing"})
            continue
        _mirror_asset(src, "chips")
        fixed.append(_rel(WORLD_ASSETS / "chips" / f"{chip_id}.png"))
    for lang_id in _lang_ids():
        src = BOOKS_DIR / f"{lang_id}.png"
        if not src.is_file():
            errors.append({"path": _rel(src), "error": "source_missing"})
            continue
        _mirror_asset(src, "books")
        fixed.append(_rel(WORLD_ASSETS / "books" / f"{lang_id}.png"))
    return {"ok": not errors, "fixed": fixed, "errors": errors}


def repair_row(row: dict[str, Any]) -> dict[str, Any]:
    pattern = row.get("pattern", "")
    cmd = row.get("repair_cmd", "")
    try:
        if pattern in ("chip_png", "chip_mirror"):
            chip_id = row.get("chip_id")
            if not chip_id:
                return {"ok": False, "error": "no_chip_id"}
            if pattern == "chip_mirror":
                src = CHIPS_DIR / f"{chip_id}.png"
                if not src.is_file():
                    return generate_chip(chip_id)
                return {"ok": True, "mirrored": str(_mirror_asset(src, "chips"))}
            return generate_chip(chip_id)
        if pattern in ("book_cover", "book_mirror", "h7_manual", "book_json"):
            lang_id = row.get("lang_id")
            if not lang_id:
                return {"ok": False, "error": "no_lang_id"}
            if pattern == "book_mirror":
                src = BOOKS_DIR / f"{lang_id}.png"
                if not src.is_file():
                    return generate_book(lang_id)
                return {"ok": True, "mirrored": str(_mirror_asset(src, "books"))}
            return generate_book(lang_id)
        if pattern == "manifest":
            return generate_all()
        if pattern == "registry":
            return build_registry()
        if pattern == "panel":
            return visuals_panel()
        if cmd == "repair mirror":
            return repair_mirror()
    except Exception as exc:
        return {"ok": False, "path": row.get("path"), "error": str(exc)}
    return {"ok": False, "error": "unknown_pattern", "pattern": pattern}


def repair_all(*, only_broken: bool = True) -> dict[str, Any]:
    inv = inventory()
    targets = inv["broken_rows"] if only_broken else inv["rows"]
    results: list[dict[str, Any]] = []
    for row in targets:
        if row.get("role") == "source":
            continue
        results.append({**row, "repair": repair_row(row)})
    after = inventory()
    return {
        "schema": "field-combinatronic-visuals-repair/v1",
        "ok": after["complete"],
        "generated": _now(),
        "attempted": len(results),
        "before_broken": inv["broken"],
        "after_broken": after["broken"],
        "results": results,
        "inventory": after,
    }


def build_registry() -> dict[str, Any]:
    inv = inventory()
    patterns = (_load(DOCTRINE, {}) or {}).get("patterns") or {}
    files = []
    for row in inv["rows"]:
        v = row.get("verify") or {}
        files.append(
            {
                "pattern": row.get("pattern"),
                "path": row.get("path"),
                "chip_id": row.get("chip_id"),
                "lang_id": row.get("lang_id"),
                "status": v.get("status"),
                "bytes": v.get("bytes"),
                "sha256": v.get("sha256"),
                "repair_cmd": row.get("repair_cmd"),
            }
        )
    doc = {
        "schema": "field-combinatronic-visuals-registry/v1",
        "generated": _now(),
        "install_root": str(INSTALL),
        "chip_count": len(_chip_ids()),
        "lang_count": len(_lang_ids()),
        "file_count": len(files),
        "ok_count": inv["ok"],
        "broken_count": inv["broken"],
        "patterns": patterns,
        "sources": (_load(DOCTRINE, {}) or {}).get("sources") or {},
        "repair": (_load(DOCTRINE, {}) or {}).get("repair") or {},
        "files": files,
    }
    _save(REGISTRY, doc)
    reg_check = _verify_json(REGISTRY)
    for entry in doc["files"]:
        if entry.get("pattern") == "registry":
            entry["status"] = reg_check.get("status")
            entry["bytes"] = reg_check.get("bytes")
            entry["sha256"] = reg_check.get("sha256")
    doc["ok_count"] = sum(1 for f in doc["files"] if f.get("status") == "ok")
    doc["broken_count"] = sum(1 for f in doc["files"] if f.get("status") != "ok")
    _save(REGISTRY, doc)
    return doc


def explain_pattern(pattern_id: str) -> dict[str, Any]:
    doctrine = _load(DOCTRINE, {})
    pat = (doctrine.get("patterns") or {}).get(pattern_id)
    if not pat:
        return {"ok": False, "error": "unknown_pattern", "pattern_id": pattern_id, "known": sorted((doctrine.get("patterns") or {}).keys())}
    examples = [r for r in _expected_file_rows() if r.get("pattern") == pattern_id][:5]
    return {
        "ok": True,
        "pattern_id": pattern_id,
        "pattern": pat,
        "examples": examples,
        "doctrine": _rel(DOCTRINE),
    }


def _hex_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 6:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 30, 30, 30


def _font(size: int, *, bold: bool = False):
    from PIL import ImageFont  # noqa: WPS433

    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _felt_texture(w: int, h: int, felt: tuple[int, int, int], felt_dark: tuple[int, int, int], seed: int):
    from PIL import Image  # noqa: WPS433

    rng = random.Random(seed)
    img = Image.new("RGB", (w, h), felt)
    px = img.load()
    for y in range(h):
        for x in range(w):
            n = rng.randint(-18, 18)
            fib = ((x * 7 + y * 13) % 5) - 2
            r = max(0, min(255, felt[0] + n + fib))
            g = max(0, min(255, felt[1] + n + fib))
            b = max(0, min(255, felt[2] + n + fib))
            if (x + y) % 17 == 0:
                r, g, b = felt_dark[0], felt_dark[1], felt_dark[2]
            px[x, y] = (r, g, b)
    return img


def _vignette(img, strength: float = 0.55):
    from PIL import Image, ImageDraw  # noqa: WPS433

    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.ellipse((-w * 0.15, -h * 0.15, w * 1.15, h * 1.15), fill=(0, 0, 0, int(255 * strength)))
    base = img.convert("RGBA")
    return Image.alpha_composite(base, overlay).convert("RGB")


def _draw_dip_pins(draw, cx: int, cy: int, bw: int, bh: int, pins: int, pin_color: tuple[int, int, int]):
    per_side = pins // 2
    pitch_y = bh / (per_side + 1)
    pin_w, pin_h = 5, 14
    for i in range(per_side):
        py = int(cy - bh // 2 + pitch_y * (i + 1))
        draw.rectangle((cx - bw // 2 - pin_w, py - pin_h // 2, cx - bw // 2, py + pin_h // 2), fill=pin_color)
        draw.rectangle((cx + bw // 2, py - pin_h // 2, cx + bw // 2 + pin_w, py + pin_h // 2), fill=pin_color)


def _draw_qfp_pins(draw, cx: int, cy: int, bw: int, bh: int, pins: int, pin_color: tuple[int, int, int]):
    per_side = pins // 4
    pitch_x = bw / (per_side + 1)
    pitch_y = bh / (per_side + 1)
    pin_len = 10
    for i in range(per_side):
        px = int(cx - bw // 2 + pitch_x * (i + 1))
        py_top = cy - bh // 2 - pin_len
        py_bot = cy + bh // 2
        draw.rectangle((px - 2, py_top, px + 2, cy - bh // 2), fill=pin_color)
        draw.rectangle((px - 2, cy + bh // 2, px + 2, py_bot + pin_len), fill=pin_color)
    for i in range(per_side):
        py = int(cy - bh // 2 + pitch_y * (i + 1))
        draw.rectangle((cx - bw // 2 - pin_len, py - 2, cx - bw // 2, py + 2), fill=pin_color)
        draw.rectangle((cx + bw // 2, py - 2, cx + bw // 2 + pin_len, py + 2), fill=pin_color)


def _draw_plcc_pins(draw, cx: int, cy: int, bw: int, bh: int, pins: int, pin_color: tuple[int, int, int]):
    per_side = pins // 4
    pitch_x = bw / (per_side + 1)
    pitch_y = bh / (per_side + 1)
    for i in range(per_side):
        px = int(cx - bw // 2 + pitch_x * (i + 1))
        draw.rectangle((px - 3, cy - bh // 2 - 8, px + 3, cy - bh // 2), fill=pin_color)
        draw.rectangle((px - 3, cy + bh // 2, px + 3, cy + bh // 2 + 8), fill=pin_color)
    for i in range(per_side):
        py = int(cy - bh // 2 + pitch_y * (i + 1))
        draw.rectangle((cx - bw // 2 - 8, py - 3, cx - bw // 2, py + 3), fill=pin_color)
        draw.rectangle((cx + bw // 2, py - 3, cx + bw // 2 + 8, py + 3), fill=pin_color)


def _draw_pga_pins(draw, cx: int, cy: int, bw: int, bh: int, pins: int, pin_color: tuple[int, int, int]):
    cols = max(8, int(pins ** 0.5))
    rows = max(8, pins // cols)
    pad = 6
    gx0, gy0 = cx - bw // 2 + pad, cy - bh // 2 + pad
    gx1, gy1 = cx + bw // 2 - pad, cy + bh // 2 - pad
    step_x = (gx1 - gx0) / max(1, cols - 1)
    step_y = (gy1 - gy0) / max(1, rows - 1)
    drawn = 0
    for row in range(rows):
        for col in range(cols):
            if drawn >= pins:
                return
            px = int(gx0 + col * step_x)
            py = int(gy0 + row * step_y)
            draw.ellipse((px - 2, py - 2, px + 2, py + 2), fill=pin_color)
            drawn += 1


def render_chip_closeup(chip: dict[str, Any], *, out: Path | None = None) -> Path:
    from PIL import Image, ImageDraw  # noqa: WPS433

    catalog = _load(CATALOG, {})
    backdrop = catalog.get("backdrop") or {}
    felt = _hex_rgb(backdrop.get("felt", "#d4899a"))
    felt_dark = _hex_rgb(backdrop.get("felt_dark", "#b86b7f"))
    bg = _hex_rgb(backdrop.get("background", "#080808"))

    chip_id = str(chip.get("id", "chip"))
    w, h = 960, 720
    rng_seed = int(hashlib.md5(chip_id.encode()).hexdigest()[:8], 16)

    img = Image.new("RGB", (w, h), bg)
    felt_w, felt_h = int(w * 0.82), int(h * 0.62)
    fx, fy = (w - felt_w) // 2, (h - felt_h) // 2 + 30
    felt_img = _felt_texture(felt_w, felt_h, felt, felt_dark, rng_seed)
    img.paste(felt_img, (fx, fy))

    draw = ImageDraw.Draw(img)
    cx, cy = w // 2, h // 2 + 10
    package = str(chip.get("package", "dip"))
    pins = int(chip.get("pins", 40))
    body_hex = chip.get("body", "#1a1a1a")
    body = _hex_rgb(str(body_hex))
    pin_color = (192, 192, 200)

    scale = 1.0
    if pins > 200:
        scale = 1.35
    elif pins > 100:
        scale = 1.15
    elif pins <= 16:
        scale = 0.75
    bw = int(220 * scale)
    bh = int(180 * scale) if package == "dip" else int(200 * scale)

    if package == "dip":
        _draw_dip_pins(draw, cx, cy, bw, bh, pins, pin_color)
    elif package == "qfp":
        _draw_qfp_pins(draw, cx, cy, bw, bh, pins, pin_color)
    elif package == "plcc":
        _draw_plcc_pins(draw, cx, cy, bw, bh, pins, pin_color)
    else:
        _draw_pga_pins(draw, cx, cy, bw + 40, bh + 40, pins, pin_color)

    draw.rounded_rectangle((cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2), radius=8, fill=body, outline=(60, 60, 68), width=2)

    notch_x = cx - bw // 2 + 12
    draw.polygon(
        [(notch_x, cy - bh // 2), (notch_x + 18, cy - bh // 2 + 10), (notch_x, cy - bh // 2 + 20)],
        fill=(bg[0], bg[1], bg[2]),
    )

    imprint = chip.get("imprint") or [chip.get("label", chip_id)]
    line_font = _font(max(11, int(14 * scale)))
    y0 = cy - (len(imprint) * 16) // 2
    for i, line in enumerate(imprint):
        tw = draw.textlength(str(line), font=line_font)
        draw.text((cx - tw / 2, y0 + i * 18), str(line), fill=(210, 210, 218), font=line_font)

    badge = f"{pins} PINS"
    socket = chip.get("socket", "")
    badge_font = _font(18, bold=True)
    pin_font = _font(14)
    draw.text((24, 24), chip.get("label", chip_id), fill=(230, 230, 235), font=_font(22, bold=True))
    draw.text((24, 52), badge, fill=(94, 234, 212), font=badge_font)
    if socket:
        draw.text((24, 76), str(socket), fill=(180, 190, 200), font=pin_font)
    draw.text((24, h - 36), f"macro · pink felt · {package.upper()}", fill=(120, 130, 140), font=pin_font)

    img = _vignette(img, 0.42)
    out = out or CHIPS_DIR / f"{chip_id}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return out


def render_book_cover(lang_id: str, *, label: str | None = None, command_count: int = 0, out: Path | None = None) -> Path:
    from PIL import Image, ImageDraw  # noqa: WPS433

    title_label = label or LANG_LABELS.get(lang_id, lang_id.replace("_", " ").title())
    accent = LANG_ACCENT.get(lang_id, (94, 234, 212))
    w, h = 400, 600

    img = Image.new("RGB", (w, h), (12, 14, 18))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, w, 8), fill=accent)
    draw.rectangle((0, h - 48, w, h), fill=(20, 24, 30))

    title_font = _font(28, bold=True)
    sub_font = _font(16)
    small_font = _font(12)

    draw.text((28, 80), "Explaining", fill=(200, 205, 215), font=_font(20))
    draw.text((28, 108), title_label, fill=accent, font=title_font)
    draw.text((28, 160), "Hostess 7 · H7 Manual", fill=(140, 150, 165), font=sub_font)
    draw.text((28, 190), f"{command_count} commands · g16 combinatronic", fill=(110, 120, 135), font=small_font)

    draw.rectangle((28, 240, w - 28, 420), outline=accent, width=2)
    lines = [
        "Distilled from the language reference",
        "Boiled to canonical ops",
        "What · Why · How · Pitfalls",
        "Field program combinatronic facet",
    ]
    y = 260
    for line in lines:
        draw.text((44, y), line, fill=(175, 180, 190), font=small_font)
        y += 28

    draw.text((28, h - 36), "NEXUS-Shield · Dewey 000", fill=(90, 100, 115), font=small_font)

    out = out or BOOKS_DIR / f"{lang_id}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return out


def _resolve_language_pack(seed: dict[str, Any], lang_id: str) -> dict[str, Any]:
    packs = seed.get("language_packs") or {}
    pack = dict(packs.get(lang_id) or {})
    if pack.get("extends"):
        base = dict(packs.get(pack["extends"]) or {})
        merged_cmds = dict(base.get("commands") or {})
        merged_cmds.update(pack.get("commands") or {})
        pack["commands"] = merged_cmds
    return pack


def _canonical_labels(seed: dict[str, Any]) -> dict[str, str]:
    return {op["id"]: op.get("label", op["id"]) for op in seed.get("canonical_ops") or []}


_LANG_PROFILE_ALIASES = {
    "cxx": "cpp",
    "asm": "assembly",
    "ammolang": "ammoasm",
    "visual_basic": "vb",
    "qbasic": "basic",
    "quickbasic": "basic",
    "freebasic": "basic",
    "turbo_pascal": "pascal",
    "delphi": "pascal",
    "modula2": "pascal",
    "objc": "objc",
    "csharp": "csharp",
    "cobol_copy": "cobol",
}


def _lang_profile(lang_id: str) -> dict[str, Any]:
    """Best-effort language metadata from Hostess7 langs catalog."""
    for base in (INSTALL / "Hostess7" / "scripts", INSTALL.parent / "Hostess7" / "scripts"):
        path = base / "field_langs_data.py"
        if not path.is_file():
            continue
        try:
            spec = importlib.util.spec_from_file_location("field_langs_data_v", path)
            if not spec or not spec.loader:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            lookup = _LANG_PROFILE_ALIASES.get(lang_id, lang_id)
            for entry in getattr(mod, "LANG_ENTRIES", ()) or ():
                eid = str(entry.get("id") or "").lower()
                tags = tuple(str(t).lower() for t in (entry.get("tags") or ()))
                if eid == lookup or lang_id in tags or lookup in tags:
                    return dict(entry)
        except Exception:
            pass
    return {}


def render_syntax_diagram(
    lang_id: str,
    *,
    label: str | None = None,
    commands: dict[str, str] | None = None,
    out: Path | None = None,
) -> Path:
    from PIL import Image, ImageDraw  # noqa: WPS433

    title_label = label or LANG_LABELS.get(lang_id, lang_id.replace("_", " ").title())
    accent = LANG_ACCENT.get(lang_id, (94, 234, 212))
    w, h = 720, 420
    img = Image.new("RGB", (w, h), (14, 16, 22))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, w, 44), fill=accent)
    draw.text((16, 10), f"{title_label} — syntax surface", fill=(12, 14, 18), font=_font(18, bold=True))
    sample = sorted((commands or {}).keys(), key=str.lower)[:14]
    y = 64
    for cmd in sample:
        canon = (commands or {}).get(cmd, "?")
        draw.text((24, y), f"{cmd}", fill=accent, font=_font(14, bold=True))
        draw.text((200, y), f"→ {canon}", fill=(190, 195, 205), font=_font(13))
        y += 24
    if not sample:
        draw.text((24, 80), "No commands in seed pack.", fill=(140, 150, 165), font=_font(14))
    draw.text((16, h - 28), "Hostess 7 · H7c embedded figure · syntax", fill=(100, 110, 125), font=_font(11))
    out = out or BOOKS_DIR / f"{lang_id}_syntax.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return out


def render_op_map_diagram(
    lang_id: str,
    *,
    label: str | None = None,
    commands: dict[str, str] | None = None,
    seed: dict[str, Any] | None = None,
    out: Path | None = None,
) -> Path:
    from PIL import Image, ImageDraw  # noqa: WPS433

    title_label = label or LANG_LABELS.get(lang_id, lang_id.replace("_", " ").title())
    accent = LANG_ACCENT.get(lang_id, (94, 234, 212))
    used: dict[str, int] = {}
    for canon in (commands or {}).values():
        used[str(canon)] = used.get(str(canon), 0) + 1
    w, h = 720, 480
    img = Image.new("RGB", (w, h), (14, 16, 22))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, w, 44), fill=accent)
    draw.text((16, 10), f"{title_label} — canonical op map", fill=(12, 14, 18), font=_font(18, bold=True))
    cols, rows = 4, 9
    cell_w, cell_h = (w - 32) // cols, 44
    ops = seed.get("canonical_ops") if seed else []
    op_ids = [str(op.get("id")) for op in ops]
    for i, op_id in enumerate(op_ids[: cols * rows]):
        col, row = i % cols, i // cols
        x0 = 16 + col * cell_w
        y0 = 56 + row * cell_h
        count = used.get(op_id, 0)
        fill = (32, 48, 42) if count else (28, 30, 38)
        draw.rectangle((x0 + 2, y0 + 2, x0 + cell_w - 4, y0 + cell_h - 6), fill=fill, outline=accent if count else (50, 55, 65))
        draw.text((x0 + 8, y0 + 8), op_id[:10], fill=(220, 225, 235) if count else (120, 125, 135), font=_font(11, bold=True))
        if count:
            draw.text((x0 + 8, y0 + 24), f"{count} cmd", fill=accent, font=_font(10))
    draw.text((16, h - 28), "36 canonical atoms · shaded = used by this language", fill=(100, 110, 125), font=_font(11))
    out = out or BOOKS_DIR / f"{lang_id}_opmap.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    return out


def write_explaining_manual(lang_id: str, *, seed: dict[str, Any] | None = None) -> str:
    seed = seed or _load(SEED, {})
    pack = _resolve_language_pack(seed, lang_id)
    cmds: dict[str, str] = pack.get("commands") or {}
    canon = _canonical_labels(seed)
    label = LANG_LABELS.get(lang_id, lang_id.replace("_", " ").title())
    profile = _lang_profile(lang_id)
    by_canon: dict[str, list[str]] = {}
    for cmd, cop in cmds.items():
        by_canon.setdefault(str(cop), []).append(cmd)

    lines = [
        f"# Explaining {label}",
        "",
        "![Cover — Explaining " + label + "](h7fig:cover)",
        "",
        f"Hostess 7 programming language manual — complete reference distilled from the",
        f"{label} combinatronic pack and boiled to the g16 program facet (36 canonical ops).",
        "",
        f"- **Language id:** `{lang_id}`",
        f"- **Command entries:** {len(cmds)}",
        f"- **Canonical ops used:** {len(by_canon)}",
        f"- **Generated:** {_now()}",
        f"- **Format:** H7c v3 with embedded figures",
        "",
        "## At a glance",
        "",
    ]
    if profile:
        lines.extend([
            f"- **Paradigm:** {profile.get('paradigm', '—')}",
            f"- **Typing:** {profile.get('typing', '—')}",
            f"- **Memory:** {profile.get('memory', '—')}",
            f"- **Year originated:** {profile.get('year', '—')}",
            "",
            str(profile.get("body") or ""),
            "",
        ])
    else:
        lines.extend([
            f"{label} is catalogued in the Field program combinatronic seed.",
            "Profile metadata fills in when Hostess7 langs corpus matches this id.",
            "",
        ])

    lines.extend([
        "![Syntax overview](h7fig:syntax)",
        "",
        "![Canonical op map](h7fig:op_map)",
        "",
        "## Introduction",
        "",
        f"This manual explains every seeded {label} construct: surface syntax, semantic role,",
        "canonical combinatronic op, belt runner, and NEXUS-Shield integration paths.",
        "Use the GUI reader (`/field-lang-manuals`) or text mode (`field-lang-manual-reader.py text`).",
        "",
        "## Reading guide",
        "",
        "1. **At a glance** — paradigm, typing, memory model.",
        "2. **Canonical atoms** — the 36 ops all languages boil to.",
        "3. **Commands by op** — every keyword grouped by canonical target.",
        "4. **Full command index** — alphabetical reference.",
        "5. **G16 & NEXUS** — compile, belt, API, pitfalls.",
        "",
        "## Canonical combinatronic atoms",
        "",
    ])
    for op in seed.get("canonical_ops") or []:
        used = len(by_canon.get(str(op.get("id")), []))
        mark = "✓" if used else "·"
        lines.append(
            f"- {mark} **{op['id']}** — {op.get('label', '')} "
            f"(runner: {op.get('runner', 'native_bsp')}, belt: {op.get('belt', 'belt_2_0')})"
        )
    lines.extend(["", f"## {label} commands by canonical op", ""])
    for cop in sorted(by_canon.keys()):
        desc = canon.get(cop, cop)
        lines.extend([f"### `{cop}` — {desc}", ""])
        for cmd in sorted(by_canon[cop], key=str.lower):
            lines.append(f"- `{cmd}`")
        lines.append("")

    lines.extend([f"## {label} full command reference", ""])
    for cmd in sorted(cmds.keys(), key=lambda s: (cmds[s], s.lower())):
        canonical = cmds[cmd]
        desc = canon.get(canonical, canonical)
        lines.extend([
            f"### `{cmd}`",
            f"- **Boils to:** `{canonical}` — {desc}",
            f"- **Runner:** from canonical op belt map",
            f"- **Verify:** `field-program-combinatronic.py boil {lang_id} \"{cmd}\"`",
            "",
        ])

    lines.extend([
        "## G16 compile path",
        "",
        f"- **Boil:** `field-program-combinatronic.py boil {lang_id}`",
        "- **Universal facet:** `field-g16-universal-combinatronic.json`",
        "- **Grok16 compile:** `g16-compile-combinatronics.py` with program facet profile",
        "- **Belt runners:** native_bsp (belt_2_0) and python (belt_1_0) per canonical op",
        "",
        "## Code patterns",
        "",
        f"Representative {label} patterns map to canonical ops as follows:",
        "",
        "- **Declaration + assign** → declare, assign",
        "- **Conditional** → branch",
        "- **Iteration** → loop, break, continue",
        "- **Procedure call** → call, return",
        "- **Module boundary** → import, export, module",
        "- **I/O** → io",
        "- **Error handling** → throw, catch",
        "",
        "## Pitfalls",
        "",
        f"- Case sensitivity varies — {label} keywords may not match heuristic boil.",
        "- Extended packs inherit parent commands; check `extends` in the seed.",
        "- Unknown tokens fall through to heuristic_keywords before defaulting to exec.",
        "- CDN and macro expansion are advisory until combinatronic rebalance runs.",
        "",
        "## Where in NEXUS-Shield",
        "",
        "- Seed: `data/field-program-combinatronic-seed.json`",
        "- Battery: `field-program-combinatronic.json` (STATE)",
        "- Manual: `library/dewey/000-computer-science/explaining_" + lang_id + "/`",
        "- Reader API: `/api/lang-manuals` · `/api/lang-manuals/" + lang_id + "`",
        "- H7c figures: cover, syntax, op_map (embedded lossless)",
        "",
    ])
    if pack.get("extends"):
        lines.extend([f"- **Extends pack:** `{pack['extends']}`", ""])
    return "\n".join(lines) + "\n"


def _h7_module():
    for base in (INSTALL / "Hostess7" / "scripts", INSTALL.parent / "Hostess7" / "scripts"):
        path = base / "field_h7_book.py"
        if path.is_file():
            spec = importlib.util.spec_from_file_location("field_h7_book", path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod
    return None


def pack_explaining_h7(lang_id: str, text: str) -> Path:
    h7c_mod = _h7c_module()
    if not h7c_mod:
        raise RuntimeError("field-h7c-compression.py missing")
    label = LANG_LABELS.get(lang_id, lang_id.replace("_", " ").title())
    book_id = f"explaining_{lang_id}"
    dest = LIBRARY_SHELF / book_id
    dest.mkdir(parents=True, exist_ok=True)
    h7c_path = dest / f"{book_id}.h7c"
    meta = {
        "id": book_id,
        "title": f"Explaining {label}",
        "author": "Hostess 7",
        "license": "Field",
        "subject": "programming languages",
        "category": "computer science",
        "dewey": "000",
        "combinatronic_lang": lang_id,
        "uploaded": _now(),
        "reader": "NEXUS_H7C",
    }
    figures_dir = dest / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    cover_path = BOOKS_DIR / f"{lang_id}.png"
    syntax_path = render_syntax_diagram(lang_id, label=label, commands=_resolve_language_pack(_load(SEED, {}), lang_id).get("commands") or {})
    opmap_path = render_op_map_diagram(
        lang_id,
        label=label,
        commands=_resolve_language_pack(_load(SEED, {}), lang_id).get("commands") or {},
        seed=_load(SEED, {}),
    )
    figures = {
        "cover": {"path": cover_path if cover_path.is_file() else syntax_path, "alt": f"Explaining {label} cover", "mime": "image/png"},
        "syntax": {"path": syntax_path, "alt": f"{label} syntax overview", "mime": "image/png"},
        "op_map": {"path": opmap_path, "alt": f"{label} canonical op map", "mime": "image/png"},
    }
    packed = h7c_mod.pack_h7c(text, meta, use_optimizer=True, format_version=3, figures=figures)
    h7c_path.write_bytes(packed)
    ein = "H7C-FIELD-" + hashlib.sha256(text.encode()).hexdigest()[:12]
    book_json = {
        "id": book_id,
        "title": f"Explaining {label}",
        "author": "Hostess 7",
        "dewey": "000",
        "dewey_label": "Computer science, information & general works",
        "ein": ein,
        "format": "h7c",
        "format_version": 3,
        "embedded_figures": ["cover", "syntax", "op_map"],
        "manual_reader": "/field-lang-manuals",
        "h7c": _rel(h7c_path),
        "h7": None,
        "field_path": _rel(h7c_path),
        "github_shelf": "000-computer-science",
        "combinatronic_lang": lang_id,
        "cover": f"/world/assets/combinatronic/books/{lang_id}.png",
        "updated": _now(),
    }
    (dest / "book.json").write_text(json.dumps(book_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return h7c_path


def _mirror_asset(src: Path, sub: str) -> Path:
    dest = WORLD_ASSETS / sub / src.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    return dest


def generate_chip(chip_id: str) -> dict[str, Any]:
    catalog = _load(CATALOG, {})
    chip = next((c for c in catalog.get("chips") or [] if c.get("id") == chip_id), None)
    if not chip:
        return {"ok": False, "error": "chip_not_in_catalog", "chip_id": chip_id}
    png = render_chip_closeup(chip)
    mirrored = _mirror_asset(png, "chips")
    return {
        "ok": True,
        "chip_id": chip_id,
        "path": str(png),
        "world_url": f"/world/assets/combinatronic/chips/{chip_id}.png",
        "mirrored": str(mirrored),
        "pins": chip.get("pins"),
        "package": chip.get("package"),
    }


def generate_book(lang_id: str) -> dict[str, Any]:
    seed = _load(SEED, {})
    packs = seed.get("language_packs") or {}
    if lang_id not in packs:
        return {"ok": False, "error": "language_not_in_seed", "lang_id": lang_id}
    pack = _resolve_language_pack(seed, lang_id)
    cmds = pack.get("commands") or {}
    label = LANG_LABELS.get(lang_id, lang_id.replace("_", " ").title())
    cover = render_book_cover(lang_id, label=label, command_count=len(cmds))
    mirrored = _mirror_asset(cover, "books")
    text = write_explaining_manual(lang_id, seed=seed)
    h7c_path = pack_explaining_h7(lang_id, text)
    return {
        "ok": True,
        "lang_id": lang_id,
        "label": label,
        "cover": str(cover),
        "world_url": f"/world/assets/combinatronic/books/{lang_id}.png",
        "mirrored": str(mirrored),
        "h7c_path": str(h7c_path),
        "h7_path": str(h7c_path),
        "command_count": len(cmds),
        "char_count": len(text),
    }


def build_manifest(*, chips: list[dict[str, Any]] | None = None, books: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    catalog = _load(CATALOG, {})
    seed = _load(SEED, {})
    chip_rows = chips or []
    book_rows = books or []
    return {
        "schema": "field-combinatronic-visuals-manifest/v1",
        "generated": _now(),
        "chips": {
            "count": len(chip_rows),
            "catalog_count": len(catalog.get("chips") or []),
            "items": chip_rows,
        },
        "books": {
            "count": len(book_rows),
            "language_count": len(seed.get("language_packs") or {}),
            "items": book_rows,
        },
        "assets_root": str(ASSETS),
        "world_root": "/world/assets/combinatronic",
    }


def _balance_mod() -> Any | None:
    path = INSTALL / "lib" / "field-combinatronic-balance.py"
    if not path.is_file():
        return None
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("vis_bal", path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    except Exception:
        pass
    return None


def publish_panel(*, refresh: bool = False, force: bool = False) -> dict[str, Any]:
    """Synchronous combinatoric entry — manifest/registry without full regen at balance."""
    import time
    t0 = time.perf_counter()
    bal = _balance_mod()
    entry: dict[str, Any] = {}
    if bal and hasattr(bal, "combinatoric_entry"):
        entry = bal.combinatoric_entry("visuals", refresh=refresh, force=force, battery_path=PANEL)
        if entry.get("skip_build") and entry.get("cached_doc"):
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            if hasattr(bal, "record_cycle"):
                bal.record_cycle(reorganized=False, elapsed_ms=elapsed_ms)
            panel = dict(entry["cached_doc"])
            panel["fast_path"] = True
            panel["balance_hold"] = True
            panel["balance_gate"] = entry.get("gate")
            panel["elapsed_ms"] = elapsed_ms
            panel["combinatronic"] = True
            return {"ok": True, "panel": panel, "skipped": True}
    if refresh:
        return generate_all()
    panel = _load(PANEL, {})
    if panel:
        registry = build_registry()
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
        gate = entry.get("gate") or {}
        if bal and hasattr(bal, "record_cycle"):
            bal.record_cycle(reorganized=not gate.get("skip_reorganize"), elapsed_ms=elapsed_ms)
        return {
            "ok": True,
            "panel": {**panel, "combinatronic": True, "entry_synchronous": True, "balance_gate": gate},
            "registry": {"path": _rel(REGISTRY), "file_count": registry.get("file_count")},
        }
    return generate_all()


def generate_all(*, chips_only: bool = False, books_only: bool = False) -> dict[str, Any]:
    catalog = _load(CATALOG, {})
    seed = _load(SEED, {})
    chip_results: list[dict[str, Any]] = []
    book_results: list[dict[str, Any]] = []

    if not books_only:
        for chip in catalog.get("chips") or []:
            cid = chip.get("id")
            if not cid:
                continue
            try:
                chip_results.append(generate_chip(str(cid)))
            except Exception as exc:
                chip_results.append({"ok": False, "chip_id": cid, "error": str(exc)})

    if not chips_only:
        for lang_id in sorted((seed.get("language_packs") or {}).keys()):
            try:
                book_results.append(generate_book(lang_id))
            except Exception as exc:
                book_results.append({"ok": False, "lang_id": lang_id, "error": str(exc)})

    manifest = build_manifest(chips=chip_results, books=book_results)
    _save(MANIFEST, manifest)
    panel = {
        "schema": "field-combinatronic-visuals-panel/v1",
        "generated": manifest["generated"],
        "chip_ok": sum(1 for r in chip_results if r.get("ok")),
        "book_ok": sum(1 for r in book_results if r.get("ok")),
        "manifest": str(MANIFEST),
        "world_root": manifest["world_root"],
    }
    _save(PANEL, panel)
    registry = build_registry()
    return {
        "ok": True,
        "manifest": manifest,
        "panel": panel,
        "registry": {"path": _rel(REGISTRY), "file_count": registry.get("file_count")},
    }


def visuals_panel() -> dict[str, Any]:
    cached = _load(PANEL, {})
    manifest = _load(MANIFEST, {})
    if cached and manifest:
        return {**cached, "manifest": manifest, "ok": True}
    return generate_all()


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "manifest"
    if cmd == "generate":
        chips_only = "--chips" in sys.argv
        books_only = "--books" in sys.argv
        doc = generate_all(chips_only=chips_only, books_only=books_only)
        print(json.dumps(doc, ensure_ascii=False, indent=2))
        return 0
    if cmd == "chip" and len(sys.argv) > 2:
        print(json.dumps(generate_chip(sys.argv[2]), ensure_ascii=False, indent=2))
        return 0
    if cmd == "book" and len(sys.argv) > 2:
        print(json.dumps(generate_book(sys.argv[2]), ensure_ascii=False, indent=2))
        return 0
    if cmd == "inventory":
        print(json.dumps(inventory(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "verify":
        print(json.dumps(verify_all(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "registry":
        print(json.dumps(build_registry(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "repair":
        if len(sys.argv) > 2 and sys.argv[2] == "mirror":
            print(json.dumps(repair_mirror(), ensure_ascii=False, indent=2))
            return 0
        only_broken = "--all" not in sys.argv
        print(json.dumps(repair_all(only_broken=only_broken), ensure_ascii=False, indent=2))
        return 0
    if cmd == "pattern" and len(sys.argv) > 2:
        print(json.dumps(explain_pattern(sys.argv[2]), ensure_ascii=False, indent=2))
        return 0
    if cmd == "manifest":
        print(json.dumps(visuals_panel(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "panel":
        print(json.dumps(visuals_panel(), ensure_ascii=False, indent=2))
        return 0
    print(
        json.dumps(
            {
                "error": "usage",
                "hint": (
                    "field-combinatronic-visuals.py "
                    "[generate|manifest|inventory|verify|registry|repair|repair mirror|pattern <id>|chip <id>|book <lang>]"
                ),
                "doctrine": _rel(DOCTRINE),
            },
            indent=2,
        )
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())