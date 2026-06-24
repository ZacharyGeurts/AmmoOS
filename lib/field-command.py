#!/usr/bin/env python3
"""Field Command — unified Good Guy vs Bad Guy pulse + know-everything index."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))

GOOD_VERDICTS = frozenset({"USER_OK", "EPHEMERAL"})
WATCH_VERDICTS = frozenset({"MONITOR", "SUSPICIOUS"})
BAD_VERDICTS = frozenset({"HARM_CANDIDATE"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _slim_flow(row: dict[str, Any]) -> dict[str, Any]:
    sug = row.get("suggestion") or {}
    pol = row.get("flow_policy") or {}
    return {
        "process": row.get("process") or row.get("proc") or "—",
        "remote_ip": row.get("remote_ip") or row.get("rip") or "—",
        "remote_port": row.get("remote_port") or row.get("rport") or "",
        "verdict": row.get("verdict") or "—",
        "direction": row.get("direction") or row.get("direction_label") or "",
        "trust_meter": sug.get("trust_meter"),
        "concern_meter": sug.get("concern_meter"),
        "permit": pol.get("permit"),
        "block_scope": pol.get("block_scope"),
        "summary": (sug.get("summary") or row.get("reason") or "")[:160],
    }


def build_command(panel: dict[str, Any] | None = None) -> dict[str, Any]:
    panel = panel or _load_json(STATE / "threat-panel.json", {})
    gk = panel.get("gatekeeper") or {}
    conns = gk.get("connections") or []

    good = [c for c in conns if str(c.get("verdict") or "") in GOOD_VERDICTS]
    watch = [c for c in conns if str(c.get("verdict") or "") in WATCH_VERDICTS]
    bad = [c for c in conns if str(c.get("verdict") or "") in BAD_VERDICTS]
    other = [c for c in conns if c not in good and c not in watch and c not in bad]

    ha = panel.get("host_attacks") or {}
    ha_stats = ha.get("stats") or {}
    ak = panel.get("attack_kit") or {}
    rf = panel.get("field_rf") or {}
    hd = panel.get("human_dossier") or {}
    ad = panel.get("angel_dossiers") or {}
    vi = panel.get("vector_intel") or {}

    total = len(conns) or 1
    good_pct = round(100 * len(good) / total)
    bad_pct = round(100 * len(bad) / total)

    heaven = [c for c in conns if str(c.get("soul_side") or "") == "heaven"]
    hell = [c for c in conns if str(c.get("soul_side") or "") == "hell"]
    hell_chosen = [c for c in conns if c.get("hell_chosen")]

    return {
        "motto": (
            "We know Heaven from Hell. To those who chose Hell, we also choose it for them. "
            "No mercy. No friendly fire. God Bless."
        ),
        "tagline": (
            "Heaven passes at zero nft cost — no friendly fire. "
            "Hell gets ripped: forever block, eradicate, strike."
        ),
        "heaven_hell": {
            "heaven_count": len(heaven),
            "hell_count": len(hell),
            "hell_chosen_count": len(hell_chosen),
            "heaven_flows": [_slim_flow(c) for c in heaven[:10]],
            "hell_flows": [_slim_flow(c) for c in hell[:10]],
            "no_mercy": True,
            "no_friendly_fire": True,
        },
        "updated": panel.get("updated") or _now(),
        "version": panel.get("version"),
        "vigil_mode": panel.get("vigil_mode"),
        "truth_signal": panel.get("truth_signal"),
        "correlation_score": panel.get("correlation_score"),
        "packet_permission": {
            "enabled": bool(gk.get("packet_permission") or gk.get("strict_trust")),
            "why": gk.get("why_no_auto_block") or "",
            "permitted_flow_count": gk.get("permitted_flow_count", 0),
            "segment_block_count": gk.get("segment_block_count", 0),
            "harm_candidates": gk.get("harm_candidates", 0),
            "pending_trust_count": gk.get("pending_trust_count", 0),
            "connection_count": gk.get("connection_count", len(conns)),
        },
        "good_guy": {
            "label": "Good Guy",
            "count": len(good),
            "percent": good_pct,
            "verdicts": sorted(GOOD_VERDICTS),
            "flows": [_slim_flow(c) for c in good[:14]],
        },
        "watch": {
            "label": "Watch",
            "count": len(watch),
            "verdicts": sorted(WATCH_VERDICTS),
            "flows": [_slim_flow(c) for c in watch[:10]],
        },
        "bad_guy": {
            "label": "Bad Guy",
            "count": len(bad),
            "percent": bad_pct,
            "verdicts": sorted(BAD_VERDICTS),
            "flows": [_slim_flow(c) for c in bad[:14]],
        },
        "other_count": len(other),
        "pulse": {
            "firewall": panel.get("firewall"),
            "firewall_blocks": panel.get("firewall_blocks", 0),
            "threat_warnings": len(panel.get("threats") or []),
            "trusted_count": panel.get("trust_count", 0),
            "host_total": ha_stats.get("total", 0),
            "host_hot": ha_stats.get("hot", 0),
            "attack_kit_killed": ak.get("disabled_count", 0),
            "rf_recent_bursts": len(rf.get("recent_bursts") or []),
            "human_dossier_ips": hd.get("ip_count") or len(hd.get("ips") or []),
            "angel_dossiers": ad.get("dossier_count", 0),
            "vector_pests": vi.get("pest_count", 0),
            "honor_pending": len(
                ((panel.get("browser_awareness") or {}).get("honorability") or {}).get("pending_acceptance") or []
            ),
        },
        "know_everything": [
            {"id": "us", "label": "This machine", "stat": (panel.get("us_field") or {}).get("identity", {}).get("hostname", "—"), "jump": "us"},
            {"id": "packets-live", "label": "Live connections", "stat": f"{len(conns)} scored", "jump": "packets/live"},
            {"id": "packets-dpi", "label": "Packet DPI", "stat": f"{gk.get('segment_block_count', 0)} segment holds", "jump": "packets/dpi"},
            {"id": "threats-map", "label": "Threat map", "stat": f"{ha_stats.get('hot', 0)} hot", "jump": "threats/map"},
            {"id": "threats-kill", "label": "Kill orders", "stat": f"{hd.get('ip_count', 0)} IPs", "jump": "threats/kill"},
            {"id": "intel-trust", "label": "Honorability", "stat": f"{panel.get('trust_count', 0)} trusted", "jump": "intel/trust"},
            {"id": "intel-rf", "label": "Field RF", "stat": f"{len(rf.get('recent_bursts') or [])} bursts", "jump": "intel/rf"},
            {"id": "dns", "label": "Truth DNS", "stat": (panel.get("field_dns") or {}).get("planetary_security_level") or "—", "jump": "dns"},
            {"id": "intel-research", "label": "Research", "stat": f"{vi.get('active_count', 0)} vectors", "jump": "intel/research"},
            {"id": "system", "label": "System", "stat": panel.get("version") or "—", "jump": "system/settings"},
        ],
    }


def panel_json() -> dict[str, Any]:
    return build_command()


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: field-command.py [json]"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())