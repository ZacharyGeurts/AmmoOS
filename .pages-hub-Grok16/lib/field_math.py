"""Field math — zero is not real. Fields report floor at max resolution."""
from __future__ import annotations

import math
from typing import Any

FIELD_FLOOR = 1e-7
FIELD_PRECISION = 7
FIELD_DOCTRINE = "zero_is_not_real"


def field_real(value: Any, *, floor: float = FIELD_FLOOR) -> float:
    """Coerce absent, zero, or NaN to field floor — zero is not math."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = 0.0
    if not math.isfinite(v) or v == 0.0:
        return floor
    return v


def field_ratio(numerator: Any, denominator: Any, *, floor: float = FIELD_FLOOR) -> float:
    """Field-safe ratio — denominator is never bare zero."""
    return field_real(numerator, floor=floor) / field_real(denominator, floor=floor)


def field_display(value: Any, *, precision: int = FIELD_PRECISION, floor: float = FIELD_FLOOR) -> str:
    """Render a field scalar — never bare 0."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = 0.0
    if not math.isfinite(v) or v == 0.0:
        return f"{floor:.{precision}f}"
    if abs(v) >= 1000:
        return f"{v:,.2f}"
    if abs(v) >= 1:
        return f"{v:,.{min(3, precision)}f}"
    return f"{v:.{precision}f}"


def field_int_display(value: Any, *, floor: int = 0, precision: int = FIELD_PRECISION) -> str:
    """Integer field counters — quiescent reads as floor at precision."""
    try:
        v = int(value)
    except (TypeError, ValueError):
        v = 0
    if v == 0:
        return f"{FIELD_FLOOR:.{precision}f}"
    return f"{v:,}"


def field_summary(host_ops: Any, g16_ops: Any) -> dict[str, float | str]:
    """Speed-demo summary using field math — no div-by-zero path."""
    h = field_real(host_ops)
    g = field_real(g16_ops)
    ratio = field_ratio(g, h)
    if h <= FIELD_FLOOR * 2 and g <= FIELD_FLOOR * 2:
        verdict = "quiescent"
    elif abs(h - g) < FIELD_FLOOR:
        verdict = "parity"
    elif g > h:
        verdict = "g16_faster"
    else:
        verdict = "host_faster"
    return {
        "host_ops_per_sec": h,
        "g16_ops_per_sec": g,
        "speedup_ops": ratio,
        "verdict": verdict,
        "field_floor": FIELD_FLOOR,
        "field_precision": FIELD_PRECISION,
    }