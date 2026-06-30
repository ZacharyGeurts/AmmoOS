#!/usr/bin/env pythong
"""G16 RTX gate — queen_rtx / vulkan_rtx only when RTX-class GPU is present."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GROK16 = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
STATE = GROK16 / ".grok16-state"
DOCTRINE = GROK16 / "data" / "g16-rtx-gate.json"
PANEL = STATE / "g16-rtx-gate-panel.json"
RTX_RE = re.compile(r"\bRTX\b", re.IGNORECASE)


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


def _force_override() -> bool:
    doctrine = _load(DOCTRINE, {})
    key = doctrine.get("override_env") or "G16_RTX_GATE_FORCE"
    return os.environ.get(key, "").strip().lower() in ("1", "true", "yes", "on")


def _nvidia_smi() -> list[dict[str, str]]:
    gpus: list[dict[str, str]] = []
    try:
        proc = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version,compute_cap", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        if proc.returncode != 0:
            return gpus
        for line in (proc.stdout or "").strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if not parts or not parts[0]:
                continue
            gpus.append({
                "name": parts[0],
                "driver": parts[1] if len(parts) > 1 else "",
                "compute_cap": parts[2] if len(parts) > 2 else "",
                "rtx": bool(RTX_RE.search(parts[0])),
            })
    except (OSError, subprocess.TimeoutExpired):
        pass
    return gpus


def _sysfs_drm() -> list[dict[str, str]]:
    gpus: list[dict[str, str]] = []
    drm = Path("/sys/class/drm")
    if not drm.is_dir():
        return gpus
    for card in sorted(drm.glob("card*")):
        if not card.is_dir() or card.name.endswith(("-DP-", "-HDMI-", "-DVI-", "-eDP-")):
            continue
        vendor = card / "device" / "vendor"
        device = card / "device" / "device"
        try:
            if vendor.read_text().strip() != "0x10de":
                continue
        except OSError:
            continue
        name = ""
        for path in (card / "device" / "name", card / "device" / "uevent"):
            try:
                raw = path.read_text(encoding="utf-8", errors="replace")
                if path.name == "uevent":
                    for line in raw.splitlines():
                        if line.startswith("PCI_ID=") or line.startswith("DRIVER="):
                            name += line + " "
                else:
                    name = raw.strip()
            except OSError:
                pass
        try:
            dev_id = device.read_text().strip()
        except OSError:
            dev_id = ""
        label = name.strip() or f"nvidia:{dev_id}"
        gpus.append({"name": label, "source": "sysfs", "rtx": bool(RTX_RE.search(label))})
    return gpus


def _lspci_nvidia() -> list[dict[str, str]]:
    gpus: list[dict[str, str]] = []
    try:
        proc = subprocess.run(
            ["lspci", "-nn"],
            capture_output=True,
            text=True,
            timeout=6,
        )
        if proc.returncode != 0:
            return gpus
        for line in (proc.stdout or "").splitlines():
            if "vga" not in line.lower() and "3d" not in line.lower() and "display" not in line.lower():
                continue
            if "nvidia" not in line.lower() and "[10de:" not in line.lower():
                continue
            gpus.append({"name": line.strip(), "source": "lspci", "rtx": bool(RTX_RE.search(line))})
    except (OSError, subprocess.TimeoutExpired):
        pass
    return gpus


def detect_rtx() -> dict[str, Any]:
    doctrine = _load(DOCTRINE, {})
    forced = _force_override()
    gpus = _nvidia_smi()
    method = "nvidia-smi" if gpus else ""
    if not gpus:
        gpus = _sysfs_drm()
        method = "sysfs_drm" if gpus else method
    if not gpus:
        gpus = _lspci_nvidia()
        method = "lspci" if gpus else method
    rtx_gpus = [g for g in gpus if g.get("rtx")]
    satisfied = forced or bool(rtx_gpus)
    return {
        "schema": "g16-rtx-gate-panel/v1",
        "updated": _now(),
        "satisfied": satisfied,
        "forced": forced,
        "method": method or "none",
        "gpu_count": len(gpus),
        "rtx_count": len(rtx_gpus),
        "gpus": gpus,
        "rtx_gpus": rtx_gpus,
        "profiles_gated": doctrine.get("profiles_gated") or ["queen_rtx", "vulkan_rtx"],
        "fallback_profile": "field_opt",
    }


def profile_allowed(profile: str) -> bool:
    doctrine = _load(DOCTRINE, {})
    gated = set(doctrine.get("profiles_gated") or ["queen_rtx", "vulkan_rtx"])
    if profile not in gated:
        return True
    return bool(detect_rtx().get("satisfied"))


def gate_status() -> dict[str, Any]:
    doc = detect_rtx()
    doc["ok"] = True
    return doc


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "panel", "status"):
        doc = gate_status()
        _save(PANEL, doc)
        print(json.dumps(doc, ensure_ascii=False))
        return 0
    if cmd == "check" and len(sys.argv) > 2:
        ok = profile_allowed(sys.argv[2])
        print(json.dumps({"profile": sys.argv[2], "allowed": ok}, ensure_ascii=False))
        return 0 if ok else 1
    if cmd == "satisfied":
        print("1" if detect_rtx().get("satisfied") else "0")
        return 0 if detect_rtx().get("satisfied") else 1
    print(json.dumps({"error": "usage: rtx_gate.py [json|check PROFILE|satisfied]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())