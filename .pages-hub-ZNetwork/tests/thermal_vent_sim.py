#!/usr/bin/env python3
"""Lab sim — thermal vent paths declared; monolithic blast forbidden."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STACK = ROOT.parent
THERMAL = STACK / "data" / "field-thermal-guard-doctrine.json"
WIRE = STACK / "Grok16" / "data" / "grok16-znetwork-field-wire-doctrine.json"


def main() -> int:
    for path in (THERMAL, WIRE):
        if not path.is_file():
            print(f"thermal_vent_sim: missing {path}", file=sys.stderr)
            return 1
    thermal = json.loads(THERMAL.read_text(encoding="utf-8"))
    policy = thermal.get("policy") or {}
    if not policy.get("monolithic_global_blast_forbidden"):
        print("thermal_vent_sim: monolithic blast must be forbidden", file=sys.stderr)
        return 1
    wire = json.loads(WIRE.read_text(encoding="utf-8"))
    vent = (wire.get("field_stream_mode") or {}).get("thermal_venting") or {}
    cool_sort = str(vent.get("cool_sort") or "").strip()
    if not cool_sort or "thermal" not in cool_sort.lower():
        print("thermal_vent_sim: cool_sort vent path required", file=sys.stderr)
        return 1
    cold_paths = vent.get("cold_vent_paths") or []
    if not cold_paths:
        print("thermal_vent_sim: cold_vent_paths required", file=sys.stderr)
        return 1
    print(json.dumps({
        "ok": True,
        "sim": "thermal_vent",
        "incremental_redata_only": policy.get("incremental_redata_only"),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())