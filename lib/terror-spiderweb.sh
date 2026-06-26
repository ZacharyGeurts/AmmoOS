#!/bin/bash
# Global terror Spiderweb — operator-triggered only (no auto probe storms).

nexus_terror_spiderweb_publish() {
  # Default OFF — rebuild via /api/terror-spiderweb/rebuild or panel button only.
  [[ "${NEXUS_TERROR_SPIDERWEB:-0}" == "1" ]] || return 0
  command -v pythong >/dev/null 2>&1 || return 0
  local script="${NEXUS_INSTALL_ROOT}/lib/terror-spiderweb.py"
  [[ -f "$script" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    pythong "$script" build >/dev/null 2>&1 || true
}

nexus_terror_spiderweb_json() {
  local script="${NEXUS_INSTALL_ROOT}/lib/terror-spiderweb.py"
  if [[ ! -f "$script" ]]; then
    printf '{"nodes":[],"edges":[],"focus":{}}'
    return 0
  fi
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    pythong "$script" json 2>/dev/null \
    || printf '{"nodes":[],"edges":[],"focus":{}}'
}