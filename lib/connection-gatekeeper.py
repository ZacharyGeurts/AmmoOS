#!/usr/bin/env python3
"""NEXUS Connection Gatekeeper — 10-axis intent breakdown per live connection.

Distinguishes user-initiated browsing/streaming from ephemeral search,
bandwidth abuse, and stream-theft / harm candidates.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
HISTORY = STATE / "connection-history.json"
TRUSTED_TSV = STATE / "firewall-trusted.tsv"
THREATS_TSV = STATE / "threat-vectors.tsv"

BROWSER_PROCS = frozenset({
    "firefox", "chrome", "chromium", "brave", "vivaldi", "opera",
    "msedge", "waterfox", "librewolf", "floorp", "thorium",
})
MEDIA_PROCS = BROWSER_PROCS | frozenset({
    "vlc", "mpv", "totem", "spotify", "discord", "obs", "ffmpeg",
    "youtube", "celluloid", "streamlink", "grok",
})
SEARCH_CDN_PREFIXES = (
    "34.", "35.", "142.250.", "172.217.", "216.58.",  # Google
    "13.", "20.", "40.", "52.", "104.",  # Azure/CF misc
    "151.101.", "199.16.",  # Fastly
)
STREAM_CDN_PREFIXES = (
    "104.18.", "104.16.", "172.64.", "172.66.",  # Cloudflare
    "140.82.", "185.199.", "140.82.113.",  # GitHub
    "34.107.", "64.233.",  # Google CDN
    "151.101.", "23.", "34.120.",  # Akamai/Fastly
    "13.32.", "13.33.", "13.35.",  # CloudFront
)
HARM_PORTS = frozenset({"4444", "5555", "1337", "31337", "6666", "9001", "9050", "1080", "3128"})
PRIVATE_RE = re.compile(
    r"^(127\.|10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.|169\.254\.|::1|fe80:|fd)"
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _load_trusted() -> set[str]:
    ips: set[str] = set()
    if not TRUSTED_TSV.is_file():
        return ips
    for line in TRUSTED_TSV.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) >= 3 and parts[2]:
            ips.add(parts[2])
    return ips


def _recent_threat_ips(limit: int = 80) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    if not THREATS_TSV.is_file():
        return out
    lines = THREATS_TSV.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]
    for line in lines[1:] if len(lines) > 1 else lines:
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        vector, detail = parts[1], parts[3]
        for key in ("dst=", "ip="):
            m = re.search(rf"{re.escape(key)}([0-9]{{7,15}})", detail)
            if m:
                ip = m.group(1)
                out.setdefault(ip, []).append(vector)
    return out


def _parse_addr(addr: str) -> tuple[str, str]:
    if not addr or addr in ("*:*", "[*]:*"):
        return "", ""
    host = addr.strip("[]")
    if host.count(":") > 1 and "]" not in addr:
        # bare IPv6 host:port
        idx = host.rfind(":")
        return host[:idx], host[idx + 1 :]
    if addr.startswith("["):
        m = re.match(r"\[([^\]]+)\]:(\d+)", addr)
        if m:
            return m.group(1), m.group(2)
    if ":" in host:
        h, p = host.rsplit(":", 1)
        return h, p
    return host, ""


def _parse_ss(line: str) -> dict[str, str]:
    parts = line.split()
    proc = ""
    m = re.search(r'users:\(\("([^"]+)"', line)
    if m:
        proc = m.group(1).lower()
        if proc.endswith("-bin"):
            proc = proc[:-4]
    elif "pid=" in line:
        proc = "pid-unknown"
    state = parts[0] if parts else ""
    local_idx, remote_idx = 3, 4
    if parts and parts[0] in ("tcp", "udp", "tcp6", "udp6"):
        state = parts[1] if len(parts) > 1 else state
        local_idx, remote_idx = 4, 5
    local = parts[local_idx] if len(parts) > local_idx else ""
    remote = parts[remote_idx] if len(parts) > remote_idx else ""
    lip, lport = _parse_addr(local)
    rip, rport = _parse_addr(remote)
    return {
        "state": state,
        "local": local,
        "remote": remote,
        "local_ip": lip,
        "local_port": lport,
        "remote_ip": rip,
        "remote_port": rport,
        "proc": proc,
        "line": line,
    }


def _ip_class(ip: str) -> str:
    if not ip or PRIVATE_RE.match(ip):
        return "private"
    for p in STREAM_CDN_PREFIXES:
        if ip.startswith(p):
            return "stream_cdn"
    for p in SEARCH_CDN_PREFIXES:
        if ip.startswith(p):
            return "search_cdn"
    return "public_unknown"


def _axis_user_browser(proc: str) -> tuple[int, str]:
    if proc in BROWSER_PROCS:
        return 9, f"browser:{proc}"
    if proc in MEDIA_PROCS:
        return 7, f"media_app:{proc}"
    if proc in ("", "pid-unknown"):
        return 2, "unknown_process"
    if "/tmp/" in proc or "/dev/shm/" in proc:
        return 0, f"tmp_binary:{proc}"
    return 4, f"daemon:{proc}"


def _axis_media_stream(proc: str, rport: str, ip_class: str) -> tuple[int, str]:
    score = 0
    notes = []
    if rport in ("443", "80", "8080", "8443") and ip_class in ("stream_cdn", "search_cdn"):
        score += 5
        notes.append("https_cdn")
    if proc in BROWSER_PROCS and rport == "443":
        score += 4
        notes.append("browser_https")
    if proc in ("vlc", "mpv", "totem", "spotify", "obs", "ffmpeg", "streamlink"):
        score += 8
        notes.append("media_client")
    if rport in ("1935", "554", "8554", "8081"):
        score += 9
        notes.append("raw_stream_port")
    return min(10, score), ",".join(notes) or "none"


def _axis_search_ephemeral(key: str, history: dict, ip_class: str) -> tuple[int, str]:
    h = history.get(key, {})
    seen = int(h.get("seen_count", 0))
    age = int(h.get("age_ticks", 0))
    if ip_class == "search_cdn":
        base = 7
    elif ip_class == "stream_cdn":
        base = 3
    else:
        base = 1
    if seen <= 2 and age <= 3:
        base += 3
        note = "ephemeral_search_tab"
    elif seen >= 8:
        base -= 2
        note = "stable_session"
    else:
        note = "normal_churn"
    return max(0, min(10, base)), note


def _axis_bandwidth_abuse(proc: str, ip_class: str, rport: str) -> tuple[int, str]:
    if proc in BROWSER_PROCS | MEDIA_PROCS:
        return 1, "user_app_expected"
    if ip_class == "public_unknown" and rport == "443":
        return 6, "unknown_bulk_https"
    if ip_class == "public_unknown":
        return 8, "unknown_non_cdn_egress"
    return 2, "cdn_normal"


def _axis_stream_theft(proc: str, rport: str, lip: str) -> tuple[int, str]:
    if proc in BROWSER_PROCS | MEDIA_PROCS:
        return 0, "user_media_path"
    if rport in ("1935", "554", "8554", "8081", "9000"):
        return 10, "non_browser_stream_port"
    if lip.endswith(":443") and rport not in ("443", "80"):
        return 7, "tls_downgrade_hint"
    if proc and proc not in MEDIA_PROCS and rport == "443":
        return 5, "daemon_https_possible_exfil"
    return 1, "low"


def _axis_beacon(proc: str, key: str, history: dict) -> tuple[int, str]:
    h = history.get(key, {})
    seen = int(h.get("seen_count", 0))
    if proc in BROWSER_PROCS:
        return 1, "browser_on_demand"
    if seen >= 20 and proc not in BROWSER_PROCS:
        return 7, "persistent_daemon_session"
    if seen >= 5:
        return 4, "recurring"
    return 2, "fresh"


def _axis_process_trust(proc: str) -> tuple[int, str]:
    if proc in BROWSER_PROCS:
        return 10, "signed_browser"
    if proc in MEDIA_PROCS:
        return 8, "known_media"
    if "/tmp/" in proc or "/dev/shm/" in proc or proc.startswith("."):
        return 0, "untrusted_path"
    if proc in ("", "pid-unknown"):
        return 3, "unidentified"
    return 5, "system_daemon"


def _axis_destination(ip_class: str, rport: str) -> tuple[int, str]:
    harm = 0
    if ip_class == "public_unknown":
        harm = 7
    elif ip_class == "search_cdn":
        harm = 2
    elif ip_class == "stream_cdn":
        harm = 1
    elif ip_class == "private":
        harm = 0
    if rport in HARM_PORTS:
        harm = 10
    return harm, ip_class if rport not in HARM_PORTS else f"{ip_class}+bad_port"


def _axis_threat_linked(rip: str, threats: dict[str, list[str]]) -> tuple[int, str]:
    vecs = threats.get(rip, [])
    if not vecs:
        return 0, "clean"
    real = [v for v in vecs if v not in ("C2_CORRELATION", "RST_FLOOD")]
    if real:
        return min(10, 4 + len(real)), ",".join(real[:3])
    return min(6, len(vecs)), "meta_noise:" + ",".join(vecs[:2])


def _axis_auth(rip: str, trusted: set[str]) -> tuple[int, str]:
    if rip in trusted:
        return 10, "operator_authorized"
    return 0, "not_authorized"


def _build_suggestion(
    scores: dict[str, int],
    notes: dict[str, str],
    verdict: str,
    reason: str,
    proc: str,
    rip: str,
    rport: str,
    ip_class: str,
    harm_total: int,
    user_total: int,
    block_rec: bool,
) -> dict[str, Any]:
    friendly: list[str] = []
    unfriendly: list[str] = []
    proc_name = proc or "unknown app"

    ub = int(scores.get("user_browser", 0))
    if ub >= 7:
        friendly.append(f"{proc_name} looks like a browser or media app you opened ({ub}/10).")
    elif ub <= 3:
        unfriendly.append(
            f"{proc_name} is not a browser ({ub}/10) — background apps calling out deserve a closer look."
        )

    ms = int(scores.get("media_stream", 0))
    if ms >= 6:
        friendly.append(f"HTTPS/stream pattern matches normal video or web traffic ({ms}/10).")

    se = int(scores.get("search_ephemeral", 0))
    if se >= 6:
        friendly.append(f"Short-lived tab-style traffic to a search or social CDN ({se}/10).")

    ba = int(scores.get("bandwidth_abuse", 0))
    if ba >= 6:
        unfriendly.append(
            f"Unusual outbound data volume for this app type ({ba}/10: {notes.get('bandwidth_abuse', '')})."
        )
    elif ba <= 2:
        friendly.append(f"Data amount looks normal for this kind of connection ({ba}/10).")

    st = int(scores.get("stream_theft_risk", 0))
    if st >= 8:
        unfriendly.append(
            f"Non-browser path that could move video or large streams ({st}/10: {notes.get('stream_theft_risk', '')})."
        )
    elif st <= 1:
        friendly.append("Not using suspicious stream-theft style ports.")

    bp = int(scores.get("beacon_pattern", 0))
    if bp >= 6:
        unfriendly.append(
            f"Repeating check-ins to the same server ({bp}/10: {notes.get('beacon_pattern', '')})."
        )
    elif bp <= 2:
        friendly.append("Connects on demand — not a constant hidden beacon.")

    pt = int(scores.get("process_trust", 0))
    if pt >= 8:
        friendly.append(f"App is on NEXUS consumer whitelist ({pt}/10: {notes.get('process_trust', '')}).")
    elif pt <= 3:
        unfriendly.append(
            f"App is unidentified or from an untrusted location ({pt}/10: {notes.get('process_trust', '')})."
        )

    dc = int(scores.get("destination_class", 0))
    cdn_labels = {
        "stream_cdn": "Address is a major CDN (Cloudflare, GitHub, etc.) — everyday web traffic.",
        "search_cdn": "Address is a Google/search CDN — typical when browsing or searching.",
    }
    if ip_class in cdn_labels and dc <= 3:
        friendly.append(cdn_labels[ip_class])
    elif ip_class == "public_unknown" and dc >= 6:
        unfriendly.append(f"{rip} is an unknown public server, not a well-known CDN ({dc}/10).")
    if rport in HARM_PORTS:
        unfriendly.append(f"Port {rport} is commonly used by malware and remote-control tools.")

    tl = int(scores.get("threat_linked", 0))
    if tl >= 4:
        unfriendly.append(f"Same IP triggered other warnings recently ({notes.get('threat_linked', '')}).")
    elif tl == 0:
        friendly.append("Not linked to any other warning on your machine right now.")

    if int(scores.get("operator_auth", 0)) >= 10:
        friendly.append("You already marked this address Trust forever.")

    actions = {
        "USER_OK": "No action needed. Use Trust forever only if it gets flagged again later.",
        "EPHEMERAL": "Usually fine — quick tabs come and go. Trust forever if the same CDN keeps nagging you.",
        "SUSPICIOUS": "Glance at the app name. If you recognize it (game launcher, updater), Trust forever. If not, keep watching.",
        "HARM_CANDIDATE": "If you do not recognize the app, click Stop this site. If it is a game, VPN, or CDN you use, Trust forever.",
        "MONITOR": "Routine traffic — no action unless the list keeps growing.",
    }
    summaries = {
        "USER_OK": "Likely friendly — matches normal browsing or something you chose to open.",
        "EPHEMERAL": "Likely friendly — looks like a short search or social tab.",
        "SUSPICIOUS": "Mixed signals — some concern, but not enough to auto-block.",
        "HARM_CANDIDATE": "Likely unfriendly until you prove otherwise — harm scores outweigh browser trust.",
        "MONITOR": "Neutral — nothing strong either way yet.",
    }
    if block_rec:
        action = actions["HARM_CANDIDATE"]
        summary = summaries.get(verdict, reason) + " NEXUS suggests review before blocking."
    else:
        action = actions.get(verdict, "Watch the connection list; click ? on any row for detail.")
        summary = summaries.get(verdict, reason)

    return {
        "summary": summary,
        "action": action,
        "friendly_signals": friendly[:6],
        "unfriendly_signals": unfriendly[:6],
        "trust_meter": min(100, user_total * 5),
        "concern_meter": min(100, harm_total * 4),
        "harm_total": harm_total,
        "trust_total": user_total,
    }


def _verdict(scores: dict[str, int], proc: str, ip_class: str) -> tuple[str, str, bool]:
    harm = (
        scores["stream_theft_risk"] * 2
        + scores["bandwidth_abuse"]
        + scores["destination_class"]
        + scores["threat_linked"]
        - scores["user_browser"]
        - scores["operator_auth"] // 2
        - scores["process_trust"] // 2
    )
    user_ok = (
        scores["user_browser"] >= 7
        and scores["stream_theft_risk"] <= 2
        and scores["bandwidth_abuse"] <= 3
    )
    ephemeral = scores["search_ephemeral"] >= 6 and scores["stream_theft_risk"] <= 3
    media_ok = scores["media_stream"] >= 6 and scores["user_browser"] >= 6

    if scores["operator_auth"] >= 10:
        return "USER_OK", "You authorized this peer — gate open", False
    if user_ok and media_ok:
        return "USER_OK", "Browser/media — you chose this (YouTube, stream, etc.)", False
    if user_ok and ephemeral:
        return "EPHEMERAL", "Search/social tab — dies and comes back, normal", False
    if user_ok:
        return "USER_OK", "Browser egress — intentional user browsing", False
    if scores["stream_theft_risk"] >= 8:
        return "HARM_CANDIDATE", "Non-browser stream path — possible video exfil/theft", True
    if harm >= 14 and scores["process_trust"] <= 4:
        return "HARM_CANDIDATE", "Daemon to unknown host — bandwidth with harm intent", True
    if harm >= 10:
        return "SUSPICIOUS", "Worth watching — not typical user browsing", False
    if ephemeral:
        return "EPHEMERAL", "Short-lived CDN — likely search/social", False
    if ip_class in ("stream_cdn", "search_cdn") and scores["process_trust"] >= 5:
        return "USER_OK", "Known CDN + trusted process", False
    return "MONITOR", "Routine connection — no harm signal", False


def analyze_connections(lines: list[str]) -> dict[str, Any]:
    trusted = _load_trusted()
    threats = _recent_threat_ips()
    history: dict[str, Any] = _load_json(HISTORY, {"ticks": 0, "peers": {}})
    history["ticks"] = int(history.get("ticks", 0)) + 1
    peers: dict[str, Any] = history.get("peers", {})
    current_keys: set[str] = set()
    results: list[dict[str, Any]] = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        p = _parse_ss(line)
        state = p["state"]
        if state not in ("ESTAB", "ESTABLISHED", "SYN-SENT", "SYN-RECV"):
            continue
        rip, rport = p["remote_ip"], p["remote_port"]
        if not rip or PRIVATE_RE.match(rip):
            continue
        proc = p["proc"]
        ip_class = _ip_class(rip)
        key = f"{rip}:{rport}:{proc}"
        current_keys.add(key)
        peer_hist = peers.get(key, {"seen_count": 0, "first_tick": history["ticks"]})
        peer_hist["seen_count"] = int(peer_hist.get("seen_count", 0)) + 1
        peer_hist["last_tick"] = history["ticks"]
        peer_hist["age_ticks"] = history["ticks"] - int(peer_hist.get("first_tick", history["ticks"]))
        peers[key] = peer_hist

        scores: dict[str, Any] = {}
        notes: dict[str, str] = {}

        s, n = _axis_user_browser(proc)
        scores["user_browser"] = s
        notes["user_browser"] = n

        s, n = _axis_media_stream(proc, rport, ip_class)
        scores["media_stream"] = s
        notes["media_stream"] = n

        s, n = _axis_search_ephemeral(key, peers, ip_class)
        scores["search_ephemeral"] = s
        notes["search_ephemeral"] = n

        s, n = _axis_bandwidth_abuse(proc, ip_class, rport)
        scores["bandwidth_abuse"] = s
        notes["bandwidth_abuse"] = n

        s, n = _axis_stream_theft(proc, rport, p["local"])
        scores["stream_theft_risk"] = s
        notes["stream_theft_risk"] = n

        s, n = _axis_beacon(proc, key, peers)
        scores["beacon_pattern"] = s
        notes["beacon_pattern"] = n

        s, n = _axis_process_trust(proc)
        scores["process_trust"] = s
        notes["process_trust"] = n

        s, n = _axis_destination(ip_class, rport)
        scores["destination_class"] = s
        notes["destination_class"] = n

        s, n = _axis_threat_linked(rip, threats)
        scores["threat_linked"] = s
        notes["threat_linked"] = n

        s, n = _axis_auth(rip, trusted)
        scores["operator_auth"] = s
        notes["operator_auth"] = n

        harm_total = sum(
            scores[k] for k in ("stream_theft_risk", "bandwidth_abuse", "destination_class", "threat_linked")
        )
        user_total = sum(scores[k] for k in ("user_browser", "media_stream", "operator_auth", "process_trust"))

        verdict, reason, block_rec = _verdict(scores, proc, ip_class)
        suggestion = _build_suggestion(
            scores, notes, verdict, reason, proc, rip, rport, ip_class,
            harm_total, user_total, block_rec,
        )

        results.append({
            "remote_ip": rip,
            "remote_port": rport,
            "process": proc,
            "state": state,
            "ip_class": ip_class,
            "line": line,
            "scores": scores,
            "notes": notes,
            "harm_total": harm_total,
            "user_total": user_total,
            "verdict": verdict,
            "reason": reason,
            "block_recommended": block_rec,
            "direction": "out",
            "suggestion": suggestion,
        })

    # decay history
    stale = [k for k in peers if k not in current_keys]
    for k in stale:
        peers[k]["miss_ticks"] = int(peers[k].get("miss_ticks", 0)) + 1
        if peers[k]["miss_ticks"] > 30:
            del peers[k]
    for k in current_keys:
        if k in peers:
            peers[k]["miss_ticks"] = 0

    history["peers"] = peers
    history["updated"] = _now()
    _save_json(HISTORY, history)

    results.sort(key=lambda x: (-int(x["block_recommended"]), -x["harm_total"], x["verdict"]))
    harm_candidates = [r for r in results if r["block_recommended"]]
    return {
        "updated": _now(),
        "connection_count": len(results),
        "harm_candidates": len(harm_candidates),
        "why_no_auto_block": (
            "Safe mode: NEXUS scores everything but only suggests actions. "
            "CDNs and browsers are never crushed automatically — you pick Trust forever or Stop this site."
        ),
        "connections": results[:60],
    }


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--stdin":
        lines = sys.stdin.read().splitlines()
    else:
        import subprocess
        proc = subprocess.run(
            ["ss", "-H", "-tunap"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        lines = proc.stdout.splitlines()

    out = analyze_connections(lines)
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())