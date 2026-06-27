"""Queen → Final_Eye root resolution — v1.1 teach-authority bridge."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

QUEEN = Path(__file__).resolve().parents[1]
SG = QUEEN.parent.parent


def final_eye_root() -> Path:
    """Canonical Final_Eye product tree (v1.1+), fallback ZOCR when Final_Eye absent."""
    env = os.environ.get("FINAL_EYE_ROOT", "").strip()
    if env:
        p = Path(env)
        if p.is_dir():
            return p
    fe = SG / "Final_Eye"
    if (fe / "zocr_product.py").is_file() or (fe / "VERSION").is_file():
        return fe
    zocr_env = os.environ.get("ZOCR_ROOT", "").strip()
    if zocr_env and Path(zocr_env).is_dir():
        return Path(zocr_env)
    for candidate in (SG / "ZOCR", SG / "final_eye"):
        if (candidate / "zocr_product.py").is_file() or (candidate / "VERSION").is_file():
            return candidate
    return fe


def final_eye_env(*, queen: Path | None = None) -> dict[str, str]:
    """Environment for subprocess / import of Final_Eye stack."""
    root = final_eye_root()
    q = queen or QUEEN
    hostess = Path(os.environ.get("HOSTESS7_ROOT", SG / "Hostess7"))
    gmf = root / "GrokMediaFormat"
    if not gmf.is_dir():
        gmf = SG / "GrokMediaFormat"
    py_parts = [str(root)]
    if gmf.is_dir():
        py_parts.append(str(gmf))
    py = os.pathsep.join(py_parts)
    if os.environ.get("PYTHONPATH"):
        py = py + os.pathsep + os.environ["PYTHONPATH"]
    return {
        **os.environ,
        "SG_ROOT": str(SG),
        "FINAL_EYE_ROOT": str(root),
        "QUEEN_ROOT": str(q),
        "HOSTESS7_ROOT": str(hostess),
        "NEXUS_INSTALL_ROOT": os.environ.get("NEXUS_INSTALL_ROOT", str(q)),
        "FINAL_EYE_ASSIST": os.environ.get("FINAL_EYE_ASSIST", "1"),
        "FINAL_EYE_LOW_END": os.environ.get("FINAL_EYE_LOW_END", "1"),
        "FINAL_EYE_COOL": os.environ.get("FINAL_EYE_COOL", "1"),
        "PYTHONPATH": py,
    }


def import_final_eye() -> Path:
    """Insert Final_Eye on sys.path; return root."""
    env = final_eye_env()
    root = Path(env["FINAL_EYE_ROOT"])
    for part in env.get("PYTHONPATH", "").split(os.pathsep):
        if part and part not in sys.path:
            sys.path.insert(0, part)
    return root


def final_eye_version() -> dict[str, Any]:
    import_final_eye()
    from zocr_product import product_info
    return product_info()