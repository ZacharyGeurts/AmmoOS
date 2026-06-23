#!/bin/bash
# GitHub update lock — panel + stealth_install coordination.

NEXUS_UPDATE_LOCK_SCRIPT="${NEXUS_UPDATE_LOCK_SCRIPT:-${NEXUS_INSTALL_ROOT}/lib/nexus-update-lock.py}"
if [[ ! -f "$NEXUS_UPDATE_LOCK_SCRIPT" ]]; then
  _lock_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  NEXUS_UPDATE_LOCK_SCRIPT="${_lock_dir}/nexus-update-lock.py"
fi
NEXUS_UPDATE_LOCK_TOKEN="${NEXUS_UPDATE_LOCK_TOKEN:-}"

nexus_update_lock_py() {
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    python3 "$NEXUS_UPDATE_LOCK_SCRIPT" "$@" 2>/dev/null
}

nexus_update_lock_status() {
  nexus_update_lock_py status
}

nexus_update_lock_acquire() {
  local holder="${1:-stealth_install}"
  local phase="${2:-stealth_install}"
  local target="${3:-}"
  local previous="${4:-}"
  nexus_update_lock_py acquire \
    "--holder=${holder}" "--phase=${phase}" "--target=${target}" "--previous=${previous}"
}

nexus_update_lock_adopt() {
  local token="${1:-$NEXUS_UPDATE_LOCK_TOKEN}"
  local holder="${2:-stealth_install}"
  local phase="${3:-stealth_install}"
  [[ -n "$token" ]] || return 1
  nexus_update_lock_py adopt "$token" "--holder=${holder}" "--phase=${phase}"
}

nexus_update_lock_phase() {
  local phase="${1:-stealth_install}"
  local token="${2:-$NEXUS_UPDATE_LOCK_TOKEN}"
  [[ -n "$token" ]] && nexus_update_lock_py phase "$phase" "--token=${token}"
}

nexus_update_lock_heartbeat() {
  local token="${1:-$NEXUS_UPDATE_LOCK_TOKEN}"
  [[ -n "$token" ]] && nexus_update_lock_py heartbeat "--token=${token}"
}

nexus_update_lock_release() {
  local token="${1:-$NEXUS_UPDATE_LOCK_TOKEN}"
  if [[ -n "$token" ]]; then
    nexus_update_lock_py release "--token=${token}"
  else
    nexus_update_lock_py release --force
  fi
}

nexus_update_lock_ensure() {
  [[ -f "$NEXUS_UPDATE_LOCK_SCRIPT" ]] || return 0
  if [[ -n "${NEXUS_UPDATE_LOCK_TOKEN:-}" ]]; then
    nexus_update_lock_adopt "$NEXUS_UPDATE_LOCK_TOKEN" "stealth_install" "stealth_install" | grep -q '"ok": true'
    return $?
  fi
  local cur prev
  cur="${NEXUS_VERSION:-}"
  prev="${NEXUS_UPDATE_PREVIOUS_VERSION:-$cur}"
  nexus_update_lock_acquire "stealth_install" "stealth_install" "$cur" "$prev" | grep -q '"ok": true'
}