#!/usr/bin/env pythong
"""Grok16 AI agent compile — structured JSON for machines, not humans at the TTY."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1])).resolve()
PREFIX = Path(os.environ.get("G16_PREFIX", ROOT)).resolve()
os.environ.setdefault("GROK16_ROOT", str(ROOT))
os.environ.setdefault("G16_PREFIX", str(PREFIX))
G16 = PREFIX / "bin" / "g16"
PROFILE = os.environ.get("G16_AI_PROFILE", "ai_agent")
PROFILE_SCRIPT = ROOT / "scripts" / "grok16-profile-flags.py"
COMB_SCRIPT = ROOT / "lib" / "g16-compile-combinatronics.py"
RECEIPT_SCRIPT = ROOT / "lib" / "g16-compile-receipt.py"

# Grok16 crt objects are non-PIE — strip profile PIE and static-link executables.
_PIE_FLAGS = frozenset({"-fPIE", "-pie", "-fpie", "-fpic", "-fPIC", "-Wl,-pie"})


def _exec_link_fixup(flags: list[str]) -> list[str]:
    cleaned = [
        f for f in flags
        if f not in _PIE_FLAGS and not f.startswith("-Wl,-pie")
    ]
    for req in ("-fno-pie", "-no-pie", "-static"):
        if req not in cleaned:
            cleaned.append(req)
    extra = os.environ.get("G16_EXTRA_LINK_FLAGS", "").strip().split()
    for f in extra:
        if f and f not in cleaned:
            cleaned.append(f)
    return cleaned


def _comb_mod():
    if not COMB_SCRIPT.is_file():
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location("g16_compile_combinatronics", COMB_SCRIPT)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _receipt_mod():
    if not RECEIPT_SCRIPT.is_file():
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location("g16_compile_receipt", RECEIPT_SCRIPT)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _profile_flags(kind: str = "cxx", *, profile: str | None = None) -> list[str]:
    prof = profile or PROFILE
    if not PROFILE_SCRIPT.is_file():
        return ["-std=gnu++26", "-O2"]
    env = {**os.environ, "GROK16_ROOT": str(ROOT), "G16_PREFIX": str(PREFIX), "G16_BENCH_PROFILE": prof}
    proc = subprocess.run(
        [sys.executable, str(PROFILE_SCRIPT), prof, kind],
        capture_output=True, text=True, timeout=30, env=env,
    )
    if proc.returncode != 0:
        return ["-std=gnu++26", "-O2"]
    return proc.stdout.strip().split()


def _parse_errors(stderr: str) -> list[dict]:
    rows: list[dict] = []
    for line in stderr.splitlines():
        m = re.match(r"([^:]+):(\d+):(\d+):\s*(error|warning|note):\s*(.*)", line)
        if m:
            rows.append({
                "file": m.group(1),
                "line": int(m.group(2)),
                "column": int(m.group(3)),
                "severity": m.group(4),
                "message": m.group(5),
            })
    return rows


def compile_source(
    source: str,
    *,
    lang: str = "cxx",
    out_name: str = "g16_ai_out",
    out_dir: str | Path | None = None,
) -> dict:
    if not G16.is_file():
        return {"ok": False, "error": f"missing g16 at {G16}"}
    comb_mod = _comb_mod()
    gate: dict = {}
    profile = PROFILE
    if comb_mod and hasattr(comb_mod, "compile_gate"):
        gate = comb_mod.compile_gate(profile=PROFILE, sustained=True)
        if gate.get("blocked"):
            return {
                "schema": "grok16-ai-compile/v1",
                "ok": False,
                "blocked": True,
                "reason": gate.get("reason"),
                "truth": gate.get("truth"),
                "profile": gate.get("profile"),
            }
        profile = str(gate.get("profile") or PROFILE)
    suffix = ".cpp" if lang == "cxx" else ".c"
    std_flag = "-std=gnu++26" if lang == "cxx" else "-std=gnu17"
    with tempfile.TemporaryDirectory(prefix="g16-ai-") as td:
        src = Path(td) / f"snippet{suffix}"
        out = Path(td) / out_name
        src.write_text(source, encoding="utf-8")
        env = {**os.environ, "GROK16_ROOT": str(ROOT), "G16_PREFIX": str(PREFIX), "G16_BENCH_PROFILE": profile}
        flags = _profile_flags("cxx" if lang == "cxx" else "c", profile=profile)
        if std_flag not in flags:
            flags = [std_flag, *flags]
        flags = _exec_link_fixup(flags)
        cmd = [str(G16), *flags, "-o", str(out), str(src)]
        t0 = time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120, env=env)
        ms = int((time.time() - t0) * 1000)
        errors = _parse_errors(proc.stderr)
        stamp: dict = {}
        receipt: dict = {}
        if proc.returncode == 0 and out.is_file() and comb_mod and hasattr(comb_mod, "stamp_compiled_artifact"):
            stamp = comb_mod.stamp_compiled_artifact(
                out,
                comb=gate.get("combinatronics"),
                compile_meta={"profile": profile, "lang": lang, "compile_ms": ms},
            )
        binary_path = ""
        if proc.returncode == 0 and out.is_file():
            persist = out_dir or os.environ.get("G16_COMPILE_PERSIST_DIR", "").strip()
            if persist:
                dest = Path(persist) / out_name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(out, dest)
                binary_path = str(dest)
            else:
                state = Path(os.environ.get("NEXUS_STATE_DIR", ROOT / ".grok16-state"))
                state.mkdir(parents=True, exist_ok=True)
                dest = state / f"{out_name}-{int(time.time() * 1000)}"
                shutil.copy2(out, dest)
                binary_path = str(dest)
        rec_mod = _receipt_mod()
        if rec_mod and hasattr(rec_mod, "record"):
            receipt = rec_mod.record(
                source_text=source,
                binary_path=binary_path,
                profile=profile,
                lang=lang,
            )
        return {
            "schema": "grok16-ai-compile/v1",
            "ok": proc.returncode == 0,
            "profile": profile,
            "lang": lang,
            "compile_ms": ms,
            "returncode": proc.returncode,
            "diagnostics": errors,
            "stderr_tail": proc.stderr[-4000:] if proc.stderr else "",
            "stdout": proc.stdout.strip(),
            "binary": binary_path,
            "combinatronics_gate": gate or None,
            "combinatronics_stamp": stamp or None,
            "compile_receipt": receipt or None,
            "hostess_truth_floor": 58,
        }


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({
            "usage": "grok16-ai-compile.py -c 'code' | file.cpp | --json doc.json",
            "profile": PROFILE,
            "default_for": "AI agents — presumes compiler used more than human TTY",
        }, indent=2))
        return 2
    if sys.argv[1] in ("-c", "--code"):
        code = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
        lang = "cxx" if "int main" in code or "#include" in code else "cxx"
        doc = compile_source(code, lang=lang)
        print(json.dumps(doc, indent=2))
        return 0 if doc.get("ok") else 1
    path = Path(sys.argv[1])
    if path.is_file():
        lang = "cxx" if path.suffix in (".cpp", ".cxx", ".cc") else "c"
        doc = compile_source(path.read_text(encoding="utf-8"), lang=lang)
        print(json.dumps(doc, indent=2))
        return 0 if doc.get("ok") else 1
    print(json.dumps({"ok": False, "error": "usage: -c code or file"}, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())