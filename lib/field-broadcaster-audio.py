#!/usr/bin/env pythong
"""Broadcaster audio chain — echo cancel, static filter, dB shaping before output."""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", Path(__file__).resolve().parents[1]))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", INSTALL / ".nexus-state"))
DOCTRINE = INSTALL / "data" / "field-broadcaster-audio-doctrine.json"
SETTINGS = STATE / "field-broadcaster-audio-settings.json"
PANEL = STATE / "field-broadcaster-audio-panel.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _save_atomic(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _run(cmd: list[str], *, timeout: float = 8.0) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return proc.returncode, ((proc.stdout or "") + (proc.stderr or "")).strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)


def _detect_backend() -> dict[str, Any]:
    for name in ("pipewire", "pulse"):
        code, out = _run(["pactl", "info"])
        if code == 0:
            server = ""
            for line in out.splitlines():
                if "Server Name:" in line:
                    server = line.split(":", 1)[-1].strip().lower()
            if "pipewire" in server or name == "pipewire":
                return {"id": "pipewire", "name": "PipeWire", "pactl": True}
            if "pulse" in server:
                return {"id": "pulse", "name": "PulseAudio", "pactl": True}
    return {"id": "alsa", "name": "ALSA", "pactl": False}


def _default_sink() -> str:
    code, out = _run(["pactl", "get-default-sink"])
    return out if code == 0 else ""


def _default_source() -> str:
    code, out = _run(["pactl", "get-default-source"])
    return out if code == 0 else ""


def _parse_volume_pct(device: str, kind: str = "sink") -> int | None:
    code, out = _run(["pactl", "list", kind + "s"])
    if code != 0:
        return None
    block = ""
    for line in out.splitlines():
        if line.startswith("Name: ") and device in line:
            block = line
        elif block and "Volume:" in line:
            m = re.search(r"(\d+)%", line)
            if m:
                return int(m.group(1))
    return None


def _db_to_linear(db: float) -> float:
    return 10 ** (db / 20.0)


def _linear_to_db(linear: float) -> float:
    if linear <= 1e-9:
        return -96.0
    return 20.0 * math.log10(linear)


def _chain_posture(settings: dict[str, Any]) -> list[dict[str, Any]]:
    doctrine = _load(DOCTRINE, {})
    steps = []
    for row in doctrine.get("chain") or []:
        sid = str(row.get("id") or "")
        on = True
        if sid == "echo_cancel":
            on = bool(settings.get("echo_cancel", True))
        elif sid == "noise_gate":
            on = bool(settings.get("noise_gate", True))
        elif sid in ("static_suppress", "highpass"):
            on = bool(settings.get("static_filter", True))
        elif sid == "input_gain_db":
            on = settings.get("input_gain_db", 0) != 0
        elif sid == "output_gain_db":
            on = settings.get("output_gain_db", 0) != 0
        steps.append({
            "id": sid,
            "label": row.get("label"),
            "active": on,
            "physics": row.get("physics"),
            "value": settings.get(sid.replace("_db", "_gain_db"), settings.get(sid)),
        })
    return steps


def _apply_pipewire_echo_cancel(*, enable: bool) -> dict[str, Any]:
    if not enable:
        return {"ok": True, "skipped": "echo_cancel_off"}
    sink = _default_sink()
    source = _default_source()
    if not sink or not source:
        return {"ok": False, "error": "no_default_devices"}
    return {
        "ok": True,
        "method": "pipewire_echo_cancel",
        "hint": "Load echo-cancel sink/source pair in PipeWire session",
        "sink": sink,
        "source": source,
        "module": (_load(DOCTRINE, {}).get("pipewire_modules") or {}).get("echo_cancel"),
    }


def _apply_volume_db(device: str, db: float, *, kind: str = "sink") -> dict[str, Any]:
    if not device:
        return {"ok": False, "error": "missing_device"}
    pct = max(0, min(150, int(round(_linear_to_db(_db_to_linear(db)) + 100))))
    code, out = _run(["pactl", f"set-{kind}-volume", device, f"{pct}%"])
    return {"ok": code == 0, "device": device, "target_db": db, "detail": out[:200]}


def _passthrough_settings() -> dict[str, Any]:
    doctrine = _load(DOCTRINE, {})
    defaults = doctrine.get("defaults") or {}
    return {
        **defaults,
        "echo_cancel": False,
        "noise_gate": False,
        "static_filter": False,
        "input_gain_db": 0,
        "output_gain_db": 0,
    }


def clear_chain() -> dict[str, Any]:
    """Remove Broadcaster filters — reset saved settings, restore 100% on default devices."""
    merged = _passthrough_settings()
    _save_atomic(SETTINGS, merged)
    backend = _detect_backend()
    sink = _default_sink()
    source = _default_source()
    results: list[dict[str, Any]] = []
    if backend.get("pactl"):
        if source:
            results.append(_apply_volume_db(source, 0, kind="source"))
        if sink:
            results.append(_apply_volume_db(sink, 0, kind="sink"))
    return {
        "ok": True,
        "cleared": True,
        "passthrough": True,
        "backend": backend,
        "default_sink": sink,
        "default_source": source,
        "settings": merged,
        "chain": _chain_posture(merged),
        "results": results,
    }


def apply_chain(settings: dict[str, Any] | None = None) -> dict[str, Any]:
    """Apply Broadcaster audio chain only when filters or gain explicitly enabled."""
    doctrine = _load(DOCTRINE, {})
    defaults = doctrine.get("defaults") or {}
    saved = _load(SETTINGS, {})
    merged = {**defaults, **saved}
    if settings:
        merged.update(settings)
    _save_atomic(SETTINGS, merged)

    filters_on = any(merged.get(k) for k in ("echo_cancel", "noise_gate", "static_filter"))
    gain_on = float(merged.get("input_gain_db", 0)) != 0 or float(merged.get("output_gain_db", 0)) != 0
    if not filters_on and not gain_on:
        return clear_chain()

    backend = _detect_backend()
    sink = merged.get("default_sink") or _default_sink()
    source = merged.get("default_source") or _default_source()
    results: list[dict[str, Any]] = []

    if backend.get("pactl"):
        in_db = float(merged.get("input_gain_db", 0))
        out_db = float(merged.get("output_gain_db", 0))
        if source and in_db:
            results.append(_apply_volume_db(source, in_db, kind="source"))
        if sink and out_db:
            results.append(_apply_volume_db(sink, out_db, kind="sink"))
        if merged.get("echo_cancel"):
            results.append(_apply_pipewire_echo_cancel(enable=True))

    return {
        "ok": all(r.get("ok", True) for r in results) if results else True,
        "backend": backend,
        "default_sink": sink,
        "default_source": source,
        "settings": merged,
        "chain": _chain_posture(merged),
        "results": results,
    }


def snapshot() -> dict[str, Any]:
    doctrine = _load(DOCTRINE, {})
    settings = _load(SETTINGS, doctrine.get("defaults") or {})
    backend = _detect_backend()
    sink = settings.get("default_sink") or _default_sink()
    source = settings.get("default_source") or _default_source()
    sink_pct = _parse_volume_pct(sink, "sink") if sink else None
    src_pct = _parse_volume_pct(source, "source") if source else None
    return {
        "ok": True,
        "schema": "field-broadcaster-audio/v1",
        "ts": _now(),
        "backend": backend,
        "default_sink": sink,
        "default_source": source,
        "sink_volume_pct": sink_pct,
        "source_volume_pct": src_pct,
        "settings": settings,
        "chain": _chain_posture(settings),
        "motto": doctrine.get("motto"),
    }


def posture(*, apply: bool = False) -> dict[str, Any]:
    if apply:
        apply_chain(_load(SETTINGS, _passthrough_settings()))
    snap = snapshot()
    doc = {
        **snap,
        "title": "Broadcaster Audio",
        "routes": {"api": "/api/field-broadcaster/audio", "apply": "POST"},
        "posture": (
            f"Audio — {snap.get('backend', {}).get('name', '?')} · "
            f"echo={'on' if (snap.get('settings') or {}).get('echo_cancel') else 'off'} · "
            f"gate={'on' if (snap.get('settings') or {}).get('noise_gate') else 'off'}"
        ),
    }
    _save_atomic(PANEL, doc)
    return doc


def save_settings(patch: dict[str, Any], *, apply: bool = False) -> dict[str, Any]:
    allowed = {
        "echo_cancel", "noise_gate", "static_filter", "input_gain_db", "output_gain_db",
        "default_sink", "default_source", "monitor",
    }
    saved = _load(SETTINGS, {})
    for k, v in patch.items():
        if k in allowed:
            saved[k] = v
    _save_atomic(SETTINGS, saved)
    if apply:
        apply_chain(saved)
    return posture()


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "status", "posture"):
        print(json.dumps(posture(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "apply":
        print(json.dumps(apply_chain(), ensure_ascii=False, indent=2))
        return 0
    if cmd in ("clear", "clear-filters", "passthrough"):
        print(json.dumps(clear_chain(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "settings" and len(sys.argv) > 2:
        try:
            patch = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            patch = {}
        print(json.dumps(save_settings(patch), ensure_ascii=False, indent=2))
        return 0
    print("usage: field-broadcaster-audio.py [json|apply|settings JSON]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())