#!/usr/bin/env python3
"""Lab sim — FEC repair burst only; backoff before re-burst."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIRE = ROOT.parent / "Grok16" / "data" / "grok16-znetwork-field-wire-doctrine.json"
LAB = ROOT / "data" / "znetwork-outside-lab-doctrine.json"


def main() -> int:
    for path in (WIRE, LAB):
        if not path.is_file():
            print(f"fec_repair_sim: missing {path}", file=sys.stderr)
            return 1
    wire = json.loads(WIRE.read_text(encoding="utf-8"))
    lab = json.loads(LAB.read_text(encoding="utf-8"))
    ec = (wire.get("field_stream_mode") or {}).get("error_correction") or {}
    if ec.get("no_retry_storm") != "thermal_guard_backoff_ms before re-burst":
        print("fec_repair_sim: missing retry storm guard", file=sys.stderr)
        return 1
    if not lab.get("policy", {}).get("field_stream_forbidden_until_lab"):
        print("fec_repair_sim: field stream must be lab-forbidden", file=sys.stderr)
        return 1
    repair = (wire.get("field_stream_mode") or {}).get("phases", {}).get("repair") or {}
    allowed = repair.get("only") or []
    if "fec_subframe" not in allowed:
        print("fec_repair_sim: repair phase must list fec_subframe", file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "sim": "fec_repair", "retry_storm_guard": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())