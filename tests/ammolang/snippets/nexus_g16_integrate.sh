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
  [[ -f "/home/default/Desktop/SG/NewLatest/lib/nexus-g16-recompile.py" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/data/nexus-g16-integrate-doctrine.json" ]]
  [[ -f "/home/default/Desktop/SG/NewLatest/scripts/nexus-g16-recompile.sh" ]]
  grep -q '_combinatronics_profile' "/home/default/Desktop/SG/NewLatest/lib/nexus-g16-bridge.py"
  grep -q 'balance_combinatronics' "/home/default/Desktop/SG/NewLatest/lib/nexus-g16-recompile.py"
  grep -q 'integrate' "/home/default/Desktop/SG/NewLatest/scripts/sync-field-stack.sh"
  grep -q '_g16_combinatronics_gate' "${sg}/Queen/scripts/g16-build.sh"
  grep -q '_combinatronics_compile_gate' "${sg}/Queen/lib/forge/tools.py"
  grep -q 'g16-compile-combinatronics.py' "/home/default/Desktop/SG/NewLatest/lib/field-outside-asm.sh"
  grep -q 'integrate' "/home/default/Desktop/SG/NewLatest/data/nexus-g16-compile-doctrine.json"
  if command -v pythong >/dev/null 2>&1; then
    GROK16_ROOT="${sg}/Grok16" SG_ROOT="${sg}" NEXUS_INSTALL_ROOT="/home/default/Desktop/SG/NewLatest" NEXUS_STATE_DIR="/home/default/Desktop/SG/NewLatest/.nexus-state" \
out=$(pythong "/home/default/Desktop/SG/NewLatest/lib/nexus-g16-recompile.py" balance 2>/dev/null || true); echo "$out" | grep -q 'nexus-g16-recompile-balance/v1'
  fi
