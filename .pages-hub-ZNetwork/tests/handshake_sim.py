#!/usr/bin/env python3
"""Lab sim — handshake packets only; no steady stream."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIRE = ROOT.parent / "Grok16" / "data" / "grok16-znetwork-field-wire-doctrine.json"


def main() -> int:
    if not WIRE.is_file():
        print("handshake_sim: missing field wire doctrine", file=sys.stderr)
        return 1
    doc = json.loads(WIRE.read_text(encoding="utf-8"))
    fsm = doc.get("field_stream_mode") or {}
    if fsm.get("status") not in ("lab_locked_not_ready", "proposed"):
        print("handshake_sim: field_stream status must be lab_locked", file=sys.stderr)
        return 1
    phases = fsm.get("phases") or {}
    steady = phases.get("steady") or {}
    if steady.get("application_packets") is not False:
        print("handshake_sim: steady must forbid app packets", file=sys.stderr)
        return 1
    hs = phases.get("handshake") or {}
    if not hs.get("packets_allowed"):
        print("handshake_sim: handshake must allow brief packets", file=sys.stderr)
        return 1
    takeover = fsm.get("takeover") or {}
    if "REVIEW_ONLY" not in str(takeover.get("forbidden_in") or ""):
        print("handshake_sim: REVIEW_ONLY must forbid takeover", file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "sim": "handshake", "steady_app_packets": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())