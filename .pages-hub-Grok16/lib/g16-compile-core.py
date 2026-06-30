#!/usr/bin/env pythong
"""G16 compile core — shared lower→bin/g16 path (Grok16-owned, no host toolchains)."""
from __future__ import annotations

import importlib.util
import os
import time
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1])).resolve()
AI_COMPILE = ROOT / "scripts" / "grok16-ai-compile.py"

os.environ.setdefault("GROK16_ROOT", str(ROOT))
os.environ.setdefault("G16_PREFIX", str(ROOT))


def ai_mod() -> Any | None:
    if not AI_COMPILE.is_file():
        return None
    spec = importlib.util.spec_from_file_location("g16_ai_core", AI_COMPILE)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def compile_lowered(
    source: str,
    *,
    kind: str = "cxx",
    lang: str = "",
    lane: str = "",
    out_name: str = "g16_out",
    out_dir: str | Path | None = None,
    profile: str = "",
) -> dict[str, Any]:
    """Compile lowered C/C++ with bin/g16 only."""
    t0 = time.perf_counter()
    ai = ai_mod()
    if not ai or not hasattr(ai, "compile_source"):
        return {"ok": False, "error": "g16_ai_unavailable", "compiler": "g16", "lang": lang}
    if profile:
        os.environ["G16_AI_PROFILE"] = profile
    elif not os.environ.get("G16_AI_PROFILE"):
        os.environ["G16_AI_PROFILE"] = "ai_agent"
    out = ai.compile_source(source, lang=kind, out_name=out_name, out_dir=out_dir)
    ms = int((time.perf_counter() - t0) * 1000)
    return {
        "ok": bool(out.get("ok")),
        "compiled": bool(out.get("ok")),
        "compiler": "g16",
        "lang": lang,
        "lane": lane or f"{lang}→{kind}",
        "lowered": True,
        "host_toolchain": False,
        "third_party": False,
        "compile_ms": ms,
        "binary": out.get("binary"),
        "stderr": out.get("stderr_tail") or out.get("stderr"),
        "errors": out.get("diagnostics"),
        "g16": out,
    }