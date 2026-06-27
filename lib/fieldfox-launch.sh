#!/bin/bash
# Queen integrated field browser launcher — Field Gecko profile, Webbrowser shell (no OS browser).
set -euo pipefail

ROOT="${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}"
STATE="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}"
URL="${1:-about:blank}"
QUEEN="${QUEEN_ROOT:-${ROOT}/Queen}"
PY="${NEXUS_PYTHONG:-pythong}"

nexus_fieldfox_launch() {
  local url="${1:-about:blank}"
  local route=""
  if [[ "$url" == *"#"* ]]; then
    route="${url#*#}"
  fi
  if [[ -f "${ROOT}/lib/queen-integrated-browser.py" ]]; then
    NEXUS_INSTALL_ROOT="${ROOT}" NEXUS_STATE_DIR="${STATE}" QUEEN_ROOT="${QUEEN}" \
      QUEEN_NO_OS_BROWSER=1 QUEEN_WEB_SHELL=1 QUEEN_SKIP_RTX_BOOT=1 \
      NEXUS_C2_DESKTOP_LAUNCH=1 NEXUS_C2_KIOSK=1 \
      "$PY" "${ROOT}/lib/queen-integrated-browser.py" open 2>/dev/null \
      && echo "{\"launched\":true,\"engine\":\"queen-field-gecko\",\"url\":\"${url}\",\"queen\":true}" \
      && return 0
  fi
  if [[ -f "${ROOT}/lib/queen-panel-open.py" ]]; then
    NEXUS_INSTALL_ROOT="${ROOT}" NEXUS_STATE_DIR="${STATE}" QUEEN_ROOT="${QUEEN}" \
      "$PY" "${ROOT}/lib/queen-panel-open.py" nexus "$route" 2>/dev/null \
      && echo "{\"launched\":true,\"engine\":\"queen-browser\",\"url\":\"${url}\",\"queen\":true}" \
      && return 0
  fi
  if [[ -x "${QUEEN}/scripts/start-world.sh" ]]; then
    NEXUS_INSTALL_ROOT="${ROOT}" QUEEN_ROOT="${QUEEN}" "${QUEEN}/scripts/start-world.sh" --daemon >/dev/null 2>&1 || true
  fi
  echo "{\"launched\":false,\"error\":\"queen_panel_open_missing\",\"url\":\"${url}\"}" >&2
  return 1
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  nexus_fieldfox_launch "${URL}"
fi