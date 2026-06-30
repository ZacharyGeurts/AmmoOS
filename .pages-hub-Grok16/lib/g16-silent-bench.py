#!/usr/bin/env python3
"""G3 — silent bench gate; speaks only on >5% regression vs locked plate."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
THRESHOLD = float(os.environ.get("G16_BENCH_REGRESS_PCT", "5.0"))
TRIAD = ROOT / "data" / "bench" / "triad-latest.json"
PLATE = ROOT / "data" / "g16-power-sort-plate.json"
BENCH = ROOT / "docs" / "field-exec-full-bench.json"


def _load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _best_ops(doc: dict[str, Any]) -> float | None:
    for key in ("best_exec_ops_per_sec", "best_ops_per_sec", "ops_per_sec"):
        v = doc.get(key)
        if isinstance(v, (int, float)) and v > 0:
            return float(v)
    cases = doc.get("cases") or doc.get("contexts") or {}
    best = 0.0
    if isinstance(cases, dict):
        for c in cases.values():
            if isinstance(c, dict):
                for k in ("ops_per_sec", "best_exec_ops_per_sec", "run_wall_ms"):
                    v = c.get(k)
                    if k == "run_wall_ms" and isinstance(v, (int, float)) and v > 0:
                        best = max(best, 1e6 / v)
                    elif isinstance(v, (int, float)) and v > best:
                        best = float(v)
    return best if best > 0 else None


def check_regression() -> dict[str, Any]:
    baseline_doc = _load(PLATE) if PLATE.is_file() else _load(BENCH)
    current_doc = _load(TRIAD) if TRIAD.is_file() else _load(BENCH)
    baseline = _best_ops(baseline_doc)
    current = _best_ops(current_doc)
    if baseline is None or current is None:
        return {"ok": True, "skipped": True, "reason": "no_baseline_or_current"}
    if current >= baseline:
        return {"ok": True, "baseline": baseline, "current": current, "delta_pct": 0.0}
    delta_pct = ((baseline - current) / baseline) * 100.0
    ok = delta_pct <= THRESHOLD
    return {
        "ok": ok,
        "baseline": baseline,
        "current": current,
        "delta_pct": round(delta_pct, 2),
        "threshold_pct": THRESHOLD,
    }


def main() -> int:
    rep = check_regression()
    if rep.get("skipped") or rep.get("ok"):
        return 0
    print(
        f"g16-bench REGRESSION: {rep['delta_pct']}% worse than plate "
        f"(threshold {rep['threshold_pct']}%) baseline={rep['baseline']} current={rep['current']}",
        file=sys.stderr,
        flush=True,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())