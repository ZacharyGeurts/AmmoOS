#!/usr/bin/env pythong
"""NEXUS Field Polkit posture — hardened elevation bridge + policy integrity."""
from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
DOCTRINE = INSTALL / "data" / "field-polkit-doctrine.json"
PANEL_FILE = STATE / "field-polkit-panel.json"
STAMP_FILE = STATE / "field-polkit.stamp"

POLICY = Path("/usr/share/polkit-1/actions/com.nexus.field.policy")
LEGACY_POLICY = Path("/usr/share/polkit-1/actions/com.nexus.field.install.policy")
RULES = Path("/etc/polkit-1/rules.d/49-com.nexus.field.rules")
AUDIT = STATE / "pkexec-audit.jsonl"


def _bridge_path() -> Path:
    for candidate in (
        INSTALL / "lib" / "nexus-pkexec-bridge.sh",
        Path("/usr/local/lib/nexus-shield/lib/nexus-pkexec-bridge.sh"),
    ):
        if candidate.is_file():
            return candidate
    return INSTALL / "lib" / "nexus-pkexec-bridge.sh"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _path_is_file(path: Path) -> bool:
    try:
        return path.is_file()
    except OSError:
        return False


def _file_mode_ok(path: Path, *, must_exec: bool = False) -> bool:
    try:
        st = path.stat()
    except OSError:
        return False
    if stat.S_IWOTH & st.st_mode:
        return False
    if must_exec and not (st.st_mode & stat.S_IXUSR):
        return False
    return True


def _audit_tail(limit: int = 5) -> list[dict[str, Any]]:
    if not AUDIT.is_file():
        return []
    lines: list[str] = []
    try:
        lines = AUDIT.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    out: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _polkitd_active() -> str:
    try:
        proc = subprocess.run(
            ["systemctl", "is-active", "polkit"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return (proc.stdout or proc.stderr or "unknown").strip()
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"


def posture() -> dict[str, Any]:
    doctrine = _load(DOCTRINE, {})
    checks = {
        "policy_present": _path_is_file(POLICY),
        "rules_present": _path_is_file(RULES),
        "bridge_present": _path_is_file(_bridge_path()),
        "bridge_secure": _file_mode_ok(_bridge_path(), must_exec=True),
        "legacy_policy_absent": not _path_is_file(LEGACY_POLICY),
        "polkitd": _polkitd_active(),
    }
    deny_recent = sum(
        1 for row in _audit_tail(20) if str(row.get("event", "")).startswith("deny")
    )
    verdict = "GREEN"
    if not all(
        (
            checks["policy_present"],
            checks["rules_present"],
            checks["bridge_present"],
            checks["bridge_secure"],
            checks["legacy_policy_absent"],
        )
    ):
        verdict = "WARN"
    if deny_recent >= 3:
        verdict = "WARN"
    if checks["polkitd"] not in ("active", "unknown"):
        verdict = "WARN"
    return {
        "schema": "field-polkit/v1",
        "ts": _now(),
        "verdict": verdict,
        "doctrine": doctrine.get("title", "field-polkit"),
        "checks": checks,
        "actions": [a.get("id") for a in doctrine.get("actions", []) if isinstance(a, dict)],
        "audit_tail": _audit_tail(),
        "deny_recent": deny_recent,
    }


def board_once() -> dict[str, Any]:
    doc = posture()
    _save_panel(doc)
    STAMP_FILE.write_text(_now() + "\n", encoding="utf-8")
    return doc


def _save_panel(doc: dict[str, Any]) -> None:
    PANEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = PANEL_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(PANEL_FILE)


def main() -> int:
    mode = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if mode == "board":
        board_once()
        return 0
    if mode == "json":
        print(json.dumps(posture(), ensure_ascii=False, indent=2))
        return 0
    print("usage: field-polkit.py [json|board]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())