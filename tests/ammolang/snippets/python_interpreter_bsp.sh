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
  [[ -f "${sg}/Grok16/lib/field_python_interpreter.py" ]]
  grep -q '_resolve_bsp_python' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-launch-chamber.py"
  grep -q 'interpreter_bsp' "/home/default/Desktop/SG/NewLatest/Queen/lib/queen-launch-chamber.py"
  python3 "${sg}/Grok16/tests/test_field_python_interpreter.py"
  py_chamber="$(mktemp -d)"
  cp "${sg}/Grok16/examples/speed-demo/speed_demo.py" "$py_chamber/main.py"
  GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" QUEEN_ROOT="$ROOT/Queen" NEXUS_INSTALL_ROOT="$ROOT" \
    QUEEN_LAUNCH_IRON_EXEC=0 pythong -c "
import importlib.util, json
from pathlib import Path
spec = importlib.util.spec_from_file_location('ch', Path('/home/default/Desktop/SG/NewLatest/Queen/lib/queen-launch-chamber.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
root = Path('${py_chamber}')
plane = mod.resolve_organized_runner(root, 'main.py', mod.build_manifest(root), {})
assert plane.get('ok'), plane
assert plane.get('toolchain') == 'python_gpy', plane
assert plane.get('interpreter'), plane
print('python_interpreter_bsp_ok')
" | grep -q 'python_interpreter_bsp_ok'
