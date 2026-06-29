#!/usr/bin/env pythong
"""Final_Eye OCR core — one lane, in-process, H7/7 output. No subprocess loopbacks."""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

_LIB = Path(__file__).resolve().parent
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", str(_LIB.parent)))
SG = Path(os.environ.get("SG_ROOT", str(INSTALL.parent)))

_ZOCR_MOD: Any = None
_ZOCR_H7_MOD: Any = None
_H7_MOD: Any = None


def final_eye_root() -> Path:
    env = os.environ.get("FINAL_EYE_ROOT", "").strip()
    if env:
        p = Path(env).expanduser()
        if p.is_dir():
            return p.resolve()
    try:
        if str(_LIB) not in sys.path:
            sys.path.insert(0, str(_LIB))
        from sg_paths import final_eye_root as _fer
        return _fer()
    except Exception:
        pass
    for cand in (INSTALL / "Final_Eye", SG / "NewLatest" / "Final_Eye", SG / "Final_Eye"):
        if (cand / "zocr.py").is_file():
            return cand.resolve()
    return (INSTALL / "Final_Eye").resolve()


def _ensure_zocr_path() -> Path:
    root = final_eye_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root


def _zocr() -> Any | None:
    global _ZOCR_MOD
    if _ZOCR_MOD is not None:
        return _ZOCR_MOD
    root = _ensure_zocr_path()
    zocr_py = root / "zocr.py"
    if not zocr_py.is_file():
        return None
    spec = importlib.util.spec_from_file_location("zocr_core", zocr_py)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _ZOCR_MOD = mod
    return mod


def _zocr_h7() -> Any | None:
    global _ZOCR_H7_MOD
    if _ZOCR_H7_MOD is not None:
        return _ZOCR_H7_MOD
    root = _ensure_zocr_path()
    h7_py = root / "zocr_h7.py"
    if not h7_py.is_file():
        return None
    spec = importlib.util.spec_from_file_location("zocr_h7_core", h7_py)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _ZOCR_H7_MOD = mod
    return mod


def _h7_format() -> Any | None:
    global _H7_MOD
    if _H7_MOD is not None:
        return _H7_MOD
    path = INSTALL / "lib" / "field-h7-format.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("field_h7_format_core", path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _H7_MOD = mod
    return mod


def read_ocr_text(path: Path | str) -> str:
    fp = Path(path)
    if not fp.is_file():
        return ""
    h7 = _zocr_h7()
    if h7 and hasattr(h7, "read_ocr_text"):
        try:
            return str(h7.read_ocr_text(fp) or "")
        except Exception:
            pass
    fmt = _h7_format()
    if fp.suffix.lower() == ".h7" and fmt and hasattr(fmt, "open_any_h7_path"):
        try:
            text, _ = fmt.open_any_h7_path(fp)
            return str(text or "")
        except Exception:
            pass
    try:
        return fp.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def ocr_image_path(path: Path | str, *, label: str = "") -> dict[str, Any]:
    """Single-hop OCR: Final_Eye zocr in-process → H7 capture row."""
    fp = Path(path).expanduser()
    if not fp.is_file():
        return {"ok": False, "error": "file_missing", "path": str(fp)}
    zocr = _zocr()
    if not zocr:
        return {"ok": False, "error": "final_eye_missing", "final_eye_root": str(final_eye_root())}
    try:
        text = str(zocr.ocr_image(fp) or "")
        row = zocr.write_capture(label=label or fp.stem, image=fp, ocr_text=text, copy_image=True)
        row["ok"] = bool(text) or bool(row.get("ocr_len"))
        row["text"] = text
        row["engine"] = "Final_Eye/zocr.py"
        row["format"] = row.get("format") or "h7/7"
        row["final_eye_root"] = str(final_eye_root())
        return row
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__, "detail": str(exc)[:200], "path": str(fp)}


def final_eye_status() -> dict[str, Any]:
    zocr = _zocr()
    if not zocr or not hasattr(zocr, "status"):
        return {"ok": False, "error": "final_eye_missing", "final_eye_root": str(final_eye_root())}
    try:
        st = zocr.status()
        st["commander"] = "Hostess7"
        st["sovereign"] = True
        return st
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__, "detail": str(exc)[:200]}


def ocr_image_text(path: Path | str) -> str:
    row = ocr_image_path(path)
    return str(row.get("text") or row.get("ocr") or "").strip()


def final_eye_look(*, prefer: str = "auto", label: str = "look") -> dict[str, Any]:
    root = _ensure_zocr_path()
    vision = root / "zocr_vision.py"
    if vision.is_file():
        spec = importlib.util.spec_from_file_location("zocr_vision_core", vision)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "look"):
                return mod.look(label=label, prefer=prefer)
    return {"ok": False, "error": "look_unavailable", "final_eye_root": str(root)}


def final_eye_browser_smoke() -> dict[str, Any]:
    root = _ensure_zocr_path()
    smoke = root / "queen_browser_smoke.py"
    if not smoke.is_file():
        return {"ok": False, "error": "smoke_unavailable", "final_eye_root": str(root)}
    import json
    import subprocess
    import sys
    try:
        proc = subprocess.run(
            [sys.executable, str(smoke)],
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "FINAL_EYE_ROOT": str(root), "NEXUS_INSTALL_ROOT": str(INSTALL)},
            cwd=str(root),
        )
        try:
            doc = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError:
            doc = {"ok": proc.returncode == 0, "tail": (proc.stdout or proc.stderr or "")[-2000:]}
        doc["returncode"] = proc.returncode
        doc["final_eye_root"] = str(root)
        doc["engine"] = "Final_Eye/queen_browser_smoke.py"
        return doc
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "smoke_timeout", "final_eye_root": str(root)}


def final_eye_dispatch(body: dict[str, Any]) -> dict[str, Any]:
    """Direct Final_Eye lane — no Queen bridge loopback."""
    sub = str(body.get("subaction") or body.get("action") or "status").strip().lower()
    if sub in ("status", "json"):
        return final_eye_status()
    if sub in ("look", "watch", "vision", "poll"):
        prefer = str(body.get("prefer") or "auto")
        return final_eye_look(prefer=prefer, label=str(body.get("label") or "look"))
    if sub in ("smoke", "browser-smoke", "browser_smoke", "final-eye-smoke"):
        return final_eye_browser_smoke()
    if sub == "ocr":
        path = str(body.get("image") or body.get("path") or "")
        if not path:
            return {"ok": False, "error": "missing_image"}
        return ocr_image_path(path, label=str(body.get("label") or ""))
    if sub == "read":
        path = str(body.get("path") or body.get("h7_file") or body.get("ocr_file") or "")
        text = read_ocr_text(path)
        return {"ok": bool(text), "path": path, "text": text, "format": "h7/7" if path.endswith(".h7") else "text"}
    return {"ok": False, "error": "unknown_subaction", "subaction": sub}