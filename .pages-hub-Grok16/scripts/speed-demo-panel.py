#!/usr/bin/env python3
"""Live speed-demo terminal dashboard — reads data/bench/speed-demo-live.json."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from field_math import FIELD_FLOOR, FIELD_PRECISION, field_display, field_int_display, field_real  # noqa: E402

LIVE = ROOT / "data" / "bench" / "speed-demo-live.json"
RESULT = ROOT / "data" / "bench" / "speed-demo-result.json"


def bar(pct: float, width: int = 40) -> str:
    pct = max(0.0, min(100.0, float(pct) if pct else 0.0))
    filled = int(round(width * pct / 100.0))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def clear() -> None:
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def render(doc: dict) -> None:
    clear()
    print("Grok16 Field Execution — wave conversion instant, rank execution only")
    print("=" * 78)
    print(f"Target: {doc.get('target_sec', 60)}s per binary  |  Phase: {doc.get('phase', 'idle')}")
    print(f"Updated: {doc.get('updated', '—')}")
    print(f"Web UI:  http://127.0.0.1:{os.environ.get('SPEED_DASHBOARD_PORT', '9416')}/")
    print(f"Field floor: {FIELD_FLOOR:.{FIELD_PRECISION}f}")
    print()

    cases = doc.get("cases", {})
    order = doc.get("order", list(cases.keys()))
    for cid in order:
        c = cases.get(cid, {})
        label = c.get("label", cid)
        status = c.get("status", "pending")
        grp = c.get("group", "")
        tag = "HOST" if grp == "host" else "G16 "
        print(f"  [{tag}] {label}")
        print(f"    status: {status}")
        if status in ("executing", "running"):
            pct = field_real(c.get("pct", 0), floor=0.0000001)
            print(f"    progress: {bar(pct)} {pct:.0f}%")
            print(
                f"    elapsed: {field_int_display(c.get('elapsed_sec', 0))}s  "
                f"epochs: {field_int_display(c.get('epochs', 0))}  "
                f"ops: {field_int_display(c.get('total_ops', 0))}"
            )
        elif status == "done":
            print(f"    field_execution_ms: {field_display(c.get('field_execution_ms', c.get('wall_ms', 0)))}")
            print(f"    ops/sec: {field_display(c.get('ops_per_sec', 0))}")
        elif status == "failed":
            print(f"    error: {c.get('error', 'run_failed')}")
            if c.get("detail"):
                print(f"    detail: {c.get('detail')[:72]}")
        elif status == "converging":
            print("    wave convert → single plane…")
        elif status == "converged":
            print("    plane: ironclad instant ✓")
        print()

    summary = doc.get("summary")
    if summary and summary.get("rankings"):
        print("-" * 78)
        print("RANKINGS (ops/sec)")
        for i, row in enumerate(summary["rankings"], 1):
            print(
                f"  {i:2}. {row.get('label', row.get('id'))[:50]:50}  "
                f"{field_display(row.get('ops_per_sec', 0)):>14}  "
                f"{field_display(row.get('speedup_vs_baseline', 0)):>6}x"
            )
        print()
        print(f"  Best G16: {summary.get('best_g16_id', '—')}  "
              f"({field_display(summary.get('best_g16_speedup', 0))}x vs baseline)")
        print(f"  Full report: {RESULT}")
    print()
    print("Ctrl+C to close panel")


def main() -> int:
    os.chdir(ROOT)
    print("Speed demo panel — waiting for live data…")
    while True:
        if LIVE.is_file():
            try:
                doc = json.loads(LIVE.read_text(encoding="utf-8"))
                render(doc)
                if doc.get("phase") == "complete":
                    time.sleep(3)
                    render(doc)
                    return 0
            except (json.JSONDecodeError, OSError):
                pass
        time.sleep(0.4)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nPanel closed.")
        raise SystemExit(0)