#!/usr/bin/env pythong
"""Queen → Final_Eye bridge — browser smoke OCR lands in Final_Eye/out/."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from queen_final_eye import final_eye_env, final_eye_root

QUEEN = Path(__file__).resolve().parents[1]
SG = QUEEN.parent.parent
FINAL_EYE = final_eye_root()
SMOKE = FINAL_EYE / "queen_browser_smoke.py"
ZOCR_PY = FINAL_EYE / "zocr.py"
ZOCR_WATCH = FINAL_EYE / "zocr_watch.py"
FORGE_WATCH = FINAL_EYE / "queen_forge_watch.py"
EYEBALL = QUEEN / "lib" / "queen-eyeball.py"


def _run(script: Path, *args: str, timeout: int = 120) -> dict[str, Any]:
    if not script.is_file():
        return {"ok": False, "error": f"missing {script}"}
    proc = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        env=final_eye_env(queen=QUEEN),
    )
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError:
        doc = {"ok": False, "tail": (proc.stdout or "")[-2000:]}
    doc["returncode"] = proc.returncode
    doc["final_eye_root"] = str(FINAL_EYE)
    return doc


def dispatch(body: dict[str, Any]) -> dict[str, Any]:
    action = str(body.get("action") or "status").strip().lower()
    if action in ("status", "json"):
        return _run(ZOCR_PY, "status")
    if action in ("live", "live-status", "live_status"):
        return _run(ZOCR_PY, "live")
    if action in ("look", "poll", "vision-poll", "watch"):
        if FORGE_WATCH.is_file():
            return _run(FORGE_WATCH, "once", "queen_zocr_watch")
        return _run(ZOCR_WATCH, "look")
    if action in ("forge-watch", "forge_watch", "hangup-watch"):
        return _run(FORGE_WATCH if FORGE_WATCH.is_file() else ZOCR_WATCH, "once", "queen_forge_watch")
    if action in ("observe", "robotics"):
        return _run(ZOCR_WATCH, "observe")
    if action == "capabilities":
        return _run(ZOCR_WATCH, "capabilities")
    if action in ("smoke", "browser-smoke", "browser_smoke", "queen-smoke"):
        return _run(SMOKE)
    if action == "ocr" and body.get("image"):
        return _run(ZOCR_PY, "ocr", str(body["image"]))
    if action in ("eyeball", "eyeball-status", "final-eye"):
        return _run(EYEBALL, "json")
    if action in ("eyeball-arm", "arm-dishes"):
        mode = str(body.get("mode") or ("dishes" if action == "arm-dishes" else "dishes"))
        return _run(EYEBALL, "arm", mode)
    if action in ("eyeball-verify", "eyeball-verify-hostess"):
        return _run(EYEBALL, "verify")
    if action in ("eyeball-weaponize", "weaponize-eyeball"):
        mode = str(body.get("mode") or "war")
        return _run(EYEBALL, "weaponize", mode)
    if action in ("bench-low-end", "eyeball-bench"):
        return _run(EYEBALL, "bench")
    if action in ("teach", "teach-doctrine"):
        return _run(EYEBALL, "dispatch")  # stdin dispatch — use eyeball subprocess
    return {"ok": False, "error": "unknown_action"}


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "status").strip()
    if cmd == "dispatch":
        try:
            body = json.loads(sys.stdin.read() or "{}")
        except json.JSONDecodeError:
            print(json.dumps({"ok": False, "error": "bad_json"}))
            return 1
        print(json.dumps(dispatch(body), ensure_ascii=False))
        return 0
    if cmd in ("smoke", "browser-smoke"):
        print(json.dumps(_run(SMOKE), ensure_ascii=False))
        return 0
    if cmd in ("live", "live-status"):
        print(json.dumps(_run(ZOCR_PY, "live"), ensure_ascii=False))
        return 0
    if cmd in ("look", "poll", "watch", "vision"):
        print(json.dumps(_run(ZOCR_WATCH, "look"), ensure_ascii=False))
        return 0
    if cmd in ("observe", "robotics"):
        print(json.dumps(_run(ZOCR_WATCH, "observe"), ensure_ascii=False))
        return 0
    print(json.dumps(_run(ZOCR_PY, "status"), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())