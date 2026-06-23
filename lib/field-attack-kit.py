#!/usr/bin/env python3
"""NEXUS Field Attack Kit — batch crush, KILL targets, permanent dossier archive."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
HOST_ATTACKS = STATE / "host-attacks.json"
HOSTILE_TSV = STATE / "field-hostile.tsv"
DOSSIERS = STATE / "angel-dossiers.json"

import importlib.util

_fg_spec = importlib.util.spec_from_file_location("friendly_guard", INSTALL / "lib" / "friendly-guard.py")
_fg = importlib.util.module_from_spec(_fg_spec)
assert _fg_spec and _fg_spec.loader
_fg_spec.loader.exec_module(_fg)
refuse_kill = _fg.refuse_kill

_hi_spec = importlib.util.spec_from_file_location("host_identity", INSTALL / "lib" / "host-identity.py")
_hi = importlib.util.module_from_spec(_hi_spec)
assert _hi_spec and _hi_spec.loader
_hi_spec.loader.exec_module(_hi)
check_target_online = _hi.check_target_online
extract_identity_fingerprint = _hi.extract_identity_fingerprint
fingerprint_from_point_or_dossier = _hi.fingerprint_from_point_or_dossier
load_archived_dossier = _hi.load_archived_dossier


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def _point_for_ip(ip: str) -> dict[str, Any]:
    doc = _load_json(HOST_ATTACKS, {})
    for p in doc.get("points") or []:
        if str(p.get("ip") or "") == ip:
            return p
    return {}


def _full_dossier_for_ip(ip: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    point = _point_for_ip(ip)
    if extra:
        point = {**point, **{k: v for k, v in extra.items() if v is not None}}

    dossier_doc = _load_json(DOSSIERS, {"dossiers": []})
    angel = None
    for d in dossier_doc.get("dossiers") or []:
        if str(d.get("peer") or "") == ip:
            angel = d
            break

    bleed_doc: dict[str, Any] = {}
    bleed_script = INSTALL / "lib" / "target-bleed.py"
    if bleed_script.is_file():
        _tb_spec = importlib.util.spec_from_file_location("target_bleed_kit", bleed_script)
        _tb = importlib.util.module_from_spec(_tb_spec)
        assert _tb_spec and _tb_spec.loader
        _tb_spec.loader.exec_module(_tb)
        bleed_doc = _tb.bleed_target(ip, conn_hint=point.get("monitor"), online=False)

    return {
        "archived": _now(),
        "ip": ip,
        "vector": point.get("vector") or (extra or {}).get("vector") or "HOSTILE",
        "severity": point.get("severity") or (extra or {}).get("severity") or "high",
        "verdict": point.get("verdict", ""),
        "heat": point.get("heat"),
        "geo": {
            "lat": point.get("lat"),
            "lon": point.get("lon"),
            "city": point.get("city"),
            "region": point.get("region"),
            "country": point.get("country"),
            "org": point.get("org"),
            "asn": point.get("asn"),
            "registrar": point.get("registrar"),
            "geo_source": point.get("geo_source"),
        },
        "monitor": point.get("monitor") or (extra or {}).get("monitor"),
        "dossier": point.get("dossier") or (extra or {}).get("dossier"),
        "angel_dossier": angel,
        "host_context": point.get("host_context") or bleed_doc.get("host"),
        "target_bleed": point.get("target_bleed") or bleed_doc,
        "target_os": point.get("target_os") or bleed_doc.get("target_os") or "",
        "intel": {
            "hostname": point.get("hostname"),
            "mac": point.get("mac"),
            "mac_vendor": point.get("mac_vendor"),
            "abuse_contact": point.get("abuse_contact"),
            "standards": point.get("standards"),
            "detail": point.get("detail"),
            "process": point.get("process"),
            "direction": point.get("direction"),
            "source": point.get("source"),
        },
        "permanent": True,
        "action": "KILL",
        "identity_fingerprint": extract_identity_fingerprint(
            {
                "ip": ip,
                **point,
                "geo": {
                    "lat": point.get("lat"),
                    "lon": point.get("lon"),
                    "city": point.get("city"),
                    "region": point.get("region"),
                    "country": point.get("country"),
                    "org": point.get("org"),
                    "asn": point.get("asn"),
                    "registrar": point.get("registrar"),
                    "geo_source": point.get("geo_source"),
                },
                "intel": {
                    "hostname": point.get("hostname"),
                    "mac": point.get("mac"),
                    "mac_vendor": point.get("mac_vendor"),
                    "mac_oui": point.get("mac_oui"),
                },
            }
        ),
    }


def _run_kill(
    ip: str,
    vector: str,
    severity: str,
    reason: str,
    dossier: dict[str, Any],
) -> bool:
    monitor = dossier.get("monitor") if isinstance(dossier.get("monitor"), dict) else None
    refuse, _guard_reason = refuse_kill(ip, monitor=monitor)
    if refuse:
        return False
    script = INSTALL / "lib" / "field-attack-kit.sh"
    if not script.is_file():
        return False
    meta_path = STATE / "attack-kit-meta.tmp"
    dossier_path = STATE / "attack-kit-dossier.tmp"
    meta_path.write_text(json.dumps(dossier, ensure_ascii=False) + "\n", encoding="utf-8")
    dossier_path.write_text(json.dumps(dossier, ensure_ascii=False) + "\n", encoding="utf-8")
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL)
    env["NEXUS_STATE_DIR"] = str(STATE)
    env["NEXUS_ATTACK_META"] = str(meta_path)
    env["NEXUS_ATTACK_DOSSIER"] = str(dossier_path)
    safe_ip = ip.replace("'", "'\"'\"'")
    safe_vector = vector.replace("'", "'\"'\"'")
    safe_reason = reason.replace("'", "'\"'\"'")
    cmd = (
        f"source {INSTALL}/lib/nexus-common.sh && "
        f"source {INSTALL}/lib/firewall-sentinel.sh && "
        f"source {INSTALL}/lib/firewall-trust.sh && "
        f"source {INSTALL}/lib/self-access.sh && "
        f"source {INSTALL}/lib/friendly-guard.sh && "
        f"source {script} && "
        f'DOSSIER_JSON="$(cat "{dossier_path}")" && '
        f"nexus_field_attack_kill_target '{safe_ip}' '{safe_vector}' '{severity}' '{safe_reason}' 'attack-kit' \"$DOSSIER_JSON\""
    )
    proc = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=45, env=env)
    return proc.returncode == 0


def kill_target(
    ip: str,
    vector: str = "HOSTILE",
    severity: str = "high",
    reason: str = "target_kill",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    point = _point_for_ip(ip)
    monitor = (extra or {}).get("monitor") or point.get("monitor")
    monitor_dict = monitor if isinstance(monitor, dict) else None
    refuse, guard_reason = refuse_kill(ip, monitor=monitor_dict)
    if refuse:
        return {
            "ok": False,
            "ip": ip,
            "permanent": False,
            "killed": False,
            "dossier_archived": False,
            "friendly_refused": True,
            "reason": guard_reason,
            "dossier": {},
        }
    dossier = _full_dossier_for_ip(ip, extra)
    ok = _run_kill(ip, vector, severity, reason, dossier)
    return {
        "ok": ok,
        "ip": ip,
        "permanent": ok,
        "killed": ok,
        "dossier_archived": ok,
        "friendly_refused": False,
        "dossier": dossier if ok else {},
    }


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
        result = kill_target(ip, vector, severity, reason)
        if result.get("ok"):
            crushed.append(ip)
            disabled.add(ip)

    return {"ok": True, "crushed": crushed, "crushed_count": len(crushed), "killed_count": len(crushed), "skipped": len(skipped)}


def disable_one(ip: str, vector: str = "HOSTILE", severity: str = "high", reason: str = "operator_disable") -> dict[str, Any]:
    return kill_target(ip, vector, severity, reason)


def _save_online_check(ip: str, doc: dict[str, Any]) -> None:
    path = STATE / "target-online-check.json"
    cache = _load_json(path, {"checks": {}})
    checks = cache.get("checks")
    if not isinstance(checks, dict):
        checks = {}
    checks[ip] = doc
    cache["checks"] = checks
    cache["updated"] = _now()
    try:
        path.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def check_online(ip: str) -> dict[str, Any]:
    doc = check_target_online(ip, _point_for_ip(ip) or None)
    if doc.get("ok"):
        _save_online_check(ip, doc)
    return doc


def _run_rekill(
    ip: str,
    vector: str,
    severity: str,
    reason: str,
    dossier: dict[str, Any],
) -> bool:
    script = INSTALL / "lib" / "field-attack-kit.sh"
    if not script.is_file():
        return False
    dossier_path = STATE / "attack-kit-dossier.tmp"
    dossier_path.write_text(json.dumps(dossier, ensure_ascii=False) + "\n", encoding="utf-8")
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL)
    env["NEXUS_STATE_DIR"] = str(STATE)
    safe_ip = ip.replace("'", "'\"'\"'")
    safe_vector = vector.replace("'", "'\"'\"'")
    safe_reason = reason.replace("'", "'\"'\"'")
    cmd = (
        f"source {INSTALL}/lib/nexus-common.sh && "
        f"source {INSTALL}/lib/firewall-sentinel.sh && "
        f"source {INSTALL}/lib/firewall-trust.sh && "
        f"source {INSTALL}/lib/self-access.sh && "
        f"source {INSTALL}/lib/friendly-guard.sh && "
        f"source {script} && "
        f'DOSSIER_JSON="$(cat "{dossier_path}")" && '
        f"nexus_field_attack_rekill_target '{safe_ip}' '{safe_vector}' '{severity}' '{safe_reason}' 'attack-kit' \"$DOSSIER_JSON\""
    )
    proc = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=45, env=env)
    return proc.returncode == 0


def rekill_target(ip: str, vector: str = "HOSTILE", severity: str = "high") -> dict[str, Any]:
    point = _point_for_ip(ip)
    online_doc = check_target_online(ip, point or None)
    if not online_doc.get("online"):
        return {
            "ok": False,
            "ip": ip,
            "rekill": False,
            "reason": "target_offline",
            "online_check": online_doc,
        }
    if not online_doc.get("same_host"):
        return {
            "ok": False,
            "ip": ip,
            "rekill": False,
            "reason": online_doc.get("validation", {}).get("reason", "identity_mismatch"),
            "online_check": online_doc,
        }
    archived = load_archived_dossier(ip) or _full_dossier_for_ip(ip)
    dossier = dict(archived)
    dossier.update({
        "action": "REKILL",
        "rekill": True,
        "rekill_ts": _now(),
        "online_check": online_doc,
        "identity_validation": online_doc.get("validation"),
    })
    reason = "rekill_same_host_validated"
    ok = _run_rekill(ip, vector, severity, reason, dossier)
    return {
        "ok": ok,
        "ip": ip,
        "rekill": ok,
        "killed": ok,
        "same_host": True,
        "online": True,
        "online_check": online_doc,
        "dossier_archived": ok,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: field-attack-kit.py [crush-hot|kill|disable|check-online|rekill <ip> ...]", file=sys.stderr)
        return 1
    cmd = sys.argv[1]
    if cmd == "check-online" and len(sys.argv) >= 3:
        json.dump(check_online(sys.argv[2]), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if cmd == "rekill" and len(sys.argv) >= 3:
        json.dump(
            rekill_target(
                sys.argv[2],
                sys.argv[3] if len(sys.argv) > 3 else "HOSTILE",
                sys.argv[4] if len(sys.argv) > 4 else "high",
            ),
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
        return 0
    if cmd == "crush-hot":
        json.dump(crush_hot(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if cmd in ("kill", "disable") and len(sys.argv) >= 3:
        json.dump(
            kill_target(
                sys.argv[2],
                sys.argv[3] if len(sys.argv) > 3 else "HOSTILE",
                sys.argv[4] if len(sys.argv) > 4 else "high",
                "target_kill" if cmd == "kill" else "operator_disable",
            ),
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())