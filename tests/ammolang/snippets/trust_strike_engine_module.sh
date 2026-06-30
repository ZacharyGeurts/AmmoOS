#!/bin/bash
set -euo pipefail
set +o pipefail
ROOT="/home/default/Desktop/SG/NewLatest"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/home/default/Desktop/SG/NewLatest/.nexus-state}"
export SG_ROOT="${SG_ROOT:-/home/default/Desktop/SG}"
mkdir -p "$NEXUS_STATE_DIR"
source "$ROOT/lib/nexus-common.sh" 2>/dev/null || true
source "$ROOT/lib/eternal-vigil.sh" 2>/dev/null || true
source "$ROOT/lib/entropy-oracle.sh" 2>/dev/null || true
source "$ROOT/lib/shadow-reality.sh" 2>/dev/null || true
source "$ROOT/lib/self-defense.sh" 2>/dev/null || true
source "$ROOT/lib/device-whitelist.sh" 2>/dev/null || true
source "$ROOT/lib/ultra-stealth.sh" 2>/dev/null || true
source "$ROOT/lib/predictive-guard.sh" 2>/dev/null || true
source "$ROOT/lib/network-lockdown.sh" 2>/dev/null || true
source "$ROOT/lib/threat-vectors.sh" 2>/dev/null || true
source "$ROOT/lib/packet-oracle.sh" 2>/dev/null || true
source "$ROOT/lib/threat-panel.sh" 2>/dev/null || true
source "$ROOT/lib/firewall-sentinel.sh" 2>/dev/null || true
source "$ROOT/lib/firewall-trust.sh" 2>/dev/null || true
source "$ROOT/lib/seal-vault.sh" 2>/dev/null || true
source "$ROOT/lib/tamper-guard.sh" 2>/dev/null || true
source "$ROOT/lib/znetwork-field.sh" 2>/dev/null || true
source "$ROOT/lib/nexus-settings.sh" 2>/dev/null || true
source "$ROOT/lib/adblock-loader.sh" 2>/dev/null || true
source "$ROOT/lib/host-attack.sh" 2>/dev/null || true
source "$ROOT/lib/field-attack-kit.sh" 2>/dev/null || true
nexus_ensure_dirs 2>/dev/null || true
panel="$ROOT/panel/threat-panel.html"

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/trust-strike-engine.py" ]]
  grep -q 'STRIKE_AUTO_MIN' "/home/default/Desktop/SG/NewLatest/lib/trust-strike-engine.py"
  grep -q 'build_hostile_corpus' "/home/default/Desktop/SG/NewLatest/lib/trust-strike-engine.py"
  grep -q 'trust_strike' "/home/default/Desktop/SG/NewLatest/lib/host-attack-map.py"
  grep -q '3.8.4' "/home/default/Desktop/SG/NewLatest/lib/nexus-common.sh"
  grep -q 'json-panel' "/home/default/Desktop/SG/NewLatest/lib/host-attack-map.py"
  grep -q 'build-fast' "/home/default/Desktop/SG/NewLatest/lib/host-attack-map.py"
  grep -q 'nexus_host_attacks_panel_json' "/home/default/Desktop/SG/NewLatest/lib/host-attack.sh"
  grep -q 'resolve_wire_point' "/home/default/Desktop/SG/NewLatest/lib/trust-strike-engine.py"
  grep -q 'consumer_collateral' "/home/default/Desktop/SG/NewLatest/lib/trust-strike-engine.py"
  grep -q 'wire_point' "/home/default/Desktop/SG/NewLatest/lib/host-attack-map.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/trust-strike-engine.py" summary 2>/dev/null || true); echo "$out" | grep -q 'trust-strike-v2-pinpoint'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong - <<'PY'
import importlib.util
from pathlib import Path
root = Path(__import__("os").environ["NEXUS_INSTALL_ROOT"])
spec = importlib.util.spec_from_file_location("tse", root / "lib" / "trust-strike-engine.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
hot = {
    "ip": "47.82.234.12",
    "vector": "HOSTILE",
    "heat": 0.88,
    "source": "gatekeeper",
    "is_monitor_target": True,
    "globe_pin": True,
    "verdict": "HARM_CANDIDATE",
    "detail": "Cobalt Strike beacon ThreatFox abuse.ch",
    "our_process": "suspicious.bin",
    "ptr_hostname": "c2.evil.example.com",
    "target_tls_subject": "CN=c2.evil.example.com",
    "ip_class": "hosting",
    "monitor": {"verdict": "HARM_CANDIDATE", "harm_total": 16, "trust_rank": 4,
                "ip_class": "hosting", "process": "suspicious.bin", "remote_port": "4444",
                "axis_scores": {"threat_linked": 8, "beacon_pattern": 7}},
    "target_ports": [443, 4444],
    "identity_fingerprint": {"markers": {"ptr_hostname": "c2.evil.example.com",
        "tls_subject": "cn=c2.evil.example.com", "asn": "as45102"}},
}
score = mod.score_strike(hot)
assert score["wire_point"]["confirmed"]
assert score["malware_evidence"]
assert score["strike_certain"]
assert score["pinpoint_confidence"] == 1.0
assert score["hardware_destroy"]
assert score["strike_mode"] == "destroy"
assert score["strike_ready_manual"]
gate = mod.gate_strike("47.82.234.12", hot, mode="auto")
assert gate["hardware_destroy"]
assert gate["certainty"] == 1.0
assert gate["allowed"] is True
viewer = {
    "ip": "185.199.108.154",
    "vector": "HOSTILE",
    "heat": 0.65,
    "org": "fastly",
    "verdict": "SUSPICIOUS",
    "detail": "insecure HTTP adult content stream",
    "monitor": {"verdict": "SUSPICIOUS", "harm_total": 8, "trust_rank": 3,
                "ip_class": "stream_cdn", "process": "firefox", "remote_port": "80",
                "axis_scores": {"media_stream": 8, "user_browser": 9}},
}
viewer_score = mod.score_strike(viewer)
assert viewer_score["consumer_collateral"]
assert not viewer_score["strike_ready_manual"]
viewer_gate = mod.gate_strike("185.199.108.154", viewer, mode="auto")
assert viewer_gate["allowed"] is False
lan = {
    "ip": "192.168.1.55",
    "mac": "aa:bb:cc:dd:ee:ff",
    "mac_oui": "aabbcc",
    "mac_vendor": "iot-camera",
    "detail": "AsyncRAT LAN callback",
    "monitor": {"ip_class": "private", "process": "unknown", "harm_total": 15, "verdict": "HARM_CANDIDATE"},
}
lan_wire = mod.resolve_wire_point(lan, mod.build_hostile_corpus())
assert lan_wire["lan_device"]
assert lan_wire["confirmed"]
refuse = mod.gate_strike("8.8.8.8", {"ip": "8.8.8.8", "vector": "HOSTILE", "heat": 0.99}, mode="auto")
assert refuse["friendly_refused"] and not refuse["allowed"]
PY
