#!/usr/bin/env pythong
"""Broadcaster Studio — native OBS/XSplit-style engine, scenes, devices, threat-gated live."""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", Path(__file__).resolve().parents[1]))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", INSTALL / ".nexus-state"))
SG = Path(os.environ.get("SG_ROOT", INSTALL.parent.parent))
DOCTRINE = INSTALL / "data" / "field-broadcaster-studio-doctrine.json"
STUDIO = STATE / "field-broadcaster-studio.json"
PANEL = STATE / "field-broadcaster-studio-panel.json"
RECORDINGS = STATE / "field-broadcaster-portable" / "recordings"
PROC = STATE / "field-broadcaster-studio-proc.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _save(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _uid() -> str:
    return uuid.uuid4().hex[:12]


def _default_studio() -> dict[str, Any]:
    return {
        "schema": "field-broadcaster-studio/v1",
        "updated": _now(),
        "collection": "AmmoOS Default",
        "profile": "Streaming",
        "active_scene": "scene_main",
        "preview_scene": "scene_main",
        "studio_mode": True,
        "streaming": False,
        "recording": False,
        "virtualcam": False,
        "scenes": [
            {"id": "scene_main", "name": "Main", "order": 0},
            {"id": "scene_brb", "name": "BRB", "order": 1},
        ],
        "sources": {
            "scene_main": [
                {"id": "src_display", "name": "Display Capture", "kind": "display", "device": ":0.0", "visible": True, "locked": False},
                {"id": "src_mic", "name": "Microphone", "kind": "audio_input", "device": "default", "visible": True, "muted": False},
            ],
            "scene_brb": [
                {"id": "src_text", "name": "Be Right Back", "kind": "text", "text": "AmmoOS · BRB", "visible": True},
            ],
        },
        "encoder": {"video": "x264", "preset": "veryfast", "bitrate_kbps": 4500, "audio": "aac"},
        "output": {"path": str(RECORDINGS), "format": "mkv"},
    }


def load_studio() -> dict[str, Any]:
    doc = _load(STUDIO, {})
    if not doc.get("scenes"):
        doc = _default_studio()
        _save(STUDIO, doc)
    return doc


def _run_cmd(argv: list[str], *, timeout: int = 8) -> str:
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return (proc.stdout or "") + (proc.stderr or "")
    except (OSError, subprocess.TimeoutExpired):
        return ""


def enumerate_devices() -> dict[str, Any]:
    displays: list[dict[str, Any]] = []
    cameras: list[dict[str, Any]] = []
    audio_in: list[dict[str, Any]] = []
    audio_out: list[dict[str, Any]] = []

    xout = _run_cmd(["xrandr", "--current"])
    for line in xout.splitlines():
        m = re.match(r"^(\S+)\s+connected", line)
        if m:
            displays.append({"id": m.group(1), "name": m.group(1), "kind": "display"})

    if not displays:
        displays = [{"id": ":0.0", "name": "Primary Display", "kind": "display"}]

    vout = _run_cmd(["v4l2-ctl", "--list-devices"])
    dev = ""
    for line in vout.splitlines():
        if line.strip() and not line.startswith("\t") and not line.startswith(" "):
            dev = line.strip().rstrip(":")
        elif "/dev/video" in line:
            cameras.append({"id": line.strip(), "name": dev or line.strip(), "kind": "camera"})

    if not cameras:
        for p in Path("/dev").glob("video*"):
            if p.is_char_device():
                cameras.append({"id": str(p), "name": p.name, "kind": "camera"})

    pout = _run_cmd(["pactl", "list", "short", "sources"])
    for line in pout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            audio_in.append({"id": parts[1], "name": parts[-1] if len(parts) > 3 else parts[1], "kind": "audio_input"})

    pout2 = _run_cmd(["pactl", "list", "short", "sinks"])
    for line in pout2.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            audio_out.append({"id": parts[1], "name": parts[-1] if len(parts) > 3 else parts[1], "kind": "audio_output"})

    if not audio_in:
        audio_in = [{"id": "default", "name": "Default Input", "kind": "audio_input"}]
    if not audio_out:
        audio_out = [{"id": "default", "name": "Default Output", "kind": "audio_output"}]

    return {
        "displays": displays[:8],
        "cameras": cameras[:8],
        "audio_inputs": audio_in[:12],
        "audio_outputs": audio_out[:12],
    }


def _threat_gate() -> dict[str, Any]:
    bridge = INSTALL / "lib" / "obs-threat-posterity-bridge.py"
    if bridge.is_file():
        try:
            spec = importlib.util.spec_from_file_location("bc_threat", bridge)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "panel_json"):
                    doc = mod.panel_json()
                    summary = (doc.get("threat_ledger") or {}).get("summary") or doc.get("threat_summary") or {}
                    blocked = int(summary.get("harm_candidate") or summary.get("blocked") or 0)
                    return {
                        "ok": blocked == 0,
                        "blocked": blocked,
                        "summary": summary,
                        "scene_guard": True,
                        "product": "Broadcaster",
                    }
        except Exception:
            pass
    return {"ok": True, "scene_guard": True, "blocked": 0, "summary": {}}


def _proc_state() -> dict[str, Any]:
    return _load(PROC, {"streaming": False, "recording": False, "pids": {}})


def _set_proc(**kwargs: Any) -> None:
    doc = _proc_state()
    doc.update(kwargs)
    doc["updated"] = _now()
    _save(PROC, doc)


def _ffmpeg_record_start(scene_id: str) -> dict[str, Any]:
    RECORDINGS.mkdir(parents=True, exist_ok=True)
    out = RECORDINGS / f"ammoos-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.mkv"
    display = ":0.0"
    studio = load_studio()
    for src in (studio.get("sources") or {}).get(scene_id) or []:
        if src.get("kind") == "display" and src.get("device"):
            display = str(src["device"])
    argv = [
        "ffmpeg", "-y", "-f", "x11grab", "-framerate", "30", "-i", display,
        "-f", "pulse", "-i", "default", "-c:v", "libx264", "-preset", "veryfast",
        "-c:a", "aac", "-shortest", str(out),
    ]
    try:
        proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        _set_proc(recording=True, record_pid=proc.pid, record_path=str(out), scene_id=scene_id)
        return {"ok": True, "pid": proc.pid, "path": str(out)}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}


def _stop_proc(key: str) -> dict[str, Any]:
    doc = _proc_state()
    pid = doc.get(key)
    if pid:
        try:
            os.kill(int(pid), 15)
        except (OSError, ProcessLookupError, ValueError):
            pass
    _set_proc(recording=False, streaming=False, record_pid=None, stream_pid=None)
    return {"ok": True, "stopped": key}


def scene_add(name: str) -> dict[str, Any]:
    studio = load_studio()
    sid = f"scene_{_uid()}"
    studio.setdefault("scenes", []).append({"id": sid, "name": name or "Scene", "order": len(studio["scenes"])})
    studio.setdefault("sources", {})[sid] = []
    studio["updated"] = _now()
    _save(STUDIO, studio)
    return {"ok": True, "scene_id": sid, "scenes": studio["scenes"]}


def scene_remove(scene_id: str) -> dict[str, Any]:
    studio = load_studio()
    studio["scenes"] = [s for s in studio.get("scenes") or [] if s.get("id") != scene_id]
    sources = studio.get("sources") or {}
    sources.pop(scene_id, None)
    studio["sources"] = sources
    if studio.get("active_scene") == scene_id:
        studio["active_scene"] = (studio["scenes"][0]["id"] if studio["scenes"] else "")
    studio["updated"] = _now()
    _save(STUDIO, studio)
    return {"ok": True, "scenes": studio["scenes"]}


def scene_set_active(scene_id: str, *, preview: bool = False) -> dict[str, Any]:
    studio = load_studio()
    if preview:
        studio["preview_scene"] = scene_id
    else:
        studio["active_scene"] = scene_id
    studio["updated"] = _now()
    _save(STUDIO, studio)
    return {"ok": True, "active_scene": studio.get("active_scene"), "preview_scene": studio.get("preview_scene")}


def source_add(scene_id: str, *, kind: str, name: str = "", device: str = "") -> dict[str, Any]:
    studio = load_studio()
    sid = f"src_{_uid()}"
    src = {"id": sid, "name": name or kind.title(), "kind": kind, "device": device or "default", "visible": True}
    studio.setdefault("sources", {}).setdefault(scene_id, []).append(src)
    studio["updated"] = _now()
    _save(STUDIO, studio)
    return {"ok": True, "source": src}


def source_remove(scene_id: str, source_id: str) -> dict[str, Any]:
    studio = load_studio()
    rows = studio.setdefault("sources", {}).get(scene_id) or []
    studio["sources"][scene_id] = [r for r in rows if r.get("id") != source_id]
    studio["updated"] = _now()
    _save(STUDIO, studio)
    return {"ok": True}


def source_move(scene_id: str, source_id: str, direction: str) -> dict[str, Any]:
    studio = load_studio()
    rows = studio.setdefault("sources", {}).get(scene_id) or []
    idx = next((i for i, r in enumerate(rows) if r.get("id") == source_id), -1)
    if idx < 0:
        return {"ok": False, "error": "source_not_found"}
    j = idx - 1 if direction == "up" else idx + 1
    if 0 <= j < len(rows):
        rows[idx], rows[j] = rows[j], rows[idx]
    studio["sources"][scene_id] = rows
    studio["updated"] = _now()
    _save(STUDIO, studio)
    return {"ok": True, "sources": rows}


def go_live(*, scene_id: str = "") -> dict[str, Any]:
    gate = _threat_gate()
    if not gate.get("ok"):
        return {"ok": False, "error": "threat_blocked", "threat": gate}
    studio = load_studio()
    sid = scene_id or studio.get("active_scene") or "scene_main"
    studio["streaming"] = True
    studio["active_scene"] = sid
    studio["updated"] = _now()
    _save(STUDIO, studio)
    _set_proc(streaming=True, scene_id=sid)
    return {"ok": True, "streaming": True, "scene_id": sid, "threat": gate, "engine": "studio"}


def start_record(*, scene_id: str = "") -> dict[str, Any]:
    gate = _threat_gate()
    studio = load_studio()
    sid = scene_id or studio.get("active_scene") or "scene_main"
    rec = _ffmpeg_record_start(sid)
    if rec.get("ok"):
        studio["recording"] = True
        studio["updated"] = _now()
        _save(STUDIO, studio)
    return {**rec, "threat": gate, "engine": "studio"}


def stop_all() -> dict[str, Any]:
    studio = load_studio()
    studio["streaming"] = False
    studio["recording"] = False
    studio["updated"] = _now()
    _save(STUDIO, studio)
    _stop_proc("record_pid")
    return {"ok": True}


def posture() -> dict[str, Any]:
    studio = load_studio()
    proc = _proc_state()
    devices = enumerate_devices()
    threat = _threat_gate()
    comb: dict[str, Any] = {}
    seq_py = INSTALL / "lib" / "field-combinatorics-sequence.py"
    if seq_py.is_file():
        try:
            spec = importlib.util.spec_from_file_location("bc_seq", seq_py)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "publish_panel"):
                    comb = (mod.publish_panel().get("panel") or {})
        except Exception:
            pass
    panel = {
        "schema": "field-broadcaster-studio-panel/v1",
        "updated": _now(),
        "ok": True,
        "engine": "studio",
        "legacy_obs": False,
        "collection": studio.get("collection"),
        "profile": studio.get("profile"),
        "active_scene": studio.get("active_scene"),
        "preview_scene": studio.get("preview_scene"),
        "studio_mode": studio.get("studio_mode", True),
        "streaming": proc.get("streaming") or studio.get("streaming"),
        "recording": proc.get("recording") or studio.get("recording"),
        "scene_count": len(studio.get("scenes") or []),
        "scenes": studio.get("scenes") or [],
        "sources": studio.get("sources") or {},
        "devices": devices,
        "encoder": studio.get("encoder"),
        "threat": threat,
        "combinatorics": {"sequence_length": comb.get("sequence_length"), "gapless": comb.get("gapless")},
    }
    _save(PANEL, panel)
    return panel


def dispatch(body: dict[str, Any]) -> dict[str, Any]:
    action = str(body.get("action") or "posture").strip().lower().replace("-", "_")
    if action in ("posture", "json", "status"):
        return posture()
    if action in ("go_live", "golive", "stream_start"):
        return go_live(scene_id=str(body.get("scene_id") or ""))
    if action in ("record", "record_start"):
        return start_record(scene_id=str(body.get("scene_id") or ""))
    if action in ("stop", "stream_stop", "record_stop"):
        return stop_all()
    if action == "scene_add":
        return scene_add(str(body.get("name") or "Scene"))
    if action == "scene_remove":
        return scene_remove(str(body.get("scene_id") or ""))
    if action == "scene_activate":
        return scene_set_active(str(body.get("scene_id") or ""), preview=bool(body.get("preview")))
    if action == "source_add":
        return source_add(str(body.get("scene_id") or ""), kind=str(body.get("kind") or "display"), name=str(body.get("name") or ""), device=str(body.get("device") or ""))
    if action == "source_remove":
        return source_remove(str(body.get("scene_id") or ""), str(body.get("source_id") or ""))
    if action == "source_move":
        return source_move(str(body.get("scene_id") or ""), str(body.get("source_id") or ""), str(body.get("direction") or "up"))
    if action == "devices":
        return {"ok": True, "devices": enumerate_devices()}
    if action == "threat":
        return _threat_gate()
    return {"ok": False, "error": "unknown_action", "actions": ["posture", "go_live", "record", "stop", "scene_add", "source_add"]}


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "posture", "panel"):
        print(json.dumps(posture(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "dispatch" and len(sys.argv) > 2:
        try:
            body = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            body = {}
        print(json.dumps(dispatch(body), ensure_ascii=False, indent=2))
        return 0
    if cmd == "devices":
        print(json.dumps(enumerate_devices(), ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({"usage": "field-broadcaster-studio.py [json|devices|dispatch JSON]"}, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())