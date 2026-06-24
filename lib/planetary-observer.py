#!/usr/bin/env python3
"""Planetary observation + proactive kills — global sight, local destroy, keep us safe."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
PANEL_CACHE = STATE / "planetary-observer-panel.json"
OPS_LOG = STATE / "planetary-proactive-kills.jsonl"

PROACTIVE_DEFAULT = os.environ.get("NEXUS_PLANETARY_PROACTIVE_KILL", "1") == "1"
REGIONAL_MIN_CLUSTER = int(os.environ.get("NEXUS_PLANETARY_REGIONAL_MIN", "5"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _mod(name: str, rel: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, INSTALL / "lib" / rel)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def _log_op(entry: dict[str, Any]) -> None:
    try:
        OPS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with OPS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": _now(), **entry}, ensure_ascii=False) + "\n")
    except OSError:
        pass


def observe() -> dict[str, Any]:
    """Aggregate planetary-scale threat sight from all field tables."""
    host = _load_json(STATE / "host-attacks.json", {"points": [], "stats": {}})
    points = [p for p in host.get("points") or [] if isinstance(p, dict)]
    gk = _load_json(STATE / "connection-intent.json", {})
    conns = gk.get("connections") or []
    harm = [c for c in conns if c.get("verdict") in ("HARM_CANDIDATE", "BLOCK_RECOMMENDED")]
    kill_ready = [c for c in conns if c.get("kill_eligible")]
    certain_pts = [p for p in points if p.get("strike_certain")]
    hot_pts = [p for p in points if (p.get("heat") or 0) >= 0.65 or p.get("severity") in ("critical", "high")]

    by_country: Counter[str] = Counter()
    by_asn: Counter[str] = Counter()
    zones_hot: dict[str, int] = defaultdict(int)
    for p in points:
        cc = str(p.get("country_code") or p.get("country") or "unknown").upper()[:8]
        asn = str(p.get("asn") or p.get("org") or "unknown")[:48]
        if cc and cc not in ("UNKNOWN", "—", "-"):
            by_country[cc] += 1
        if asn and asn.lower() != "unknown":
            by_asn[asn] += 1
        if p.get("strike_certain") or p.get("killable"):
            zones_hot[cc] += 1

    planetary_dns: dict[str, Any] = {}
    try:
        planetary_dns = _mod("dns_planetary", "dns-planetary-security.py").build_planetary_dns()
    except Exception:
        planetary_dns = {}

    hostile_ai: dict[str, Any] = {}
    try:
        hostile_ai = _mod("hostile_ai", "hostile-ai-destroy.py").build_panel()
    except Exception:
        hostile_ai = _load_json(STATE / "hostile-ai-panel.json", {})

    threat_lines = 0
    if (STATE / "threat-vectors.tsv").is_file():
        threat_lines = max(0, sum(1 for _ in (STATE / "threat-vectors.tsv").read_text(encoding="utf-8", errors="replace").splitlines()) - 1)

    top_regions = [
        {"country": k, "count": v, "hostile": zones_hot.get(k, 0)}
        for k, v in by_country.most_common(12)
    ]
    top_asn = [{"asn": k, "count": v} for k, v in by_asn.most_common(8)]

    return {
        "schema": "planetary-observer/v1",
        "updated": _now(),
        "motto": "Planetary observation — proactive kills to keep us all safe.",
        "doctrine": "Observe the whole planet. Destroy only at certainty. RE-KILL forever.",
        "planetary_dns": {
            "level": planetary_dns.get("planetary_security_level"),
            "zones": len(planetary_dns.get("zones") or []),
            "foreign_ipv4_blocked": len(planetary_dns.get("foreign_resolver_ipv4") or []),
            "foreign_ipv6_blocked": len(planetary_dns.get("foreign_resolver_ipv6") or []),
            "ipv6_truth": (planetary_dns.get("resolv") or {}).get("ipv6_truth_enforced"),
        },
        "globe": {
            "total_targets": len(points),
            "hot_targets": len(hot_pts),
            "strike_certain": len(certain_pts),
            "monitor_targets": sum(1 for p in points if p.get("is_monitor_target")),
            "top_regions": top_regions,
            "top_asn": top_asn,
        },
        "wire": {
            "connections": len(conns),
            "harm_candidates": len(harm),
            "kill_eligible": len(kill_ready),
            "strict_trust": gk.get("strict_trust"),
        },
        "hostile_ai": {
            "active": hostile_ai.get("active_count", 0),
            "certain": hostile_ai.get("certain_count", 0),
        },
        "threat_vector_events": threat_lines,
        "proactive_enabled": PROACTIVE_DEFAULT,
    }


def _top_hostile_region(obs: dict[str, Any]) -> tuple[str, str, int] | None:
    regions = obs.get("globe", {}).get("top_regions") or []
    for row in regions:
        hostile = int(row.get("hostile") or 0)
        if hostile >= REGIONAL_MIN_CLUSTER:
            cc = str(row.get("country") or "")
            if cc and cc not in ("UNKNOWN", "—"):
                return "country_code", cc, hostile
    return None


def proactive_cycle(*, force: bool = False) -> dict[str, Any]:
    """Run proactive destroy passes — planetary observation drives kills."""
    if not PROACTIVE_DEFAULT and not force:
        return {"ok": True, "skipped": True, "reason": "proactive_disabled"}

    obs = observe()
    results: dict[str, Any] = {
        "ok": True,
        "ts": _now(),
        "observation": obs,
        "actions": [],
    }

    ak = _mod("field_attack_kit", "field-attack-kit.py")
    ha = _mod("hostile_ai", "hostile-ai-destroy.py")
    ft = _mod("field_toolkit", "field-toolkit-db.py")

    # 1. Hostile AI at destroy certainty
    if int(obs.get("hostile_ai", {}).get("certain") or 0) > 0:
        out = ha.destroy_targets(all_certain=True)
        results["actions"].append({"step": "hostile_ai_destroy", **out})
        _log_op({"step": "hostile_ai_destroy", "killed": out.get("killed_count"), "attempted": out.get("attempted")})

    # 2. PINPOINT CERTAIN globe targets — autokill
    autokill = ak.autokill_certain()
    if autokill.get("destroyed_count"):
        results["actions"].append({"step": "autokill_certain", **autokill})
        _log_op({"step": "autokill_certain", "destroyed": autokill.get("destroyed_count")})

    # 3. RE-KILL validated returners
    rekill = ak.auto_rekill_validated()
    if rekill.get("rekilled_count"):
        results["actions"].append({"step": "auto_rekill", **rekill})
        _log_op({"step": "auto_rekill", "rekilled": rekill.get("rekilled_count")})

    # 4. Forever-kill enforce (capped per cycle)
    enforce = ak.forever_kill_enforce(max_ips=8)
    if enforce.get("enforced_count"):
        results["actions"].append({"step": "forever_kill_enforce", **enforce})
        _log_op({"step": "forever_kill_enforce", "enforced": enforce.get("enforced_count")})

    # 5. Regional cluster — planetary proactive disable
    cluster = _top_hostile_region(obs)
    if cluster:
        field, value, hostile_n = cluster
        regional = ft.regional_disable(f"{field}:{value}")
        if regional.get("killed_count") or regional.get("severed_count"):
            results["actions"].append({
                "step": "regional_disable",
                "field": field,
                "value": value,
                "hostile_in_cluster": hostile_n,
                **regional,
            })
            _log_op({
                "step": "regional_disable",
                "field": field,
                "value": value,
                "killed": regional.get("killed_count"),
            })

    results["action_count"] = len(results["actions"])
    results["summary"] = (
        f"Proactive cycle — {results['action_count']} action(s). "
        f"Globe {obs['globe']['total_targets']} targets · "
        f"{obs['globe']['strike_certain']} certain · "
        f"{obs['wire']['harm_candidates']} harm on wire."
    )
    return results


def build_panel(*, run_proactive: bool = False) -> dict[str, Any]:
    obs = observe()
    cycle: dict[str, Any] | None = None
    if run_proactive or PROACTIVE_DEFAULT:
        cycle = proactive_cycle()
    doc = {
        **obs,
        "last_proactive_cycle": cycle,
        "proactive_summary": (cycle or {}).get("summary") or "Observation only — proactive kill disabled.",
    }
    tmp = PANEL_CACHE.with_suffix(".tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(PANEL_CACHE)
    return doc


def panel_json() -> dict[str, Any]:
    if PANEL_CACHE.is_file():
        try:
            return json.loads(PANEL_CACHE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return build_panel(run_proactive=False)


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "panel").strip().lower()
    if cmd == "observe":
        print(json.dumps(observe(), ensure_ascii=False))
        return 0
    if cmd == "proactive":
        force = "--force" in sys.argv
        print(json.dumps(proactive_cycle(force=force), ensure_ascii=False))
        return 0
    if cmd == "cycle":
        print(json.dumps(build_panel(run_proactive=True), ensure_ascii=False))
        return 0
    if cmd == "panel":
        print(json.dumps(build_panel(run_proactive=PROACTIVE_DEFAULT), ensure_ascii=False))
        return 0
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: planetary-observer.py [observe|proactive|cycle|panel|json]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    import sys
    raise SystemExit(main())