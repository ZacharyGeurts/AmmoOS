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

  tmp_state="$(mktemp -d)"
  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  grep -q 'retaliate_threat' "${sg}/Grok16/lib/field_combinatorics.py"
  grep -q 'record_rejection' "${sg}/Grok16/lib/field_combinatorics.py"
  grep -q 'reject_retaliate' "${sg}/Grok16/data/g16-field-combinatorics-doctrine.json"
  grep -q 'combinatorics_threat_retaliate' "/home/default/Desktop/SG/NewLatest/data/field-diagnostic-mode-doctrine.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" \
    python3 "$sg/Grok16/lib/field_truth_blocks.py" publish >/dev/null
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" \
    python3 "$sg/Grok16/lib/field_combinatorics.py" rebuild >/dev/null
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" \
    python3 -c "
import json
from pathlib import Path
state = Path('${tmp_state}')
panel_path = state / 'g16-field-combinatorics-panel.json'
panel = json.loads(panel_path.read_text())
panel.setdefault('hard_limits', {})['tampered'] = True
panel_path.write_text(json.dumps(panel, indent=2) + '\n')
print('tampered')
" | grep -q 'tampered'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-plate-combinatorics-bridge.py" build 2>/dev/null || true); echo "$out" | grep -q '"ok": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-plate-combinatorics-bridge.py" build 2>/dev/null || true); echo "$out" | grep -q 'combinatorics_rejected'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" \
    python3 "$sg/Grok16/lib/field_combinatorics.py" fast | grep -q '"rejected": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" \
    python3 "$sg/Grok16/lib/field_combinatorics.py" threat | grep -q 'field-combinatorics-threat'
  [[ -f "${tmp_state}/field-combinatorics-reject-ledger.jsonl" ]]
  mkdir -p "${tmp_state}"
  echo '{"role":"operator","ts":"2099-01-01T00:00:00Z","text":"active"}' > "${tmp_state}/hostess7-command.jsonl"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" \
    python3 "$sg/Grok16/lib/field_combinatorics.py" fast | grep -q '"deferred": true'
