#!/usr/bin/env pythong
"""GPY-16 CHIPs accelerator — wire 79-language field_opt hot paths into gpy-16 runtime."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

GROK16 = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", GROK16.parent))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", INSTALL / ".nexus-state"))
CHIPS_MANIFEST = INSTALL / "Queen" / "data" / "chips-g16-manifest.json"
DOCTRINE = GROK16 / "data" / "gpy-16-speed-doctrine.json"
PANEL = STATE / "gpy16-chips-accelerate-panel.json"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def apply_fast_profile(*, profile: str | None = None) -> dict[str, str]:
    """Apply CHIPs-aligned fast env — call before gpy-16 hot runs."""
    doctrine = _load(DOCTRINE, {})
    prof = profile or os.environ.get("GPY16_PROFILE", "fastest")
    fast = dict(doctrine.get("fast_env") or {})
    if prof == "field_opt":
        fast.pop("GPY16_SKIP_AI_BOOT", None)
    applied: dict[str, str] = {}
    for k, v in fast.items():
        if k not in os.environ:
            os.environ[k] = str(v)
            applied[k] = str(v)
    os.environ.setdefault("GROKPY_PROFILE", prof)
    os.environ.setdefault("GPY16_PROFILE", prof)
    return applied


def chips_posture() -> dict[str, Any]:
    manifest = _load(CHIPS_MANIFEST, {})
    langs = _load(GROK16 / "data" / "grok16-languages.json", {})
    language_count = len(langs.get("languages") or {})
    written = sum(1 for m in (langs.get("languages") or {}).values() if m.get("compiler_written"))
    return {
        "ok": bool(manifest.get("hot_paths")),
        "profile": manifest.get("profile", "field_opt"),
        "hot_path_count": len(manifest.get("hot_paths") or []),
        "compiler_flags": manifest.get("compiler_flags") or [],
        "languages_total": language_count,
        "compiler_written": written,
        "chips_universal": bool(langs.get("chips_universal")),
        "gpy_pair": "Grok16/g16",
    }


def publish_panel(*, refresh: bool = False) -> dict[str, Any]:
    applied = apply_fast_profile()
    chips = chips_posture()
    cache_dir = STATE / "gpy16-bytecode-cache"
    panel = {
        "schema": "gpy16-chips-accelerate/v1",
        "updated": _now(),
        "ok": chips.get("ok", False),
        "profile": os.environ.get("GPY16_PROFILE", "fastest"),
        "fast_applied": applied,
        "chips": chips,
        "bytecode_cache_dir": str(cache_dir),
        "bytecode_cache_entries": len(list(cache_dir.glob("*.gpy16c"))) if cache_dir.is_dir() else 0,
        "motto": "CHIPs + 79 langs → GPY-16 huge speedups",
    }
    STATE.mkdir(parents=True, exist_ok=True)
    PANEL.write_text(json.dumps(panel, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": panel["ok"], "panel": panel}


def main() -> int:
    import sys
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "panel").strip().lower()
    if cmd in ("apply", "fast", "boot"):
        applied = apply_fast_profile(profile=sys.argv[2] if len(sys.argv) > 2 else None)
        print(json.dumps({"ok": True, "applied": applied}, indent=2))
        return 0
    if cmd in ("panel", "json", "status"):
        rep = publish_panel(refresh="--refresh" in sys.argv)
        print(json.dumps(rep.get("panel") or rep, indent=2))
        return 0
    print(json.dumps({"usage": "gpy16-chips-accelerate.py [panel|apply [profile]]"}, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())