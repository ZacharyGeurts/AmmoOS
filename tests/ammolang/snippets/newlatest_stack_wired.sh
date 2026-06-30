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

  [[ -f "/home/default/Desktop/SG/NewLatest/scripts/wire-stack.sh" ]]
  [[ -x "/home/default/Desktop/SG/NewLatest/scripts/wire-stack.sh" ]]
  grep -q 'wire-stack.sh' "/home/default/Desktop/SG/NewLatest/data/sg-canonical.json"
  grep -q 'NewLatest/Grok16' "/home/default/Desktop/SG/NewLatest/data/sg-canonical.json"
  [[ -L "/home/default/Desktop/SG/NewLatest/Grok16" || -d "/home/default/Desktop/SG/NewLatest/Grok16" ]]
  [[ -L "/home/default/Desktop/SG/NewLatest/KILROY" || -d "/home/default/Desktop/SG/NewLatest/KILROY" ]]
  [[ -d "/home/default/Desktop/SG/NewLatest/hostess7-training-viewer" ]]
  NEXUS_INSTALL_ROOT="$ROOT" pythong -c "
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('sg_paths', Path('/home/default/Desktop/SG/NewLatest') / 'lib' / 'sg_paths.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod.sg_root() == Path('/home/default/Desktop/SG/NewLatest').resolve(), mod.sg_root()
assert mod.grok16_root().name == 'Grok16', mod.grok16_root()
assert mod.kilroy_root().name == 'KILROY', mod.kilroy_root()
"
