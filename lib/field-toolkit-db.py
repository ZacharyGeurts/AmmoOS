#!/usr/bin/env python3
"""Field toolkit — attack study catalog and automated defense profiles."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
SEED = INSTALL / "data" / "field-toolkit-seed.json"
USER = STATE / "field-toolkit-user.json"


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


def _seed() -> dict[str, Any]:
    return _load_json(SEED, {"attacks": [], "defenses": []})


def _user() -> dict[str, Any]:
    return _load_json(USER, {"defense_overrides": {}, "study_notes": {}, "updated": None})


def _defense_enabled(defn: dict[str, Any], overrides: dict[str, Any]) -> bool:
    did = str(defn.get("id") or "")
    if did in overrides:
        return bool(overrides[did])
    return bool(defn.get("default", False))


def list_attacks(category: str | None = None, query: str | None = None) -> list[dict[str, Any]]:
    rows = list(_seed().get("attacks") or [])
    if category:
        rows = [r for r in rows if r.get("category") == category]
    if query:
        q = query.lower()
        rows = [
            r for r in rows
            if q in str(r.get("label") or "").lower()
            or q in str(r.get("vector") or "").lower()
            or q in str(r.get("study") or "").lower()
            or any(q in str(i).lower() for i in (r.get("indicators") or []))
        ]
    return rows


def get_attack(attack_id: str) -> dict[str, Any] | None:
    for row in _seed().get("attacks") or []:
        if str(row.get("id")) == attack_id:
            udoc = _user()
            notes = (udoc.get("study_notes") or {}).get(attack_id)
            out = dict(row)
            if notes:
                out["operator_notes"] = notes
            return out
    return None


def list_defenses() -> list[dict[str, Any]]:
    udoc = _user()
    overrides = udoc.get("defense_overrides") or {}
    out: list[dict[str, Any]] = []
    for row in _seed().get("defenses") or []:
        did = str(row.get("id") or "")
        out.append({
            **row,
            "enabled": _defense_enabled(row, overrides),
        })
    return out


def toggle_defense(defense_id: str, enabled: bool | None = None) -> dict[str, Any]:
    seed_ids = {str(d.get("id")) for d in (_seed().get("defenses") or [])}
    if defense_id not in seed_ids:
        return {"ok": False, "error": "unknown_defense"}
    udoc = _user()
    overrides = dict(udoc.get("defense_overrides") or {})
    if enabled is None:
        seed = next(d for d in (_seed().get("defenses") or []) if d.get("id") == defense_id)
        enabled = not _defense_enabled(seed, overrides)
    overrides[defense_id] = bool(enabled)
    udoc["defense_overrides"] = overrides
    udoc["updated"] = _now()
    _save_json(USER, udoc)
    return {"ok": True, "defense_id": defense_id, "enabled": bool(enabled)}


def add_study_note(attack_id: str, note: str) -> dict[str, Any]:
    if not get_attack(attack_id):
        return {"ok": False, "error": "unknown_attack"}
    udoc = _user()
    notes = dict(udoc.get("study_notes") or {})
    prev = str(notes.get(attack_id) or "").strip()
    merged = f"{prev}\n{note}".strip() if prev and note.strip() else (note.strip() or prev)
    notes[attack_id] = merged
    udoc["study_notes"] = notes
    udoc["updated"] = _now()
    _save_json(USER, udoc)
    return {"ok": True, "attack_id": attack_id}


def panel_json() -> dict[str, Any]:
    seed = _seed()
    defenses = list_defenses()
    enabled_count = sum(1 for d in defenses if d.get("enabled"))
    return {
        "motto": seed.get("motto") or "Study attacks — expand automated defenses.",
        "attack_count": len(seed.get("attacks") or []),
        "defense_count": len(defenses),
        "defenses_enabled": enabled_count,
        "attacks": list_attacks(),
        "defenses": defenses,
        "categories": sorted({str(a.get("category") or "other") for a in (seed.get("attacks") or [])}),
        "updated": _now(),
    }


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False))
        return 0
    if cmd == "get" and len(sys.argv) >= 3:
        row = get_attack(sys.argv[2])
        print(json.dumps(row or {"error": "not_found"}, ensure_ascii=False))
        return 0 if row else 1
    if cmd == "toggle" and len(sys.argv) >= 3:
        enabled = None
        if len(sys.argv) >= 4:
            enabled = sys.argv[3].lower() in ("1", "true", "on", "yes")
        print(json.dumps(toggle_defense(sys.argv[2], enabled), ensure_ascii=False))
        return 0
    if cmd == "note" and len(sys.argv) >= 4:
        print(json.dumps(add_study_note(sys.argv[2], sys.argv[3]), ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: field-toolkit-db.py [json|get ID|toggle ID [on|off]|note ID TEXT]"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())