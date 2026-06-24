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
    sleep 1
  fi

  if nexus_panel_wait_ready "$ready_url" 45 \
    || nexus_panel_wait_ready "$url" 30 \
    || nexus_panel_wait_ready "${url%/field}/" 15; then
    served="$(nexus_panel_served_version 2>/dev/null || true)"
    nexus_log "INFO" "nexus.sh" "PANEL_READY url=${url} version=${served:-unknown}"
    return 0
  fi

  echo "Panel not ready after start — see ${NEXUS_STATE_DIR}/panel-http.log" >&2
  return 1
}

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

panel_root="$(nexus_resolve_panel_root)"
if [[ -f "${panel_root}/lib/threat-panel.sh" ]]; then
  # shellcheck source=/dev/null
  source "${panel_root}/lib/threat-panel.sh"
  NEXUS_THREAT_PANEL=1 nexus_threat_panel_publish 2>/dev/null || true
fi

URL="$(nexus_panel_url)"

if [[ "${1:-}" == "--url" ]]; then
  echo "$URL"
  exit 0
fi

if [[ "${1:-}" == "--wait" ]]; then
  if nexus_panel_wait_ready "$URL" 45; then
    echo "Panel ready: $URL ($(nexus_panel_served_version 2>/dev/null || echo unknown))"
    exit 0
  fi
  echo "Panel not ready: $URL" >&2
  exit 1
fi

if [[ "${1:-}" == "--no-browser" ]]; then
  echo "Panel: $URL"
  echo "Version: $(nexus_panel_served_version 2>/dev/null || nexus_panel_desired_version 2>/dev/null || echo unknown)"
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