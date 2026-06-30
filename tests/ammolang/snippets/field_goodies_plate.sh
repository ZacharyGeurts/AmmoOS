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

  [[ -f "/home/default/Desktop/SG/NewLatest/data/field-field-surfaces-doctrine.json" ]]
  grep -q 'c2_taskbar' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'shell_dock' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'field_popcorn' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'field_g16_launch' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'field_gpu' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'field_audio' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'field_broadcaster' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q '_refresh_shell_dock' "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py"
  grep -q 'field_surface_slices' "/home/default/Desktop/SG/NewLatest/lib/field-plate-combinatorics-bridge.py"
  grep -q 'field_surfaces' "/home/default/Desktop/SG/NewLatest/lib/field-plate-combinatorics-bridge.py"
  grep -q 'field_shell_dock' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q 'field_popcorn' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q 'field_g16_launch' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q 'field_audio' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q 'field_lock' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q 'c2_taskbar' "/home/default/Desktop/SG/NewLatest/lib/field-panel-parallel.py"
  grep -q 'operator_surfaces' "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/lib/field_combinatorics.py"
  grep -q 'c2_taskbar' "${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}/Grok16/lib/field_combinatorics.py"
  grep -q 'field_surfaces' "/home/default/Desktop/SG/NewLatest/lib/field-combinatorics-comb.py"
  grep -q 'comb-surfaces-grid' "/home/default/Desktop/SG/NewLatest/panel/combinatorics-studio.html"
  tmp_state="$(mktemp -d)"
  sg="${SG_ROOT:-$(cd "/home/default/Desktop/SG/NewLatest/.." && pwd)}"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" GROK16_ROOT="$sg/Grok16" \
    pythong "/home/default/Desktop/SG/NewLatest/lib/field-shell-dock.py" json >/dev/null
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" \
    pythong "/home/default/Desktop/SG/NewLatest/lib/field-popcorn-player.py" json >/dev/null
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" \
    pythong "/home/default/Desktop/SG/NewLatest/lib/field-g16-launch.py" json >/dev/null
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" SG_ROOT="$sg" \
    pythong "/home/default/Desktop/SG/NewLatest/lib/field-gpu-control.py" json >/dev/null
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-audio-settings.py" json 2>/dev/null || true); echo "$out" | grep -q 'field-audio-settings/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" GROK16_ROOT="$sg/Grok16" SG_ROOT="$sg" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-plate-combinatorics-bridge.py" build 2>/dev/null || true); echo "$out" | grep -q 'field-surfaces-slice'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/field-plate-meld.py" fuse 2>/dev/null || true); echo "$out" | grep -q 'shell_dock'
