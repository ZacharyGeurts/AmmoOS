#!/usr/bin/env python3
"""Panel tab audit — verify each tab has required API data and DOM anchors before next tab."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", str(ROOT)))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
PANEL_PORT = int(os.environ.get("NEXUS_THREAT_PANEL_PORT", "9477"))
PANEL_URL = os.environ.get("NEXUS_PANEL_URL", f"https://127.0.0.1:{PANEL_PORT}")

TAB_SPECS: dict[str, dict[str, Any]] = {
    "command": {"keys": ["field_command", "gatekeeper"], "dom": ["command-motto", "command-know"]},
    "us": {"keys": ["us_field"], "dom": ["us-motto", "us-hostess-profile"]},
    "packets": {"keys": ["gatekeeper"], "dom": ["connections"]},
    "threats": {"keys": ["home_protector", "host_attacks"], "dom": ["home-protector-stats"]},
    "intel": {"keys": ["audio_train", "field_rf"], "dom": ["audio-train-motto"]},
    "signals": {"keys": ["signals_field", "field_antenna", "field_radio"], "dom": ["signals-operator", "signals-antenna-banner", "signals-radio-menu"]},
    "dns": {"keys": ["field_dns"], "dom": ["dns-hero-title", "dns-posture-strip"]},
    "outside": {"keys": ["field_outside_talk"], "dom": ["outside-hero-title"]},
    "library": {"keys": ["h7_library"], "dom": ["library-search"]},
    "system": {"keys": ["settings"], "dom": ["settings-profile"]},
}

PENDING_RE = re.compile(r"^(Loading|Awaiting|Harvesting|Building|Scanning|Pulling)", re.I)


def _read_json_file(fp: Path) -> dict[str, Any] | None:
    if not fp.is_file() or fp.stat().st_size < 32:
        return None
    try:
        doc = json.loads(fp.read_text(encoding="utf-8", errors="replace"))
        return doc if isinstance(doc, dict) and doc else None
    except (OSError, json.JSONDecodeError, PermissionError):
        pass
    try:
        out = subprocess.check_output(
            ["sudo", "-n", "cat", str(fp)],
            stderr=subprocess.DEVNULL,
            timeout=20,
        )
        doc = json.loads(out.decode("utf-8", errors="replace"))
        return doc if isinstance(doc, dict) and doc else None
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
        return None


def _load_state_json() -> dict[str, Any] | None:
    for state_dir in (STATE, Path("/var/lib/nexus-shield")):
        doc = _read_json_file(state_dir / "threat-panel.json")
        if doc:
            return doc
    return None


def _fetch_panel_json() -> dict[str, Any] | None:
    ctx = __import__("ssl").create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = __import__("ssl").CERT_NONE
    for url in (f"{PANEL_URL}/api/field?full=1", f"{PANEL_URL}/api/field"):
        req = urllib.request.Request(url, headers={"User-Agent": "NEXUS-Panel-Tab-Audit"})
        try:
            with urllib.request.urlopen(req, timeout=45, context=ctx) as resp:
                doc = json.loads(resp.read().decode("utf-8", errors="replace"))
                if isinstance(doc, dict) and len(doc) > 2:
                    return doc
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError):
            continue
    return _load_state_json()


def _build_local_field() -> dict[str, Any]:
    env = {
        **os.environ,
        "NEXUS_INSTALL_ROOT": str(INSTALL),
        "NEXUS_STATE_DIR": str(STATE),
        "NEXUS_THREAT_PANEL": "1",
        "NEXUS_FIELD_ANTENNA": "1",
        "NEXUS_FIELD_RADIO": "1",
        "NEXUS_SIGNALS_FIELD": "1",
    }
    subprocess.run(
        [
            "bash", "-c",
            (
                f'source "{INSTALL}/lib/nexus-common.sh" && '
                f'source "{INSTALL}/lib/field-antenna.sh" 2>/dev/null; '
                f'source "{INSTALL}/lib/field-radio-catcher.sh" 2>/dev/null; '
                f'source "{INSTALL}/lib/signals-field.sh" 2>/dev/null; '
                f'NEXUS_STATE_DIR="{STATE}" NEXUS_INSTALL_ROOT="{INSTALL}" '
                f'python3 "{INSTALL}/lib/operator-default.py" seed >/dev/null 2>&1; '
                f'nexus_field_antenna_cycle 2>/dev/null; '
                f'source "{INSTALL}/lib/threat-panel.sh" && nexus_threat_panel_publish'
            ),
        ],
        capture_output=True,
        text=True,
        timeout=180,
        env=env,
        cwd=str(INSTALL),
    )
    panel_json = STATE / "threat-panel.json"
    if not panel_json.is_file():
        return {}
    try:
        return json.loads(panel_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _key_ready(data: dict[str, Any], key: str) -> bool:
    val = data.get(key)
    if val is None:
        return False
    if key == "gatekeeper":
        return isinstance(val, dict) and isinstance(val.get("connections"), list)
    if key == "signals_field":
        st = (val.get("stats") or {}) if isinstance(val, dict) else {}
        fr = (val.get("field_radio") or {}) if isinstance(val, dict) else {}
        return isinstance(val, dict) and (
            st.get("pulse_channels", 0) > 0
            or len(val.get("antennas") or []) > 0
            or len(fr.get("station_menu") or []) > 0
        )
    if key == "field_antenna":
        return isinstance(val, dict) and ((val.get("readiness") or {}).get("score") is not None or val.get("schema") == "field-antenna/v1")
    if key == "field_radio":
        return isinstance(val, dict) and len(val.get("station_menu") or []) > 0
    if key == "field_dns":
        return isinstance(val, dict) and (val.get("rfc_matrix") is not None or val.get("schema") == "field-dns/v2")
    if key == "h7_library":
        return isinstance(val, dict) and (val.get("books") is not None or val.get("updated"))
    if isinstance(val, dict):
        return bool(val.get("updated") or val.get("schema") or len(val) > 0)
    if isinstance(val, list):
        return len(val) > 0
    return bool(val)


def _dom_ids_present(html: str, ids: list[str]) -> list[str]:
    missing = []
    for dom_id in ids:
        if not re.search(rf'id=["\']{re.escape(dom_id)}["\']', html):
            missing.append(dom_id)
    return missing


def _ocr_smoke(asset: Path) -> str:
    if not asset.is_file():
        return "missing asset"
    try:
        out = subprocess.check_output(
            ["tesseract", str(asset), "stdout", "-l", "eng", "--psm", "6"],
            stderr=subprocess.DEVNULL,
            timeout=15,
        )
        return out.decode("utf-8", errors="replace").strip()[:120]
    except (subprocess.SubprocessError, OSError):
        return ""


def audit_tab(name: str, data: dict[str, Any], html: str) -> tuple[bool, list[str]]:
    spec = TAB_SPECS[name]
    errors: list[str] = []
    for key in spec["keys"]:
        if not _key_ready(data, key):
            errors.append(f"api:{key}")
    missing_dom = _dom_ids_present(html, spec["dom"])
    for dom_id in missing_dom:
        errors.append(f"dom:{dom_id}")
    return not errors, errors


def main() -> int:
    html_path = INSTALL / "panel" / "threat-panel.html"
    html = html_path.read_text(encoding="utf-8", errors="replace") if html_path.is_file() else ""

    data = _fetch_panel_json()
    source = "panel"
    if not data and os.environ.get("NEXUS_PANEL_AUDIT_SKIP_BUILD") != "1":
        data = _build_local_field()
        source = "local-build"
    if not data:
        print("TAB AUDIT FAIL: no panel JSON (start panel or run from installed tree)")
        return 1

    avatar = INSTALL / "panel" / "assets" / "amouranth-twitch-avatar.png"
    wordmark = INSTALL / "panel" / "assets" / "amouranthrtx-wordmark.svg"
    header_checks = []
    if "amouranth-twitch-avatar.png" not in html:
        header_checks.append("missing twitch avatar in HTML")
    if "amouranthrtx-wordmark.svg" not in html:
        header_checks.append("missing AMOURANTHRTX wordmark in HTML")
    if not avatar.is_file():
        header_checks.append("missing amouranth-twitch-avatar.png asset")
    if not wordmark.is_file():
        header_checks.append("missing amouranthrtx-wordmark.svg asset")
    ocr_note = _ocr_smoke(avatar)
    if ocr_note:
        print(f"Header avatar OCR smoke: {ocr_note[:80]}")

    fail = 0
    print(f"=== NEXUS Panel Tab Audit (source={source}) ===")
    if header_checks:
        print("HEADER FAIL:", "; ".join(header_checks))
        fail += 1
    else:
        print("HEADER OK — Amouranth Twitch + AMOURANTHRTX wordmark present")

    for tab in TAB_SPECS:
        ok, errs = audit_tab(tab, data, html)
        if ok:
            print(f"TAB {tab}: PASS")
        else:
            print(f"TAB {tab}: FAIL — {', '.join(errs)}")
            fail += 1
            break  # stop at first failing tab (sequential gate)

    if fail:
        print("\nTAB AUDIT FAILED")
        return 1
    print("\nTAB AUDIT PASSED — all tabs have required data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())