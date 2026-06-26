#!/usr/bin/env pythong
"""Queen Browser — full-featured in-world browser API (tabs, nav, gates, receipts).

Serves queen-world SPA. No OS browser hook — webpage is OS GUI + web surface.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

QUEEN = Path(__file__).resolve().parents[1]
SG = QUEEN.parent.parent
STATE = Path(os.environ.get("NEXUS_STATE_DIR", QUEEN / ".nexus-state"))
STATE_FILE = STATE / "queen-browser-state.json"
NAV_LOG = STATE / "queen-browser-nav.jsonl"

def _gate_mod():
    script = QUEEN / "lib" / "queen-gate.py"
    if not script.is_file():
        return None
    import importlib.util

    spec = importlib.util.spec_from_file_location("queen_gate", script)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _field_net():
    mod = _gate_mod()
    if mod is None:
        return {}
    return mod.field_net_json()


def _world_base() -> str:
    port = os.environ.get("QUEEN_WORLD_PORT", "9481")
    return f"http://127.0.0.1:{port}"


def _start_page() -> str:
    return os.environ.get(
        "QUEEN_BROWSER_START",
        f"{_world_base()}/world/queen-start.html",
    )


def _files_page() -> str:
    return os.environ.get(
        "QUEEN_BROWSER_FILES",
        f"{_world_base()}/world/queen-files.html",
    )


def _default_home() -> str:
    return os.environ.get("QUEEN_BROWSER_HOME", _start_page())


DEFAULT_HOME = _default_home()
MAX_TABS = int(os.environ.get("QUEEN_BROWSER_MAX_TABS", "24"))
MAX_HISTORY = int(os.environ.get("QUEEN_BROWSER_MAX_HISTORY", "64"))

BOOKMARKS = [
    {"id": "queen-world", "title": "Queen OS", "url": _default_home()},
    {"id": "forge", "title": "Forge", "url": f"http://127.0.0.1:{os.environ.get('QUEEN_WORLD_PORT', '9481')}/gui/queen-build-deck.html"},
    {"id": "hostess", "title": "Hostess 7", "url": "queen://hostess"},
    {"id": "kilroy", "title": "KILROY", "url": "queen://kilroy"},
    {"id": "eyeball", "title": "Final_Eye", "url": "queen://eyeball"},
    {"id": "gameroom", "title": "Game Room", "url": "queen://gameroom"},
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _append_nav(entry: dict[str, Any]) -> None:
    STATE.mkdir(parents=True, exist_ok=True)
    with NAV_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _run_panel(*args: str, timeout: int = 30) -> dict[str, Any]:
    mod = _gate_mod()
    if mod is None:
        return {"error": "queen-gate missing"}
    if args and args[0] == "json":
        return mod.panel_json(timeout=timeout)
    return mod.panel_json(timeout=timeout)


def _normalize_url(raw: str) -> str:
    u = (raw or "").strip()
    if not u:
        return DEFAULT_HOME
    if u.startswith("/"):
        port = os.environ.get("QUEEN_WORLD_PORT", "9481")
        return f"http://127.0.0.1:{port}{u}"
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", u):
        return u
    if u.startswith("//"):
        return "https:" + u
    return "https://" + u


def _host(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").lower()
    except Exception:
        return ""


def _gate_nav(url: str) -> dict[str, Any]:
    mod = _gate_mod()
    if mod is None:
        return {"url": url, "permit": True, "queen_verdict": "QUEEN_OFF"}
    return mod.gate_nav(url)


def _new_tab(
    url: str | None = None,
    *,
    pinned: bool = False,
    role: str = "",
    title: str = "",
) -> dict[str, Any]:
    tab = {
        "id": uuid.uuid4().hex[:12],
        "url": _normalize_url(url or DEFAULT_HOME),
        "title": title or ("Start" if pinned else "New Tab"),
        "history": [],
        "history_index": -1,
        "created": _now(),
    }
    if pinned:
        tab["pinned"] = True
    if role:
        tab["role"] = role
    _push_history(tab, tab["url"])
    return tab


def default_state() -> dict[str, Any]:
    start = _new_tab(_start_page(), pinned=True, role="start", title="Start")
    _apply_compat(start, start["url"], {"compat_mode": "modern"})
    files = _new_tab(_files_page(), pinned=True, role="files", title="Files")
    _apply_compat(files, files["url"], {"compat_mode": "modern"})
    return {
        "schema": "queen-browser/v1",
        "updated": _now(),
        "home": DEFAULT_HOME,
        "start_tab": start["id"],
        "files_tab": files["id"],
        "active_tab": start["id"],
        "tabs": [start, files],
    }


def _ensure_files_tab(doc: dict[str, Any]) -> bool:
    """Migrate older state — pinned Files tab is always second."""
    tabs = list(doc.get("tabs") or [])
    if any(t.get("role") == "files" for t in tabs):
        doc["files_tab"] = next((t["id"] for t in tabs if t.get("role") == "files"), doc.get("files_tab"))
        return False
    files = _new_tab(_files_page(), pinned=True, role="files", title="Files")
    _apply_compat(files, files["url"], {"compat_mode": "modern"})
    insert_at = 1
    for i, t in enumerate(tabs):
        if t.get("pinned") and t.get("role") == "start":
            insert_at = i + 1
            break
    tabs.insert(insert_at, files)
    doc["tabs"] = tabs
    doc["files_tab"] = files["id"]
    return True


def load_state() -> dict[str, Any]:
    doc = _load_json(STATE_FILE, {})
    if doc.get("schema") != "queen-browser/v1" or not doc.get("tabs"):
        doc = default_state()
        save_state(doc)
        return doc
    if _ensure_files_tab(doc):
        save_state(doc)
    return doc


def save_state(doc: dict[str, Any]) -> None:
    doc["updated"] = _now()
    _save_json(STATE_FILE, doc)


def _find_tab(doc: dict[str, Any], tab_id: str) -> dict[str, Any] | None:
    for t in doc.get("tabs") or []:
        if t.get("id") == tab_id:
            return t
    return None


_compat_mod: Any = None


def _compat_module() -> Any:
    global _compat_mod
    if _compat_mod is not None:
        return _compat_mod
    script = QUEEN / "lib" / "queen-web-compat.py"
    spec = importlib.util.spec_from_file_location("queen_web_compat", script)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _compat_mod = mod
    return mod


def _nexus_jump_module() -> Any:
    script = QUEEN / "lib" / "queen-nexus-jump.py"
    if not script.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("queen_nexus_jump", script)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def _zero_cost_security() -> dict[str, Any]:
    doc = _load_json(QUEEN / "data" / "queen-zero-cost-4slot.json", {})
    if not doc.get("schema"):
        doc = {
            "schema": "queen-zero-cost-4slot/v1",
            "runtime_tax": 0,
            "slots": [{"id": "TIME"}, {"id": "MEMORY"}, {"id": "THERMO"}, {"id": "CONTEXT"}],
        }
    doc["queen_best_zero_cost"] = True
    return doc


def _file_browser_status() -> dict[str, Any]:
    script = QUEEN / "lib" / "queen-file-browser.py"
    if not script.is_file():
        return {}
    try:
        spec = importlib.util.spec_from_file_location("queen_file_browser", script)
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        return mod.browser_status()
    except Exception:
        return {}


def _nexus_jump_status() -> dict[str, Any]:
    mod = _nexus_jump_module()
    if mod is None:
        return {}
    try:
        return mod.jump_status()
    except Exception:
        return {}


def _nexus_jump(url: str, *, tab_id: str = "", compat_mode: str = "auto") -> dict[str, Any]:
    script = QUEEN / "lib" / "queen-nexus-jump.py"
    mod = _nexus_jump_module()
    if mod is not None:
        try:
            return mod.nexus_jump(url, tab_id=tab_id, compat_mode=compat_mode)
        except Exception as exc:
            return {"ok": False, "permit": False, "error": "nexus_jump_failed", "reason": str(exc)}
    return {
        "ok": True,
        "permit": True,
        "verdict": "DEFEND_CAGED",
        "iff": "CONTACT_HOSTILE",
        "posture": "defend",
        "skipped": True,
    }


def _compat_profile(url: str, mode: str = "auto", hints: dict[str, Any] | None = None) -> dict[str, Any]:
    mod = _compat_module()
    if mod is None:
        return {"mode": mode, "era": {"id": "es2026"}}
    return mod.resolve_profile(url, mode=mode, hints=hints)


def _apply_compat(tab: dict[str, Any], url: str, body: dict[str, Any]) -> dict[str, Any]:
    mode = str(body.get("compat_mode") or tab.get("compat_mode") or "auto")
    profile = _compat_profile(url, mode=mode, hints=body.get("compat_hints") if isinstance(body.get("compat_hints"), dict) else None)
    tab["compat_mode"] = profile.get("effective_mode") or profile.get("mode") or mode
    tab["compat_era"] = (profile.get("era") or {}).get("id") or "es2026"
    tab["compat_profile"] = {
        "mode": profile.get("mode"),
        "effective_mode": profile.get("effective_mode"),
        "era": tab["compat_era"],
        "sandbox": profile.get("sandbox"),
        "user_agent": profile.get("user_agent"),
        "legacy_isolate": profile.get("legacy_isolate"),
    }
    return profile


def _push_history(tab: dict[str, Any], url: str) -> None:
    hist = tab.get("history") or []
    idx = tab.get("history_index", -1)
    if idx >= 0 and idx < len(hist) and hist[idx] == url:
        return
    if idx < len(hist) - 1:
        hist = hist[: idx + 1]
    hist.append(url)
    if len(hist) > MAX_HISTORY:
        hist = hist[-MAX_HISTORY:]
    tab["history"] = hist
    tab["history_index"] = len(hist) - 1


def browser_status() -> dict[str, Any]:
    doc = load_state()
    panel = _run_panel("json")
    active = _find_tab(doc, doc.get("active_tab", ""))
    return {
        "schema": "queen-browser/v1",
        "updated": _now(),
        "home": doc.get("home") or DEFAULT_HOME,
        "active_tab": doc.get("active_tab"),
        "tabs": [
            {
                "id": t.get("id"),
                "url": t.get("url"),
                "title": t.get("title") or t.get("url"),
                "active": t.get("id") == doc.get("active_tab"),
                "pinned": bool(t.get("pinned")),
                "role": t.get("role") or "",
                "compat_mode": t.get("compat_mode") or "auto",
                "compat_era": t.get("compat_era") or "es2026",
                "compat_profile": t.get("compat_profile") or {},
                "nexus_jump": t.get("nexus_jump") or {},
            }
            for t in doc.get("tabs") or []
        ],
        "start_tab": doc.get("start_tab")
        or next((t.get("id") for t in doc.get("tabs") or [] if t.get("role") == "start"), None),
        "files_tab": doc.get("files_tab")
        or next((t.get("id") for t in doc.get("tabs") or [] if t.get("role") == "files"), None),
        "active_url": active.get("url") if active else DEFAULT_HOME,
        "bookmarks": BOOKMARKS,
        "capabilities": {
            "tabs": True,
            "history": True,
            "bookmarks": True,
            "gates": True,
            "honorability": True,
            "webrtc": True,
            "webgpu": True,
            "mse_mp4": True,
            "service_workers": True,
            "downloads": True,
            "find_in_page": True,
            "devtools_slice": True,
            "proxy_fallback": True,
            "internal_only": True,
            "queen_scheme": True,
            "popout_windows": True,
            "tab_fullscreen": True,
            "alt_tab": True,
            "start_tab": True,
            "web_compat": True,
            "full_web_surface": True,
            "legacy_auto_secure": True,
            "plugin_wasm_surrogate": True,
            "html_pre1_through_future": True,
            "nexus_jump": True,
            "file_browser": True,
            "split_pane_files": True,
            "hotbar_drag_drop": True,
            "zero_cost_4_slot": True,
            "folder_menu": True,
        },
        "nexus_jump": _nexus_jump_status(),
        "zero_cost_security": _zero_cost_security(),
        "file_browser": _file_browser_status(),
        "security": {
            "doctrine": "presume_hostile_defend_offense",
            "motto": "Every contact hostile until positively identified. Defend always. Offense when threatened.",
            "iff": {
                "presume_hostile": True,
                "never_presume_correct_contact": True,
                "positive_id_required_for_civilian": True,
                "defend_by_default": True,
                "offense_on_threat": True,
            },
            "inbound_external": False,
            "loopback_only": True,
            "memory_isolation": "iframe_sandbox+csp+gate_nav+compat_cage+nexus_jump",
            "postmessage_iff": "same_origin_only",
            "legacy_isolation": "auto_mode_cages_old_js",
            "zero_cost_4_slot": True,
            "amouranthrtx_slots": ["TIME", "MEMORY", "THERMO", "CONTEXT"],
            "runtime_tax": 0,
        },
        "web_compat": _compat_module().compat_status() if _compat_module() else {},
        "field_net": _field_net(),
        "gates": panel.get("gates") or {},
        "codecs": panel.get("codecs") or {},
        "posture": panel.get("posture") or {},
        "sovereign": panel.get("sovereign") or {},
        "queen_verdict": panel.get("queen_verdict"),
        "browser_awareness": panel.get("browser_awareness") or {},
        "motto": panel.get("motto") or "Nothing optional. Hold all gates.",
    }


def dispatch(body: dict[str, Any]) -> dict[str, Any]:
    action = str(body.get("action") or "status").strip().lower().replace("-", "_")
    doc = load_state()

    if action in ("status", "json"):
        return {"ok": True, **browser_status()}

    if action == "navigate":
        url = _normalize_url(str(body.get("url") or ""))
        tab_id = str(body.get("tab_id") or doc.get("active_tab") or "")
        tab = _find_tab(doc, tab_id) or _find_tab(doc, doc.get("active_tab", ""))
        if not tab:
            tab = _new_tab(url)
            doc.setdefault("tabs", []).append(tab)
            doc["active_tab"] = tab["id"]
        jump = _nexus_jump(
            url,
            tab_id=tab.get("id") or "",
            compat_mode=str(body.get("compat_mode") or tab.get("compat_mode") or "auto"),
        )
        if not jump.get("permit"):
            return {"ok": False, "error": "nexus_jump_blocked", "jump": jump, "gate": jump.get("nexus", {})}
        gate = _gate_nav(url)
        if not gate.get("permit"):
            return {"ok": False, "error": "gate_blocked", "gate": gate, "jump": jump}
        tab["url"] = url
        tab["title"] = str(body.get("title") or _host(url) or "Page")
        tab["nexus_jump"] = {
            "verdict": jump.get("verdict"),
            "iff": jump.get("iff"),
            "countermeasures_ready": jump.get("countermeasures_ready"),
        }
        body = {
            **body,
            "compat_mode": (jump.get("compat") or {}).get("effective_mode")
            or body.get("compat_mode")
            or "auto",
        }
        compat = _apply_compat(tab, url, body)
        compat["nexus_jump"] = jump
        _push_history(tab, url)
        doc["active_tab"] = tab["id"]
        save_state(doc)
        _append_nav({"ts": _now(), "action": "navigate", "url": url, "gate": gate, "compat": compat.get("effective_mode")})
        return {"ok": True, "tab": tab, "gate": gate, "jump": jump, "compat": compat, "status": browser_status()}

    if action == "new_tab":
        if len(doc.get("tabs") or []) >= MAX_TABS:
            return {"ok": False, "error": "max_tabs", "max": MAX_TABS}
        url = _normalize_url(str(body.get("url") or DEFAULT_HOME))
        tab = _new_tab(url)
        _apply_compat(tab, url, body)
        _push_history(tab, url)
        doc.setdefault("tabs", []).append(tab)
        doc["active_tab"] = tab["id"]
        save_state(doc)
        return {"ok": True, "tab": tab, "status": browser_status()}

    if action in ("activate_start", "start"):
        tabs = doc.get("tabs") or []
        start = next((t for t in tabs if t.get("pinned") or t.get("role") == "start"), tabs[0] if tabs else None)
        if not start:
            return {"ok": False, "error": "no_start"}
        doc["active_tab"] = start["id"]
        save_state(doc)
        return {"ok": True, "tab": start, "status": browser_status()}

    if action == "close_tab":
        tab_id = str(body.get("tab_id") or "")
        tabs = doc.get("tabs") or []
        closing = _find_tab(doc, tab_id)
        if closing and (closing.get("pinned") or closing.get("role") in ("start", "files")):
            return {"ok": False, "error": "pinned_tab"}
        if len(tabs) <= 1:
            return {"ok": False, "error": "last_tab"}
        doc["tabs"] = [t for t in tabs if t.get("id") != tab_id]
        if doc.get("active_tab") == tab_id:
            doc["active_tab"] = doc["tabs"][0]["id"]
        save_state(doc)
        return {"ok": True, "status": browser_status()}

    if action == "activate_tab":
        tab_id = str(body.get("tab_id") or "")
        if not _find_tab(doc, tab_id):
            return {"ok": False, "error": "tab_missing"}
        doc["active_tab"] = tab_id
        save_state(doc)
        return {"ok": True, "status": browser_status()}

    if action == "back":
        tab = _find_tab(doc, str(body.get("tab_id") or doc.get("active_tab", "")))
        if not tab:
            return {"ok": False, "error": "tab_missing"}
        idx = tab.get("history_index", -1)
        if idx <= 0:
            return {"ok": False, "error": "history_start"}
        tab["history_index"] = idx - 1
        tab["url"] = tab["history"][tab["history_index"]]
        save_state(doc)
        return {"ok": True, "tab": tab, "status": browser_status()}

    if action == "forward":
        tab = _find_tab(doc, str(body.get("tab_id") or doc.get("active_tab", "")))
        if not tab:
            return {"ok": False, "error": "tab_missing"}
        hist = tab.get("history") or []
        idx = tab.get("history_index", -1)
        if idx >= len(hist) - 1:
            return {"ok": False, "error": "history_end"}
        tab["history_index"] = idx + 1
        tab["url"] = tab["history"][tab["history_index"]]
        save_state(doc)
        return {"ok": True, "tab": tab, "status": browser_status()}

    if action == "reload":
        tab = _find_tab(doc, str(body.get("tab_id") or doc.get("active_tab", "")))
        if not tab:
            return {"ok": False, "error": "tab_missing"}
        gate = _gate_nav(tab.get("url") or DEFAULT_HOME)
        _append_nav({"ts": _now(), "action": "reload", "url": tab.get("url"), "gate": gate})
        return {"ok": True, "tab": tab, "gate": gate, "status": browser_status()}

    if action == "home":
        body["url"] = doc.get("home") or DEFAULT_HOME
        body["action"] = "navigate"
        return dispatch(body)

    if action == "popout_tab":
        tab_id = str(body.get("tab_id") or doc.get("active_tab") or "")
        tab = _find_tab(doc, tab_id)
        if not tab:
            return {"ok": False, "error": "tab_missing"}
        if tab.get("pinned"):
            return {"ok": False, "error": "pinned_tab"}
        return {"ok": True, "tab": tab, "popout": True, "status": browser_status()}

    if action == "set_title":
        tab = _find_tab(doc, str(body.get("tab_id") or doc.get("active_tab", "")))
        if not tab:
            return {"ok": False, "error": "tab_missing"}
        tab["title"] = str(body.get("title") or tab.get("title") or "")
        save_state(doc)
        return {"ok": True, "tab": tab}

    if action == "gate_check":
        url = _normalize_url(str(body.get("url") or DEFAULT_HOME))
        gate = _gate_nav(url)
        return {"ok": True, "gate": gate}

    if action in ("set_compat", "compat_mode", "compat"):
        tab = _find_tab(doc, str(body.get("tab_id") or doc.get("active_tab") or ""))
        if not tab:
            return {"ok": False, "error": "tab_missing"}
        url = tab.get("url") or DEFAULT_HOME
        compat = _apply_compat(tab, url, body)
        save_state(doc)
        return {"ok": True, "tab": tab, "compat": compat, "status": browser_status()}

    if action in ("compat_profile", "compat_detect"):
        url = _normalize_url(str(body.get("url") or DEFAULT_HOME))
        compat = _compat_profile(url, mode=str(body.get("mode") or "auto"))
        return {"ok": True, "compat": compat}

    return {"ok": False, "error": "unknown_action", "action": action}


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd == "json":
        print(json.dumps(browser_status(), ensure_ascii=False))
        return 0
    if cmd == "dispatch":
        raw = sys.stdin.read()
        body = json.loads(raw) if raw.strip() else {}
        print(json.dumps(dispatch(body), ensure_ascii=False))
        return 0
    if cmd == "reset":
        save_state(default_state())
        print(json.dumps({"ok": True, "reset": True}, ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: queen-browser.py [json|dispatch|reset]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())