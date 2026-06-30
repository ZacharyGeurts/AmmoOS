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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.sh" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.py" ]]
  grep -q 'attack_kit' "/home/default/Desktop/SG/NewLatest/lib/threat-panel.sh"
  grep -q '/api/attack-kit/disable' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/attack-kit/kill' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/hostile-ai-destroy.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/hostile-ai-threats-seed.json" ]]
  grep -q 'hostile-ai-panel' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'AI_BEACON_PRECISION' "/home/default/Desktop/SG/NewLatest/lib/threat-vectors.sh"
  grep -q '/api/hostile-ai' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/hostile-ai-destroy.py" panel 2>/dev/null || true); echo "$out" | grep -q 'hostile-ai-destroy/v1'
  grep -q '/api/attack-kit/check-online' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/attack-kit/rekill' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/attack-kit/nokill' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'nexus_field_attack_nokill_target' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.sh"
  grep -q 'nokill_target' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.py"
  grep -q 'field-nokill.tsv' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.py"
  grep -q '"nokill"' "/home/default/Desktop/SG/NewLatest/lib/host-attack-map.py"
  grep -q 'nexus_field_attack_kill_target' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.sh"
  grep -q 'nexus_field_attack_rekill_target' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.sh"
  grep -q 'nexus_target_dossier' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.sh"
  grep -q 'kill_target' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.py"
  grep -q 'check_online' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.py"
  grep -q 'rekill_target' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.py"
  grep -q 'auto_rekill_validated' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.py"
  grep -q 'nexus_field_attack_autokill' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.sh"
  grep -q 'nexus_field_attack_install_autokill' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.sh"
  grep -q 'refuse_kill' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.py"
  grep -q 'gate_strike' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.py"
  grep -q 'trust-strike-engine' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.sh"
  grep -q 'nexus_field_attack_publish_deep' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.sh"
  grep -q 'nexus_field_attack_rekill_cycle' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.sh"
  grep -q 'nexus_field_attack_rekill_cycle' "/home/default/Desktop/SG/NewLatest/lib/threat-panel.sh"
  grep -q 'nexus_field_attack_rekill_cycle' "/home/default/Desktop/SG/NewLatest/lib/kill-detect.sh"
  grep -q 'NEXUS_FIELD_AUTO_REKILL' "/home/default/Desktop/SG/NewLatest/lib/nexus-settings.sh"
  grep -q 'hardware_destroy' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.py"
  grep -q 'nexus_hardware_destroy_target' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.sh"
  grep -q 'nexus_field_attack_autokill_certain' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.sh"
  grep -q 'nexus_field_attack_forever_kill_enforce' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.sh"
  grep -q 'autokill_certain' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.py"
  grep -q 'forever_kill_enforce' "/home/default/Desktop/SG/NewLatest/lib/field-attack-kit.py"
  ! grep -q 'nexus_field_attack_auto_crush' "/home/default/Desktop/SG/NewLatest/lib/threat-panel.sh"
  grep -q 'killable' "/home/default/Desktop/SG/NewLatest/lib/host-attack-map.py"
  grep -q 'strike_confidence' "/home/default/Desktop/SG/NewLatest/lib/host-attack-map.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong - <<'PY'
import importlib.util
import time
from pathlib import Path
root = Path(__import__("os").environ["NEXUS_INSTALL_ROOT"])
spec = importlib.util.spec_from_file_location("fak", root / "lib" / "field-attack-kit.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod._record_auto_rekill("203.0.113.99")
assert mod._auto_rekill_cooldown_active("203.0.113.99")
mod.AUTO_REKILL_LOG.unlink(missing_ok=True)
empty = mod.auto_rekill_validated()
assert empty.get("rekilled_count") == 0
mod.NOKILL_TSV.write_text("ts\tip\tvector\tseverity\treason\tsource\n2026-01-01T00:00:00Z\t203.0.113.55\tHOSTILE\thigh\ttest\ttest\n", encoding="utf-8")
refused = mod.kill_target("203.0.113.55")
assert refused.get("nokill_refused")
mod.NOKILL_TSV.unlink(missing_ok=True)
PY
  declare -f nexus_field_attack_json >/dev/null 2>&1
