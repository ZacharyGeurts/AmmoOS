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
  [[ -f "${sg}/Grok16/lib/g16-compile-combinatronics.py" ]]
  [[ -f "${sg}/Grok16/data/g16-compile-combinatronics-doctrine.json" ]]
  [[ -f "${sg}/Grok16/tests/test_g16_compile_combinatronics.py" ]]
  grep -q 'compile_gate' "${sg}/Grok16/scripts/grok16-ai-compile.py"
  grep -q '_compile_combinatronics_mod' "${sg}/Queen/lib/queen-launch-singular-field.py"
  grep -q '_ideal_compile_profile' "${sg}/Grok16/scripts/grok16-profile-flags.py"
  grep -q 'g16-compile-combinatronics.py' "${sg}/Grok16/scripts/grok16-toolchain.sh"
  grep -q 'compiled_creation' "${sg}/Grok16/data/g16-field-combinatorics-doctrine.json"
  grep -q 'combinatronics' "${sg}/Grok16/data/field-exec-uncompiled-doctrine.json"
  if command -v pythong >/dev/null 2>&1; then
    GROK16_ROOT="${sg}/Grok16" SG_ROOT="${sg}" NEXUS_INSTALL_ROOT="/home/default/Desktop/SG/NewLatest" NEXUS_STATE_DIR="/home/default/Desktop/SG/NewLatest/.nexus-state" \
out=$(pythong "${sg}/Grok16/lib/g16-compile-combinatronics.py" gate 2>/dev/null || true); echo "$out" | grep -q 'g16-compile-combinatronics/v1'
    GROK16_ROOT="${sg}/Grok16" SG_ROOT="${sg}" NEXUS_INSTALL_ROOT="/home/default/Desktop/SG/NewLatest" NEXUS_STATE_DIR="/home/default/Desktop/SG/NewLatest/.nexus-state" \
      pythong "${sg}/Grok16/tests/test_g16_compile_combinatronics.py"
  fi
