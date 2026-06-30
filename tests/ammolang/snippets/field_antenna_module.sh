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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-antenna-orchestrator.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-antenna.sh" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-antenna-launcher.sh" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/scripts/field-antenna-test.sh" ]]
  grep -q 'field_antenna' "/home/default/Desktop/SG/NewLatest/lib/threat-panel.sh"
  grep -q 'nexus_field_antenna_cycle' "/home/default/Desktop/SG/NewLatest/lib/threat-panel.sh"
  grep -q '/api/field-antenna' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'NEXUS_FIELD_ANTENNA' "/home/default/Desktop/SG/NewLatest/config/nexus.conf"
  grep -q 'antenna)' "/home/default/Desktop/SG/NewLatest/bin/nexus"
  grep -q 'field_antenna' "/home/default/Desktop/SG/NewLatest/lib/signals-field.py"
  grep -q 'fcc_laser_part15' "/home/default/Desktop/SG/NewLatest/data/fcc-signal-registry.json"
  grep -q 'kind == "laser"' "/home/default/Desktop/SG/NewLatest/lib/fcc-signal-lookup.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-antenna-orchestrator.py" build 2>/dev/null || true); echo "$out" | grep -q 'field-antenna/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/fcc-signal-lookup.py" lookup laser 0 0 2>/dev/null || true); echo "$out" | grep -q 'fcc_laser_part15'
  mkdir -p "$NEXUS_STATE_DIR"
  printf '{"lat":37.7749,"lon":-122.4194,"source":"test"}\n' > "$NEXUS_STATE_DIR/operator-location.json"
  ant_test_out="$(NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "/home/default/Desktop/SG/NewLatest/lib/field-antenna-orchestrator.py" test 2>/dev/null || true)"
  [[ "$ant_test_out" == *'field-antenna-test/v1'* ]]
