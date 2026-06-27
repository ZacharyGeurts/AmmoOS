#!/usr/bin/env pythong
"""Queen CHIPS / Game Room bridge — retro systems, G16-optimized silicon, Webbrowser surface."""
from __future__ import annotations

import json
import mimetypes
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

QUEEN = Path(__file__).resolve().parents[1]
SG = QUEEN.parent.parent
NEXUS = Path(os.environ.get("NEXUS_INSTALL_ROOT", SG / "NewLatest"))
NEXUS_STATE = Path(os.environ.get("NEXUS_STATE_DIR", NEXUS / ".nexus-state"))
RTX = Path(os.environ.get("AMOURANTHRTX_ROOT", SG / "NewLatest" / "AMOURANTHRTX"))
GROK16 = Path(os.environ.get("GROK16_ROOT", SG / "Grok16"))
MANIFEST = QUEEN / "data" / "queen-game-room.json"
G16_CHIPS = QUEEN / "data" / "chips-g16-manifest.json"
CHIPS_HPP = RTX / "Navigator" / "engine" / "CHIPS" / "FieldChips.hpp"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _chips_tree_stats() -> dict[str, Any]:
    chips = RTX / "Navigator" / "engine" / "CHIPS"
    if not chips.is_dir():
        return {"present": False, "headers": 0}
    headers = list(chips.rglob("*.hpp"))
    platforms = [d.name for d in chips.iterdir() if d.is_dir()]
    return {
        "present": True,
        "root": str(chips),
        "headers": len(headers),
        "platforms": sorted(platforms),
        "aggregator": str(CHIPS_HPP) if CHIPS_HPP.is_file() else None,
    }


def _rtx_binary() -> Path | None:
    for p in (
        RTX / "build-release" / "bin" / "Linux" / "queen-browser",
        RTX / "build" / "bin" / "Linux" / "queen-browser",
        QUEEN / "build" / "rtx" / "bin" / "Linux" / "queen-browser",
    ):
        if p.is_file():
            return p.resolve()
    return None


def _queen_process_running() -> bool:
    try:
        r = subprocess.run(
            ["pgrep", "-f", "queen-browser"],
            capture_output=True,
            timeout=3,
        )
        return r.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _fb_snap_paths() -> list[Path]:
    names = ("nes_fb.ppm", "snap.ppm", "game_room_fb.ppm", "framebuffer.ppm")
    dirs = (
        RTX / "build" / "snap",
        RTX / "build",
        RTX / "cache" / "snap",
        QUEEN / "data" / "snap",
    )
    out: list[Path] = []
    for d in dirs:
        for n in names:
            p = d / n
            if p.is_file():
                out.append(p.resolve())
    return out


def _g16_status() -> dict[str, Any]:
    g16 = GROK16 / "bin" / "g16"
    manifest = _load(G16_CHIPS)
    tc = _load(GROK16 / "data" / "grok16-toolchain.json")
    return {
        "ready": g16.is_file(),
        "g16": str(g16) if g16.is_file() else None,
        "profile": manifest.get("profile") or "field_opt",
        "version": tc.get("version") or "16.1.1",
        "chips_optimizations": manifest.get("hot_paths") or [],
    }


def _qa_hint() -> dict[str, Any]:
    qa = RTX / "scripts" / "qa_nes_cpu_test.cpp"
    linux_sh = RTX / "linux.sh"
    return {
        "qa_nes": qa.is_file(),
        "linux_sh": linux_sh.is_file(),
        "launch_cmd": str(linux_sh) + " run" if linux_sh.is_file() else None,
    }


def _chip_battery_script() -> Path:
    for root in (NEXUS, SG / "NewLatest"):
        p = root / "lib" / "field-chip-battery.py"
        if p.is_file():
            return p
    return NEXUS / "lib" / "field-chip-battery.py"


def _chip_battery_env() -> dict[str, str]:
    return {
        **os.environ,
        "SG_ROOT": str(SG),
        "QUEEN_ROOT": str(QUEEN),
        "NEXUS_INSTALL_ROOT": str(NEXUS),
        "NEXUS_STATE_DIR": str(NEXUS_STATE),
        "GROK16_ROOT": str(GROK16),
    }


def combinatronic_status(*, refresh: bool = False) -> dict[str, Any]:
    script = _chip_battery_script()
    if not script.is_file():
        return {
            "schema": "field-chips-combinatronic/v1",
            "ok": False,
            "error": "chip_battery_missing",
            "path": str(script),
        }
    args = ["combinatronic"]
    if refresh:
        args.append("--refresh")
    try:
        proc = subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(QUEEN),
            env=_chip_battery_env(),
        )
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"schema": "field-chips-combinatronic/v1", "ok": False, "error": "bad_json"}
    except subprocess.TimeoutExpired:
        return {"schema": "field-chips-combinatronic/v1", "ok": False, "error": "timeout"}


def chip_battery_panel() -> dict[str, Any]:
    script = _chip_battery_script()
    if not script.is_file():
        return {"schema": "field-chip-battery-panel/v1", "ok": False, "error": "chip_battery_missing"}
    try:
        proc = subprocess.run(
            [sys.executable, str(script), "json"],
            capture_output=True,
            text=True,
            timeout=90,
            cwd=str(QUEEN),
            env=_chip_battery_env(),
        )
        return json.loads(proc.stdout or "{}")
    except (json.JSONDecodeError, subprocess.TimeoutExpired):
        return {"schema": "field-chip-battery-panel/v1", "ok": False, "error": "chip_battery_failed"}


def game_room_status() -> dict[str, Any]:
    room = _load(MANIFEST)
    comb = combinatronic_status()
    pred = comb.get("path_prediction") or {}
    return {
        "schema": "queen-chips/v1",
        "updated": _now(),
        "title": room.get("title"),
        "motto": room.get("motto"),
        "systems": room.get("systems") or [],
        "host_cpus": room.get("host_cpus") or [],
        "memory_profiles": room.get("memory_profiles") or [],
        "movie_formats": room.get("movie_formats") or [],
        "aspect": room.get("aspect") or {},
        "chips": _chips_tree_stats(),
        "grok16": _g16_status(),
        "surface": "webbrowser",
        "web_surface": True,
        "game_room_url": "/world/queen-game-room.html",
        "chips_cores_url": "/world/queen-chips-cores.html",
        "combinatronic_url": "/world/queen-chips-cores.html#combinatronic",
        "combinatronic": comb,
        "chip_battery": {
            "counts": comb.get("counts"),
            "leaf_count": comb.get("leaf_count"),
            "path_total_pct": pred.get("total_pct"),
            "narrow_band_width": (comb.get("line_safety") or {}).get("narrow_band_width"),
            "band_count": len(pred.get("bands") or []),
        },
        "rtx": {
            "root": str(RTX),
            "present": RTX.is_dir(),
            "desktop_comp_shader": False,
            "note": "CHIPS/cores route through Queen Webbrowser — no RTX comp shader boot",
        },
        "qa": _qa_hint(),
        "selected": {
            "system": "nes",
            "host_cpu": "native",
            "memory": "stock",
            "aspect": "16/9",
        },
    }


def dispatch(body: dict[str, Any]) -> dict[str, Any]:
    action = str(body.get("action") or "status").strip().lower()
    if action in ("status", "json"):
        return {"ok": True, **game_room_status()}

    status = game_room_status()
    system = str(body.get("system") or body.get("system_id") or "nes").strip()
    host_cpu = str(body.get("host_cpu") or body.get("cpu") or "native").strip()
    memory = str(body.get("memory") or "stock").strip()
    aspect = str(body.get("aspect") or "16/9").strip()

    if action in ("configure", "select"):
        status["selected"] = {"system": system, "host_cpu": host_cpu, "memory": memory, "aspect": aspect}
        systems = {s["id"]: s for s in status.get("systems") or []}
        sel = systems.get(system)
        if not sel:
            return {"ok": False, "error": "unknown_system", "systems": list(systems.keys())}
        return {
            "ok": True,
            "configured": status["selected"],
            "system": sel,
            "grok16_profile": status["grok16"].get("profile"),
            "message": f"Game Room armed: {sel.get('label')} · CPU {host_cpu} · {memory} RAM",
        }

    if action in ("launch", "run", "start"):
        systems = {s["id"]: s for s in status.get("systems") or []}
        sel = systems.get(system)
        if not sel:
            return {"ok": False, "error": "unknown_system"}
        if sel.get("movie"):
            return {
                "ok": True,
                "mode": "cinema",
                "system": sel,
                "message": "Cinema mode — load a movie file in the Game Room theater",
            }
        app_id = sel.get("app_id", system.upper())
        return {
            "ok": True,
            "mode": "chips",
            "surface": "webbrowser",
            "spawned": False,
            "spawn_rtx": False,
            "system": sel,
            "host_cpu": host_cpu,
            "memory": memory,
            "url": "/world/queen-game-room.html",
            "grok16_profile": status["grok16"].get("profile"),
            "message": f"{sel.get('label')} armed on Queen Webbrowser canvas — no desktop comp shader",
        }

    if action in ("rebuild", "rebuild_chips", "g16_rebuild"):
        g16 = GROK16 / "bin" / "g16"
        script = RTX / "linux.sh"
        cmd = (
            f"cd {RTX} && G16_PREFIX={GROK16} QUEEN_BROWSER_BUILD=1 "
            f"cmake -B build -DQUEEN_BROWSER_BUILD=ON && cmake --build build -j$(nproc)"
        )
        if body.get("run"):
            try:
                subprocess.Popen(
                    ["bash", "-lc", cmd],
                    cwd=str(RTX),
                    start_new_session=True,
                    stdout=open(QUEEN / ".queen-chips-rebuild.log", "a", encoding="utf-8"),
                    stderr=subprocess.STDOUT,
                )
                return {"ok": True, "started": True, "cmd": cmd, "log": str(QUEEN / ".queen-chips-rebuild.log")}
            except OSError as e:
                return {"ok": False, "error": "rebuild_start_failed", "detail": str(e)}
        return {
            "ok": True,
            "cmd": cmd,
            "g16_ready": g16.is_file(),
            "linux_sh": script.is_file(),
            "profile": _load(G16_CHIPS).get("profile") or "field_opt",
            "message": "POST action=rebuild run=true to start G16 CHIPS rebuild in background",
        }

    if action in ("fullscreen", "aspect"):
        return {"ok": True, "aspect": aspect, "fullscreen": body.get("fullscreen", True)}

    if action in ("combinatronic", "chips_combinatronic", "chip_battery", "chip-battery"):
        refresh = bool(body.get("refresh"))
        panel = combinatronic_status(refresh=refresh) if action != "chip-battery" else chip_battery_panel()
        return {"ok": True, **panel}

    return {
        "ok": False,
        "error": "unknown_action",
        "actions": ["status", "configure", "launch", "rebuild", "combinatronic", "chip_battery"],
    }


def _fb_image_path() -> Path | None:
    rtx = RTX
    for name in ("nes_fb.png", "game_room_fb.png", "framebuffer.png", "snap.png"):
        for d in (rtx / "build" / "snap", rtx / "build", rtx / "cache" / "snap", QUEEN / "data" / "snap"):
            p = d / name
            if p.is_file():
                return p.resolve()
    return None


def framebuffer_status() -> dict[str, Any]:
    snaps = _fb_snap_paths()
    img = _fb_image_path()
    running = _queen_process_running()
    out: dict[str, Any] = {
        "schema": "queen-game-room-fb/v1",
        "updated": _now(),
        "surface": "webbrowser",
        "web_surface": True,
        "desktop_comp_shader": False,
        "ready": True,
        "programs_canvas_ready": True,
        "queen_process": running,
        "snap": str(snaps[0]) if snaps else None,
        "image": str(img) if img else None,
    }
    if img:
        out["image_url"] = "/api/game-room/fb/image"
    return out


def framebuffer_image_bytes() -> tuple[bytes, str] | None:
    img = _fb_image_path()
    if not img:
        return None
    mime = mimetypes.guess_type(str(img))[0] or "application/octet-stream"
    try:
        return img.read_bytes(), mime
    except OSError:
        return None


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "fb":
        print(json.dumps(framebuffer_status(), ensure_ascii=False))
        return 0
    if len(sys.argv) > 1 and sys.argv[1] in ("combinatronic", "chip-battery"):
        refresh = "--refresh" in sys.argv[2:]
        if sys.argv[1] == "chip-battery":
            print(json.dumps(chip_battery_panel(), ensure_ascii=False))
        else:
            print(json.dumps(combinatronic_status(refresh=refresh), ensure_ascii=False))
        return 0
    if len(sys.argv) > 1 and sys.argv[1] == "dispatch":
        try:
            body = json.loads(sys.stdin.read() or "{}")
        except json.JSONDecodeError:
            print(json.dumps({"ok": False, "error": "bad_json"}))
            return 1
        print(json.dumps(dispatch(body), ensure_ascii=False))
        return 0
    print(json.dumps(game_room_status(), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())