#!/usr/bin/env bash
# Reboot NEXUS panel + optional genius daemon — apply heat/power fixes immediately.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-$ROOT/.nexus-state}"
export NEXUS_FIELD_STANDALONE=1

# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-common.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/panel-browser.sh"

echo "=== NEXUS reboot v$(nexus_read_version) ==="
echo "Timers capped at 5s · panel refresh 5s · active-tab slices only"

nexus_panel_stop

if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files nexus-genius.service >/dev/null 2>&1; then
  if [[ "$(id -u)" -eq 0 ]]; then
    systemctl restart nexus-genius.service || true
  elif [[ -n "${SUDO_PASSWORD:-}" ]]; then
    echo "${SUDO_PASSWORD}" | sudo -S systemctl restart nexus-genius.service || true
  else
    sudo systemctl restart nexus-genius.service || true
  fi
  echo "nexus-genius.service restarted"
fi

mkdir -p "$NEXUS_STATE_DIR"
nohup "${ROOT}/nexus.sh" --no-browser >>"${NEXUS_STATE_DIR}/panel-http.log" 2>&1 &
echo "Panel starting in background — log: ${NEXUS_STATE_DIR}/panel-http.log"
if nexus_panel_wait_ready "$(nexus_panel_app_url)" 5; then
  echo "READY $(nexus_panel_url)"
  exit 0
fi
echo "Panel not ready yet — check ${NEXUS_STATE_DIR}/panel-http.log"
exit 1
