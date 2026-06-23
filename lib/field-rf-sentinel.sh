#!/bin/bash
# Field RF Sentinel — internal software antenna publish helpers.

nexus_field_rf_cycle() {
  local script="${NEXUS_INSTALL_ROOT}/lib/field-rf-sentinel.py"
  [[ -f "$script" ]] || return 0
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    python3 "$script" cycle >/dev/null 2>&1 || true
}

nexus_field_rf_json() {
  local script="${NEXUS_INSTALL_ROOT}/lib/field-rf-sentinel.py"
  if [[ ! -f "$script" ]]; then
    printf '{"antenna":{"mode":"unavailable"},"bursts":[],"recent_bursts":[],"shield":{"enabled":true}}'
    return 0
  fi
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    python3 "$script" json 2>/dev/null \
    || printf '{"antenna":{"mode":"error"},"bursts":[],"recent_bursts":[],"shield":{"enabled":true}}'
}

nexus_field_rf_forever_enforce() {
  local script="${NEXUS_INSTALL_ROOT}/lib/field-rf-sentinel.py"
  [[ -f "$script" ]] || return 0
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    python3 "$script" forever-enforce >/dev/null 2>&1 || true
}