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

panel="/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'Field Attack Kit' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'ak-crush-hot' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'attack-kit/kill' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'KILL' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'FRIENDLY' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'friendly_refused' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'NEXUS_ATTACK_KIT_AUTO_CRUSH' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'Auto-kill hostile targets' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'God Bless' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'ha-strike-badge' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'Trust Strike' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'ak-strike-corpus' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'field-toolkit-panel' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'ft-attack-select' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'update-busy' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -qE 'v3\.8\.2' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'lastPanelUpdated' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'consumer_collateral' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'PINPOINT' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'HARDWARE DESTROY' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'strike-destroy' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'old-man' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'Comfort reading' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'set-old-man' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'v6.0.0' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  ! grep -q 'Grandmas' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
