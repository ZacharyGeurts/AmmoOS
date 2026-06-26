#!/bin/bash
# Precision field — sub-micron map & spiderweb panel publish helpers.

nexus_precision_field_publish() {
  [[ "${NEXUS_PRECISION_FIELD:-0}" == "1" ]] || return 0
  command -v pythong >/dev/null 2>&1 || return 0
  local script="${NEXUS_INSTALL_ROOT}/lib/precision-field.py"
  [[ -f "$script" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    pythong "$script" build >/dev/null 2>&1 || true
}

nexus_precision_field_json() {
  local script="${NEXUS_INSTALL_ROOT}/lib/precision-field.py"
  if [[ ! -f "$script" ]]; then
    printf '{"entities":[],"edges":[],"stats":{}}'
    return 0
  fi
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    pythong "$script" json 2>/dev/null \
    || printf '{"entities":[],"edges":[],"stats":{}}'
}