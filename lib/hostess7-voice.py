#!/usr/bin/env pythong
"""Hostess 7 voice — American English female, high-quality spoken output."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
DOCTRINE = INSTALL / "data" / "hostess7-voice-doctrine.json"
PANEL = STATE / "hostess7-voice-panel.json"
SAMPLES = INSTALL / "data" / "hostess7-voice-samples"

ENABLED = os.environ.get("NEXUS_HOSTESS7_VOICE", os.environ.get("HOSTESS7_VOICE", "1")) not in ("0", "false", "no")


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


def _clean_speech_text(text: str) -> str:
    clean = re.sub(r"\033\[[0-9;]*m", "", text or "")
    clean = re.sub(r"`[^`]+`", "", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def _chunk_text(text: str, *, max_chars: int = 420) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    buf: list[str] = []
    for w in words:
        buf.append(w)
        if len(" ".join(buf)) > max_chars:
            chunks.append(" ".join(buf[:-1]))
            buf = [w]
    if buf:
        chunks.append(" ".join(buf))
    return [c for c in chunks if len(c) >= 3]


def _piper_speak(chunk: str, *, voice_model: Path, out_wav: Path) -> bool:
    piper = shutil.which("piper")
    if not piper or not voice_model.is_file():
        return False
    try:
        proc = subprocess.run(
            [piper, "--model", str(voice_model), "--output_file", str(out_wav)],
            input=chunk,
            text=True,
            capture_output=True,
            check=False,
            timeout=90,
        )
        if proc.returncode != 0 or not out_wav.is_file():
            return False
        for player in ("aplay", "paplay", "ffplay"):
            play = shutil.which(player)
            if not play:
                continue
            args = [play, str(out_wav)] if player != "ffplay" else [play, "-nodisp", "-autoexit", str(out_wav)]
            subprocess.run(args, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        return out_wav.is_file()
    except (subprocess.TimeoutExpired, OSError):
        return False


def _spd_speak(chunk: str, *, voice: str, rate: int, pitch: int) -> bool:
    spd = shutil.which("spd-say")
    if not spd:
        return False
    subprocess.run(
        [spd, "-y", voice, "-r", str(rate), "-p", str(pitch), "-i", "en-US", chunk],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return True


def _mouth_neural_prepare(thought: str) -> dict[str, Any]:
    mm = INSTALL / "lib" / "hostess7-mouth-neural.py"
    if not mm.is_file() or os.environ.get("NEXUS_HOSTESS7_MOUTH_NEURAL", "1") != "1":
        return {"ok": True, "utterance": thought, "thought_voice_alignment": 1.0, "skipped": True}
    try:
        proc = subprocess.run(
            [sys.executable, str(mm), "dispatch"],
            input=json.dumps({"action": "prepare", "text": thought}),
            capture_output=True,
            text=True,
            timeout=45,
            env={**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL), "NEXUS_STATE_DIR": str(STATE)},
        )
        doc = json.loads(proc.stdout or "{}")
        if doc.get("utterance"):
            return doc
    except (json.JSONDecodeError, subprocess.TimeoutExpired, OSError):
        pass
    return {"ok": True, "utterance": thought, "thought_voice_alignment": 1.0, "skipped": True}


def speak(text: str, *, save_sample: bool = True) -> dict[str, Any]:
    """Speak through mouth field neural — thought→voice hemisphere, then Piper/spd-say."""
    if not ENABLED:
        return {"ok": False, "error": "voice_disabled"}
    thought = _clean_speech_text(text)
    neural = _mouth_neural_prepare(thought)
    clean = _clean_speech_text(str(neural.get("utterance") or thought))
    if len(clean) < 3:
        return {"ok": False, "error": "text_too_short"}

    doctrine = _load(DOCTRINE, {})
    chunk_max = int(doctrine.get("chunk_max_chars") or 420)
    max_chunks = int(doctrine.get("max_chunks") or 16)
    chunks = _chunk_text(clean, max_chars=chunk_max)[:max_chunks]
    engines = sorted(doctrine.get("engines") or [], key=lambda e: int(e.get("priority") or 99))

    SAMPLES.mkdir(parents=True, exist_ok=True)
    piper_model = SAMPLES / "en_US-amy-medium.onnx"
    spoken = 0
    engine_used = None

    for chunk in chunks:
        ok = False
        for eng in engines:
            eid = str(eng.get("id") or "")
            if eid == "piper":
                wav = SAMPLES / f"utterance_{spoken:04d}.wav"
                ok = _piper_speak(chunk, voice_model=piper_model, out_wav=wav)
                if ok:
                    engine_used = "piper"
                    if save_sample:
                        try:
                            (SAMPLES / "latest.txt").write_text(chunk + "\n", encoding="utf-8")
                        except OSError:
                            pass
            elif eid in ("spd-say", "spd"):
                ok = _spd_speak(
                    chunk,
                    voice=str(eng.get("voice") or "female2"),
                    rate=int(eng.get("rate") or -8),
                    pitch=int(eng.get("pitch") or 18),
                )
                if ok:
                    engine_used = engine_used or "spd-say"
            if ok:
                break
        if ok:
            spoken += 1

    out = {
        "ok": spoken > 0,
        "spoken_chunks": spoken,
        "total_chunks": len(chunks),
        "engine": engine_used,
        "locale": doctrine.get("locale") or "en-US",
        "gender": doctrine.get("gender") or "female",
        "quality": doctrine.get("quality") or "high",
        "thought": thought,
        "utterance": clean,
        "field_neural": {
            "thought_voice_alignment": neural.get("thought_voice_alignment"),
            "deception_risk": neural.get("deception_risk"),
            "top_label": neural.get("top_label"),
            "deception_possible": neural.get("deception_possible", True),
        },
    }
    _save(PANEL, {
        "schema": "hostess7-voice/v1",
        "enabled": ENABLED,
        "last_engine": engine_used,
        "last_locale": out["locale"],
        "last_spoken_chunks": spoken,
        "fluency_claim": doctrine.get("fluency_claim"),
    })
    return out


def build_panel(*, write: bool = True) -> dict[str, Any]:
    doctrine = _load(DOCTRINE, {})
    panel = _load(PANEL, {})
    field_neural = doctrine.get("field_neural") or {}
    doc = {
        "schema": "hostess7-voice/v1",
        "enabled": ENABLED,
        "locale": doctrine.get("locale") or "en-US",
        "dialect": doctrine.get("dialect") or "american_english",
        "gender": doctrine.get("gender") or "female",
        "quality": doctrine.get("quality") or "high",
        "fluency_claim": doctrine.get("fluency_claim"),
        "engines": doctrine.get("engines"),
        "sample_dir": str(SAMPLES),
        "piper_available": bool(shutil.which("piper")),
        "spd_available": bool(shutil.which("spd-say")),
        "last_engine": panel.get("last_engine"),
        "field_neural": {
            "voice_hemisphere": True,
            "deception_possible": field_neural.get("deception_possible", True),
            "thought_voice_alignment": "not_guaranteed",
            "mouth_neural_engine": field_neural.get("mouth_neural_engine"),
        },
    }
    if write:
        _save(PANEL, doc)
    return doc


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "panel", "status"):
        print(json.dumps(build_panel(), ensure_ascii=False))
        return 0
    if cmd == "speak":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        result = speak(text)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result.get("ok") else 1
    print(json.dumps({"error": "usage: hostess7-voice.py [json|speak TEXT]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())