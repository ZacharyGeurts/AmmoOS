#!/usr/bin/env python3
"""Police / public-safety agency database — global dropdown + format import."""
from __future__ import annotations

import csv
import io
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
SEED = INSTALL / "data" / "police-agencies-seed.json"
USER_DB = STATE / "police-agencies-user.json"
SELECTED = STATE / "police-agency-selected.json"
IMPORTS_DIR = STATE / "police-imports"


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


def _seed_doc() -> dict[str, Any]:
    return _load_json(SEED, {"agencies": [], "regions": []})


def _user_doc() -> dict[str, Any]:
    return _load_json(USER_DB, {"imports": [], "custom_agencies": [], "updated": None})


def _selected_id() -> str | None:
    doc = _load_json(SELECTED, {"agency_id": None})
    aid = doc.get("agency_id")
    return str(aid) if aid else None


def _agency_index() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in _seed_doc().get("agencies") or []:
        aid = str(row.get("id") or "")
        if aid:
            out[aid] = {**row, "source": "seed"}
    for row in _user_doc().get("custom_agencies") or []:
        aid = str(row.get("id") or "")
        if aid:
            out[aid] = {**row, "source": "operator"}
    return out


def list_agencies(region: str | None = None) -> list[dict[str, Any]]:
    idx = _agency_index()
    rows = list(idx.values())
    if region:
        rows = [r for r in rows if r.get("region") == region or region == "all"]
    return sorted(rows, key=lambda r: (r.get("country") or "", r.get("name") or ""))


def get_agency(agency_id: str) -> dict[str, Any] | None:
    return _agency_index().get(agency_id)


def surrounding_agencies(agency_id: str) -> list[dict[str, Any]]:
    base = get_agency(agency_id)
    if not base:
        return []
    idx = _agency_index()
    out: list[dict[str, Any]] = []
    for sid in base.get("surrounding") or []:
        row = idx.get(str(sid))
        if row:
            out.append(row)
    return out


def select_agency(agency_id: str) -> bool:
    if not get_agency(agency_id):
        return False
    _save_json(SELECTED, {"agency_id": agency_id, "updated": _now()})
    return True


def _parse_csv(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]


def _parse_ics205(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = re.split(r"\t|,|;", line)
        if len(parts) < 4:
            continue
        rows.append({
            "channel": parts[0].strip(),
            "function": parts[1].strip() if len(parts) > 1 else "",
            "rx_freq": parts[2].strip() if len(parts) > 2 else "",
            "tx_freq": parts[3].strip() if len(parts) > 3 else "",
            "mode": parts[4].strip() if len(parts) > 4 else "",
            "remarks": parts[5].strip() if len(parts) > 5 else "",
        })
    return rows


def import_format(agency_id: str, format_id: str, payload: str, filename: str = "") -> dict[str, Any]:
    agency = get_agency(agency_id)
    if not agency:
        return {"ok": False, "error": "unknown_agency"}
    fmt = None
    for row in agency.get("formats") or []:
        if str(row.get("id")) == format_id:
            fmt = row
            break
    if not fmt:
        return {"ok": False, "error": "unknown_format"}

    ext = str(fmt.get("ext") or "csv").lower()
    parsed: list[dict[str, Any]]
    if ext == "json":
        try:
            doc = json.loads(payload)
            parsed = doc if isinstance(doc, list) else [doc]
        except json.JSONDecodeError as exc:
            return {"ok": False, "error": f"invalid_json: {exc}"}
    elif ext == "ics205":
        parsed = _parse_ics205(payload)
    else:
        parsed = _parse_csv(payload)

    if not parsed:
        return {"ok": False, "error": "empty_import"}

    IMPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_name = re.sub(r"[^a-zA-Z0-9._-]+", "_", filename or f"{format_id}.import")[:80]
    out_path = IMPORTS_DIR / f"{agency_id}__{format_id}__{stamp}__{safe_name}.json"
    record = {
        "agency_id": agency_id,
        "format_id": format_id,
        "format_name": fmt.get("name"),
        "filename": filename,
        "imported_at": _now(),
        "row_count": len(parsed),
        "rows": parsed[:500],
    }
    _save_json(out_path, record)

    udoc = _user_doc()
    imports = list(udoc.get("imports") or [])
    imports.append({
        "agency_id": agency_id,
        "format_id": format_id,
        "path": str(out_path),
        "row_count": len(parsed),
        "imported_at": record["imported_at"],
        "filename": filename,
    })
    udoc["imports"] = imports[-200:]
    udoc["updated"] = _now()
    _save_json(USER_DB, udoc)

    return {
        "ok": True,
        "agency_id": agency_id,
        "format_id": format_id,
        "row_count": len(parsed),
        "path": str(out_path),
        "preview": parsed[:8],
    }


def panel_json() -> dict[str, Any]:
    seed = _seed_doc()
    sel_id = _selected_id()
    selected = get_agency(sel_id) if sel_id else None
    surrounding = surrounding_agencies(sel_id) if sel_id else []
    udoc = _user_doc()
    regions = seed.get("regions") or []
    agencies = list_agencies()
    return {
        "motto": seed.get("motto") or "Police protection systems — local and surrounding import.",
        "schema": seed.get("schema"),
        "default_region": seed.get("default_region") or "us",
        "regions": regions,
        "agencies": agencies,
        "agency_count": len(agencies),
        "selected_id": sel_id,
        "selected": selected,
        "surrounding": surrounding,
        "imports": (udoc.get("imports") or [])[-20:],
        "import_count": len(udoc.get("imports") or []),
        "updated": _now(),
    }


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False))
        return 0
    if cmd == "list":
        region = sys.argv[2] if len(sys.argv) > 2 else None
        print(json.dumps({"agencies": list_agencies(region)}, ensure_ascii=False))
        return 0
    if cmd == "select" and len(sys.argv) >= 3:
        ok = select_agency(sys.argv[2])
        print(json.dumps({"ok": ok, "agency_id": sys.argv[2]}))
        return 0 if ok else 1
    if cmd == "import" and len(sys.argv) >= 5:
        agency_id = sys.argv[2]
        format_id = sys.argv[3]
        payload = sys.argv[4]
        if payload == "-" and not sys.stdin.isatty():
            payload = sys.stdin.read()
        filename = sys.argv[5] if len(sys.argv) > 5 else ""
        result = import_format(agency_id, format_id, payload, filename)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result.get("ok") else 1
    if cmd == "get" and len(sys.argv) >= 3:
        row = get_agency(sys.argv[2])
        print(json.dumps(row or {"error": "not_found"}, ensure_ascii=False))
        return 0 if row else 1
    print(json.dumps({
        "error": "usage: police-agency-db.py [json|list [region]|select ID|get ID|import ID FORMAT PAYLOAD [filename]]",
    }))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())