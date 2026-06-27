#!/usr/bin/env pythong
"""Sweet Anita · Field Broadcasting — OBS stack, platforms, decks, best dB, panel preview."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
SG = Path(os.environ.get("SG_ROOT", str(INSTALL.parent.parent)))
DOCTRINE = INSTALL / "data" / "field-sweet-anita-broadcast-doctrine.json"
PANEL_CACHE = STATE / "sweet-anita-broadcast-panel.json"


def _now() -> str:
    global _SOVEREIGN_CLOCK_MOD
    if _SOVEREIGN_CLOCK_MOD is None:
        import importlib.util
        _p = Path(__file__).resolve().parent / "sovereign-clock.py"
        _s = importlib.util.spec_from_file_location("sovereign_clock", _p)
        if not _s or not _s.loader:
            raise ImportError("sovereign-clock.py missing")
        _SOVEREIGN_CLOCK_MOD = importlib.util.module_from_spec(_s)
        _s.loader.exec_module(_SOVEREIGN_CLOCK_MOD)
    return _SOVEREIGN_CLOCK_MOD.utc_z()


_SOVEREIGN_CLOCK_MOD = None



def _load(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _sg_root() -> Path:
    if SG.is_dir():
        return SG
    return INSTALL.parent.parent


def _obs_plugin_home() -> Path:
    return Path.home() / ".config/obs-studio/plugins/obs-field-voice-filter"


def _obs_running() -> bool:
    try:
        out = subprocess.run(
            ["pgrep", "-x", "obs"],
            capture_output=True,
            timeout=2,
        )
        return out.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _posterity_bridge() -> dict[str, Any]:
    try:
        import importlib.util
        bridge_py = Path(__file__).resolve().parent / "obs-threat-posterity-bridge.py"
        spec = importlib.util.spec_from_file_location("obs_threat_posterity_bridge", bridge_py)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.panel_json()
    except Exception:
        pass
    cached = _load(STATE / "obs-threat-posterity-panel.json", {})
    return cached if cached else {}


def _obs_stack_doc() -> dict[str, Any]:
    for p in (
        _obs_plugin_home() / "data/field-obs-stack.json",
        _sg_root() / "OBS-FieldVoiceFilter/data/field-obs-stack.json",
    ):
        doc = _load(p, {})
        if doc:
            doc["_path"] = str(p)
            return doc
    return {}


def _obs_plugin_installed() -> bool:
    so = _obs_plugin_home() / "bin/64bit/obs-field-voice-filter.so"
    return so.is_file()


def _audio_train() -> dict[str, Any]:
    for p in (STATE / "audio-train-panel.json", INSTALL / "state/audio-train-panel.json"):
        doc = _load(p, {})
        if doc:
            return doc
    return {}


def panel_json(*, refresh: bool = False) -> dict[str, Any]:
    doctrine = _load(DOCTRINE, {})
    stack = _obs_stack_doc()
    posterity = _posterity_bridge()
    audio = _audio_train()
    audio_best = doctrine.get("audio_best") or {}

    obs_filters = (stack.get("filters") or []) if stack else (doctrine.get("obs_field_stack") or {}).get("filters", [])

    platforms = doctrine.get("platforms") or []
    decks = doctrine.get("decks") or []
    preview = doctrine.get("preview") or {
        "mode": "embedded",
        "tunnel_desktop": False,
        "tunnel_obs_nested": False,
    }

    doc: dict[str, Any] = {
        "schema": "sweet-anita-broadcast/v1",
        "updated": _now(),
        "title": doctrine.get("title") or "Sweet_Anita · Field Broadcasting",
        "channel_name": doctrine.get("channel_name") or "Sweet_Anita",
        "motto": doctrine.get("motto") or "",
        "branding": doctrine.get("branding") or {},
        "preview": preview,
        "audio_best": audio_best,
        "platforms": platforms,
        "decks": decks,
        "obs": {
            "running": _obs_running(),
            "field_plugin_installed": _obs_plugin_installed(),
            "plugin_home": str(_obs_plugin_home()),
            "stack": stack,
            "filters": obs_filters,
            "recommended_stack": [
                {"target": "scene", "filter": "Field Best — Scene Guard", "id": "sg_field_scene_guard", "spiderweb": True, "prune_tree": True},
            ],
            "defaults": stack.get("defaults") or "clean_passthrough",
            "security": posterity.get("security") or stack.get("security") or {},
            "posterity": posterity.get("posterity") or {},
            "repeat_inspect": posterity.get("repeat_inspect") or {},
            "threat_summary": (posterity.get("threat_ledger") or {}).get("summary") or {},
        },
        "posterity_motto": posterity.get("motto") or doctrine.get("security_posterity", {}).get("motto"),
        "audio_live": {
            "sources": (audio.get("stats") or {}).get("sources", 0),
            "acceptable": (audio.get("stats") or {}).get("acceptable", 0),
            "dimensions": audio.get("dimensions") or {},
            "tagline": audio.get("tagline") or "",
        },
        "status": {
            "broadcast_ready": _obs_plugin_installed(),
            "preview_mode": preview.get("mode", "embedded"),
            "platform_count": len(platforms),
            "deck_count": len(decks),
        },
    }

    if refresh or not PANEL_CACHE.is_file():
        PANEL_CACHE.parent.mkdir(parents=True, exist_ok=True)
        PANEL_CACHE.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc


def us_obs_slice() -> dict[str, Any]:
    """Compact OBS block for US tab."""
    full = panel_json()
    obs = full.get("obs") or {}
    threat = obs.get("threat_summary") or {}
    posterity = obs.get("posterity") or {}
    return {
        "schema": "us-obs-field/v2",
        "updated": full.get("updated"),
        "motto": full.get("posterity_motto")
        or "Posterity inspect + repeat removal — Scene Guard on the scene.",
        "obs_running": obs.get("running"),
        "plugin_installed": obs.get("field_plugin_installed"),
        "filters": obs.get("filters"),
        "defaults": obs.get("defaults"),
        "audio_best": full.get("audio_best"),
        "posterity_engine": posterity.get("engine"),
        "repeat_inspect": obs.get("repeat_inspect", {}).get("engine"),
        "posterity_confirm_avg": threat.get("avg_posterity_confirm"),
        "threat_rows": threat.get("rows", 0),
        "last_markers": threat.get("markers") or {},
        "jump": "sweet-anita",
    }


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").lower()
    if cmd in ("json", "panel", "status"):
        print(json.dumps(panel_json(refresh=cmd == "panel"), ensure_ascii=False, indent=2))
        return 0
    if cmd == "us":
        print(json.dumps(us_obs_slice(), ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({"error": f"unknown command {cmd}"}, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())