#!/usr/bin/env pythong
"""Grok16 Field Profiler — AI-ready bottleneck reporter for builds and field programs.

One command → one JSON document. Profile .launch chambers, sources, binaries, or profiles.
Suggest and apply .launch / profile / flag reconfiguration.

Schema: grok16-profiler/v1
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
SCRIPTS = ROOT / "scripts"
PROFILE_DIR = ROOT / "data" / "profile"
BENCH_DIR = ROOT / "data" / "bench"
SCHEMA = "grok16-profiler/v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _env_true(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _g16() -> Path:
    prefix = Path(os.environ.get("G16_PREFIX", ROOT))
    return prefix / "bin" / "g16"


def _gpy_run(script: Path, *args: str, timeout: int = 120) -> tuple[int, str]:
    gpy = os.environ.get("GPY16_DRIVER", "")
    candidates = [gpy, str(ROOT / "bin" / "gpy-16"), str(ROOT.parent / "GrokPy" / "bin" / "gpy-16"), sys.executable]
    runner = next((c for c in candidates if c and Path(c).exists()), sys.executable)
    cmd = [runner, str(script), *args]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(ROOT), env={**os.environ, "GROK16_ROOT": str(ROOT), "G16_PREFIX": str(os.environ.get("G16_PREFIX", ROOT))})
        return proc.returncode, (proc.stdout or proc.stderr or "").strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, str(exc)


def _profile_flags(profile: str, kind: str = "cxx") -> str:
    script = SCRIPTS / "grok16-profile-flags.py"
    if not script.is_file():
        return "-std=gnu++26 -O3"
    rc, out = _gpy_run(script, profile, kind, timeout=30)
    return out if rc == 0 else "-std=gnu++26 -O3"


def _bench_source(profile: str) -> Path | None:
    rc, rel = _gpy_run(SCRIPTS / "grok16-profile-flags.py", profile, "source", timeout=15)
    if rc != 0 or not rel.strip():
        return None
    src = ROOT / rel.strip()
    return src if src.is_file() else None


def _expand(text: str) -> str:
    env = {
        "GROK16_ROOT": str(ROOT),
        "G16_PREFIX": str(os.environ.get("G16_PREFIX", ROOT)),
        "GROK16_SG_ROOT": str(os.environ.get("GROK16_SG_ROOT", ROOT.parent)),
        "QUEEN_ROOT": str(os.environ.get("QUEEN_ROOT", ROOT.parent / "NewLatest" / "Queen")),
    }
    out = text
    for key, val in env.items():
        out = out.replace(f"${{{key}}}", val)
    return out


def _mem_kb() -> dict[str, int]:
    mem: dict[str, int] = {}
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            mem[k.strip()] = int(v.strip().split()[0])
    except OSError:
        pass
    total = mem.get("MemTotal", 0)
    avail = mem.get("MemAvailable", mem.get("MemFree", 0))
    used = max(0, total - avail) if total else 0
    return {"total_kb": total, "used_kb": used, "available_kb": avail}


def _load_launch(path: Path) -> dict[str, Any]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    if "chamber_root" in doc:
        doc["chamber_root"] = _expand(str(doc["chamber_root"]))
    return doc


def _launch_source(launch: dict[str, Any]) -> Path | None:
    root = Path(str(launch.get("chamber_root") or "."))
    entry = str(launch.get("entry") or "").strip()
    if not entry:
        return None
    candidate = root / entry
    if candidate.is_file():
        return candidate
    if launch.get("runtime") == "cmake" and (root / "CMakeLists.txt").is_file():
        return root / "CMakeLists.txt"
    return candidate if candidate.exists() else None


def _driver_extra() -> list[str]:
    flags: list[str] = []
    if (ROOT / "libexec" / "grok16" / ".relocated").is_file():
        build_gcc = ROOT / "build" / "gcc" / "gcc"
        if build_gcc.is_dir():
            flags.extend(["-B", str(build_gcc)])
    return flags


def _compile_one(src: Path, profile: str, *, out: Path | None = None) -> dict[str, Any]:
    g16 = _g16()
    if not g16.is_file():
        return {"ok": False, "error": "g16_missing", "path": str(g16)}
    out_path = out or (BENCH_DIR / f"g16_profile_{profile}_{src.stem}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pflags = _profile_flags(profile, "cxx").split()
    lflags = _profile_flags(profile, "link").split()
    xflags = _driver_extra()
    if src.suffix.lower() in (".cpp", ".cc", ".cxx", ".c++"):
        for lib in ("-lstdc++", "-lm"):
            if lib not in lflags:
                lflags.append(lib)
    mem_before = _mem_kb()
    t0 = time.perf_counter()
    cmd = [str(g16), *xflags, *pflags, *lflags, "-o", str(out_path), str(src)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=str(src.parent))
    compile_ms = round((time.perf_counter() - t0) * 1000, 2)
    mem_after = _mem_kb()
    ok = proc.returncode == 0 and out_path.is_file()
    result: dict[str, Any] = {
        "id": "compile",
        "ok": ok,
        "ms": compile_ms,
        "profile": profile,
        "source": str(src),
        "binary": str(out_path) if out_path.is_file() else "",
        "binary_bytes": out_path.stat().st_size if out_path.is_file() else 0,
        "compiler": str(g16),
        "flags": {"cxx": pflags, "link": lflags, "driver": xflags},
        "returncode": proc.returncode,
        "stderr_tail": (proc.stderr or "")[-2000:],
        "mem_delta_kb": mem_after.get("used_kb", 0) - mem_before.get("used_kb", 0),
    }
    if ok:
        t1 = time.perf_counter()
        run_proc = subprocess.run([str(out_path)], capture_output=True, text=True, timeout=120)
        run_ms = round((time.perf_counter() - t1) * 1000, 2)
        result["run"] = {
            "id": "run",
            "ok": run_proc.returncode == 0,
            "ms": run_ms,
            "stdout_tail": (run_proc.stdout or "").strip()[-1500:],
            "stderr_tail": (run_proc.stderr or "")[-500:],
            "returncode": run_proc.returncode,
        }
    return result


def _parse_ninja_log(build_dir: Path) -> list[dict[str, Any]]:
    log_path = build_dir / ".ninja_log"
    if not log_path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    try:
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            start, end, _mtime, target = parts[0], parts[1], parts[2], parts[3]
            try:
                ms = max(0, int(end) - int(start))
            except ValueError:
                continue
            rows.append({"target": target, "ms": ms})
    except OSError:
        return []
    rows.sort(key=lambda r: r["ms"], reverse=True)
    return rows[:32]


def _profile_cmake_build(
    *,
    source: Path,
    build: Path,
    profile: str,
    target: str = "",
) -> dict[str, Any]:
    field_cmake = SCRIPTS / "field-cmake.sh"
    if not field_cmake.is_file():
        return {"ok": False, "error": "field_cmake_missing"}
    env = {
        **os.environ,
        "GROK16_ROOT": str(ROOT),
        "G16_PREFIX": str(os.environ.get("G16_PREFIX", ROOT)),
        "GROK16_FIELD_PROFILE": profile,
        "GROK16_CMAKE_SOURCE": str(source if source.is_dir() else source.parent),
        "GROK16_CMAKE_BUILD": str(build),
        "GROK16_BUILD_JOBS": os.environ.get("GROK16_BUILD_JOBS", str(os.cpu_count() or 4)),
    }
    if target:
        env["GROK16_CMAKE_TARGET"] = target
    phases: list[dict[str, Any]] = []
    mem_before = _mem_kb()
    for phase, args in (("configure", ["configure"]), ("build", ["build"])):
        t0 = time.perf_counter()
        proc = subprocess.run(
            ["bash", str(field_cmake), *args],
            capture_output=True,
            text=True,
            timeout=3600,
            cwd=str(ROOT),
            env=env,
        )
        ms = round((time.perf_counter() - t0) * 1000, 2)
        phases.append({
            "id": phase,
            "ok": proc.returncode == 0,
            "ms": ms,
            "stderr_tail": (proc.stderr or "")[-1500:],
            "stdout_tail": (proc.stdout or "")[-1500:],
        })
        if proc.returncode != 0:
            break
    ninja_slow = _parse_ninja_log(build)
    binary = ""
    binary_bytes = 0
    for candidate in (
        build / "bin" / "Linux" / "queen-browser",
        build / "bin" / "Linux" / "amouranth_engine",
        build / "field_nexus_bench",
        build / "field_dispatch",
    ):
        if candidate.is_file():
            binary = str(candidate)
            binary_bytes = candidate.stat().st_size
            break
    run_phase: dict[str, Any] | None = None
    if binary:
        t0 = time.perf_counter()
        rp = subprocess.run([binary], capture_output=True, text=True, timeout=120)
        run_phase = {
            "id": "run",
            "ok": rp.returncode == 0,
            "ms": round((time.perf_counter() - t0) * 1000, 2),
            "stdout_tail": (rp.stdout or "").strip()[-1500:],
        }
        phases.append(run_phase)
    mem_after = _mem_kb()
    return {
        "ok": all(p.get("ok") for p in phases[:2]),
        "kind": "cmake",
        "profile": profile,
        "source": str(source),
        "build": str(build),
        "phases": phases,
        "ninja_slowest": ninja_slow,
        "binary": binary,
        "binary_bytes": binary_bytes,
        "mem_delta_kb": mem_after.get("used_kb", 0) - mem_before.get("used_kb", 0),
    }


def _bottlenecks(doc: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    phases = doc.get("phases") or []
    if doc.get("compile"):
        phases = [doc["compile"], *([doc["compile"]["run"]] if doc["compile"].get("run") else [])]
    total = sum(int(p.get("ms") or 0) for p in phases if isinstance(p, dict))
    total = max(total, 1)
    for p in phases:
        if not isinstance(p, dict):
            continue
        ms = int(p.get("ms") or 0)
        if ms < 50:
            continue
        pid = str(p.get("id") or "phase")
        pct = round(100.0 * ms / total, 1)
        hint = {
            "compile": "Switch to ai_agent profile for faster iterative compiles; field_opt/belt_2_0 for release throughput.",
            "link": "LTO link dominates — try ai_agent (-O2, no thin LTO) for dev; enable PGO only for release.",
            "configure": "CMake configure slow — reuse build cache; set GROK16_CMAKE_BUILD to a persistent dir.",
            "build": "Ninja build slow — check ninja_slowest targets; raise GROK16_BUILD_JOBS or split translation units.",
            "run": "Runtime bottleneck — compare profiles with: grok16-profiler.py compare --profiles field_opt,belt_2_0",
        }.get(pid, "Inspect phase stderr_tail and flags.")
        out.append({
            "id": pid,
            "severity": "high" if pct >= 40 else ("medium" if pct >= 15 else "low"),
            "ms": ms,
            "pct": pct,
            "hint": hint,
        })
    for row in (doc.get("ninja_slowest") or [])[:5]:
        ms = int(row.get("ms") or 0)
        if ms < 100:
            continue
        out.append({
            "id": "ninja_target",
            "severity": "medium" if ms >= 500 else "low",
            "ms": ms,
            "target": row.get("target"),
            "hint": f"Slow translation unit — inspect {row.get('target')} or enable parallel jobs.",
        })
    profile = doc.get("profile") or doc.get("active_profile") or ""
    if profile in ("field_opt", "belt_2_0", "vulkan_rtx"):
        out.append({
            "id": "profile_heavy",
            "severity": "info",
            "profile": profile,
            "hint": "Heavy release profile active — use ai_agent during development, then belt_2_0 for ship.",
        })
    return sorted(out, key=lambda b: {"high": 0, "medium": 1, "low": 2, "info": 3}.get(str(b.get("severity")), 9))


def _suggestions(doc: dict[str, Any], launch: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    sugg: list[dict[str, Any]] = []
    profile = doc.get("profile") or doc.get("active_profile") or os.environ.get("G16_BENCH_PROFILE", "field_opt")
    compile_ms = 0
    run_ms = 0
    for p in doc.get("phases") or []:
        if p.get("id") == "compile":
            compile_ms = int(p.get("ms") or 0)
        if p.get("id") == "run":
            run_ms = int(p.get("ms") or 0)
    if doc.get("compile"):
        compile_ms = int(doc["compile"].get("ms") or compile_ms)
        if doc["compile"].get("run"):
            run_ms = int(doc["compile"]["run"].get("ms") or run_ms)
    if compile_ms > 1500 and profile != "ai_agent":
        sugg.append({
            "action": "set_profile",
            "profile": "ai_agent",
            "reason": f"compile_ms={compile_ms} — ai_agent is 2–4× faster for dev iteration",
            "env": {"G16_BENCH_PROFILE": "ai_agent", "GROK16_FIELD_PROFILE": "ai_agent"},
        })
    if run_ms > 5 and profile not in ("belt_2_0", "field_opt"):
        sugg.append({
            "action": "set_profile",
            "profile": "field_opt",
            "reason": f"run_ms={run_ms} — field_opt optimizes kernel throughput",
            "env": {"G16_BENCH_PROFILE": "field_opt", "GROK16_FIELD_PROFILE": "field_opt"},
        })
    if not _env_true("G16_ENABLE_PGO") and profile in ("field_opt", "belt_2_0"):
        sugg.append({
            "action": "enable_pgo",
            "reason": "PGO not enabled — ~10–30% runtime win on hot kernels after profile + rebuild",
            "commands": [
                "./scripts/grok16-toolchain.sh profile",
                "G16_ENABLE_PGO=1 ./scripts/grok16-toolchain.sh field-bench",
            ],
        })
    if launch:
        sugg.append({
            "action": "patch_launch",
            "path": launch.get("_path", ""),
            "changes": {
                "env": {
                    **(launch.get("env") or {}),
                    "G16_BENCH_PROFILE": profile,
                    "GROK16_FIELD_PROFILE": profile,
                    "G16_PROFILE_BUILD": "1",
                },
                "g16_profiler": {"active_profile": profile, "profile_build": True},
            },
        })
    if not sugg:
        sugg.append({
            "action": "noop",
            "reason": "No automatic changes — metrics within expected range for active profile",
        })
    return sugg


def profile_run(
    *,
    profile: str | None = None,
    source: Path | None = None,
    launch_path: Path | None = None,
    binary: Path | None = None,
    build_dir: Path | None = None,
) -> dict[str, Any]:
    active = profile or os.environ.get("G16_BENCH_PROFILE") or os.environ.get("GROK16_FIELD_PROFILE") or "field_opt"
    launch_doc: dict[str, Any] | None = None
    target: dict[str, Any] = {"kind": "profile", "profile": active}
    body: dict[str, Any] = {"profile": active, "active_profile": active}

    if launch_path:
        launch_doc = _load_launch(launch_path)
        launch_doc["_path"] = str(launch_path)
        target = {"kind": "launch", "path": str(launch_path), "title": launch_doc.get("title")}
        src = _launch_source(launch_doc)
        runtime = str(launch_doc.get("runtime") or "native")
        env_profile = (launch_doc.get("env") or {}).get("GROK16_FIELD_PROFILE") or (launch_doc.get("env") or {}).get("G16_BENCH_PROFILE")
        if env_profile:
            active = str(env_profile)
            body["profile"] = active
        if runtime == "cmake" and src:
            bdir = build_dir or Path(str(launch_doc.get("chamber_root") or ".")) / "build" / "profile"
            body.update(_profile_cmake_build(source=src.parent, build=bdir, profile=active))
        elif src and src.suffix in (".cpp", ".c", ".cc", ".cxx"):
            body["compile"] = _compile_one(src, active)
            body["ok"] = body["compile"].get("ok", False)
        else:
            body["ok"] = False
            body["error"] = "launch_runtime_unsupported"
            body["runtime"] = runtime
            body["entry"] = str(src or "")
    elif binary:
        target = {"kind": "binary", "path": str(binary)}
        t0 = time.perf_counter()
        proc = subprocess.run([str(binary)], capture_output=True, text=True, timeout=120)
        ms = round((time.perf_counter() - t0) * 1000, 2)
        body = {
            "ok": proc.returncode == 0,
            "profile": active,
            "phases": [{
                "id": "run",
                "ok": proc.returncode == 0,
                "ms": ms,
                "stdout_tail": (proc.stdout or "").strip()[-2000:],
                "stderr_tail": (proc.stderr or "")[-500:],
            }],
            "binary": str(binary),
            "binary_bytes": binary.stat().st_size if binary.is_file() else 0,
        }
    elif source:
        target = {"kind": "source", "path": str(source)}
        body["compile"] = _compile_one(source, active)
        body["ok"] = body["compile"].get("ok", False)
    else:
        src = _bench_source(active)
        if not src:
            return {"schema": SCHEMA, "ok": False, "error": "bench_source_missing", "profile": active}
        target = {"kind": "bench", "path": str(src), "profile": active}
        body["compile"] = _compile_one(src, active)
        body["ok"] = body["compile"].get("ok", False)

    phases = body.get("phases") or []
    if body.get("compile"):
        phases = [body["compile"]]
        if body["compile"].get("run"):
            phases.append(body["compile"]["run"])
    totals = {
        "wall_ms": sum(int(p.get("ms") or 0) for p in phases),
        "compile_ms": sum(int(p.get("ms") or 0) for p in phases if p.get("id") == "compile"),
        "run_ms": sum(int(p.get("ms") or 0) for p in phases if p.get("id") == "run"),
    }
    report = {
        "schema": SCHEMA,
        "session_id": uuid.uuid4().hex[:12],
        "updated": _now(),
        "ok": body.get("ok", False),
        "target": target,
        "active_profile": active,
        "phases": phases,
        "totals": totals,
        "ninja_slowest": body.get("ninja_slowest") or [],
        "binary": body.get("binary") or (body.get("compile") or {}).get("binary", ""),
        "binary_bytes": body.get("binary_bytes") or (body.get("compile") or {}).get("binary_bytes", 0),
        "resources": {
            "cpu_cores": os.cpu_count() or 1,
            "loadavg": list(os.getloadavg()) if hasattr(os, "getloadavg") else [],
            "mem": _mem_kb(),
        },
        "bottlenecks": _bottlenecks(body),
        "suggestions": _suggestions(body, launch_doc),
        "launch": {k: v for k, v in (launch_doc or {}).items() if not k.startswith("_")},
        "motto": "One command, one JSON — AI reads bottlenecks, applies fixes.",
    }
    return report


def profile_compare(profiles: list[str]) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    for prof in profiles:
        doc = profile_run(profile=prof)
        runs.append({
            "profile": prof,
            "ok": doc.get("ok"),
            "totals": doc.get("totals"),
            "binary_bytes": doc.get("binary_bytes"),
            "bottlenecks": doc.get("bottlenecks"),
        })
    best_compile = min(runs, key=lambda r: (r.get("totals") or {}).get("compile_ms", 10**9))
    best_run = min(runs, key=lambda r: (r.get("totals") or {}).get("run_ms", 10**9))
    return {
        "schema": SCHEMA,
        "kind": "compare",
        "updated": _now(),
        "profiles": profiles,
        "runs": runs,
        "winner": {
            "compile": best_compile.get("profile"),
            "run": best_run.get("profile"),
        },
        "motto": "Pick ai_agent for compile loop, field_opt/belt_2_0 for runtime ship.",
    }


def wrap_build(*, build_dir: Path | None = None, target: str = "") -> dict[str, Any]:
    build = build_dir or Path(os.environ.get("GROK16_CMAKE_BUILD", ROOT / "build" / "field"))
    source = Path(os.environ.get("GROK16_CMAKE_SOURCE", ""))
    profile = os.environ.get("GROK16_FIELD_PROFILE", os.environ.get("G16_BENCH_PROFILE", "field_opt"))
    ninja_slow = _parse_ninja_log(build)
    doc = {
        "schema": SCHEMA,
        "kind": "wrap_build",
        "updated": _now(),
        "ok": build.is_dir(),
        "active_profile": profile,
        "build": str(build),
        "source": str(source),
        "target": target or os.environ.get("GROK16_CMAKE_TARGET", ""),
        "ninja_slowest": ninja_slow,
        "phases": [{"id": "build", "ok": True, "ms": sum(r.get("ms", 0) for r in ninja_slow)}],
        "bottlenecks": _bottlenecks({"ninja_slowest": ninja_slow, "profile": profile}),
        "suggestions": _suggestions({"profile": profile, "phases": [{"id": "build", "ms": sum(r.get("ms", 0) for r in ninja_slow)}]}),
    }
    out = PROFILE_DIR / "latest-build.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc


def apply_launch(
    launch_path: Path,
    *,
    profile: str | None = None,
    env_extra: dict[str, str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    doc = _load_launch(launch_path)
    before = json.loads(json.dumps(doc))
    doc.setdefault("env", {})
    prof = profile or os.environ.get("G16_BENCH_PROFILE", "ai_agent")
    doc["env"]["G16_BENCH_PROFILE"] = prof
    doc["env"]["GROK16_FIELD_PROFILE"] = prof
    doc["env"]["G16_PROFILE_BUILD"] = "1"
    if env_extra:
        doc["env"].update(env_extra)
    doc["g16_profiler"] = {
        "schema": "grok16-profiler-launch/v1",
        "active_profile": prof,
        "profile_build": True,
        "updated": _now(),
    }
    if not dry_run:
        launch_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "schema": SCHEMA,
        "ok": True,
        "dry_run": dry_run,
        "path": str(launch_path),
        "profile": prof,
        "before": before,
        "after": doc,
    }


def diagnose() -> dict[str, Any]:
    speed_script = SCRIPTS / "grok16-speed-diagnosis.py"
    speed: dict[str, Any] = {}
    if speed_script.is_file():
        rc, out = _gpy_run(speed_script, timeout=90)
        if rc == 0:
            try:
                speed = json.loads(out)
            except json.JSONDecodeError:
                speed = {"raw": out[-3000:]}
    prof = profile_run(profile=os.environ.get("G16_BENCH_PROFILE", "field_opt"))
    return {
        "schema": SCHEMA,
        "kind": "diagnose",
        "updated": _now(),
        "speed_diagnosis": speed,
        "compile_profile": prof,
        "bottlenecks": (speed.get("gaps") or []) + prof.get("bottlenecks", []),
        "suggestions": prof.get("suggestions", []),
        "verdict": speed.get("verdict") or prof.get("motto"),
    }


def collect(out_path: Path | None = None) -> dict[str, Any]:
    doc = diagnose()
    path = out_path or PROFILE_DIR / "latest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    doc["report_path"] = str(path)
    return doc


def posture() -> dict[str, Any]:
    g16 = _g16()
    return {
        "schema": SCHEMA,
        "product": "Grok16 Field Profiler",
        "grok16_root": str(ROOT),
        "g16_ready": g16.is_file(),
        "g16_path": str(g16),
        "profile_dir": str(PROFILE_DIR),
        "active_profile": os.environ.get("G16_BENCH_PROFILE") or os.environ.get("GROK16_FIELD_PROFILE") or "field_opt",
        "profile_build": _env_true("G16_PROFILE_BUILD"),
        "commands": {
            "run": "grok16-profiler.py run [--profile NAME] [--launch PATH] [--source PATH] [--binary PATH]",
            "compare": "grok16-profiler.py compare --profiles field_opt,ai_agent,belt_2_0",
            "diagnose": "grok16-profiler.py diagnose",
            "collect": "grok16-profiler.py collect [--out PATH]",
            "apply": "grok16-profiler.py apply --launch PATH.launch [--profile ai_agent] [--dry-run]",
            "wrap_build": "G16_PROFILE_BUILD=1 — auto after field-cmake build",
        },
        "motto": "One command, one JSON — AI reads bottlenecks, applies fixes.",
    }


def _parse_args(argv: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {"cmd": argv[0] if argv else "json"}
    i = 1
    while i < len(argv):
        a = argv[i]
        if a in ("--profile", "-p") and i + 1 < len(argv):
            out["profile"] = argv[i + 1]
            i += 2
            continue
        if a == "--launch" and i + 1 < len(argv):
            out["launch"] = Path(argv[i + 1])
            i += 2
            continue
        if a == "--source" and i + 1 < len(argv):
            out["source"] = Path(argv[i + 1])
            i += 2
            continue
        if a == "--binary" and i + 1 < len(argv):
            out["binary"] = Path(argv[i + 1])
            i += 2
            continue
        if a == "--out" and i + 1 < len(argv):
            out["out"] = Path(argv[i + 1])
            i += 2
            continue
        if a == "--profiles" and i + 1 < len(argv):
            out["profiles"] = [p.strip() for p in argv[i + 1].split(",") if p.strip()]
            i += 2
            continue
        if a == "--build-dir" and i + 1 < len(argv):
            out["build_dir"] = Path(argv[i + 1])
            i += 2
            continue
        if a == "--target" and i + 1 < len(argv):
            out["target"] = argv[i + 1]
            i += 2
            continue
        if a == "--dry-run":
            out["dry_run"] = True
            i += 1
            continue
        i += 1
    return out


def main() -> int:
    argv = sys.argv[1:]
    while argv and argv[0].endswith((".py", ".gpy")):
        argv = argv[1:]
    cmd = (argv[0] if argv else "json").strip().lower()
    opts = _parse_args(argv)

    if cmd in ("json", "status", "posture"):
        print(json.dumps(posture(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "run":
        doc = profile_run(
            profile=opts.get("profile"),
            source=opts.get("source"),
            launch_path=opts.get("launch"),
            binary=opts.get("binary"),
            build_dir=opts.get("build_dir"),
        )
        print(json.dumps(doc, ensure_ascii=False, indent=2))
        return 0 if doc.get("ok") is not False else 1
    if cmd == "compare":
        profiles = opts.get("profiles") or ["field_opt", "ai_agent", "belt_2_0"]
        print(json.dumps(profile_compare(profiles), ensure_ascii=False, indent=2))
        return 0
    if cmd == "diagnose":
        print(json.dumps(diagnose(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "collect":
        print(json.dumps(collect(opts.get("out")), ensure_ascii=False, indent=2))
        return 0
    if cmd == "wrap-build":
        print(json.dumps(wrap_build(build_dir=opts.get("build_dir"), target=opts.get("target", "")), ensure_ascii=False, indent=2))
        return 0
    if cmd == "apply":
        launch = opts.get("launch")
        if not launch:
            print(json.dumps({"error": "apply requires --launch PATH.launch"}, ensure_ascii=False), file=sys.stderr)
            return 2
        print(json.dumps(apply_launch(launch, profile=opts.get("profile"), dry_run=opts.get("dry_run", False)), ensure_ascii=False, indent=2))
        return 0
    if cmd == "suggest" and opts.get("out"):
        try:
            doc = json.loads(Path(opts["out"]).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            print(json.dumps({"error": "cannot read report"}, ensure_ascii=False), file=sys.stderr)
            return 1
        print(json.dumps({"suggestions": doc.get("suggestions", [])}, ensure_ascii=False, indent=2))
        return 0
    print(
        json.dumps(
            {"error": "usage: grok16-profiler.py [json|run|compare|diagnose|collect|wrap-build|apply|suggest]", "posture": posture()},
            ensure_ascii=False,
            indent=2,
        ),
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())