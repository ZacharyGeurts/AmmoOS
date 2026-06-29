#!/usr/bin/env pythong
"""Field Audio Settings — deep Pulse/PipeWire/ALSA control for the shell music icon."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", str(ROOT)))
STATE_DIR = Path(os.environ.get("NEXUS_STATE_DIR", str(ROOT / "state")))
SETTINGS_PATH = STATE_DIR / "field-audio-settings.json"
PANEL_PATH = STATE_DIR / "field-audio-settings-panel.json"

DEFAULT_SETTINGS = {
    "advanced": False,
    "default_sink": "",
    "default_source": "",
    "sink_volume": 1.0,
    "source_volume": 1.0,
    "sink_muted": False,
    "source_muted": False,
    "latency_ms": 0,
    "resample_method": "speex-float-10",
    "channel_map": "default",
    "jack_bridge": False,
    "echo_cancel": False,
    "noise_suppression": False,
    "agc": False,
    "sample_rate": 48000,
    "buffer_size": 1024,
    "periods": 3,
    "alsa_card": "default",
    "pipewire_quantum": 1024,
    "pipewire_rate": 48000,
    "monitor_sources": True,
    "flat_volumes": True,
    "rtp_latency": 200,
    "network_audio": False,
}


def _run(cmd: list[str], timeout: float = 8.0) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)


def _load_settings() -> dict[str, Any]:
    if SETTINGS_PATH.is_file():
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                merged = dict(DEFAULT_SETTINGS)
                merged.update(data)
                return merged
        except (OSError, json.JSONDecodeError):
            pass
    return dict(DEFAULT_SETTINGS)


def _save_settings(data: dict[str, Any]) -> dict[str, Any]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    merged = dict(DEFAULT_SETTINGS)
    merged.update(data)
    SETTINGS_PATH.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    return merged


def _detect_backend() -> dict[str, Any]:
    pw, _ = _run(["pactl", "info"], timeout=4.0)
    pipewire = pw == 0
    server = ""
    if pipewire:
        _, info = _run(["pactl", "info"])
        for line in info.splitlines():
            if "Server Name:" in line:
                server = line.split(":", 1)[-1].strip()
                break
    pulse = pipewire and "pulse" in server.lower()
    pipewire_native = pipewire and "pipewire" in server.lower()
    alsa, _ = _run(["aplay", "-l"], timeout=3.0)
    return {
        "pipewire": pipewire_native,
        "pulse_compat": pulse or pipewire,
        "alsa_available": alsa == 0,
        "server_name": server or "unknown",
        "jack": _run(["jack_lsp"], timeout=2.0)[0] == 0,
    }


def _parse_pactl_list(kind: str) -> list[dict[str, Any]]:
    code, out = _run(["pactl", "list", f"{kind}s" if kind != "source" else "sources", "short"])
    if code != 0:
        return []
    items: list[dict[str, Any]] = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        idx, name = parts[0], parts[1]
        desc = parts[3] if len(parts) > 3 else name
        items.append({"index": idx, "name": name, "description": desc})
    return items


def _parse_pactl_details(kind: str, name: str) -> dict[str, Any]:
    code, out = _run(["pactl", "list", f"{kind}s" if kind != "sink" else "sinks"])
    if code != 0:
        return {}
    block_re = re.compile(rf"^{kind.capitalize()} #\d+", re.MULTILINE)
    chunks = block_re.split(out)
    headers = block_re.findall(out)
    for hdr, chunk in zip(headers, chunks[1:], strict=False):
        if f"Name: {name}" not in chunk:
            continue
        detail: dict[str, Any] = {"name": name, "header": hdr.strip()}
        for line in chunk.splitlines():
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            key = key.strip().lower().replace(" ", "_")
            detail[key] = val.strip()
        vol_match = re.search(r"Volume:.*?(\d+)%", chunk)
        if vol_match:
            detail["volume_percent"] = int(vol_match.group(1))
        detail["muted"] = "Mute: yes" in chunk
        return detail
    return {}


def _default_device(kind: str) -> str:
    flag = "@DEFAULT_SINK@" if kind == "sink" else "@DEFAULT_SOURCE@"
    code, out = _run(["pactl", "get-default-" + kind])
    if code == 0 and out.strip():
        return out.strip()
    code, out = _run(["pactl", "info"])
    if code != 0:
        return ""
    key = "Default Sink" if kind == "sink" else "Default Source"
    for line in out.splitlines():
        if line.startswith(key + ":"):
            return line.split(":", 1)[-1].strip()
    return flag


def _alsa_cards() -> list[dict[str, str]]:
    code, out = _run(["aplay", "-l"])
    if code != 0:
        return []
    cards: list[dict[str, str]] = []
    for line in out.splitlines():
        m = re.match(r"card (\d+): ([^\s]+) \[(.+)\]", line)
        if m:
            cards.append({"id": m.group(1), "name": m.group(2), "description": m.group(3)})
    return cards


def _advanced_block(settings: dict[str, Any], backend: dict[str, Any]) -> dict[str, Any]:
    return {
        "latency_ms": settings.get("latency_ms", 0),
        "resample_method": settings.get("resample_method"),
        "channel_map": settings.get("channel_map"),
        "sample_rate": settings.get("sample_rate"),
        "buffer_size": settings.get("buffer_size"),
        "periods": settings.get("periods"),
        "alsa_card": settings.get("alsa_card"),
        "pipewire_quantum": settings.get("pipewire_quantum"),
        "pipewire_rate": settings.get("pipewire_rate"),
        "jack_bridge": settings.get("jack_bridge"),
        "echo_cancel": settings.get("echo_cancel"),
        "noise_suppression": settings.get("noise_suppression"),
        "agc": settings.get("agc"),
        "monitor_sources": settings.get("monitor_sources"),
        "flat_volumes": settings.get("flat_volumes"),
        "rtp_latency": settings.get("rtp_latency"),
        "network_audio": settings.get("network_audio"),
        "resample_methods": [
            "speex-float-10",
            "speex-float-5",
            "ffmpeg",
            "soxr",
            "copy",
        ],
        "pipewire_config_hint": str(STATE_DIR / "pipewire-pulse.conf.d"),
        "jack_detected": backend.get("jack", False),
    }


def _save_panel(doc: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = PANEL_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(PANEL_PATH)


def posture(*, advanced: bool | None = None) -> dict[str, Any]:
    snap = snapshot(advanced=advanced)
    backend = snap.get("backend") or {}
    sinks = snap.get("sinks") or []
    doc = {
        "schema": "field-audio-settings/v1",
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ok": bool(snap.get("ok")),
        "title": "Audio Settings",
        "backend": backend.get("name") or backend.get("id") or "unknown",
        "sink_count": len(sinks),
        "default_sink": snap.get("default_sink"),
        "default_source": snap.get("default_source"),
        "settings": snap.get("settings") or {},
        "routes": {"panel": "/field-audio-settings", "api": "/api/field-audio-settings"},
        "posture": (
            f"Audio — {backend.get('name') or backend.get('id') or 'backend'} · "
            f"{len(sinks)} sinks · advanced={'on' if (snap.get('settings') or {}).get('advanced') else 'off'}"
        ),
        "snapshot": snap,
    }
    _save_panel(doc)
    return doc


def snapshot(advanced: bool | None = None) -> dict[str, Any]:
    settings = _load_settings()
    if advanced is not None:
        settings["advanced"] = bool(advanced)
    backend = _detect_backend()
    default_sink = _default_device("sink")
    default_source = _default_device("source")
    sinks = _parse_pactl_list("sink")
    sources = [s for s in _parse_pactl_list("source") if not s["name"].endswith(".monitor")]
    sink_detail = _parse_pactl_details("sink", default_sink) if default_sink else {}
    source_detail = _parse_pactl_details("source", default_source) if default_source else {}
    payload: dict[str, Any] = {
        "ok": True,
        "settings": settings,
        "backend": backend,
        "default_sink": default_sink,
        "default_source": default_source,
        "sinks": sinks,
        "sources": sources,
        "sink_detail": sink_detail,
        "source_detail": source_detail,
        "alsa_cards": _alsa_cards(),
        "volume": {
            "sink_percent": sink_detail.get("volume_percent", int(settings.get("sink_volume", 1.0) * 100)),
            "source_percent": source_detail.get("volume_percent", int(settings.get("source_volume", 1.0) * 100)),
            "sink_muted": sink_detail.get("muted", settings.get("sink_muted")),
            "source_muted": source_detail.get("muted", settings.get("source_muted")),
        },
    }
    if settings.get("advanced"):
        payload["advanced"] = _advanced_block(settings, backend)
    return payload


def _filter_audio_patch(patch: dict[str, Any]) -> dict[str, Any]:
    try:
        import importlib.util

        mod_path = INSTALL / "lib" / "queen-settings-surface.py"
        if not mod_path.is_file():
            mod_path = Path(__file__).resolve().parent / "queen-settings-surface.py"
        if mod_path.is_file():
            spec = importlib.util.spec_from_file_location("queen_settings_surface", mod_path)
            mod = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(mod)
            return mod.audio_patch_allowed(patch)
    except Exception:
        pass
    return dict(patch or {})


def apply_settings(patch: dict[str, Any]) -> dict[str, Any]:
    patch = _filter_audio_patch(patch or {})
    settings = _load_settings()
    settings["advanced"] = False
    allowed = set(DEFAULT_SETTINGS.keys())
    for key, val in patch.items():
        if key in allowed:
            settings[key] = val
    _save_settings(settings)

    if settings.get("default_sink"):
        _run(["pactl", "set-default-sink", str(settings["default_sink"])])
    if settings.get("default_source"):
        _run(["pactl", "set-default-source", str(settings["default_source"])])

    sink_vol = max(0, min(100, int(float(settings.get("sink_volume", 1.0)) * 100)))
    src_vol = max(0, min(100, int(float(settings.get("source_volume", 1.0)) * 100)))
    sink = settings.get("default_sink") or _default_device("sink")
    source = settings.get("default_source") or _default_device("source")
    if sink:
        _run(["pactl", "set-sink-volume", sink, f"{sink_vol}%"])
        _run(["pactl", "set-sink-mute", sink, "1" if settings.get("sink_muted") else "0"])
    if source:
        _run(["pactl", "set-source-volume", source, f"{src_vol}%"])
        _run(["pactl", "set-source-mute", source, "1" if settings.get("source_muted") else "0"])

    return snapshot()


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: field-audio-settings.py [json|apply JSON]")
        return 0
    cmd = args[0]
    if cmd in ("json", "status", "posture"):
        advanced = None
        if len(args) > 1 and args[1] in ("0", "1", "true", "false"):
            advanced = args[1] in ("1", "true")
        print(json.dumps(posture(advanced=advanced), indent=2))
        return 0
    if cmd == "apply" and len(args) > 1:
        try:
            patch = json.loads(args[1])
        except json.JSONDecodeError as exc:
            print(json.dumps({"ok": False, "error": str(exc)}))
            return 1
        print(json.dumps(apply_settings(patch), indent=2))
        return 0
    print(json.dumps({"ok": False, "error": f"unknown command: {cmd}"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())