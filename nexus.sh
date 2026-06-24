#!/bin/bash
# NEXUS-Shield — open the panel (field-standalone, no sudo required from tree).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_FIELD_STANDALONE=1

# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-common.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/panel-browser.sh"

nexus_field_standalone_ensure_panel() {
  [[ "${NEXUS_FIELD_STANDALONE:-}" == "1" ]] || return 0
  local url ready_url port panel_py
  url="$(nexus_panel_url)"
  ready_url="$(nexus_panel_app_url)"
  if curl -sk --connect-timeout 1 "$ready_url" >/dev/null 2>&1 \
    || curl -sk --connect-timeout 1 "$url" >/dev/null 2>&1; then
    return 0
  fi
  panel_py="${NEXUS_INSTALL_ROOT}/lib/threat-panel-http.py"
  [[ -f "$panel_py" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  nexus_ensure_dirs 2>/dev/null || mkdir -p "$NEXUS_STATE_DIR" "${NEXUS_STATE_DIR}/tls" 2>/dev/null || true
  # shellcheck source=/dev/null
  [[ -f "${NEXUS_INSTALL_ROOT}/lib/panel-tls.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/panel-tls.sh"
  nexus_panel_tls_ensure 2>/dev/null || true
  port="${NEXUS_THREAT_PANEL_PORT:-9477}"
  local cert="${NEXUS_PANEL_TLS_CERT:-${NEXUS_STATE_DIR}/tls/nexus-panel.crt}"
  local key="${NEXUS_PANEL_TLS_KEY:-${NEXUS_STATE_DIR}/tls/nexus-panel.key}"
  if [[ -f "$cert" && -f "$key" ]] && ! pgrep -f "threat-panel-http.py.*${port}" >/dev/null 2>&1; then
    nohup env NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_PANEL_TLS=1 \
      python3 "$panel_py" "$port" "${NEXUS_INSTALL_ROOT}/panel" \
      "${NEXUS_STATE_DIR}/threat-panel.json" "$cert" "$key" \
      >>"${NEXUS_STATE_DIR}/panel-http.log" 2>&1 &
    sleep 1
  fi
}

# Installed systems: try systemd (optional, never require sudo from tree).
if [[ "${NEXUS_FIELD_STANDALONE:-}" != "1" ]] \
  && [[ -f "${ROOT}/lib/nexus-daemon.sh" ]] && command -v systemctl >/dev/null 2>&1; then
  if ! systemctl is-active --quiet nexus-genius.service 2>/dev/null; then
    if [[ "$(id -u)" -eq 0 ]]; then
      systemctl start nexus-genius.service 2>/dev/null || true
    fi
  fi
fi

nexus_field_standalone_ensure_panel

URL="$(nexus_panel_url)"

if [[ "${1:-}" == "--url" ]]; then
  echo "$URL"
  exit 0
fi

if [[ "${1:-}" == "--wait" ]]; then
  if nexus_panel_wait_ready "$URL" 45; then
    echo "Panel ready: $URL"
    exit 0
  fi
  echo "Panel not ready: $URL" >&2
  echo "Run: ./nexus.sh --no-browser  (panel starts in .nexus-state/)" >&2
  exit 1
fi

if [[ "${1:-}" == "--no-browser" ]]; then
  nexus_panel_wait_ready "$URL" 30 || true
  echo "Panel: $URL"
  echo "State: ${NEXUS_STATE_DIR}"
  echo "Tools: ${NEXUS_FIELD_TOOLS_DIR:-${NEXUS_INSTALL_ROOT}/lib/bin}"
  nexus_panel_open_help "$URL"
  exit 0
fi

if nexus_panel_open_browser "$URL"; then
  exit 0
fi

echo "Could not open a browser automatically." >&2
nexus_panel_open_help "$URL" >&2
exit 1