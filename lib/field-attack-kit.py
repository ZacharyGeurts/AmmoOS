#!/usr/bin/env python3
"""NEXUS Field Attack Kit — batch crush, KILL targets, permanent dossier archive."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
HOST_ATTACKS = STATE / "host-attacks.json"
HOSTILE_TSV = STATE / "field-hostile.tsv"
NOKILL_TSV = STATE / "field-nokill.tsv"
DOSSIERS = STATE / "angel-dossiers.json"
AUTO_REKILL_LOG = STATE / "auto-rekill-log.json"
AUTO_REKILL_COOLDOWN_SEC = 3600
AUTO_REKILL_MAX_IPS = int(os.environ.get("NEXUS_AUTO_REKILL_MAX_IPS", "64"))
AUTOKILL_NEEDS_DIE_MAX = int(os.environ.get("NEXUS_PLANETARY_AUTOKILL_MAX", "64"))
FOREVER_KILL_MAX_IPS = int(os.environ.get("NEXUS_PLANETARY_FOREVER_KILL_MAX", "64"))

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

_ts_spec = importlib.util.spec_from_file_location("trust_strike", INSTALL / "lib" / "trust-strike-engine.py")
_ts = importlib.util.module_from_spec(_ts_spec)
assert _ts_spec and _ts_spec.loader
_ts_spec.loader.exec_module(_ts)
gate_strike = _ts.gate_strike

_kr_spec = importlib.util.spec_from_file_location("kill_reason_plain", INSTALL / "lib" / "kill-reason-plain.py")
_kr = importlib.util.module_from_spec(_kr_spec)
assert _kr_spec and _kr_spec.loader
_kr_spec.loader.exec_module(_kr)
explain_kill = _kr.explain_kill
attach_to_dossier = _kr.attach_to_dossier
explain_from_archived = _kr.explain_from_archived


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


def _nokill_ips() -> set[str]:
    ips: set[str] = set()
    if not NOKILL_TSV.is_file():
        return ips
    try:
        for line in NOKILL_TSV.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) >= 2 and parts[1]:
                ips.add(parts[1])
    except OSError:
        pass
    return ips


def _is_nokill(ip: str) -> bool:
    return ip in _nokill_ips()


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


def nokill_target(
    ip: str,
    vector: str = "HOSTILE",
    severity: str = "high",
    reason: str = "operator_nokill",
) -> dict[str, Any]:
    if not ip:
        return {"ok": False, "ip": ip, "nokill": False, "reason": "missing_ip"}
    if _is_nokill(ip):
        return {"ok": True, "ip": ip, "nokill": True, "already": True, "reason": "already_nokill"}
    script = INSTALL / "lib" / "field-attack-kit.sh"
    if not script.is_file():
        return {"ok": False, "ip": ip, "nokill": False, "reason": "kit_missing"}
    safe_ip = ip.replace("'", "'\"'\"'")
    safe_vector = vector.replace("'", "'\"'\"'")
    safe_reason = reason.replace("'", "'\"'\"'")
    cmd = (
        f"source {INSTALL}/lib/nexus-common.sh && "
        f"source {script} && "
        f"nexus_field_attack_nokill_target '{safe_ip}' '{safe_vector}' '{severity}' '{safe_reason}' 'attack-kit'"
    )
    env = os.environ.copy()
    env["NEXUS_INSTALL_ROOT"] = str(INSTALL)
    env["NEXUS_STATE_DIR"] = str(STATE)
    proc = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=20, env=env)
    ok = proc.returncode == 0
    return {
        "ok": ok,
        "ip": ip,
        "nokill": ok,
        "reason": reason if ok else "nokill_failed",
    }


def kill_target(
    ip: str,
    vector: str = "HOSTILE",
    severity: str = "high",
    reason: str = "target_kill",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if _is_nokill(ip):
        return {
            "ok": False,
            "ip": ip,
            "permanent": False,
            "killed": False,
            "dossier_archived": False,
            "nokill_refused": True,
            "reason": "nokill_exempt",
            "dossier": {},
        }
    point = _point_for_ip(ip)
    monitor = (extra or {}).get("monitor") or point.get("monitor")
    monitor_dict = monitor if isinstance(monitor, dict) else None
    force = bool((extra or {}).get("force"))
    strike_mode = str((extra or {}).get("strike_mode") or "manual")
    strike_gate = gate_strike(ip, point, mode=strike_mode, monitor=monitor_dict, force=force)
    if strike_gate.get("friendly_refused"):
        return {
            "ok": False,
            "ip": ip,
            "permanent": False,
            "killed": False,
            "dossier_archived": False,
            "friendly_refused": True,
            "reason": strike_gate.get("friendly_reason") or strike_gate.get("reason"),
            "strike_gate": strike_gate,
            "dossier": {},
        }
    if not strike_gate.get("allowed"):
        return {
            "ok": False,
            "ip": ip,
            "permanent": False,
            "killed": False,
            "dossier_archived": False,
            "strike_refused": True,
            "reason": strike_gate.get("reason", "strike_confidence_low"),
            "strike_confidence": strike_gate.get("strike_confidence"),
            "strike_gate": strike_gate,
            "dossier": {},
        }
    dossier = _full_dossier_for_ip(ip, extra)
    hardware_destroy = bool(strike_gate.get("hardware_destroy") or strike_gate.get("strike_certain"))
    if hardware_destroy:
        dossier.update({
            "action": "HARDWARE_DESTROY",
            "hardware_destroy": True,
            "certainty": 1.0,
            "strike_mode": "destroy",
            "wire_point": strike_gate.get("wire_point") or (strike_gate.get("score") or {}).get("wire_point"),
        })
    dossier["strike_gate"] = {
        "strike_certain": strike_gate.get("strike_certain"),
        "hardware_destroy": hardware_destroy,
        "strike_confidence": strike_gate.get("strike_confidence"),
        "certainty": strike_gate.get("certainty"),
    }
    dossier["reason"] = reason
    dossier["kill_reason"] = reason
    dossier["source"] = (extra or {}).get("source") or "attack-kit"
    action = "HARDWARE DESTROY" if hardware_destroy else "KILL"
    attach_to_dossier(
        dossier,
        explain_kill(
            ip=ip,
            reason=reason,
            action=action,
            point=point,
            strike_gate=strike_gate,
            vector=vector,
            process=str(point.get("our_process") or point.get("process") or ""),
            source=str(dossier.get("source") or ""),
            hostile=(extra or {}).get("hostile"),
        ),
    )
    ok = _run_kill(ip, vector, severity, reason, dossier)
    why = {
        "why_killed_plain": dossier.get("why_killed_plain"),
        "why_killed_short": dossier.get("why_killed_short"),
        "why_killed_code": dossier.get("why_killed_code"),
    }
    return {
        "ok": ok,
        "ip": ip,
        "permanent": ok,
        "killed": ok,
        "hardware_destroy": hardware_destroy and ok,
        "dossier_archived": ok,
        "friendly_refused": False,
        "strike_confidence": strike_gate.get("strike_confidence"),
        "certainty": 1.0 if hardware_destroy else strike_gate.get("strike_confidence"),
        "strike_gate": strike_gate,
        "dossier": dossier if ok else {},
        **(why if ok else {}),
    }


def _kill_strike_certain_point(
    p: dict[str, Any],
    *,
    reason_prefix: str,
    disabled: set[str],
    nokill: set[str],
) -> tuple[str | None, dict[str, Any] | None]:
    ip = str(p.get("ip") or "")
    if not ip or ip in disabled or ip in nokill:
        return ip or None, None
    if not p.get("strike_certain"):
        return ip, None
    vector = str(p.get("vector") or "HOSTILE")
    severity = str(p.get("severity") or "high")
    reason = f"{reason_prefix}:strike_certain=1.0"
    result = kill_target(
        ip,
        vector,
        severity,
        reason,
        extra={"strike_mode": "auto", "monitor": p.get("monitor")},
    )
    if result.get("ok"):
        disabled.add(ip)
        return ip, result
    return ip, result


def _point_needs_die(p: dict[str, Any]) -> bool:
    if p.get("nokill") or p.get("target_status") == "killed" or p.get("disabled_permanent"):
        return False
    return bool(p.get("strike_certain") or p.get("killable"))


def _kill_killable_point(
    p: dict[str, Any],
    *,
    reason_prefix: str,
    disabled: set[str],
    nokill: set[str],
) -> tuple[str | None, dict[str, Any] | None]:
    ip = str(p.get("ip") or "")
    if not ip or ip in disabled or ip in nokill:
        return ip or None, None
    if not p.get("killable") or p.get("strike_certain"):
        return ip, None
    vector = str(p.get("vector") or "HOSTILE")
    severity = str(p.get("severity") or "high")
    reason = f"{reason_prefix}:killable=1"
    result = kill_target(
        ip,
        vector,
        severity,
        reason,
        extra={"strike_mode": "manual", "monitor": p.get("monitor")},
    )
    if result.get("ok"):
        disabled.add(ip)
    return ip, result


def autokill_needs_die(max_targets: int | None = None) -> dict[str, Any]:
    """Autokill every globe target that needs to die — PINPOINT CERTAIN + killable."""
    cap = AUTOKILL_NEEDS_DIE_MAX if max_targets is None else max_targets
    doc = _load_json(HOST_ATTACKS, {})
    points = [p for p in doc.get("points") or [] if _point_needs_die(p)]
    points.sort(
        key=lambda p: (
            0 if p.get("strike_certain") else 1,
            -(float(p.get("strike_confidence") or 0)),
            -(float(p.get("heat") or 0)),
        )
    )
    disabled = _disabled_ips()
    nokill = _nokill_ips()
    destroyed: list[str] = []
    certain_killed: list[str] = []
    killable_killed: list[str] = []
    skipped: list[str] = []
    results: list[dict[str, Any]] = []

    for p in points[:cap]:
        if p.get("strike_certain"):
            ip, result = _kill_strike_certain_point(
                p,
                reason_prefix="autokill_needs_die",
                disabled=disabled,
                nokill=nokill,
            )
        else:
            ip, result = _kill_killable_point(
                p,
                reason_prefix="autokill_needs_die",
                disabled=disabled,
                nokill=nokill,
            )
        if not ip:
            continue
        if result and result.get("ok"):
            destroyed.append(ip)
            if p.get("strike_certain"):
                certain_killed.append(ip)
            else:
                killable_killed.append(ip)
            results.append({
                "ip": ip,
                "hardware_destroy": result.get("hardware_destroy"),
                "ok": True,
                "why_killed_plain": result.get("why_killed_plain"),
            })
        elif result:
            skipped.append(ip)
            results.append({"ip": ip, "ok": False, "reason": result.get("reason")})
        else:
            skipped.append(ip)

    return {
        "ok": True,
        "autokill": True,
        "needs_die": True,
        "destroyed": destroyed,
        "destroyed_count": len(destroyed),
        "killed_count": len(destroyed),
        "certain_killed_count": len(certain_killed),
        "killable_killed_count": len(killable_killed),
        "hardware_destroy_count": sum(1 for r in results if r.get("hardware_destroy")),
        "candidates": len(points),
        "skipped": len(skipped),
        "results": results[:32],
    }


def autokill_certain() -> dict[str, Any]:
    """Autokill path — PINPOINT CERTAIN · 100% only. Hardware destroy + forever kill."""
    doc = _load_json(HOST_ATTACKS, {})
    points = doc.get("points") or []
    disabled = _disabled_ips()
    nokill = _nokill_ips()
    destroyed: list[str] = []
    skipped: list[str] = []
    results: list[dict[str, Any]] = []

    for p in points:
        ip, result = _kill_strike_certain_point(
            p,
            reason_prefix="autokill_certain",
            disabled=disabled,
            nokill=nokill,
        )
        if not ip:
            continue
        if result and result.get("ok"):
            destroyed.append(ip)
            results.append({"ip": ip, "hardware_destroy": result.get("hardware_destroy"), "ok": True})
        elif not p.get("strike_certain"):
            skipped.append(ip)
        elif result:
            skipped.append(ip)
            results.append({"ip": ip, "ok": False, "reason": result.get("reason")})

    return {
        "ok": True,
        "autokill": True,
        "destroyed": destroyed,
        "destroyed_count": len(destroyed),
        "killed_count": len(destroyed),
        "hardware_destroy_count": sum(1 for r in results if r.get("hardware_destroy")),
        "skipped": len(skipped),
        "results": results[:24],
    }


def crush_hot(heat_min: float = 0.7) -> dict[str, Any]:
    """Operator crush — 100% PINPOINT CERTAIN targets only (hardware destroy)."""
    doc = _load_json(HOST_ATTACKS, {})
    points = doc.get("points") or []
    disabled = _disabled_ips()
    nokill = _nokill_ips()
    crushed: list[str] = []
    skipped: list[str] = []

    for p in points:
        ip, result = _kill_strike_certain_point(
            p,
            reason_prefix="attack_kit:crush_hot",
            disabled=disabled,
            nokill=nokill,
        )
        if not ip:
            continue
        if result and result.get("ok"):
            crushed.append(ip)
        else:
            skipped.append(ip)

    return {
        "ok": True,
        "crushed": crushed,
        "crushed_count": len(crushed),
        "killed_count": len(crushed),
        "hardware_destroy": True,
        "skipped": len(skipped),
    }


def forever_kill_enforce(max_ips: int | None = None) -> dict[str, Any]:
    """Re-apply forever kill + hardware destroy for archived HARDWARE_DESTROY registry entries."""
    if max_ips is None:
        max_ips = FOREVER_KILL_MAX_IPS
    disabled = sorted(_disabled_ips())[:max_ips]
    if not disabled:
        return {"ok": True, "enforced": [], "enforced_count": 0, "enforced_detail": []}

    enforced: list[str] = []
    enforced_detail: list[dict[str, Any]] = []
    skipped: list[str] = []
    script = INSTALL / "lib" / "field-attack-kit.sh"

    for ip in disabled:
        archived = load_archived_dossier(ip) or {}
        hw = bool(
            archived.get("hardware_destroy")
            or archived.get("action") == "HARDWARE_DESTROY"
        )
        if not hw:
            skipped.append(ip)
            continue
        dossier = dict(archived)
        dossier.setdefault("ip", ip)
        dossier.setdefault("action", "HARDWARE_DESTROY")
        dossier.setdefault("hardware_destroy", True)
        dossier.setdefault("certainty", 1.0)
        if not script.is_file():
            skipped.append(ip)
            continue
        dossier_path = STATE / "attack-kit-dossier.tmp"
        dossier_path.write_text(json.dumps(dossier, ensure_ascii=False) + "\n", encoding="utf-8")
        env = os.environ.copy()
        env["NEXUS_INSTALL_ROOT"] = str(INSTALL)
        env["NEXUS_STATE_DIR"] = str(STATE)
        safe_ip = ip.replace("'", "'\"'\"'")
        cmd = (
            f"source {INSTALL}/lib/nexus-common.sh && "
            f"source {INSTALL}/lib/firewall-sentinel.sh && "
            f"source {INSTALL}/lib/firewall-trust.sh && "
            f"source {INSTALL}/lib/self-access.sh && "
            f"source {INSTALL}/lib/friendly-guard.sh && "
            f"source {INSTALL}/lib/pest-arsenal.sh && "
            f"source {script} && "
            f'DOSSIER_JSON="$(cat "{dossier_path}")" && '
            f"nexus_hardware_destroy_target '{safe_ip}' \"$DOSSIER_JSON\""
        )
        proc = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=45, env=env)
        if proc.returncode == 0:
            enforced.append(ip)
            why = explain_kill(
                ip=ip,
                reason="forever_kill_enforce",
                action="HARDWARE DESTROY",
                point=dossier,
                vector=str(dossier.get("vector") or "HOSTILE"),
            )
            enforced_detail.append({"ip": ip, **why})
        else:
            skipped.append(ip)

    return {
        "ok": True,
        "forever_kill": True,
        "enforced": enforced,
        "enforced_count": len(enforced),
        "enforced_detail": enforced_detail,
        "skipped": len(skipped),
    }


def disable_one(ip: str, vector: str = "HOSTILE", severity: str = "high", reason: str = "operator_disable") -> dict[str, Any]:
    return kill_target(ip, vector, severity, reason)


def forever_disable_ip(
    ip: str,
    vector: str = "WIFI_THREAT",
    severity: str = "critical",
    reason: str = "rf_unhealthy_forever",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Force permanent disable for unhealthy RF-correlated host — no strike gate."""
    meta = dict(extra or {})
    meta.setdefault("force", True)
    meta.setdefault("strike_mode", "destroy")
    return kill_target(ip, vector, severity, reason, extra=meta)


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


def _record_auto_rekill(ip: str) -> None:
    log = _load_json(AUTO_REKILL_LOG, {"entries": {}})
    entries = log.get("entries")
    if not isinstance(entries, dict):
        entries = {}
    entries[ip] = {"ts": time.time(), "at": _now()}
    log["entries"] = entries
    log["updated"] = _now()
    try:
        AUTO_REKILL_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def _auto_rekill_cooldown_active(ip: str, seconds: int = AUTO_REKILL_COOLDOWN_SEC) -> bool:
    log = _load_json(AUTO_REKILL_LOG, {"entries": {}})
    entry = (log.get("entries") or {}).get(ip)
    if not isinstance(entry, dict):
        return False
    try:
        return (time.time() - float(entry.get("ts") or 0)) < seconds
    except (TypeError, ValueError):
        return False


def auto_rekill_validated(max_ips: int = AUTO_REKILL_MAX_IPS) -> dict[str, Any]:
    """RE-KILL killed hosts that are back online with same-host identity validation."""
    disabled = sorted(_disabled_ips())
    if not disabled:
        return {"ok": True, "rekilled": [], "rekilled_count": 0, "checked": 0, "skipped": 0}

    doc = _load_json(HOST_ATTACKS, {})
    points_by_ip = {
        str(p.get("ip") or ""): p for p in doc.get("points") or [] if p.get("ip")
    }
    rekilled: list[str] = []
    rekilled_detail: list[dict[str, Any]] = []
    skipped: list[str] = []
    checked = 0

    nokill = _nokill_ips()
    for ip in disabled[:max_ips]:
        if ip in nokill:
            skipped.append(ip)
            continue
        if _auto_rekill_cooldown_active(ip):
            skipped.append(ip)
            continue
        point = points_by_ip.get(ip) or {"ip": ip}
        checked += 1
        online_doc = check_target_online(ip, point)
        if online_doc.get("ok"):
            _save_online_check(ip, online_doc)
        if not online_doc.get("rekill_eligible"):
            skipped.append(ip)
            continue
        vector = str(point.get("vector") or "HOSTILE")
        severity = str(point.get("severity") or "high")
        result = rekill_target(ip, vector, severity)
        if result.get("rekill"):
            _record_auto_rekill(ip)
            rekilled.append(ip)
            rekilled_detail.append({
                "ip": ip,
                "why_killed_plain": result.get("why_killed_plain"),
            })
        else:
            skipped.append(ip)

    return {
        "ok": True,
        "rekilled": rekilled,
        "rekilled_count": len(rekilled),
        "rekilled_detail": rekilled_detail,
        "checked": checked,
        "skipped": len(skipped),
    }


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
    if _is_nokill(ip):
        return {
            "ok": False,
            "ip": ip,
            "rekill": False,
            "nokill_refused": True,
            "reason": "nokill_exempt",
        }
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
    strike_gate = gate_strike(ip, point, mode="rekill", monitor=point.get("monitor") if isinstance(point.get("monitor"), dict) else None)
    hardware_destroy = bool(strike_gate.get("hardware_destroy") or strike_gate.get("strike_certain"))
    dossier.update({
        "action": "HARDWARE_DESTROY" if hardware_destroy else "REKILL",
        "hardware_destroy": hardware_destroy,
        "certainty": 1.0 if hardware_destroy else strike_gate.get("certainty"),
        "strike_mode": "destroy" if hardware_destroy else "rekill",
        "rekill": True,
        "rekill_ts": _now(),
        "online_check": online_doc,
        "identity_validation": online_doc.get("validation"),
        "wire_point": strike_gate.get("wire_point"),
    })
    reason = "rekill_same_host_validated"
    dossier["reason"] = reason
    dossier["kill_reason"] = reason
    attach_to_dossier(
        dossier,
        explain_kill(
            ip=ip,
            reason=reason,
            action="REKILL",
            point=point,
            strike_gate=strike_gate,
            vector=vector,
            process=str(point.get("our_process") or point.get("process") or ""),
            extra_detail="Same-host identity matched archived kill dossier while target was back online.",
        ),
    )
    ok = _run_rekill(ip, vector, severity, reason, dossier)
    return {
        "ok": ok,
        "ip": ip,
        "rekill": ok,
        "killed": ok,
        "hardware_destroy": hardware_destroy and ok,
        "same_host": True,
        "online": True,
        "online_check": online_doc,
        "dossier_archived": ok,
        "certainty": 1.0 if hardware_destroy else strike_gate.get("certainty"),
        "why_killed_plain": dossier.get("why_killed_plain") if ok else None,
        "why_killed_short": dossier.get("why_killed_short") if ok else None,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "usage: field-attack-kit.py [autokill-certain|autokill-needs-die|forever-kill-enforce|forever-disable|crush-hot|auto-rekill|kill|disable|nokill|check-online|rekill <ip> ...]",
            file=sys.stderr,
        )
        return 1
    cmd = sys.argv[1]
    if cmd == "auto-rekill":
        json.dump(auto_rekill_validated(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
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
    if cmd == "autokill-certain":
        json.dump(autokill_certain(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if cmd == "autokill-needs-die":
        json.dump(autokill_needs_die(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if cmd == "forever-kill-enforce":
        json.dump(forever_kill_enforce(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if cmd == "crush-hot":
        json.dump(crush_hot(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if cmd == "nokill" and len(sys.argv) >= 3:
        json.dump(
            nokill_target(
                sys.argv[2],
                sys.argv[3] if len(sys.argv) > 3 else "HOSTILE",
                sys.argv[4] if len(sys.argv) > 4 else "high",
                sys.argv[5] if len(sys.argv) > 5 else "operator_nokill",
            ),
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
        return 0
    if cmd == "forever-disable" and len(sys.argv) >= 3:
        extra: dict[str, Any] = {}
        if len(sys.argv) >= 7:
            try:
                extra = json.loads(sys.argv[6])
            except json.JSONDecodeError:
                extra = {}
        json.dump(
            forever_disable_ip(
                sys.argv[2],
                sys.argv[3] if len(sys.argv) > 3 else "WIFI_THREAT",
                sys.argv[4] if len(sys.argv) > 4 else "critical",
                sys.argv[5] if len(sys.argv) > 5 else "rf_unhealthy_forever",
                extra=extra,
            ),
            sys.stdout,
            indent=2,
        )
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