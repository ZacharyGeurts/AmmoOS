#!/bin/bash
# NEXUS Heaven / Hell — no friendly fire on Heaven; no mercy on Hell chosen.

nexus_heaven_hell_rip() {
  [[ "${NEXUS_HEAVEN_HELL:-1}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/heaven-hell.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$py" rip >/dev/null 2>&1 || true
}

nexus_heaven_hell_json() {
  local py="${NEXUS_INSTALL_ROOT}/lib/heaven-hell.py"
  if [[ ! -f "$py" ]]; then
    printf '{"heaven":{"count":0},"hell":{"count":0}}'
    return 0
  fi
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$py" json 2>/dev/null || printf '{"heaven":{"count":0},"hell":{"count":0}}'
}