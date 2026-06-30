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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/lethal-enforcement.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/hostess7-lethal-insight.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/spatial-target-geometry.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/lethal-enforcement-policy.json" ]]
  grep -q '/api/lethal-enforcement' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/hostess7-lethal-insight' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'lethal-status' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'kill_tier = "lethal"' "/home/default/Desktop/SG/NewLatest/lib/connection-gatekeeper.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "/home/default/Desktop/SG/NewLatest/lib/spatial-target-geometry.py" classify '{"lat":45.85,"lon":-87.05,"kind":"terror"}' \
    | grep -q 'spatial-target-geometry'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/lethal-enforcement.py" status 2>/dev/null || true); echo "$out" | grep -q 'lethal'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong - <<'PY'
import importlib.util, json
from pathlib import Path
root = Path(__import__("os").environ["NEXUS_INSTALL_ROOT"])
spec = importlib.util.spec_from_file_location("lethal", root / "lib" / "lethal-enforcement.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
heaven = mod.classify_removal({"verdict": "USER_OK", "trust_rank": 1, "remote_ip": "1.2.3.4"})
assert heaven["removal_level"] == "pass", heaven
hell = mod.classify_removal({"verdict": "HARM_CANDIDATE", "hell_chosen": True, "kind": "terror", "remote_ip": "6.6.6.6", "lat": 45.85, "lon": -87.05})
assert hell["removal_level"] in ("lethal", "total_removal", "strike"), hell
print(json.dumps({"heaven": heaven["removal_level"], "hell": hell["removal_level"]}))
PY
