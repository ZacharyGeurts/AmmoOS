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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/znetwork-wireless-fcc.py" ]]
  grep -q 'wireless_fcc' "/home/default/Desktop/SG/NewLatest/data/znetwork-doctrine.json"
  grep -q 'trace_action_behind' "/home/default/Desktop/SG/NewLatest/lib/znetwork-wireless-fcc.py"
  grep -q 'strike_action_behind' "/home/default/Desktop/SG/NewLatest/lib/znetwork-wireless-fcc.py"
  grep -q 'fix_not_kill' "/home/default/Desktop/SG/NewLatest/data/znetwork-doctrine.json"
  grep -q 'nexus_znetwork_wireless_fcc_bind_and_scan' "/home/default/Desktop/SG/NewLatest/lib/znetwork-field.sh"
  grep -q '_is_own_router' "/home/default/Desktop/SG/NewLatest/lib/field-rf-sentinel.py"
  grep -q 'fix_router_strike_actor' "/home/default/Desktop/SG/NewLatest/lib/znetwork-relayer.py"
  tmp_state="$(mktemp -d)"
  printf '{"schema":"znetwork-own-router/v1","bound":true,"gateway_ip":"192.168.1.1","bssid":"aa:bb:cc:dd:ee:ff","ssid":"HomeNet"}\n' \
    >"${tmp_state}/znetwork-own-router.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/znetwork-wireless-fcc.py" json 2>/dev/null || true); echo "$out" | grep -q '"schema": "znetwork-wireless-fcc/v1"'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/znetwork-wireless-fcc.py" is-own 192.168.1.1 2>/dev/null || true); echo "$out" | grep -q '"own": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
    pythong -c "
import json, os, sys
sys.path.insert(0, '/home/default/Desktop/SG/NewLatest/lib')
os.environ['NEXUS_INSTALL_ROOT'] = '/home/default/Desktop/SG/NewLatest'
os.environ['NEXUS_STATE_DIR'] = '${tmp_state}'
import importlib.util
spec = importlib.util.spec_from_file_location('zwf', '/home/default/Desktop/SG/NewLatest/lib/znetwork-wireless-fcc.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
tr = mod.trace_action_behind({'kind':'hostile_gateway_symptom','ip':'192.168.1.1'})
assert tr.get('symptom_is_own_router') is True
assert tr.get('policy') in ('fix_router_only','fix_router_strike_actor')
print('trace_ok')
"
  rm -rf "$tmp_state"
