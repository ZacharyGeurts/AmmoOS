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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-combinatronic-spider-wire.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-combinatronic-spider-wire-doctrine.json" ]]
  grep -q 'spider_wire' "/home/default/Desktop/SG/NewLatest/lib/g16-combinatronic-rebalance.py"
  grep -q 'ironclad_outward' "/home/default/Desktop/SG/NewLatest/lib/field-combinatronic-spider-wire.py"
  grep -q '/api/combinatronic/spider-wire' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/combinatronic/spider-wire' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-world.py"
  grep -q 'qcc-spider-wire' "/home/default/Desktop/SG/NewLatest/Queen/world/queen-chips-cores.html"
  grep -q 'combinatronic_spider_wire' "/home/default/Desktop/SG/NewLatest/Hostess7/data/hostess7-neural-stack.json"
  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
    pythong "/home/default/Desktop/SG/NewLatest/lib/field-g16-universal-combinatronic.py" combinatronic --refresh >/dev/null 2>&1 || true
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-combinatronic-spider-wire.py" build 2>/dev/null || true); echo "$out" | grep -q 'field-combinatronic-spider-wire'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/g16-combinatronic-rebalance.py" spider_wire 2>/dev/null || true); echo "$out" | grep -q '"action": "spider_wire"'
