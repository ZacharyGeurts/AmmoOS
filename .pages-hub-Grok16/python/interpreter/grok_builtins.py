"""GrokPy builtins — field AI primitives baked in, no overlay packages."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any, Callable


def grok_print(*args: Any, sep: str = " ", end: str = "\n") -> None:
    print(*args, sep=sep, end=end)


def grok_len(x: Any) -> int:
    return len(x)


def grok_range(*args: int) -> range:
    return range(*args)


def grok_int(x: Any, base: int = 10) -> int:
    return int(x, base) if base != 10 else int(x)


def grok_str(x: Any) -> str:
    return str(x)


def grok_bool(x: Any) -> bool:
    return bool(x)


def grok_type(x: Any) -> str:
    if x is None:
        return "NoneType"
    if isinstance(x, bool):
        return "bool"
    if isinstance(x, int):
        return "int"
    if isinstance(x, float):
        return "float"
    if isinstance(x, str):
        return "str"
    if isinstance(x, list):
        return "list"
    if isinstance(x, tuple):
        return "tuple"
    if isinstance(x, range):
        return "range"
    if hasattr(x, "name"):
        return "function"
    return type(x).__name__


def _sg_root() -> Path:
    env = os.environ.get("SG_ROOT", "").strip()
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2]


def grok_truth_floor(tier: str = "adapt") -> int:
    path = _sg_root() / "Hostess7" / "data" / "hostess7-truth-floor.json"
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        return int((doc.get("tiers") or {}).get(tier, {}).get("floor", 58))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return 58


def grok_encourage_cap(delta: float) -> float:
    """Cap encourage delta — never override sealed base weights."""
    return max(-0.05, min(0.05, float(delta)))


def grok_field_features(ctx: dict[str, Any] | None = None) -> list[float]:
    """12-dim feature vector for ear/eye neural assist — zero external deps."""
    c = ctx or {}
    ev = c.get("evidence") or {}
    loc = c.get("localization") or {}
    peak = float(ev.get("peak_db", -18.0))
    mouth = float(ev.get("mouth_correlation", 0.7))
    itd = min(1.0, abs(float(ev.get("itd_us", 0))) / 500.0)
    bearing = min(1.0, abs(float(loc.get("bearing_deg", 0))) / 180.0)
    existence = float(c.get("existence_correlation", ev.get("existence_correlation", 0.75)))
    sovereign = 1.0 if ev.get("sovereign_time_ok", True) else 0.0
    encoded = 0.0 if c.get("encoded_ok", True) else 1.0
    interference = 0.0 if c.get("interference_ok", True) else 1.0
    motion = 1.0 if (c.get("motion") or {}).get("is_moving") else 0.0
    return [
        round(mouth, 4),
        round(1.0 - mouth, 4),
        round(1.0 if peak >= 0 else 0.0, 4),
        round(itd, 4),
        round(bearing, 4),
        round(encoded, 4),
        round(interference, 4),
        round(motion, 4),
        round(existence, 4),
        round(sovereign, 4),
        round(peak / -60.0, 4),
        round(min(1.0, float(c.get("confidence", 0.5))), 4),
    ]


def grok_overlay_probs(
    probs: list[float],
    label: str,
    labels: list[str],
    *,
    delta: float = 0.02,
    overlay: dict[str, float] | None = None,
) -> list[float]:
    """Apply capped encourage overlay without mutating base network."""
    cap = grok_encourage_cap(delta)
    ov = dict(overlay or {})
    if label in labels:
        ov[label] = ov.get(label, 0.0) + cap
    total_ov = sum(abs(v) for v in ov.values())
    if total_ov > 0.25:
        scale = 0.25 / total_ov
        ov = {k: v * scale for k, v in ov.items()}
    out = list(probs)
    idx = {lb: i for i, lb in enumerate(labels)}
    for lb, d in ov.items():
        if lb in idx:
            out[idx[lb]] = max(0.0, min(1.0, out[idx[lb]] + d))
    s = sum(out) or 1.0
    return [p / s for p in out]


def grok_ai_status() -> dict[str, Any]:
    sg = _sg_root()
    return {
        "truth_floor": grok_truth_floor(),
        "overlay_only": True,
        "max_encourage_delta": 0.05,
        "final_ear": (sg / "Final_Ear" / "zocr_neural_assist.py").is_file(),
        "final_eye": (sg / "Final_Eye" / "zocr_neural_assist.py").is_file(),
        "field_ready": os.environ.get("GROKPY_FIELD") == "1",
    }


def make_builtins() -> dict[str, Callable[..., Any]]:
    return {
        "print": grok_print,
        "len": grok_len,
        "range": grok_range,
        "int": grok_int,
        "str": grok_str,
        "bool": grok_bool,
        "type": grok_type,
        "abs": abs,
        "min": min,
        "max": max,
        "sum": sum,
        "truth_floor": grok_truth_floor,
        "encourage_cap": grok_encourage_cap,
        "field_features": grok_field_features,
        "overlay_probs": grok_overlay_probs,
        "ai_status": grok_ai_status,
        "True": True,
        "False": False,
        "None": None,
    }