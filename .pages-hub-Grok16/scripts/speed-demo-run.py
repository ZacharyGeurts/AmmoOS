#!/usr/bin/env python3
"""Grok16 speed demo — wave conversion to single plane, then field execution only."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from field_math import field_display, field_ratio, field_real  # noqa: E402

SRC = ROOT / "examples" / "speed-demo" / "speed_demo.cpp"
OUTDIR = ROOT / "data" / "bench"
LIVE = OUTDIR / "speed-demo-live.json"
RESULT = OUTDIR / "speed-demo-result.json"
G16 = Path(os.environ.get("G16_PREFIX", str(ROOT))) / "bin" / "g16"
PROFILE_PY = ROOT / "scripts" / "grok16-profile-flags.py"
TARGET_SEC = int(os.environ.get("SPEED_DEMO_TARGET_SEC", "10"))
BASELINE_ID = os.environ.get("SPEED_DEMO_BASELINE", "host_gcc_o2")

DOCTRINE = {
    "schema": "grok16-speed-doctrine/v1",
    "wave_conversion": True,
    "single_plane": True,
    "ironclad_instant": True,
    "ironclad_citation": "ironclad:field_sanity:5",
    "compare_axis": "field_execution_ops_per_sec",
    "not_compared": ["compile_ms", "layer_ms", "link_wall"],
    "statement": (
        "Converging source to the single fabric plane is wave conversion — "
        "Ironclad truth is instant at integrate. This bench ranks field execution only."
    ),
}


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _host_cxx_std() -> str:
    for std in ("gnu++26", "gnu++23", "gnu++20", "c++20", "gnu++17"):
        proc = subprocess.run(
            ["g++", f"-std={std}", "-E", "-x", "c++", "/dev/null"],
            capture_output=True,
            timeout=8,
        )
        if proc.returncode == 0:
            return std
    return "gnu++17"


def _profile_flags(profile: str, kind: str) -> list[str]:
    if not PROFILE_PY.is_file():
        return []
    env = {**os.environ, "GROK16_ROOT": str(ROOT), "G16_PREFIX": os.environ.get("G16_PREFIX", str(ROOT))}
    proc = subprocess.run(
        [sys.executable, str(PROFILE_PY), profile, kind],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return []
    return proc.stdout.strip().split()


def _g16_extra() -> list[str]:
    env = {**os.environ, "GROK16_ROOT": str(ROOT)}
    proc = subprocess.run(
        ["bash", "-lc", f'source "{ROOT}/scripts/grok16-config.sh" && grok16_driver_extra_flags'],
        capture_output=True,
        text=True,
        env=env,
        timeout=15,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return []
    return proc.stdout.strip().split()


def _merge_g16_flags(cxx: list[str], link: list[str]) -> list[str]:
    link = [a for a in link if a not in ("-flto=thin", "-flto")]
    cxx = list(cxx)
    if "-fPIE" not in cxx and "-fpie" not in cxx:
        cxx.append("-fPIE")
    if "-pie" not in link and "-no-pie" not in link:
        link = [*link, "-pie"]
    return [*cxx, *link]


def toolchains() -> list[dict]:
    std = _host_cxx_std()
    host_o3 = [
        f"-std={std}",
        "-O3",
        "-march=native",
        "-mtune=native",
        "-ftree-vectorize",
        "-funroll-loops",
        "-ffast-math",
    ]
    host_o2 = [f"-std={std}", "-O2", "-march=native"]
    host_gxx = shutil.which("g++") or "/usr/bin/g++"
    if str(G16) in host_gxx or "grok16" in host_gxx:
        for candidate in ("/usr/bin/g++", "/usr/bin/g++-13", "/usr/bin/g++-12"):
            if Path(candidate).is_file():
                host_gxx = candidate
                break
    cases: list[dict] = [
        {
            "id": "host_gcc_o2",
            "label": "Conventional — host g++ -O2",
            "group": "host",
            "tool": host_gxx,
            "wave_args": host_o2,
            "color": "#94a3b8",
        },
        {
            "id": "host_gcc_o3",
            "label": "Conventional — host g++ -O3",
            "group": "host",
            "tool": host_gxx,
            "wave_args": host_o3,
            "color": "#64748b",
        },
    ]
    if not G16.is_file():
        return cases
    xflags = _g16_extra()
    for tid, label, profile, color in (
        ("g16_belt_1_0", "Grok16 — g16 belt_1_0 (1.0 field_opt)", "belt_1_0", "#22c55e"),
        ("g16_belt_2_0", "Grok16 — g16 belt_2_0 (2.0 single fabric)", "belt_2_0", "#3ecf8e"),
        ("g16_field_opt", "Grok16 — g16 field_opt (entropy / wave)", "field_opt", "#10b981"),
        ("g16_ai", "Grok16 — g16 ai (matrix / NEXUS)", "ai", "#f472b6"),
        ("g16_ai_agent", "Grok16 — g16 ai_agent (fast agent tier)", "ai_agent", "#eb488c"),
    ):
        cxx = _profile_flags(profile, "cxx") or ["-std=gnu++26", "-O3", "-march=native"]
        link = _profile_flags(profile, "link")
        cases.append(
            {
                "id": tid,
                "label": label,
                "group": "g16",
                "tool": str(G16),
                "wave_args": [*xflags, *_merge_g16_flags(cxx, link or [])],
                "profile": profile,
                "color": color,
            }
        )
    return cases


def _write_live(doc: dict) -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    doc["updated"] = _utc()
    LIVE.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def _converge_to_plane(case: dict, doc: dict) -> Path | None:
    """Wave conversion — source converges to single-plane executable (Ironclad instant receipt)."""
    cid = case["id"]
    doc["phase"] = "wave_convert"
    doc["cases"][cid]["status"] = "converging"
    _write_live(doc)
    out = OUTDIR / f"speed_demo_{cid}"
    args = [
        case["tool"],
        *case["wave_args"],
        f'-DTOOLCHAIN_TAG="{cid}"',
        "-o",
        str(out),
        str(SRC),
    ]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        doc["cases"][cid].update(
            {
                "status": "failed",
                "error": "wave_convert_failed",
                "detail": (proc.stderr or proc.stdout or "")[:400],
            }
        )
        _write_live(doc)
        return None
    doc["cases"][cid].update(
        {
            "status": "converged",
            "ironclad_instant": True,
            "wave_conversion": True,
            "single_plane": True,
            "plane_receipt": "ironclad:meld:2",
            "binary_bytes": out.stat().st_size,
        }
    )
    _write_live(doc)
    return out


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


def _field_execute(case: dict, binary: Path, doc: dict) -> None:
    cid = case["id"]
    doc["phase"] = "field_execution"
    doc["cases"][cid].update({"status": "executing", "elapsed_sec": 0, "pct": 0})
    _write_live(doc)
    env = {**os.environ, "SPEED_DEMO_TARGET_SEC": str(TARGET_SEC)}
    proc = subprocess.Popen(
        [str(binary)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
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
            doc["cases"][cid].update(
                {"status": "executing", "elapsed_sec": elapsed, "pct": pct, "epochs": epochs, "total_ops": total_ops}
            )
            _write_live(doc)
            print(f"  [{cid}] field execute {elapsed}s / {TARGET_SEC}s ({pct}%)", flush=True)
        elif line.startswith("speed_demo"):
            final_line = line
    proc.wait(timeout=TARGET_SEC + 120)
    parsed = _parse_run_line(final_line)
    if not parsed:
        doc["cases"][cid].update(
            {
                "status": "failed",
                "error": "no_execution_line",
                "detail": final_line[:240] or f"exit={proc.returncode}",
            }
        )
    else:
        doc["cases"][cid].update(parsed)
    _write_live(doc)


def _build_summary(doc: dict) -> dict:
    cases = doc.get("cases", {})
    baseline = cases.get(BASELINE_ID, {})
    base_ops = field_real(baseline.get("ops_per_sec"))
    rankings: list[dict] = []
    for cid in doc.get("order", []):
        c = cases.get(cid, {})
        if c.get("status") != "done":
            continue
        ops = field_real(c.get("ops_per_sec"))
        rankings.append(
            {
                "id": cid,
                "label": c.get("label", cid),
                "ops_per_sec": ops,
                "field_execution_ms": field_real(c.get("field_execution_ms")),
                "binary_bytes": int(c.get("binary_bytes") or 0),
                "speedup_vs_baseline": field_ratio(ops, base_ops),
                "color": c.get("color", "#3ecf8e"),
            }
        )
    rankings.sort(key=lambda r: r["ops_per_sec"], reverse=True)
    best = rankings[0] if rankings else {}
    g16_cases = [r for r in rankings if r["id"].startswith("g16_")]
    best_g16 = max(g16_cases, key=lambda r: r["ops_per_sec"]) if g16_cases else {}
    return {
        "schema": "grok16-speed-demo-summary/v3",
        "doctrine": DOCTRINE,
        "target_sec": TARGET_SEC,
        "baseline_id": BASELINE_ID,
        "baseline_ops_per_sec": base_ops,
        "best_id": best.get("id"),
        "best_label": best.get("label"),
        "best_ops_per_sec": field_real(best.get("ops_per_sec")),
        "best_g16_id": best_g16.get("id"),
        "best_g16_ops_per_sec": field_real(best_g16.get("ops_per_sec")),
        "best_g16_speedup": field_ratio(best_g16.get("ops_per_sec"), base_ops) if best_g16 else 0.0,
        "rankings": rankings,
        "host_count": len([r for r in rankings if r["id"].startswith("host_")]),
        "g16_count": len(g16_cases),
        "verdict": "complete" if rankings else "quiescent",
    }


def run() -> int:
    if not SRC.is_file():
        print("speed-demo: missing source", file=sys.stderr)
        return 1
    cases = toolchains()
    doc: dict = {
        "schema": "grok16-speed-demo/v3",
        "doctrine": DOCTRINE,
        "phase": "init",
        "target_sec": TARGET_SEC,
        "updated": _utc(),
        "order": [c["id"] for c in cases],
        "cases": {
            c["id"]: {
                "id": c["id"],
                "label": c["label"],
                "group": c["group"],
                "color": c.get("color", "#3ecf8e"),
                "profile": c.get("profile"),
                "status": "pending",
            }
            for c in cases
        },
        "summary": None,
    }
    _write_live(doc)
    print(f"speed-demo: {len(cases)} planes × {TARGET_SEC}s field execution")
    print("speed-demo: wave conversion = Ironclad instant (not ranked)")
    print(f"speed-demo: live → {LIVE}")

    for case in cases:
        cid = case["id"]
        print(f"\n=== {case['label']} ===")
        binary = _converge_to_plane(case, doc)
        if binary is None:
            print(f"  SKIP wave convert failed: {cid}")
            continue
        print("  converged → single plane (ironclad instant)")
        _field_execute(case, binary, doc)
        done = doc["cases"][cid]
        if done.get("status") == "done":
            print(f"  FIELD EXEC {field_display(done.get('ops_per_sec'))} ops/s")
        else:
            print(f"  FAIL {done.get('error')}")

    doc["phase"] = "complete"
    doc["summary"] = _build_summary(doc)
    _write_live(doc)
    RESULT.write_text(
        json.dumps({"schema": "grok16-speed-demo-result/v3", **doc["summary"], "cases": doc["cases"]}, indent=2) + "\n",
        encoding="utf-8",
    )
    s = doc["summary"]
    print("\n" + "=" * 60)
    print("FIELD EXECUTION RANKINGS (binary speed only)")
    for row in s.get("rankings", []):
        print(
            f"  {row['label'][:44]:44}  "
            f"{field_display(row['ops_per_sec']):>14} ops/s  "
            f"{field_display(row['speedup_vs_baseline']):>6}x vs baseline"
        )
    if s.get("best_g16_id"):
        print(
            f"\nBest G16: {s['best_g16_id']} @ {field_display(s['best_g16_ops_per_sec'])} ops/s "
            f"({field_display(s['best_g16_speedup'])}x vs {BASELINE_ID})"
        )
    print(f"\nResults: {RESULT}")
    return 0 if s.get("rankings") else 1


if __name__ == "__main__":
    raise SystemExit(run())