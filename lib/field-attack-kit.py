#!/usr/bin/env python3
"""NEXUS Field Attack Kit — batch crush + field intel for hostile hosts."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
HOST_ATTACKS = STATE / "host-attacks.json"
HOSTILE_TSV = STATE / "field-hostile.tsv"


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _disabled_ips() -> set[str]:
    ips: set[str] = set()
    if not HOSTILE_TSV.is_file():
        return ips
    try:
        for line in HOSTILE_TSV.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) >= 2 and parts[1]:
                ips.add(parts[1])
    except OSError:
        pass
    return ips


def _run_disable(ip: str, vector: str, severity: str, reason: str, meta: dict[str, Any]) -> bool:
    script = INSTALL / "lib" / "field-attack-kit.sh"
    if not script.is_file():
        return False
    meta_path = STATE / "attack-kit-meta.tmp"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False) + "\n", encoding="utf-8")
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL)
    env["NEXUS_STATE_DIR"] = str(STATE)
    env["NEXUS_ATTACK_META"] = str(meta_path)
    safe_ip = ip.replace("'", "'\"'\"'")
    safe_vector = vector.replace("'", "'\"'\"'")
    safe_reason = reason.replace("'", "'\"'\"'")
    cmd = (
        f"source {INSTALL}/lib/nexus-common.sh && "
        f"source {INSTALL}/lib/firewall-sentinel.sh && "
        f"source {INSTALL}/lib/self-access.sh && "
        f"source {script} && "
        f"nexus_field_attack_disable_host '{safe_ip}' '{safe_vector}' '{severity}' '{safe_reason}' 'attack-kit'"
    )
    proc = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=30, env=env)
    return proc.returncode == 0


def crush_hot(heat_min: float = 0.7) -> dict[str, Any]:
    doc = _load_json(HOST_ATTACKS, {})
    points = doc.get("points") or []
    disabled = _disabled_ips()
    crushed: list[str] = []
    skipped: list[str] = []

    for p in points:
        ip = str(p.get("ip") or "")
        if not ip or ip in disabled:
            skipped.append(ip)
            continue
        heat = float(p.get("heat") or 0)
        if heat < heat_min:
            skipped.append(ip)
            continue
        vector = str(p.get("vector") or "HOSTILE")
        severity = str(p.get("severity") or "high")
        reason = f"attack_kit:heat={heat:.2f}"
        meta = {
            "heat": heat,
            "org": p.get("org"),
            "registrar": p.get("registrar"),
            "city": p.get("city"),
            "country": p.get("country"),
            "standards": p.get("standards"),
            "lat": p.get("lat"),
            "lon": p.get("lon"),
        }
        if _run_disable(ip, vector, severity, reason, meta):
            crushed.append(ip)
            disabled.add(ip)

    return {"ok": True, "crushed": crushed, "crushed_count": len(crushed), "skipped": len(skipped)}


def disable_one(ip: str, vector: str = "HOSTILE", severity: str = "high", reason: str = "operator_disable") -> dict[str, Any]:
    ok = _run_disable(ip, vector, severity, reason, {"ip": ip, "vector": vector})
    return {"ok": ok, "ip": ip, "permanent": ok}


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: field-attack-kit.py [crush-hot|disable <ip> [vector] [severity]]", file=sys.stderr)
        return 1
    cmd = sys.argv[1]
    if cmd == "crush-hot":
        json.dump(crush_hot(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if cmd == "disable" and len(sys.argv) >= 3:
        json.dump(
            disable_one(
                sys.argv[2],
                sys.argv[3] if len(sys.argv) > 3 else "HOSTILE",
                sys.argv[4] if len(sys.argv) > 4 else "high",
            ),
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())