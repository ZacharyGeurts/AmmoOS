#!/bin/bash
# Planetary observation + proactive kills — global sight, certainty-gated destroy.

nexus_planetary_observer_json() {
  local py="${NEXUS_INSTALL_ROOT}/lib/planetary-observer.py"
  [[ -f "$py" ]] || { printf '{}'; return 0; }
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$py" json 2>/dev/null || printf '{}'
}

nexus_planetary_observer_cycle() {
  [[ "${NEXUS_PLANETARY_OBSERVER:-1}" == "1" ]] || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/planetary-observer.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$py" cycle >/dev/null 2>&1 || true
}

nexus_planetary_observer_proactive() {
  [[ "${NEXUS_PLANETARY_PROACTIVE_KILL:-1}" == "1" ]] || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/planetary-observer.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$py" proactive 2>/dev/null || true
}