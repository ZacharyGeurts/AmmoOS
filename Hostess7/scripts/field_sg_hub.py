#!/usr/bin/env pythong
"""SG/Hostess7 main hub — canonical folder, TEAM drive sync, reach map."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SG_ROOT = ROOT.parent
HUB_MANIFEST = ROOT / "cache" / "fieldstorage" / "brain" / "superintel" / "sg_hub.json"

LINKED_ROOTS: tuple[dict[str, str], ...] = (
    {"name": "Hostess7", "path": str(ROOT), "role": "canonical_main"},
    {"name": "AMOURANTHRTX", "path": str(SG_ROOT / "AMOURANTHRTX"), "role": "field_research"},
    {"name": "memes", "path": str(SG_ROOT / "memes"), "role": "vision_archive"},
    {"name": "KILROY", "path": str(SG_ROOT / "KILROY"), "role": "graphics_codec"},
    {"name": "NEXUS-Shield", "path": "/home/default/Downloads/NEXUS-Shield-main", "role": "security_daemon"},
    {"name": "TEAM_drive", "path": "/mnt/team/Hostess7", "role": "nvme_mirror"},
)


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def hub_status() -> dict:
    entries = []
    for item in LINKED_ROOTS:
        p = Path(item["path"])
        entries.append({
            **item,
            "present": p.is_dir() or p.is_file(),
            "writable": p.is_dir() and os.access(p, os.W_OK),
        })
    doc = {
        "updated": _ts(),
        "canonical": str(ROOT),
        "sg_root": str(SG_ROOT),
        "policy": "SG/Hostess7 is the main folder; TEAM drive mirrors Hostess7; reach points here first.",
        "roots": entries,
    }
    HUB_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    HUB_MANIFEST.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def print_hub(doc: dict) -> None:
    print("=== SG / Hostess7 Hub ===")
    print(f"Canonical: {doc['canonical']}")
    print(f"SG root:   {doc['sg_root']}")
    print(doc["policy"])
    print()
    for r in doc["roots"]:
        flag = "OK" if r["present"] else "missing"
        wr = "rw" if r.get("writable") else "ro"
        print(f"  [{flag}] {r['name']:14} {wr:3} {r['role']:16} {r['path']}")
    print(f"\nManifest: {HUB_MANIFEST}")
    print("METRIC sg_hub=1")
    print("OK sg-hub")


def sync_team_hint() -> None:
    print("\nTEAM sync: ./Hostess7.sh team-sync  (rsync Hostess7 → /mnt/team/Hostess7)")
    print("zac-pack:  HOSTESS7_TEAM=1 ./Hostess7.sh zac-pack")


def main() -> int:
    doc = hub_status()
    print_hub(doc)
    sync_team_hint()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())