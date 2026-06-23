#!/bin/bash
# Panel TLS — local HTTPS for threat panel (self-signed, localhost only).

NEXUS_PANEL_TLS_DIR="${NEXUS_PANEL_TLS_DIR:-${NEXUS_STATE_DIR}/tls}"
NEXUS_PANEL_TLS_CERT="${NEXUS_PANEL_TLS_CERT:-${NEXUS_PANEL_TLS_DIR}/nexus-panel.crt}"
NEXUS_PANEL_TLS_KEY="${NEXUS_PANEL_TLS_KEY:-${NEXUS_PANEL_TLS_DIR}/nexus-panel.key}"

nexus_panel_tls_ensure() {
  [[ "${NEXUS_PANEL_TLS:-1}" == "1" ]] || return 0
  mkdir -p "${NEXUS_PANEL_TLS_DIR}"
  chmod 700 "${NEXUS_PANEL_TLS_DIR}"
  [[ -f "${NEXUS_PANEL_TLS_CERT}" && -f "${NEXUS_PANEL_TLS_KEY}" ]] && return 0
  command -v openssl >/dev/null 2>&1 || {
    nexus_log "WARN" "panel-tls" "openssl missing — panel falls back to HTTP"
    return 1
  }
  openssl req -x509 -newkey rsa:2048 -nodes \
    -keyout "${NEXUS_PANEL_TLS_KEY}" \
    -out "${NEXUS_PANEL_TLS_CERT}" \
    -days 3650 -subj "/CN=nexus-shield.local/O=NEXUS-Shield" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" 2>/dev/null
  chmod 600 "${NEXUS_PANEL_TLS_KEY}" "${NEXUS_PANEL_TLS_CERT}"
  chown root:nexus "${NEXUS_PANEL_TLS_KEY}" "${NEXUS_PANEL_TLS_CERT}" 2>/dev/null || true
  nexus_log "INFO" "panel-tls" "TLS_CERT_READY cn=nexus-shield.local"
}