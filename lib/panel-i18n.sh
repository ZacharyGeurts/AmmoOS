#!/bin/bash
# Panel i18n — language preference JSON for threat panel.

nexus_panel_language_json() {
  local script="${NEXUS_INSTALL_ROOT}/lib/panel-i18n.py"
  if [[ ! -f "$script" ]]; then
    printf '{"schema":"panel-language/v1","active":{"code":"en-US","source":"default"},"languages":[],"messages":{}}'
    return 0
  fi
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    NEXUS_I18N_DIR="${NEXUS_I18N_DIR:-${NEXUS_INSTALL_ROOT}/data/i18n}" \
    pythong "$script" json 2>/dev/null \
    || printf '{"schema":"panel-language/v1","active":{"code":"en-US","source":"default"},"languages":[],"messages":{}}'
}