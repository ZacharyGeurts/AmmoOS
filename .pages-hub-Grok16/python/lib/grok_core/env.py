"""GrokPy field environment — Queen sovereign wire, AI paths inline."""
from __future__ import annotations

import os
import sys
from typing import Any

from grok_core.paths import gpy16_root, grok16_root, grokpy_root, hostess_root, queen_root, sg_root


def field_env(*, profile: str | None = None) -> dict[str, str]:
    root = gpy16_root()
    g16 = grok16_root()
    sg = sg_root()
    sg_s = str(sg)
    env: dict[str, str] = {
        **os.environ,
        "GROKPY_ROOT": str(root),
        "PYTHONG_ROOT": str(root),
        "GPY16_ROOT": str(root),
        "GROK16_ROOT": str(g16),
        "G16_PREFIX": os.environ.get("G16_PREFIX", str(g16)),
        "GPY16_BUILTIN": "1",
        "GROKPY_FIELD": "1",
        "PYTHONG_FIELD": "1",
        "GPY16_FIELD": "1",
        "GROKPY_AI_READY": "1",
        "PYTHONG_AI_READY": "1",
        "SG_ROOT": sg_s,
        "QUEEN_ROOT": str(queen_root()),
        "HOSTESS7_ROOT": str(hostess_root()),

        "FINAL_EYE_ROOT": os.environ.get("FINAL_EYE_ROOT", str(sg / "Final_Eye")),
        "FINAL_EAR_ROOT": os.environ.get("FINAL_EAR_ROOT", str(sg / "Final_Ear")),
        "QUEEN_SENSE_NEURAL": str(queen_root() / "lib" / "queen-sense-neural.py"),
        "FINAL_EAR_NEURAL": str(sg / "Final_Ear" / "zocr_neural_assist.py"),
        "FINAL_EYE_NEURAL": str(sg / "Final_Eye" / "zocr_neural_assist.py"),
        "FINAL_EAR_TRACKER": str(sg / "Final_Ear" / "zocr_sound_tracker.py"),
        "HOSTESS_TRUTH_FLOOR": str(hostess_root() / "data" / "hostess7-truth-floor.json"),
    }
    prof = profile or os.environ.get("GROKPY_PROFILE", os.environ.get("PYTHONG_PROFILE", "field_opt"))
    env["GROKPY_PROFILE"] = prof
    env["PYTHONG_PROFILE"] = prof
    env["GPY16_PROFILE"] = os.environ.get("GPY16_PROFILE", prof)
    if prof in ("fastest", "field_opt"):
        env.setdefault("G16_OPTIMAL_COMBINATRONICS_AT_COMPILE", "0")
    if prof == "fastest":
        for k, v in (
            ("GPY16_FAST", "1"),
            ("GPY16_CACHE", "1"),
            ("GPY16_SKIP_AI_BOOT", "1"),
            ("G16_AI_PROFILE", "ai_agent"),
            ("AML_FAST", "1"),
        ):
            env.setdefault(k, v)
    if prof == "hostess_brain":
        env["GROKPY_HOSTESS_LANE"] = "1"
        env["PYTHONG_HOSTESS_LANE"] = "1"
    lib = str(root / "lib")
    interp = str(root / "interpreter")
    stdlib = str(root / "stdlib")
    pg = str(sg / "PythonG" / "lib")
    extra = os.pathsep.join([lib, interp, stdlib, pg])
    env["PYTHONPATH"] = extra + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    path_bins = os.pathsep.join([
        str(g16 / "bin"),
        str(g16 / "libexec" / "grok16"),
        str(queen_root() / "scripts"),
        str(queen_root() / "bin"),
        str(sg / "PythonG" / "bin"),
    ])
    env["PATH"] = path_bins + (os.pathsep + env["PATH"] if env.get("PATH") else "")
    return env


def field_status_slice() -> dict[str, Any]:
    return {
        "grokpy_field": os.environ.get("GROKPY_FIELD") == "1",
        "ai_ready": os.environ.get("GROKPY_AI_READY") == "1",
        "profile": os.environ.get("GROKPY_PROFILE", "field_opt"),
        "grok_vm": True,
        "field_cpython": sys.executable,
        "hostess_lane": os.environ.get("GROKPY_HOSTESS_LANE") == "1",
        "final_ear": os.environ.get("FINAL_EAR_ROOT"),
        "final_eye": os.environ.get("FINAL_EYE_ROOT"),
    }