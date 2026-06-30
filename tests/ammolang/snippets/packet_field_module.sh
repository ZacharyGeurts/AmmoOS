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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/packet-field.py" ]]
  grep -q 'nexus_packet_field_capture' "/home/default/Desktop/SG/NewLatest/lib/packet-oracle.sh"
  grep -q 'packet_field' "/home/default/Desktop/SG/NewLatest/lib/threat-panel.sh"
  grep -q 'renderPacketField' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'packet-field-wrap' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "/home/default/Desktop/SG/NewLatest/lib/packet-field.py" parse-line \
    "1748012345.123456 IP 127.0.0.1.54321 > 104.18.29.234.443: Flags [P.], seq 1, ack 1, win 512, length 100" \
    | grep -q '"direction": "TX"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "/home/default/Desktop/SG/NewLatest/lib/packet-field.py" parse-line \
    "1748012345.123456 IP 104.18.29.234.443 > 127.0.0.1.54321: Flags [P.], seq 1, ack 1, win 512, length 200" \
    | grep -q '"direction": "RX"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong - <<'PY'
import importlib.util
from pathlib import Path
root = Path(__import__("os").environ["NEXUS_INSTALL_ROOT"])
spec = importlib.util.spec_from_file_location("pf", root / "lib" / "packet-field.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod._port_service(443) == "HTTPS"
assert "TX" in mod._english_summary({"direction": "TX", "process": "firefox", "protocol": "tcp", "src_port": 54321, "dst_ip": "1.2.3.4", "dst_port": 443, "port_service": "HTTPS", "length": 100, "flags": "P."})
= {"10.0.0.1"}
assert mod._classify_direction("10.0.0.1", "8.8.8.8", local, "Out") == "TX"
assert mod._classify_direction("8.8.8.8", "10.0.0.1", local, "In") == "RX"
line = "1782249257.017925 enp10s0 Out IP 10.0.0.1.36444 > 1.1.1.1.443: Flags [.], ack 1, win 566, length 0"
rec = mod.parse_tcpdump_line(line, local, {})
assert rec and rec["direction"] == "TX"
PY
