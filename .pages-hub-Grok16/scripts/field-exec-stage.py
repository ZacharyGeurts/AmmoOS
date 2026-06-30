#!/usr/bin/env python3
"""One-time wave conversion — stage C / C++ / CMake / Python runners on the exec plane."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from field_exec_bsp import (  # noqa: E402
    bsp_store,
    bsp_try_reuse,
    fingerprint,
    ninja_generator_args,
    rocket_compile_flags,
    rocket_tool,
)
SRC_CXX = ROOT / "examples" / "speed-demo" / "speed_demo.cpp"
SRC_C = ROOT / "examples" / "speed-demo" / "speed_demo.c"
SRC_PY = ROOT / "examples" / "speed-demo" / "speed_demo.py"
CMAKE_SRC = ROOT / "examples" / "speed-demo"
OUTDIR = ROOT / "data" / "bench" / "exec-plane"
MANIFEST = OUTDIR / "manifest.json"
G16 = Path(os.environ.get("G16_PREFIX", str(ROOT))) / "bin" / "g16"
GPY = Path(os.environ.get("G16_PREFIX", str(ROOT))) / "bin" / "gpy-16"
PROFILE_PY = ROOT / "scripts" / "grok16-profile-flags.py"
TOOLCHAIN_CMAKE = ROOT / "cmake" / "grok16-toolchain.cmake"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 600) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "GROK16_ROOT": str(ROOT), "G16_PREFIX": os.environ.get("G16_PREFIX", str(ROOT))}
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd or ROOT), env=env, timeout=timeout)


def _profile_flags(profile: str, kind: str) -> list[str]:
    if not PROFILE_PY.is_file():
        return []
    proc = _run([sys.executable, str(PROFILE_PY), profile, kind], timeout=30)
    if proc.returncode != 0 or not proc.stdout.strip():
        return []
    return proc.stdout.strip().split()


def _g16_extra() -> list[str]:
    proc = _run(["bash", "-lc", f'source "{ROOT}/scripts/grok16-config.sh" && grok16_driver_extra_flags'], timeout=15)
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


def _host_gxx() -> str:
    gxx = shutil.which("g++") or "/usr/bin/g++"
    if "grok16" in gxx or str(G16) in gxx:
        for candidate in ("/usr/bin/g++", "/usr/bin/g++-13", "/usr/bin/g++-12"):
            if Path(candidate).is_file():
                return candidate
    return gxx


def _host_gcc() -> str:
    gcc = shutil.which("gcc") or "/usr/bin/gcc"
    if "grok16" in gcc or str(G16) in gcc:
        for candidate in ("/usr/bin/gcc", "/usr/bin/gcc-13", "/usr/bin/gcc-12"):
            if Path(candidate).is_file():
                return candidate
    return gcc


def _compile_c(case_id: str, tool: str, flags: list[str], tag: str) -> Path | None:
    hit, _, _ = bsp_try_reuse(OUTDIR, case_id=case_id, sources=[SRC_C], profile=tag)
    if hit:
        print(f"  bsp {case_id}")
        return hit
    out = OUTDIR / f"{case_id}"
    args = [rocket_tool(tool), *flags, *rocket_compile_flags("c"), f'-DTOOLCHAIN_TAG="{tag}"', "-o", str(out), str(SRC_C), "-lm"]
    proc = _run(args)
    if proc.returncode != 0:
        print(f"  skip {case_id}: {(proc.stderr or proc.stdout)[:300]}", file=sys.stderr)
        return None
    out.chmod(out.stat().st_mode | 0o111)
    bsp_store(OUTDIR, case_id=case_id, binary=out, fp=fingerprint(case_id=case_id, profile=tag, sources=[SRC_C]))
    return out


def _compile_cxx(case_id: str, tool: str, flags: list[str], tag: str) -> Path | None:
    hit, _, _ = bsp_try_reuse(OUTDIR, case_id=case_id, sources=[SRC_CXX], profile=tag)
    if hit:
        print(f"  bsp {case_id}")
        return hit
    out = OUTDIR / f"{case_id}"
    args = [rocket_tool(tool), *flags, *rocket_compile_flags("cxx"), f'-DTOOLCHAIN_TAG="{tag}"', "-o", str(out), str(SRC_CXX)]
    proc = _run(args)
    if proc.returncode != 0:
        print(f"  skip {case_id}: {(proc.stderr or proc.stdout)[:300]}", file=sys.stderr)
        return None
    out.chmod(out.stat().st_mode | 0o111)
    bsp_store(OUTDIR, case_id=case_id, binary=out, fp=fingerprint(case_id=case_id, profile=tag, sources=[SRC_CXX]))
    return out


def _reuse_or_compile_cxx(case_id: str, existing: Path, tool: str, flags: list[str], tag: str) -> Path | None:
    out = OUTDIR / case_id
    if existing.is_file() and (not SRC_CXX.is_file() or existing.stat().st_mtime >= SRC_CXX.stat().st_mtime):
        shutil.copy2(existing, out)
        out.chmod(out.stat().st_mode | 0o111)
        print(f"  reuse {existing.name} → {case_id}")
        return out
    return _compile_cxx(case_id, tool, flags, tag)


def _stage_cmake(*, use_g16: bool, case_id: str, tag: str) -> Path | None:
    sources = [SRC_CXX, CMAKE_SRC / "CMakeLists.txt"]
    profile = "cmake_g16" if use_g16 else "cmake_host"
    hit, _, _ = bsp_try_reuse(OUTDIR, case_id=case_id, sources=sources, profile=profile)
    if hit:
        print(f"  bsp {case_id}")
        return hit
    build = OUTDIR / ("cmake-build-g16" if use_g16 else "cmake-build-host")
    build.mkdir(parents=True, exist_ok=True)
    cfg = ["cmake", *ninja_generator_args(), "-S", str(CMAKE_SRC), "-B", str(build)]
    if use_g16:
        cfg.extend([f"-DCMAKE_TOOLCHAIN_FILE={TOOLCHAIN_CMAKE}", "-DGROK16_PROFILE=belt_2_0"])
    else:
        cfg.extend(
            [
                f"-DCMAKE_CXX_COMPILER={_host_gxx()}",
                "-DGROK16_HOST_PLANE=ON",
            ]
        )
    proc = _run(cfg)
    if proc.returncode != 0:
        print(f"  skip cmake configure: {(proc.stderr or proc.stdout)[:400]}", file=sys.stderr)
        return None
    proc = _run(["cmake", "--build", str(build), "-j", str(os.cpu_count() or 4)])
    if proc.returncode != 0:
        print(f"  skip cmake build: {(proc.stderr or proc.stdout)[:400]}", file=sys.stderr)
        return None
    binary = build / "grok16_speed_demo"
    if not binary.is_file():
        print("  skip cmake: grok16_speed_demo unfound", file=sys.stderr)
        return None
    staged = OUTDIR / case_id
    shutil.copy2(binary, staged)
    staged.chmod(staged.stat().st_mode | 0o111)
    bsp_store(OUTDIR, case_id=case_id, binary=staged, fp=fingerprint(case_id=case_id, profile=profile, sources=sources))
    return staged


def stage() -> int:
    if not SRC_CXX.is_file() or not SRC_C.is_file() or not SRC_PY.is_file():
        print("field-exec-stage: skip — speed-demo sources unfound", file=sys.stderr)
        return 0
    OUTDIR.mkdir(parents=True, exist_ok=True)
    host_gcc = _host_gcc()
    host_gxx = _host_gxx()
    runners: list[dict] = []
    errors: list[str] = []

    print("field-exec-stage: wave conversion (one-time, not timed in compare)")

    # C — host gcc -O2
    print("\n=== C — host gcc -O2 ===")
    c_host = _compile_c(
        "c_host_o2",
        host_gcc,
        ["-std=gnu17", "-O2", "-march=native", "-fPIE"],
        "c_host_o2",
    )
    if c_host:
        runners.append(
            {
                "id": "c_host_o2",
                "label": "C — host gcc -O2",
                "lang": "c",
                "group": "host",
                "kind": "binary",
                "path": str(c_host),
                "color": "#60a5fa",
            }
        )
    else:
        errors.append("c_host_o2")

    # C — g16 belt_2
    if G16.is_file():
        print("\n=== C — g16 belt_2_0 ===")
        c_flags = _profile_flags("belt_2_0", "c") or ["-std=gnu17", "-O3", "-march=native"]
        link = _profile_flags("belt_2_0", "link") or []
        c_g16 = _compile_c("c_g16_belt_2", str(G16), [*_g16_extra(), *_merge_g16_flags(c_flags, link)], "c_g16_belt_2")
        if c_g16:
            runners.append(
                {
                    "id": "c_g16_belt_2",
                    "label": "C — g16 belt_2_0",
                    "lang": "c",
                    "group": "g16",
                    "kind": "binary",
                    "path": str(c_g16),
                    "color": "#38bdf8",
                }
            )
        else:
            errors.append("c_g16_belt_2")

    # C++ — host g++ -O2 (reuse prior bench if fresh)
    print("\n=== C++ — host g++ -O2 ===")
    cxx_host = _reuse_or_compile_cxx(
        "cxx_host_o2",
        ROOT / "data" / "bench" / "speed_demo_host_gcc_o2",
        host_gxx,
        ["-std=gnu++23", "-O2", "-march=native", "-fPIE"],
        "cxx_host_o2",
    )
    if cxx_host:
        runners.append(
            {
                "id": "cxx_host_o2",
                "label": "C++ — host g++ -O2",
                "lang": "cxx",
                "group": "host",
                "kind": "binary",
                "path": str(cxx_host),
                "color": "#94a3b8",
            }
        )
    else:
        errors.append("cxx_host_o2")

    # C++ — g16 belt_2
    if G16.is_file():
        print("\n=== C++ — g16 belt_2_0 ===")
        cxx_flags = _profile_flags("belt_2_0", "cxx") or ["-std=gnu++26", "-O3", "-march=native"]
        link = _profile_flags("belt_2_0", "link") or []
        cxx_g16 = _reuse_or_compile_cxx(
            "cxx_g16_belt_2",
            ROOT / "data" / "bench" / "speed_demo_g16_belt_2_0",
            str(G16),
            [*_g16_extra(), *_merge_g16_flags(cxx_flags, link)],
            "cxx_g16_belt_2",
        )
        if cxx_g16:
            runners.append(
                {
                    "id": "cxx_g16_belt_2",
                    "label": "C++ — g16 belt_2_0",
                    "lang": "cxx",
                    "group": "g16",
                    "kind": "binary",
                    "path": str(cxx_g16),
                    "color": "#3ecf8e",
                }
            )
        else:
            errors.append("cxx_g16_belt_2")

    # CMake — g16 belt_2, else host g++ via same CMakeLists
    if TOOLCHAIN_CMAKE.is_file() and G16.is_file():
        print("\n=== CMake — g16 belt_2_0 ===")
        cmake_bin = _stage_cmake(use_g16=True, case_id="cmake_belt_2", tag="cmake_belt_2_0")
        if cmake_bin:
            runners.append(
                {
                    "id": "cmake_belt_2",
                    "label": "CMake — g16 belt_2_0",
                    "lang": "cmake",
                    "group": "g16",
                    "kind": "binary",
                    "path": str(cmake_bin),
                    "color": "#a78bfa",
                }
            )
        else:
            errors.append("cmake_belt_2")
    print("\n=== CMake — host g++ -O2 ===")
    cmake_host = _stage_cmake(use_g16=False, case_id="cmake_host_o2", tag="cmake_host_o2")
    if cmake_host:
        runners.append(
            {
                "id": "cmake_host_o2",
                "label": "CMake — host g++ -O2",
                "lang": "cmake",
                "group": "host",
                "kind": "binary",
                "path": str(cmake_host),
                "color": "#c4b5fd",
            }
        )
    else:
        errors.append("cmake_host_o2")

    # Python — host CPython (script, no compile)
    print("\n=== Python — host CPython ===")
    runners.append(
        {
            "id": "python_host",
            "label": "Python — host CPython 3",
            "lang": "python",
            "group": "host",
            "kind": "script",
            "cmd": [shutil.which("python3") or "python3", str(SRC_PY)],
            "env": {"TOOLCHAIN_TAG": "python_host"},
            "color": "#fbbf24",
        }
    )

    # Python — gpy-16
    if GPY.is_file():
        print("\n=== Python — gpy-16 GrokVM ===")
        runners.append(
            {
                "id": "python_gpy",
                "label": "Python — gpy-16 GrokVM",
                "lang": "python",
                "group": "g16",
                "kind": "script",
                "cmd": [str(GPY), str(SRC_PY)],
                "env": {"TOOLCHAIN_TAG": "python_gpy"},
                "color": "#f472b6",
            }
        )

    doc = {
        "schema": "grok16-field-exec-manifest/v1",
        "staged_at": _utc(),
        "doctrine": {
            "wave_conversion": True,
            "ironclad_instant": True,
            "compare_axis": "field_execution_ops_per_sec",
            "not_compared": ["compile_ms", "wave_convert_wall", "cmake_configure"],
            "statement": "Stage once (wave convert). Compare runs field execution only.",
        },
        "order": [r["id"] for r in runners],
        "runners": runners,
        "errors": errors,
    }
    MANIFEST.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"\nfield-exec-stage: {len(runners)} runners → {MANIFEST}")
    if errors:
        print(f"field-exec-stage: skipped {len(errors)} unfound: {', '.join(errors)}", file=sys.stderr)
    if not runners:
        print("field-exec-stage: skip — no runners staged", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(stage())