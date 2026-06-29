#!/bin/bash
# Host OS start menu + taskbar — canonical AmmoOS launcher (idempotent).

nexus_host_desktop_install_enabled() {
  [[ "${NEXUS_HOST_DESKTOP_INSTALL:-1}" == "1" ]]
}

nexus_host_desktop_install_py() {
  local py="${NEXUS_INSTALL_ROOT}/lib/nexus-host-desktop-install.py"
  [[ -f "$py" ]] || py="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/nexus-host-desktop-install.py"
  [[ -f "$py" ]] || return 1
  printf '%s' "$py"
}

nexus_host_desktop_install_run() {
  nexus_host_desktop_install_enabled || return 0
  local py runner
  py="$(nexus_host_desktop_install_py)" || return 0
  runner="${NEXUS_PYTHONG:-pythong}"
  command -v "$runner" >/dev/null 2>&1 || runner="python3"
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
  NEXUS_HOST_DESKTOP_PIN="${NEXUS_HOST_DESKTOP_PIN:-1}" \
    "$runner" "$py" run >>"${NEXUS_STATE_DIR}/boot-impl.log" 2>&1 || {
    nexus_log "WARN" "host-desktop" "install_deferred"
    return 1
  }
  nexus_log "INFO" "host-desktop" "install_ok"
}