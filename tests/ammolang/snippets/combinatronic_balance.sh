#!/bin/bash
set -euo pipefail
set +o pipefail
ROOT="/home/default/Desktop/SG/NewLatest"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/home/default/Desktop/SG/NewLatest/.nexus-state}"
export SG_ROOT="${SG_ROOT:-/home/default/Desktop/SG}"
export AML_INLINE=1
PY=python3
if [[ "${AML_TEST_DIRECT:-0}" != "1" ]] && command -v pythong >/dev/null 2>&1; then
  PY=pythong
fi
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
sg="${SG_ROOT:-$(cd "$ROOT/.." && pwd)}"

[[ -f "$ROOT/lib/field-combinatronic-balance.py" ]]
[[ -f "$ROOT/data/field-combinatronic-balance-doctrine.json" ]]
grep -q 'combinatronic_balance' "$ROOT/lib/field-panel-parallel.py"
grep -q '/api/combinatronic/balance' "$ROOT/lib/threat-panel-http.py"
grep -q '/api/combinatronic/balance' "$ROOT/Queen/lib/queen-world.py"
grep -q 'gate_refresh' "$ROOT/lib/field-ironclad-chips-combinatorics.py"
grep -q 'gate_refresh' "$ROOT/lib/field-program-combinatronic.py"
grep -q 'gate_refresh' "$ROOT/lib/field-combinamatrix.py"
grep -q 'gate_refresh' "$ROOT/lib/field-g16-universal-combinatronic.py"
grep -q 'combinatoric_entry' "$ROOT/lib/field-combinatronic-balance.py"
grep -q 'read_content_balance' "$ROOT/lib/field-combinatronic-balance.py"
grep -q 'balance_id' "$ROOT/lib/field-combinatronic-balance.py"
grep -q 'balance_as_best_identifier' "$ROOT/data/field-combinatronic-balance-doctrine.json"
grep -q 'combinatronic_balance' "$ROOT/lib/h7-library-bridge.py"
grep -q 'sync_all_entries' "$ROOT/lib/field-combinatronic-balance.py"
grep -q 'entry_batteries' "$ROOT/data/field-combinatronic-balance-doctrine.json"
grep -q 'combinatoric_entry' "$ROOT/lib/field-combinatronics-growth.py"
grep -q 'combinatoric_entry' "$ROOT/lib/field-extensive-library.py"

tmp_state="$(mktemp -d)"
run_py() {
  local state_dir="$1"
  shift
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$state_dir" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" AML_INLINE=1 AML_TEST_DIRECT="${AML_TEST_DIRECT:-0}" \
    "$PY" "$@"
}
out=$(run_py "$tmp_state" "$ROOT/lib/field-combinatronic-balance.py" verify 2>/dev/null || true)
grep -qF '"ok": true' <<<"$out"
out=$(run_py "$tmp_state" "$ROOT/lib/field-combinatronic-balance.py" content openstax_biology --format textbook --collection textbooks 2>/dev/null || true)
grep -qF 'field-combinatronic-content-balance' <<<"$out"
out=$(run_py "$tmp_state" "$ROOT/lib/field-combinatronic-balance.py" identify openstax_biology --format textbook --collection textbooks 2>/dev/null || true)
grep -qF 'CBAL-' <<<"$out"
if [[ "${AML_TEST_DIRECT:-0}" == "1" ]]; then
  out=$(run_py "$NEXUS_STATE_DIR" "$ROOT/lib/g16-combinatronic-rebalance.py" rebalance 2>/dev/null || true)
  grep -qF '"action": "rebalance"' <<<"$out"
  grep -qF 'balanced_hold' <<<"$out"
  out=$(run_py "$NEXUS_STATE_DIR" "$ROOT/lib/field-combinatronic-balance.py" fingerprint 2>/dev/null || true)
  grep -qF '"entry_base":' <<<"$out"
else
  run_py "$tmp_state" "$ROOT/lib/field-chip-battery.py" publish >/dev/null 2>&1 || true
  run_py "$tmp_state" "$ROOT/lib/field-program-combinatronic.py" publish >/dev/null 2>&1 || true
  out=$(run_py "$tmp_state" "$ROOT/lib/g16-combinatronic-rebalance.py" rebalance --refresh 2>/dev/null || true)
  grep -qF '"action": "rebalance"' <<<"$out"
  out=$(run_py "$tmp_state" "$ROOT/lib/g16-combinatronic-rebalance.py" rebalance 2>/dev/null || true)
  grep -qF 'balanced_hold' <<<"$out"
  out=$(run_py "$tmp_state" "$ROOT/lib/field-chip-battery.py" combinatronic 2>/dev/null || true)
  grep -qF '"combinatronic": true' <<<"$out"
  out=$(run_py "$NEXUS_STATE_DIR" "$ROOT/lib/field-combinatronic-balance.py" panel 2>/dev/null || true)
  grep -qF '"optimized_combinatronic": true' <<<"$out"
  out=$(run_py "$NEXUS_STATE_DIR" "$ROOT/lib/field-combinatronic-balance.py" sync 2>/dev/null || true)
  grep -qF '"synchronous": true' <<<"$out"
  out=$(run_py "$NEXUS_STATE_DIR" "$ROOT/lib/field-combinatronic-balance.py" fingerprint 2>/dev/null || true)
  grep -qF '"entry_base":' <<<"$out"
fi
rm -rf "$tmp_state"