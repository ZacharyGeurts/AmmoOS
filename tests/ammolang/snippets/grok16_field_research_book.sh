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
  [[ -f "${sg}/Grok16/data/g16-field-research-book.json" ]]
  [[ -f "${sg}/Grok16/lib/field-research-book.py" ]]
  grep -q 'field-research-book/v1' "${sg}/Grok16/data/g16-field-research-book.json"
  grep -q 'field_research_book' "${sg}/Grok16/data/grok16-single-fabric-doctrine.json"
  grep -q 'sync_field_research_book' "${sg}/Grok16/scripts/grok16-integrate.sh"
  GROK16_SG_ROOT="$sg" SG_ROOT="$sg" python3 "${sg}/Grok16/lib/field-research-book.py" verify | grep -q '"ok": true'
  GROK16_SG_ROOT="$sg" SG_ROOT="$sg" python3 "${sg}/Grok16/lib/field-research-book.py" publish | grep -q '"ok": true'
  [[ -f "${sg}/Grok16/data/g16-field-research-book-panel.json" ]]
  [[ -f "${sg}/Grok16/docs/field-research.html" ]]
  grep -q 'field-research.html' "${sg}/Grok16/docs/build-manual.py"
