#!/usr/bin/env python3
"""Parallel field slice publish — each tab's fields refresh symmetrically."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
PANEL_JSON = STATE / "threat-panel.json"

# panel JSON key -> (script relative to lib/, cli args)
FIELD_SLICES: dict[str, tuple[str, list[str]]] = {
    "field_hardware": ("field-hardware-probe.py", ["json"]),
    "field_hazard_onset": ("field-hazard-onset.py", ["panel"]),
    "lethal_enforcement": ("lethal-enforcement.py", ["panel"]),
    "hostess7_lethal_insight": ("hostess7-lethal-insight.py", ["panel"]),
    "signals_field": ("signals-field.py", ["json"]),
    "field_antenna": ("field-antenna-orchestrator.py", ["json"]),
    "field_radio": ("field-radio-catcher.py", ["json"]),
    "field_dns": ("field-dns.py", ["json"]),
    "field_outside_talk": ("field-outside-talk.py", ["json"]),
    "field_drive": ("field-drive-system.py", ["json"]),
    "home_protector": ("home-protector.py", ["json"]),
    "audio_train": ("audio-train.py", ["json"]),
    "field_rf": ("field-rf-sentinel.py", ["json"]),
    "terror_spiderweb": ("terror-spiderweb.py", ["json"]),
    "precision_field": ("precision-field.py", ["json"]),
    "h7_library": ("h7-library-bridge.py", ["build"]),
    "field_brain": ("field-brain-panel.py", ["json"]),
    "packet_field": ("packet-field.py", ["json"]),
    "host_attacks": ("host-attack-map.py", ["json-panel"]),
    "us_field": ("field-us-intel.py", ["json"]),
    "field_command": ("field-command.py", ["json"]),
    "browser_awareness": ("browser-awareness.py", ["json"]),
}

STATE_SLICES: dict[str, tuple[str, dict[str, Any]]] = {
    "gatekeeper": ("connection-intent.json", {"connections": [], "harm_candidates": 0}),
    "angel_dossiers": ("angel-dossiers.json", {"dossier_count": 0, "dossiers": []}),
    "angel_research": ("angel-research.json", {"tables": {}}),
    "human_dossier": ("human-dossier.json", {"ip_count": 0, "ips": []}),
}


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL)
    env["NEXUS_STATE_DIR"] = str(STATE)
    env.setdefault("HOSTESS7_ROOT", "/home/default/Desktop/SG/Hostess7")
    env.setdefault("HOSTESS7_TEAM_FIELD", "/media/default/HOSTESS7_TEAM/fieldstorage")
    return env


def _read_state_slice(key: str, filename: str, default: dict[str, Any]) -> tuple[str, Any | None]:
    fp = STATE / filename
    if not fp.is_file():
        return key, dict(default)
    try:
        doc = json.loads(fp.read_text(encoding="utf-8"))
        return key, doc if isinstance(doc, (dict, list)) else dict(default)
    except (OSError, json.JSONDecodeError):
        return key, dict(default)


def _run_slice(key: str, script_rel: str, args: list[str]) -> tuple[str, Any | None]:
    script = INSTALL / "lib" / script_rel
    if not script.is_file():
        return key, None
    try:
        proc = subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True,
            text=True,
            timeout=90,
            env=_env(),
        )
        if proc.returncode != 0 or not (proc.stdout or "").strip():
            return key, None
        return key, json.loads(proc.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return key, None


def _load_panel() -> dict[str, Any]:
    try:
        return json.loads(PANEL_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"field": True}


def _save_panel(doc: dict[str, Any]) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    tmp = PANEL_JSON.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(PANEL_JSON)


def publish_parallel(*, max_workers: int = 25) -> dict[str, Any]:
    doc = _load_panel()
    doc["field"] = True
    doc["parallel_load"] = True
    updated: list[str] = []
    failed: list[str] = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures: dict[Any, str] = {
            pool.submit(_run_slice, key, script, args): key
            for key, (script, args) in FIELD_SLICES.items()
        }
        for key, (filename, default) in STATE_SLICES.items():
            futures[pool.submit(_read_state_slice, key, filename, default)] = key
        for fut in as_completed(futures):
            key = futures[fut]
            try:
                k, val = fut.result()
            except Exception:
                failed.append(key)
                continue
            if val is None:
                failed.append(k)
                continue
            doc[k] = val
            updated.append(k)

    doc["field_slices_updated"] = updated
    doc["field_slices_failed"] = failed
    _save_panel(doc)
    return {
        "ok": True,
        "updated": updated,
        "failed": failed,
        "slice_count": len(updated),
        "panel": doc,
    }


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("usage: field-panel-parallel.py [publish|json]", file=sys.stderr)
        return 1
    cmd = sys.argv[1]
    if cmd == "publish":
        publish_parallel()
        return 0
    if cmd == "json":
        print(json.dumps(publish_parallel(), ensure_ascii=False))
        return 0
    print(json.dumps({"ok": False, "error": "unknown_command"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())