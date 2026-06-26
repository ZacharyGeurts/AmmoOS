#!/usr/bin/env pythong
"""Sovereign time — operator-owned timeserver + receiver micron/squidgie verify.

Under terror-threat posture: do not trust pool NTP alone. Seal monotonic order,
sign realtime pulses from your own timeserver, and at receive verify the triple:
  CLOCK_MONOTONIC · CLOCK_REALTIME · sysfs CPU freq witness (Spiderweb Puny tier).

Squidgie = silent micron-scale tamper: RTC nudged, monotonic story disagrees, or
hardware freq fingerprint jumps without a logged thermal step.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import socket
import struct
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))

RECEIPT_LOG = STATE / "sovereign-time-receipts.jsonl"
PULSE_STATE = STATE / "sovereign-time-pulse.json"
KEY_FILE = STATE / "sovereign-time-key.bin"
CYCLE_STATE = STATE / "sovereign-cycle-state.json"
CYCLE_LEDGER = STATE / "sovereign-cycle-ledger.jsonl"
ANCHOR_STATE = STATE / "sovereign-time-anchor.json"

DEFAULT_PORT = int(os.environ.get("NEXUS_SOVEREIGN_TIME_PORT", "9123"))
HEARTBEAT_SEC = float(os.environ.get("NEXUS_SOVEREIGN_HEARTBEAT_SEC", "1"))
MAX_SKEW_MS = float(os.environ.get("NEXUS_TIME_MAX_SKEW_MS", "50"))
MAX_FREQ_DELTA_KHZ = int(os.environ.get("NEXUS_TIME_MAX_FREQ_DELTA_KHZ", "250000"))
SCHEMA = "sovereign-time/v2"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except OSError:
            pass


def _save_json(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def derived_realtime_ns() -> int:
    """Monotonic-anchored realtime — never backward, survives sonic/RF/SQUIDGIE."""
    anchor = _load_json(ANCHOR_STATE, {})
    mono_a = int(anchor.get("mono_ns") or 0)
    real_a = int(anchor.get("realtime_ns") or 0)
    if mono_a and real_a:
        return real_a + (time.monotonic_ns() - mono_a)
    return time.time_ns()


def derived_utc() -> str:
    ns = derived_realtime_ns()
    dt = datetime.fromtimestamp(ns / 1_000_000_000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _detect_sonic_rf(prev: dict[str, Any], sample: dict[str, Any]) -> list[str]:
    """RF/sonic tamper — micron witness or freq table shifts too fast for DVFS alone."""
    threats: list[str] = []
    if not prev:
        return threats
    d_mono = int(sample.get("mono_ns") or 0) - int(prev.get("mono_ns") or 0)
    prev_w = str(prev.get("micron_witness") or "")
    cur_w = str(sample.get("micron_witness") or "")
    prev_sum = int(prev.get("freq_sum_khz") or 0)
    cur_sum = int(sample.get("freq_sum_khz") or 0)
    if prev_w and cur_w and prev_w != cur_w and 0 < d_mono < 100_000_000:
        threats.append("sonic_rf_witness_flip")
    if prev_sum and cur_sum and abs(cur_sum - prev_sum) > MAX_FREQ_DELTA_KHZ and d_mono < 50_000_000:
        threats.append("sonic_rf_freq_jump")
    skew = 0.0
    if d_mono > 0:
        d_real = int(sample.get("realtime_ns") or 0) - int(prev.get("realtime_ns") or 0)
        skew = abs(d_real - d_mono) / 1_000_000.0
        if skew > MAX_SKEW_MS and d_mono < 20_000_000:
            threats.append(f"sonic_rf_skew_{skew:.1f}ms")
    return threats


def cycle_advance(*, service: str, action: str) -> dict[str, Any]:
    """Advance sovereign cycle — never skip, never decrement."""
    state = _load_json(CYCLE_STATE, {"cycle": 0, "threats": 0, "services": {}})
    cycle = int(state.get("cycle") or 0) + 1
    sample = _clock_sample()
    prev_sample = {
        "mono_ns": state.get("last_mono_ns"),
        "realtime_ns": state.get("last_realtime_ns"),
        "micron_witness": state.get("micron_witness"),
        "freq_sum_khz": state.get("freq_sum_khz"),
    }
    threats = _detect_sonic_rf(prev_sample, sample) if prev_sample.get("mono_ns") else []
    svc_stats = state.setdefault("services", {})
    svc_key = f"{service}:{action}"
    svc_stats[svc_key] = int(svc_stats.get(svc_key) or 0) + 1
    row = {
        "ts": derived_utc(),
        "cycle": cycle,
        "service": service,
        "action": action,
        "threats": threats,
        "derived_ns": derived_realtime_ns(),
        "micron_witness": sample.get("micron_witness"),
    }
    state.update({
        "schema": "sovereign-cycle/v1",
        "cycle": cycle,
        "never_lost": True,
        "last_mono_ns": sample["mono_ns"],
        "last_realtime_ns": derived_realtime_ns(),
        "micron_witness": sample.get("micron_witness"),
        "freq_sum_khz": sample.get("freq_sum_khz"),
        "updated": derived_utc(),
        "last_service": service,
        "last_action": action,
    })
    if threats:
        state["threats"] = int(state.get("threats") or 0) + 1
        state["last_threats"] = threats
    _save_json(CYCLE_STATE, state)
    _append_jsonl(CYCLE_LEDGER, row)
    return row


def cycle_gate(*, service: str, action: str = "serve") -> dict[str, Any]:
    """Security gate for DNS/DHCP/NTP — cycle always advances; time always known."""
    row = cycle_advance(service=service, action=action)
    stale = False
    pulse_state = _load_json(PULSE_STATE, {})
    last = pulse_state.get("last") if isinstance(pulse_state.get("last"), dict) else None
    issued_at = float(pulse_state.get("issued_at") or 0)
    if not last or (time.time() - issued_at) > HEARTBEAT_SEC * 2:
        stale = True
    receipt = None
    verify: dict[str, Any] = {}
    if stale or not last:
        receipt = issue_pulse(chain=f"gate:{service}")
        prev = last
        verify = verify_receipt(receipt, prev_receipt=prev if isinstance(prev, dict) else None)
    else:
        verify = pulse_state.get("verify") if isinstance(pulse_state.get("verify"), dict) else {"verdict": "USER_OK"}
    threats = list(row.get("threats") or [])
    verdict = str(verify.get("verdict") or "USER_OK")
    if verdict == "SQUIDGIE":
        threats.append("squidgie_logged")
    return {
        "ok": True,
        "never_lose_cycle": True,
        "cycle": row["cycle"],
        "service": service,
        "action": action,
        "verdict": verdict,
        "threats": threats,
        "derived_utc": derived_utc(),
        "derived_ns": derived_realtime_ns(),
        "micron_witness": row.get("micron_witness"),
        "pulse": (receipt or last or {}).get("pulse"),
        "policy": "Time always serves — threats log, never drop cycle",
    }


def cycle_status() -> dict[str, Any]:
    state = _load_json(CYCLE_STATE, {})
    anchor = _load_json(ANCHOR_STATE, {})
    return {
        "cycle": int(state.get("cycle") or 0),
        "never_lost": True,
        "threats": int(state.get("threats") or 0),
        "last_threats": state.get("last_threats") or [],
        "services": state.get("services") or {},
        "anchor_pulse": anchor.get("pulse"),
        "anchor_verdict": anchor.get("verdict"),
        "derived_utc": derived_utc(),
    }


def _signing_key() -> bytes:
    if KEY_FILE.is_file():
        return KEY_FILE.read_bytes()
    key = os.urandom(32)
    STATE.mkdir(parents=True, exist_ok=True)
    KEY_FILE.write_bytes(key)
    try:
        os.chmod(KEY_FILE, 0o600)
    except OSError:
        pass
    return key


def _read_sysfs_freq_khz() -> dict[str, int]:
    """Per-CPU scaling_cur_freq — hardware witness for micron squidgie checks."""
    out: dict[str, int] = {}
    base = Path("/sys/devices/system/cpu")
    if not base.is_dir():
        return out
    for cpu in sorted(base.glob("cpu[0-9]*")):
        for name in ("cpufreq/scaling_cur_freq", "cpufreq/cpuinfo_cur_freq"):
            p = cpu / name
            if p.is_file():
                try:
                    out[cpu.name] = int(p.read_text().strip())
                except (OSError, ValueError):
                    pass
                break
    return out


def _micron_witness(mono_ns: int, freqs: dict[str, int]) -> str:
    """Bind monotonic instant to silicon freq table — detects silent RTC nudges."""
    payload = f"{mono_ns}|" + "|".join(f"{k}:{v}" for k, v in sorted(freqs.items()))
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _clock_sample() -> dict[str, Any]:
    mono = time.monotonic_ns()
    real = time.time_ns()
    freqs = _read_sysfs_freq_khz()
    return {
        "mono_ns": mono,
        "realtime_ns": real,
        "utc": _now_iso(),
        "host": socket.gethostname(),
        "freq_khz": freqs,
        "freq_sum_khz": sum(freqs.values()) if freqs else 0,
        "micron_witness": _micron_witness(mono, freqs),
    }


def _receipt_body(sample: dict[str, Any], *, pulse: int, chain: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "pulse": pulse,
        "chain": chain,
        "host": sample["host"],
        "mono_ns": sample["mono_ns"],
        "realtime_ns": sample["realtime_ns"],
        "utc": sample["utc"],
        "freq_sum_khz": sample["freq_sum_khz"],
        "micron_witness": sample["micron_witness"],
        "entropy_tag": hashlib.sha256(f"{sample['mono_ns']}:{pulse}".encode()).hexdigest()[:12],
    }


def _sign(body: dict[str, Any]) -> str:
    key = _signing_key()
    msg = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def issue_pulse(*, chain: str = "operator") -> dict[str, Any]:
    prev_doc = _load_json(PULSE_STATE, {"pulse": 0})
    prev_pulse = int(prev_doc.get("pulse") or 0)
    pulse = prev_pulse + 1
    if pulse <= prev_pulse:
        pulse = prev_pulse + 1
    sample = _clock_sample()
    body = _receipt_body(sample, pulse=pulse, chain=chain)
    receipt = {**body, "sig": _sign(body)}
    prev_receipt = prev_doc.get("last") if isinstance(prev_doc.get("last"), dict) else None
    verify = verify_receipt(receipt, prev_receipt=prev_receipt)
    cycle_advance(service="sovereign", action="pulse")
    if verify.get("verdict") == "USER_OK" or not prev_receipt:
        _save_json(
            ANCHOR_STATE,
            {
                "schema": "sovereign-time-anchor/v1",
                "pulse": pulse,
                "mono_ns": receipt["mono_ns"],
                "realtime_ns": receipt["realtime_ns"],
                "micron_witness": receipt.get("micron_witness"),
                "verdict": verify.get("verdict"),
                "updated": derived_utc(),
            },
        )
    PULSE_STATE.write_text(
        json.dumps({
            "pulse": pulse,
            "last": receipt,
            "verify": verify,
            "issued_at": time.time(),
        }, indent=2) + "\n",
        encoding="utf-8",
    )
    _append_jsonl(RECEIPT_LOG, {"ts": derived_utc(), "receipt": receipt, "verify": verify})
    return receipt


def verify_receipt(
    receipt: dict[str, Any],
    *,
    local: dict[str, Any] | None = None,
    prev_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Receiver-side double-check. Returns verdict USER_OK or SQUIDGIE."""
    body = {k: v for k, v in receipt.items() if k != "sig"}
    sig = receipt.get("sig") or ""
    ok_sig = hmac.compare_digest(_sign(body), sig) if sig else False

    local = local or _clock_sample()
    issues: list[str] = []

    if not ok_sig:
        issues.append("bad_signature")

    if prev_receipt:
        d_mono = int(receipt.get("mono_ns") or 0) - int(prev_receipt.get("mono_ns") or 0)
        d_real = int(receipt.get("realtime_ns") or 0) - int(prev_receipt.get("realtime_ns") or 0)
        skew_ms = 0.0
        if d_mono < 0:
            issues.append("monotonic_backward")
        if d_real < 0:
            issues.append("realtime_backward")
        if d_mono > 0:
            skew_ms = abs(d_real - d_mono) / 1_000_000.0
            if skew_ms > MAX_SKEW_MS:
                issues.append(f"mono_real_skew_{skew_ms:.2f}ms")

        prev_sum = int(prev_receipt.get("freq_sum_khz") or 0)
        cur_sum = int(receipt.get("freq_sum_khz") or 0)
        freq_jump = bool(prev_sum and cur_sum and abs(cur_sum - prev_sum) > MAX_FREQ_DELTA_KHZ)

        prev_w = prev_receipt.get("micron_witness") or ""
        cur_w = receipt.get("micron_witness") or ""
        witness_flip_fast = bool(prev_w and cur_w and prev_w != cur_w and d_mono < 50_000_000)

        # Squidgie = RTC/monotonic story breaks while silicon table shifts too fast to be DVFS alone.
        if witness_flip_fast and (freq_jump or skew_ms > MAX_SKEW_MS / 2):
            issues.append("micron_squidgie")
        elif freq_jump and d_mono < 10_000_000 and skew_ms > MAX_SKEW_MS / 4:
            issues.append("freq_rtc_squidgie")

    # Cross-check against local clocks at receive (network RTT slack generous)
    recv_mono = int(local.get("mono_ns") or 0)
    recv_real = int(local.get("realtime_ns") or 0)
    remote_mono = int(receipt.get("mono_ns") or 0)
    remote_real = int(receipt.get("realtime_ns") or 0)
    if remote_mono and recv_mono:
        wall_skew_ms = abs(recv_real - remote_real) / 1_000_000.0
        if wall_skew_ms > max(MAX_SKEW_MS * 4, 500):
            issues.append(f"receive_wall_skew_{wall_skew_ms:.1f}ms")

    verdict = "USER_OK" if not issues else "SQUIDGIE"
    return {
        "schema": SCHEMA,
        "verdict": verdict,
        "issues": issues,
        "sig_ok": ok_sig,
        "local_micron_witness": local.get("micron_witness"),
        "remote_micron_witness": receipt.get("micron_witness"),
        "checked_at": _now_iso(),
    }


def sync_check(*, host: str = "127.0.0.1", port: int = DEFAULT_PORT, timeout: float = 2.0) -> dict[str, Any]:
    """Pull one signed pulse from operator timeserver and verify at receive."""
    req = json.dumps({"op": "pulse", "client": socket.gethostname()}).encode()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        sock.sendto(req, (host, port))
        data, _ = sock.recvfrom(65535)
    receipt = json.loads(data.decode())
    prev = _load_json(PULSE_STATE, {}).get("last")
    result = verify_receipt(receipt, prev_receipt=prev if isinstance(prev, dict) else None)
    PULSE_STATE.write_text(
        json.dumps({"pulse": receipt.get("pulse"), "last": receipt, "verify": result}, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"receipt": receipt, "verify": result}


def _heartbeat_loop() -> None:
    while True:
        try:
            issue_pulse(chain="heartbeat")
        except Exception:
            cycle_advance(service="sovereign", action="heartbeat_fallback")
        time.sleep(HEARTBEAT_SEC)


def serve_udp(*, host: str = "127.0.0.1", port: int = DEFAULT_PORT) -> None:
    """Operator timeserver — signed pulses on UDP; heartbeat never loses a cycle."""
    bind_host = os.environ.get("NEXUS_SOVEREIGN_TIME_BIND", host)
    threading.Thread(target=_heartbeat_loop, name="sovereign-heartbeat", daemon=True).start()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((bind_host, port))
    print(f"sovereign-time serve {bind_host}:{port} schema={SCHEMA} heartbeat={HEARTBEAT_SEC}s", flush=True)
    while True:
        data, addr = sock.recvfrom(65535)
        try:
            msg = json.loads(data.decode())
        except json.JSONDecodeError:
            continue
        if msg.get("op") != "pulse":
            continue
        cycle_gate(service="sovereign", action=f"udp:{addr[0]}")
        receipt = issue_pulse(chain=f"serve:{addr[0]}")
        sock.sendto(json.dumps(receipt).encode(), addr)


def status() -> dict[str, Any]:
    sample = _clock_sample()
    prev = _load_json(PULSE_STATE, {})
    last = prev.get("last") if isinstance(prev.get("last"), dict) else None
    verify = prev.get("verify") if isinstance(prev.get("verify"), dict) else None
    return {
        "schema": SCHEMA,
        "updated": derived_utc(),
        "port": DEFAULT_PORT,
        "heartbeat_sec": HEARTBEAT_SEC,
        "max_skew_ms": MAX_SKEW_MS,
        "max_freq_delta_khz": MAX_FREQ_DELTA_KHZ,
        "never_lose_cycle": True,
        "derived_utc": derived_utc(),
        "local": sample,
        "last_pulse": last,
        "last_verify": verify,
        "cycle": cycle_status(),
        "anchor": _load_json(ANCHOR_STATE, {}),
        "receipt_log": str(RECEIPT_LOG),
        "cycle_ledger": str(CYCLE_LEDGER),
        "posture": "Sovereign time — never lose a cycle; sonic/RF/SQUIDGIE log, derived time always known",
    }


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "status").strip().lower()
    if cmd == "json" or cmd == "status":
        print(json.dumps(status(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "gate" and len(sys.argv) > 2:
        svc = sys.argv[2]
        act = sys.argv[3] if len(sys.argv) > 3 else "serve"
        print(json.dumps(cycle_gate(service=svc, action=act), ensure_ascii=False, indent=2))
        return 0
    if cmd == "derived":
        print(json.dumps({"derived_utc": derived_utc(), "derived_ns": derived_realtime_ns()}, ensure_ascii=False))
        return 0
    if cmd == "pulse":
        print(json.dumps(issue_pulse(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "serve":
        serve_udp()
        return 0
    if cmd == "sync":
        host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_PORT
        print(json.dumps(sync_check(host=host, port=port), ensure_ascii=False, indent=2))
        return 0
    if cmd == "verify" and len(sys.argv) > 2:
        receipt = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        prev_path = sys.argv[3] if len(sys.argv) > 3 else ""
        prev = json.loads(Path(prev_path).read_text(encoding="utf-8")) if prev_path else None
        print(json.dumps(verify_receipt(receipt, prev_receipt=prev), ensure_ascii=False, indent=2))
        return 0
    print(
        json.dumps(
            {
                "error": "usage: sovereign-time.py [status|pulse|serve|sync [host] [port]|verify RECEIPT.json [PREV.json]]",
            },
            ensure_ascii=False,
        )
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())