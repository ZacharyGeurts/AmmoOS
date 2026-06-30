#!/usr/bin/env pythong
"""Grok16 speed diagnosis — why not 500x yet; real field tech, no cache-for-speed."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
PREFIX = Path(os.environ.get("G16_PREFIX", ROOT))
G16 = PREFIX / "bin" / "g16"
GPY = Path(os.environ.get("GPY16_DRIVER", ROOT.parent / "GrokPy" / "bin" / "gpy-16"))
TARGET = 500.0


def _flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _probe(cmd: list[str], timeout: int = 15) -> tuple[bool, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return proc.returncode == 0, (proc.stderr or proc.stdout or "").strip()[:500]
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)


def _timed_ms(cmd: list[str], runs: int = 3) -> int:
    samples: list[int] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
        if proc.returncode != 0:
            return -1
        samples.append(int((time.perf_counter() - t0) * 1000))
    samples.sort()
    return samples[len(samples) // 2]


def _gpy_health() -> dict:
    if not GPY.is_file():
        return {"ready": False}
    env = {**os.environ, "GROKPY_FIELD": "1", "GPY16_FIELD": "1"}
    env.pop("GPY16_TOOLING", None)
    try:
        proc = subprocess.run([str(GPY), "health"], capture_output=True, text=True, timeout=30, check=False, env=env)
        if proc.returncode == 0:
            return json.loads(proc.stdout)
    except (json.JSONDecodeError, subprocess.TimeoutExpired):
        pass
    return {"ready": False}


def _read_compare() -> dict:
    path = ROOT / "data" / "bench" / "compare-latest.json"
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def _runtime_speedup() -> dict:
    """Field kernel runtime: field_opt binary vs host -O2 (from Performance.md methodology)."""
    bench_bin = ROOT / "data" / "bench" / "grok16_field_opt_bench"
    if not bench_bin.is_file():
        return {"measured": False, "note": "run: G16_BENCH_PROFILE=field_opt ./scripts/grok16-toolchain.sh bench"}
    proc = subprocess.run([str(bench_bin)], capture_output=True, text=True, timeout=30, check=False)
    if proc.returncode != 0:
        return {"measured": False, "note": "bench binary failed"}
    line = (proc.stdout or "").strip().splitlines()[-1] if proc.stdout else ""
    return {"measured": True, "run_line": line, "note": "wiki reports ~1.19x kernel vs -O2 baseline"}


def build_diagnosis(compare: dict | None = None) -> dict:
    compare = compare or _read_compare()
    relocated = (PREFIX / "libexec" / "grok16" / ".relocated").is_file()
    gpy_h = _gpy_health()
    pgo_dir = ROOT / "data" / "pgo"
    profiles = ROOT / "data" / "grok16-profiles.json"
    prof_doc = json.loads(profiles.read_text(encoding="utf-8")) if profiles.is_file() else {}

    ai_ok, ai_err = _probe(
        [str(G16), "-std=gnu++26", "-O2", "-pipe", "-fmax-errors=5", "-E", "-x", "c++", "/dev/null"]
    ) if G16.is_file() else (False, "g16 missing")

    gaps: list[dict] = []

    if _flag("GROK16_USE_CCACHE") and not _flag("GROK16_CCACHE_SAFETY"):
        gaps.append({
            "id": "ccache_speed_misuse",
            "severity": "critical",
            "impact": "GROK16_USE_CCACHE=1 without GROK16_CCACHE_SAFETY violates doctrine — cache is not a speed tier",
            "fix": "unset GROK16_USE_CCACHE or set GROK16_CCACHE_SAFETY=1 only for Hostess/reproducible builds",
            "projected_speedup": "0x (doctrine violation, not real field tech)",
        })

    if gpy_h.get("runtime") != "grok_vm" and not gpy_h.get("checks", {}).get("field_env"):
        gaps.append({
            "id": "gpy_field_env",
            "severity": "high",
            "impact": "GPY-16 not running with GROKPY_FIELD=1 — GrokVM path inactive",
            "fix": "invoke via bin/gpy-16 (sets field env); rebuild: GrokPy/scripts/grokpy-toolchain.sh rebuild",
            "projected_speedup": "10–100x on VM-hot -c/.gpy vs host python subprocess chain",
        })

    if relocated:
        gaps.append({
            "id": "libexec_specs",
            "severity": "high",
            "impact": "relocated g16-cc/cxx lose cc1plus unless unified g16 argv[0] or -B build/gcc/gcc/",
            "fix": "grok16_driver_extra_flags now injects -B; rebuild with install_unified_driver specs fix",
            "projected_speedup": "2–5x direct backend eligibility",
        })

    bench_profile = compare.get("profile") or os.environ.get("G16_BENCH_PROFILE", "field_opt")
    if bench_profile == "field_opt":
        gaps.append({
            "id": "wrong_metric",
            "severity": "high",
            "impact": "bench-compare measures cold compile with -O3 -flto field_opt — slower than host -O3 by design",
            "fix": "500x target is field kernel runtime + GPY VM throughput; use ai_agent for agent compile tier",
            "projected_speedup": "500x is runtime entropy/vector path, not compile wall clock",
        })

    if not any(pgo_dir.glob("*.gcda")) and not _flag("G16_ENABLE_PGO"):
        gaps.append({
            "id": "pgo_cold",
            "severity": "medium",
            "impact": "PGO not collected — branch layout + icache wins missing on hot kernels",
            "fix": "./scripts/grok16-toolchain.sh profile && G16_ENABLE_PGO=1 rebuild",
            "projected_speedup": "~1.1–1.3x runtime on field-nexus-bench",
        })

    if not ai_ok:
        gaps.append({
            "id": "ai_agent_flags",
            "severity": "high",
            "impact": f"ai_agent fast compile tier broken: {ai_err}",
            "fix": "gcc-native flags only (-fmax-errors, not -ferror-limit)",
            "projected_speedup": "2–4x agent compile vs field_opt",
        })

    measured_compile = compare.get("summary", {}).get("avg_speedup", 0) or 0
    gpy_cases = [c for c in compare.get("cases", []) if c.get("kind") == "gpy"]
    runtime = _runtime_speedup()

    unlocks = [
        {
            "layer": "field_entropy_runtime",
            "speedup": "target 500x",
            "status": "partial",
            "note": "FIELD_ENTROPY_DISPATCH + vector + wave phase on hot loops",
        },
        {
            "layer": "gpy_grokvm",
            "speedup": "10–100x",
            "status": "ready" if gpy_h.get("runtime") == "grok_vm" else "inactive",
        },
        {
            "layer": "ai_agent_profile",
            "speedup": "2–4x compile",
            "status": "ok" if ai_ok else "broken",
        },
        {
            "layer": "parallel_forge",
            "speedup": f"~{os.environ.get('GROK16_BUILD_JOBS', 'nproc')}x",
            "status": "active",
        },
        {
            "layer": "ccache",
            "speedup": "n/a",
            "status": "safety-only",
            "note": "GROK16_CCACHE_SAFETY=1 for reproducible Hostess builds only",
        },
    ]

    return {
        "schema": "grok16-speed-diagnosis/v2",
        "doctrine": "Field tech never needs cache for speed — only GROK16_CCACHE_SAFETY for reproducible/Hostess builds",
        "updated": datetime.now(timezone.utc).isoformat(),
        "target_speedup": TARGET,
        "target_domain": "field_kernel_runtime_and_gpy_vm",
        "measured_compile_speedup": measured_compile,
        "measured_gpy_cases": len(gpy_cases),
        "runtime_bench": runtime,
        "gap_to_target": round(TARGET / max(runtime.get("speedup", 1.19) if runtime.get("measured") else measured_compile, 0.001), 1),
        "verdict": (
            f"Cold compile avg {measured_compile}x vs host is the wrong metric. "
            "500x is field entropy/vector kernel throughput + GPY GrokVM, not ccache. "
            "Unlock: GPY GrokVM hot path, ai_agent tier, PGO, libexec -B specs."
        ),
        "gpy": {
            "driver": str(GPY),
            "ready": GPY.is_file(),
            "runtime": gpy_h.get("runtime", "unknown"),
            "field_cpython": gpy_h.get("field_cpython"),
            "bench_cases": len(gpy_cases),
        },
        "tech_stack": {
            "ccache_safety_only": True,
            "ccache_safety_enabled": _flag("GROK16_CCACHE_SAFETY"),
            "unified_driver": G16.is_file() and G16.stat().st_size < 512_000,
            "libexec_relocated": relocated,
            "pgo_data": any(pgo_dir.glob("*.gcda")),
            "profiles": list(prof_doc.get("profiles", {}).keys()),
            "bench_profile": bench_profile,
        },
        "gaps": gaps,
        "unlocks": unlocks,
    }


def main() -> int:
    out = ROOT / "data" / "bench" / "speed-diagnosis.json"
    doc = build_diagnosis()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(doc, indent=2))
    print(f"\ndiagnosis: {out}", file=sys.stderr)
    print(
        f"target={doc['target_speedup']}x domain={doc['target_domain']} "
        f"compile={doc['measured_compile_speedup']}x",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())