#!/usr/bin/env python3
"""Field execution compare — C / C++ / CMake / Python, no compile in timed path."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from field_math import field_display, field_ratio, field_real  # noqa: E402

OUTDIR = ROOT / "data" / "bench" / "exec-plane"
MANIFEST = OUTDIR / "manifest.json"
LIVE = OUTDIR / "field-exec-live.json"
RESULT = OUTDIR / "field-exec-result.json"
TARGET_SEC = int(os.environ.get("SPEED_DEMO_TARGET_SEC", "10"))
BASELINE_ID = os.environ.get("FIELD_EXEC_BASELINE", "cxx_host_o2")

DOCTRINE = {
    "schema": "grok16-speed-doctrine/v1",
    "wave_conversion": True,
    "single_plane": True,
    "ironclad_instant": True,
    "compare_axis": "field_execution_ops_per_sec",
    "not_compared": ["compile_ms", "wave_convert_wall", "cmake_configure"],
    "statement": (
        "Runners were wave-converted at stage time. This bench ranks field execution only — "
        "C, C++, CMake, and Python on the same FieldX86 kernel."
    ),
}


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_live(doc: dict) -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    doc["updated"] = _utc()
    LIVE.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def _parse_run_line(line: str) -> dict | None:
    if not line.startswith("speed_demo"):
        return None

    def grab(key: str) -> str:
        m = re.search(rf"{key}=([0-9.eE+-]+)", line)
        return m.group(1) if m else "0"

    wall_ms = field_real(grab("wall_ms"))
    total_ops = field_real(grab("total_ops"))
    ops_per_sec = field_real(grab("ops_per_sec"))
    epochs = int(float(grab("epochs") or 0))
    if wall_ms <= field_real(0) * 2 or total_ops <= field_real(0) * 2:
        return None
    return {
        "status": "done",
        "field_execution_ms": wall_ms,
        "epochs": epochs,
        "total_ops": total_ops,
        "ops_per_sec": ops_per_sec,
    }


def _runner_cmd(runner: dict) -> list[str]:
    if runner.get("kind") == "script":
        return list(runner.get("cmd") or [])
    return [str(runner.get("path", ""))]


def _field_execute(runner: dict, doc: dict) -> None:
    rid = runner["id"]
    doc["phase"] = "field_execution"
    doc["cases"][rid].update({"status": "executing", "elapsed_sec": 0, "pct": 0})
    _write_live(doc)

    env = {**os.environ, "SPEED_DEMO_TARGET_SEC": str(TARGET_SEC)}
    env.update(runner.get("env") or {})
    cmd = _runner_cmd(runner)
    if not cmd or not cmd[0]:
        doc["cases"][rid].update({"status": "failed", "error": "no_runner"})
        _write_live(doc)
        return

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
        cwd=str(ROOT),
    )
    final_line = ""
    assert proc.stdout is not None
    for line in proc.stdout:
        line = line.strip()
        if line.startswith("SPEED_DEMO_PROGRESS"):
            elapsed = int(m.group(1)) if (m := re.search(r"elapsed_sec=([0-9]+)", line)) else 0
            pct = int(m.group(1)) if (m := re.search(r"pct=([0-9]+)", line)) else 0
            epochs = int(m.group(1)) if (m := re.search(r"epochs=([0-9]+)", line)) else 0
            total_ops = int(m.group(1)) if (m := re.search(r"total_ops=([0-9]+)", line)) else 0
            doc["cases"][rid].update(
                {"status": "executing", "elapsed_sec": elapsed, "pct": pct, "epochs": epochs, "total_ops": total_ops}
            )
            _write_live(doc)
            print(f"  [{rid}] field execute {elapsed}s / {TARGET_SEC}s ({pct}%)", flush=True)
        elif line.startswith("speed_demo"):
            final_line = line
    proc.wait(timeout=TARGET_SEC + 180)
    parsed = _parse_run_line(final_line)
    if not parsed:
        doc["cases"][rid].update(
            {
                "status": "failed",
                "error": "no_execution_line",
                "detail": final_line[:240] or f"exit={proc.returncode}",
            }
        )
    else:
        doc["cases"][rid].update(parsed)
    _write_live(doc)


def _build_summary(doc: dict) -> dict:
    cases = doc.get("cases", {})
    baseline = cases.get(BASELINE_ID, {})
    base_ops = field_real(baseline.get("ops_per_sec"))
    rankings: list[dict] = []
    for rid in doc.get("order", []):
        c = cases.get(rid, {})
        if c.get("status") != "done":
            continue
        ops = field_real(c.get("ops_per_sec"))
        rankings.append(
            {
                "id": rid,
                "label": c.get("label", rid),
                "lang": c.get("lang", "?"),
                "ops_per_sec": ops,
                "field_execution_ms": field_real(c.get("field_execution_ms")),
                "binary_bytes": int(c.get("binary_bytes") or 0),
                "speedup_vs_baseline": field_ratio(ops, base_ops),
                "color": c.get("color", "#3ecf8e"),
            }
        )
    rankings.sort(key=lambda r: r["ops_per_sec"], reverse=True)
    best = rankings[0] if rankings else {}
    by_lang: dict[str, dict] = {}
    for r in rankings:
        lang = r.get("lang", "?")
        if lang not in by_lang or r["ops_per_sec"] > by_lang[lang]["ops_per_sec"]:
            by_lang[lang] = r
    return {
        "schema": "grok16-field-exec-summary/v1",
        "doctrine": DOCTRINE,
        "target_sec": TARGET_SEC,
        "baseline_id": BASELINE_ID,
        "baseline_ops_per_sec": base_ops,
        "best_id": best.get("id"),
        "best_label": best.get("label"),
        "best_lang": best.get("lang"),
        "best_ops_per_sec": field_real(best.get("ops_per_sec")),
        "best_by_lang": by_lang,
        "rankings": rankings,
        "verdict": "complete" if rankings else "quiescent",
    }


def run() -> int:
    if not MANIFEST.is_file():
        print(f"field-exec-compare: skip — manifest unfound ({MANIFEST})", file=sys.stderr)
        return 0

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    runners = [r for r in (manifest.get("runners") or []) if _runner_cmd(r) and _runner_cmd(r)[0]]
    if not runners:
        print("field-exec-compare: skip — no runnable entries in manifest", file=sys.stderr)
        return 0

    doc: dict = {
        "schema": "grok16-field-exec/v1",
        "doctrine": DOCTRINE,
        "phase": "init",
        "target_sec": TARGET_SEC,
        "updated": _utc(),
        "order": manifest.get("order") or [r["id"] for r in runners],
        "cases": {},
        "summary": None,
    }
    for r in runners:
        rid = r["id"]
        binary_bytes = 0
        if r.get("kind") == "binary" and r.get("path"):
            p = Path(r["path"])
            if p.is_file():
                binary_bytes = p.stat().st_size
        doc["cases"][rid] = {
            "id": rid,
            "label": r.get("label", rid),
            "lang": r.get("lang", "?"),
            "group": r.get("group", "?"),
            "color": r.get("color", "#3ecf8e"),
            "kind": r.get("kind"),
            "status": "staged",
            "ironclad_instant": True,
            "wave_conversion": True,
            "single_plane": r.get("kind") == "binary",
            "binary_bytes": binary_bytes,
        }
    _write_live(doc)

    print(f"field-exec-compare: {len(runners)} runners × {TARGET_SEC}s field execution (no compile)")
    print(f"field-exec-compare: baseline = {BASELINE_ID}")
    print(f"field-exec-compare: live → {LIVE}")

    for runner in runners:
        rid = runner["id"]
        print(f"\n=== {runner.get('label', rid)} ===")
        doc["cases"][rid]["status"] = "running"
        _write_live(doc)
        t0 = time.perf_counter()
        _field_execute(runner, doc)
        wall = (time.perf_counter() - t0) * 1000.0
        done = doc["cases"][rid]
        if done.get("status") == "done":
            print(f"  FIELD EXEC {field_display(done.get('ops_per_sec'))} ops/s  (runner wall {wall:.0f} ms)")
        else:
            print(f"  skip {done.get('error')} — {done.get('detail', '')[:120]}")

    doc["phase"] = "complete"
    doc["summary"] = _build_summary(doc)
    _write_live(doc)
    RESULT.write_text(
        json.dumps({"schema": "grok16-field-exec-result/v1", **doc["summary"], "cases": doc["cases"]}, indent=2) + "\n",
        encoding="utf-8",
    )
    s = doc["summary"]
    print("\n" + "=" * 68)
    print("FIELD EXECUTION — C / C++ / CMake / Python (execution only)")
    for row in s.get("rankings", []):
        print(
            f"  {row['label'][:46]:46}  "
            f"{field_display(row['ops_per_sec']):>14} ops/s  "
            f"{field_display(row['speedup_vs_baseline']):>6}x vs {BASELINE_ID}"
        )
    best_lang = s.get("best_by_lang") or {}
    if best_lang:
        print("\nBest per language:")
        for lang in ("c", "cxx", "cmake", "python"):
            if lang in best_lang:
                b = best_lang[lang]
                print(f"  {lang:6} → {b['label']} @ {field_display(b['ops_per_sec'])} ops/s")
    print(f"\nResults: {RESULT}")
    if not s.get("rankings"):
        print("field-exec-compare: skip — no successful rankings", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())