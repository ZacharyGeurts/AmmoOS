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

  [[ -f "/home/default/Desktop/SG/NewLatest/lib/nexus-update.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/nexus-file-catalog.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/nexus-incremental-update.py" ]]
  [[ -x "/home/default/Desktop/SG/NewLatest/lib/nexus-update-apply.sh" ]]
  grep -q '/api/update/check' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/update/apply' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/update/sudo-prompt' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '/api/nexus/catalog' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q '_spawn_nexus_update_apply' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'github-update.lock' "/home/default/Desktop/SG/NewLatest/lib/nexus-update-lock.py"
  grep -q '_resolve_nexus_source_root' "/home/default/Desktop/SG/NewLatest/lib/threat-panel-http.py"
  grep -q 'NEXUS_UPDATE_TARBALL_URL' "/home/default/Desktop/SG/NewLatest/lib/nexus-update-apply.sh"
  grep -q 'NEXUS_UPDATE_APPLY_VIA' "/home/default/Desktop/SG/NewLatest/lib/nexus-update-apply.sh"
  grep -q '_apply_incremental' "/home/default/Desktop/SG/NewLatest/lib/nexus-update-apply.sh"
  grep -q 'download_tarball' "/home/default/Desktop/SG/NewLatest/lib/nexus-update-apply.sh"
  grep -q 'install-all.sh' "/home/default/Desktop/SG/NewLatest/lib/nexus-update-apply.sh"
  grep -q 'NEXUS_UPDATE_MODE' "/home/default/Desktop/SG/NewLatest/config/nexus.conf"
  grep -q 'source_tarball' "/home/default/Desktop/SG/NewLatest/lib/nexus-update.py"
  grep -q 'nexus-upgrade-btn' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'nexus-restart-btn' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q 'promptUpdateSudo' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  grep -q '"incremental"' "/home/default/Desktop/SG/NewLatest/nxf/latest.nxf"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/nexus-file-catalog.py" stats 2>/dev/null || true); echo "$out" | grep -q '"file_count"'
  ! grep -q 'window.open(data.release_url' "/home/default/Desktop/SG/NewLatest/panel/threat-panel.html"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/nexus-update.py" 2>/dev/null || true); echo "$out" | grep -q '"current"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/nexus-update.py" 2>/dev/null || true); echo "$out" | grep -q 'release_tarball'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong - <<'PY'
import importlib.util
import os
from pathlib import Path
root = Path(os.environ["NEXUS_INSTALL_ROOT"])
spec = importlib.util.spec_from_file_location("tph", root / "lib" / "threat-panel-http.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
src = mod._resolve_nexus_source_root()
assert src and ((src / "install-all.sh").is_file() or (src / "stealth_install.sh").is_file()), src
PY
