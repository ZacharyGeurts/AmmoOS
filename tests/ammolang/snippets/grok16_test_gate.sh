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

  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  [[ -x "${sg}/Grok16/scripts/grok16-test-gate.sh" ]]
  [[ -x "${sg}/Grok16/scripts/g16-run-monitored.sh" ]]
  [[ -f "${sg}/Grok16/lib/g16_self_monitor.py" ]]
  grep -q '4.2.0' "${sg}/Grok16/data/grok16-version.json"
  grep -q 'line_safety' "${sg}/Grok16/data/grok16-version.json"
  grep -q 'self_monitor' "${sg}/Grok16/data/grok16-version.json"
  grep -q 'grok16-field-exec-full-bench/v5' "${sg}/Grok16/data/grok16-speed-bench-version.json"
  SG_ROOT="$sg" NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$(mktemp -d)" \
    bash "${sg}/Grok16/scripts/grok16-test-gate.sh" smoke
