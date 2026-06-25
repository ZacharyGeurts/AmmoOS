#!/bin/bash
# NEXUS-Shield — start panel from this tree and open the browser.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_FIELD_STANDALONE=1

# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-common.sh"
nexus_init_runtime_paths
# shellcheck source=/dev/null
source "${ROOT}/lib/panel-browser.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/panel-tray.sh"

nexus_resolve_panel_root() {
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/threat-panel-http.py" ]] \
    && [[ -d "${NEXUS_INSTALL_ROOT}/panel" ]]; then
    printf '%s' "${NEXUS_INSTALL_ROOT}"
    return 0
  fi
  local candidate
  for candidate in \
    "${NEXUS_PANEL_ROOT:-}" \
    "${ROOT}/../SG/Latest/NEXUS-Shield" \
    "/home/default/Desktop/SG/Latest/NEXUS-Shield"; do
    [[ -n "$candidate" ]] || continue
    if [[ -f "${candidate}/lib/threat-panel-http.py" ]] && [[ -d "${candidate}/panel" ]]; then
      printf '%s' "${candidate}"
      return 0
    fi
  done
  printf '%s' "${NEXUS_INSTALL_ROOT}"
}

nexus_field_standalone_ensure_panel() {
  [[ "${NEXUS_FIELD_STANDALONE:-}" == "1" ]] || return 0

  local panel_root panel_py port cert key url ready_url want served
  panel_root="$(nexus_resolve_panel_root)"
  panel_py="${panel_root}/lib/threat-panel-http.py"
  [[ -f "$panel_py" ]] || {
    echo "BLOCKER: threat-panel-http.py not found — run from full NEXUS-Shield tree." >&2
    return 1
  }
  [[ -d "${panel_root}/panel" ]] || {
    echo "BLOCKER: panel/ directory missing." >&2
    return 1
  }
  command -v python3 >/dev/null 2>&1 || {
    echo "BLOCKER: python3 required for panel." >&2
    return 1
  }
  command -v curl >/dev/null 2>&1 || {
    echo "BLOCKER: curl required for panel health check." >&2
    return 1
  }

  nexus_ensure_dirs 2>/dev/null || mkdir -p "$NEXUS_STATE_DIR" "${NEXUS_STATE_DIR}/tls" 2>/dev/null || true
  # shellcheck source=/dev/null
  [[ -f "${panel_root}/lib/panel-tls.sh" ]] && source "${panel_root}/lib/panel-tls.sh"
  nexus_panel_tls_ensure 2>/dev/null || true

  want="$(nexus_panel_desired_version 2>/dev/null || true)"
  export NEXUS_THREAT_PANEL_PORT
  NEXUS_THREAT_PANEL_PORT="$(nexus_panel_pick_port "$want")"
  export NEXUS_THREAT_PANEL_PORT

  port="${NEXUS_THREAT_PANEL_PORT}"
  cert="${NEXUS_PANEL_TLS_CERT:-${NEXUS_STATE_DIR}/tls/nexus-panel.crt}"
  key="${NEXUS_PANEL_TLS_KEY:-${NEXUS_STATE_DIR}/tls/nexus-panel.key}"
  url="$(nexus_panel_url)"
  ready_url="$(nexus_panel_app_url)"

  if nexus_panel_needs_restart "$want"; then
    nexus_log "INFO" "nexus.sh" "PANEL_RESTART want=${want:-unknown} root=${panel_root}"
    nexus_panel_stop
  fi

  if [[ -f "$cert" && -f "$key" ]] && ! pgrep -f "threat-panel-http.py.*${port}" >/dev/null 2>&1; then
    nohup env \
      NEXUS_INSTALL_ROOT="${panel_root}" \
      NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
      NEXUS_PANEL_TLS=1 \
      python3 "$panel_py" "$port" "${panel_root}/panel" \
      "${NEXUS_STATE_DIR}/threat-panel.json" "$cert" "$key" \
      >>"${NEXUS_STATE_DIR}/panel-http.log" 2>&1 &
  fi

  if nexus_panel_wait_ready "$ready_url" 5 \
    || nexus_panel_wait_ready "$url" 5 \
    || nexus_panel_wait_ready "${url%/field}/" 5; then
    served="$(nexus_panel_served_version 2>/dev/null || true)"
    nexus_log "INFO" "nexus.sh" "PANEL_READY url=${url} version=${served:-unknown}"
    return 0
  fi

  echo "Panel not ready after start — see ${NEXUS_STATE_DIR}/panel-http.log" >&2
  return 1
}

nexus_panel_shutdown_immediate() {
  local port="${NEXUS_THREAT_PANEL_PORT:-9477}"
  nexus_panel_tray_watchdog_stop 2>/dev/null || true
  nexus_panel_tray_stop 2>/dev/null || true
  pkill -9 -f 'threat-panel-http\.py' 2>/dev/null || true
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" 2>/dev/null || true
    fuser -k "${NEXUS_THREAT_PANEL_FALLBACK_PORT:-9478}/tcp" 2>/dev/null || true
  fi
  nexus_await_port_free "${port}" 3 2>/dev/null || true
  rm -f "${NEXUS_STATE_DIR}/panel.pid" 2>/dev/null || true
  nexus_log "INFO" "nexus.sh" "PANEL_SHUTDOWN state=${NEXUS_STATE_DIR}"
}

nexus_panel_restart_immediate() {
  nexus_panel_shutdown_immediate
  nexus_field_standalone_ensure_panel
}

nexus_usage() {
  cat <<EOF
NEXUS-Shield — start the threat panel and open the browser
  Version: $(nexus_read_version 2>/dev/null || echo unknown)
  Install: ${NEXUS_INSTALL_ROOT}
  State:   ${NEXUS_STATE_DIR}

Usage:
  ./nexus.sh                 Start panel (if needed), open browser, tray icon
  ./nexus.sh --help          Show this help (-h, help)
  ./nexus.sh --url           Print panel URL only
  ./nexus.sh --wait          Block until panel responds
  ./nexus.sh --no-browser    Start panel; print URL and CLI hints (no browser)
  ./nexus.sh --no-tray       Skip system-tray icon (combine with other flags)
  ./nexus.sh --tray          Start tray icon only (right-click → jump to tab)
  ./nexus.sh --tab <view>    Open a panel tab in the browser (e.g. command, library)
  ./nexus.sh --shutdown      Stop panel, tray, and watchdog immediately (--stop)
  ./nexus.sh --restart       Stop and start panel immediately (--restart-immediate)

Tab views (for --tab):
  command, us, packets, threats, intel, signals, dns, outside, library, system
  Sub-views: packets/monitor, threats/map, intel/honor, system/settings, …

Environment:
  NEXUS_STATE_DIR      Field state directory (default: /var/lib/nexus-shield)
  NEXUS_PANEL_ROOT     Override panel install tree
  NEXUS_THREAT_PANEL_PORT  HTTPS port (auto-picked if unset)

CLI without browser:
  ./bin/nexus status
  ./bin/nexus panel --no-browser

Logs: \${NEXUS_STATE_DIR}/panel-http.log
EOF
}

case "${1:-}" in
  -h|--help|help)
    nexus_usage
    exit 0
    ;;
  --shutdown|--stop)
    nexus_panel_shutdown_immediate
    echo "Panel stopped."
    exit 0
    ;;
  --restart|--restart-immediate)
    if nexus_panel_restart_immediate; then
      URL="$(nexus_panel_url)"
      echo "Panel restarted: ${URL}"
      echo "Version: $(nexus_panel_served_version 2>/dev/null || nexus_panel_desired_version 2>/dev/null || echo unknown)"
      exit 0
    fi
    echo "Panel restart failed — see ${NEXUS_STATE_DIR}/panel-http.log" >&2
    exit 1
    ;;
esac

# Installed systems: try systemd only when not field-standalone.
if [[ "${NEXUS_FIELD_STANDALONE:-}" != "1" ]] \
  && [[ -f "${ROOT}/lib/nexus-daemon.sh" ]] && command -v systemctl >/dev/null 2>&1; then
  if ! systemctl is-active --quiet nexus-genius.service 2>/dev/null; then
    if [[ "$(id -u)" -eq 0 ]]; then
      systemctl start nexus-genius.service 2>/dev/null || true
    fi
  fi
fi

nexus_field_standalone_ensure_panel || {
  echo "Try: ./nexus.sh --no-browser" >&2
  exit 1
}

nexus_panel_publish_if_needed() {
  local panel_root="$1"
  local panel_json="${NEXUS_STATE_DIR}/threat-panel.json"
  [[ -f "${panel_root}/lib/threat-panel.sh" ]] || return 0
  # shellcheck source=/dev/null
  source "${panel_root}/lib/threat-panel.sh"
  if [[ -s "$panel_json" ]] && [[ "$(wc -c <"$panel_json" 2>/dev/null || echo 0)" -gt 32 ]]; then
    return 0
  fi
  local assemble="${panel_root}/scripts/panel-json-assemble.py"
  if [[ -f "$assemble" ]] && command -v python3 >/dev/null 2>&1; then
    NEXUS_INSTALL_ROOT="${panel_root}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
      python3 "$assemble" >/dev/null 2>&1 && return 0
  fi
  NEXUS_PANEL_PUBLISH_FAST="${NEXUS_PANEL_PUBLISH_FAST:-1}" \
    NEXUS_THREAT_PANEL=1 nexus_threat_panel_publish 2>/dev/null || true
}

panel_root="$(nexus_resolve_panel_root)"
nexus_panel_publish_if_needed "$panel_root"

URL="$(nexus_panel_url)"

if [[ "${1:-}" == "--url" ]]; then
  echo "$URL"
  exit 0
fi

if [[ "${1:-}" == "--wait" ]]; then
  if nexus_panel_wait_ready "$URL" 5; then
    echo "Panel ready: $URL ($(nexus_panel_served_version 2>/dev/null || echo unknown))"
    exit 0
  fi
  echo "Panel not ready: $URL" >&2
  exit 1
fi

if [[ "${1:-}" == "--no-tray" ]]; then
  export NEXUS_PANEL_TRAY=0
  shift
fi

if [[ "${1:-}" == "--no-browser" ]]; then
  echo "Panel: $URL"
  echo "Version: $(nexus_panel_served_version 2>/dev/null || nexus_panel_desired_version 2>/dev/null || echo unknown)"
  echo "State: ${NEXUS_STATE_DIR}"
  echo "Tools: ${NEXUS_FIELD_TOOLS_DIR:-${NEXUS_INSTALL_ROOT}/lib/bin}"
  nexus_panel_tray_install_autostart 2>/dev/null || true
  nexus_panel_tray_ensure_once 2>/dev/null || true
  nexus_panel_open_help "$URL"
  exit 0
fi

if [[ "${1:-}" == "--tray" ]]; then
  nexus_panel_tray_icon_refresh 2>/dev/null || true
  nexus_panel_tray_install_autostart 2>/dev/null || true
  nexus_panel_tray_ensure_once
  exit $?
fi

if [[ "${1:-}" == "--tab" && -n "${2:-}" ]]; then
  nexus_panel_open_tab "$2"
  nexus_panel_tray_ensure_once 2>/dev/null || true
  exit 0
fi

if nexus_panel_open_browser "$URL"; then
  nexus_panel_tray_install_autostart 2>/dev/null || true
  nexus_panel_tray_ensure_once 2>/dev/null || true
  exit 0
fi

echo "Could not open a browser automatically." >&2
nexus_panel_open_help "$URL" >&2
exit 1