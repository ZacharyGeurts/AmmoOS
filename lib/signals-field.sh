#!/bin/bash
# Signals field — antenna pulse payload for gorgeous Signals tab.

nexus_signals_field_publish() {
  [[ "${NEXUS_SIGNALS_FIELD:-1}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/signals-field.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$py" build >/dev/null 2>&1 || true
}

nexus_signals_field_json() {
  if declare -f nexus_signals_field_publish >/dev/null 2>&1; then
    nexus_signals_field_publish
  fi
  local py="${NEXUS_INSTALL_ROOT}/lib/signals-field.py"
  local cache="${NEXUS_STATE_DIR}/signals-field-panel.json"
  if [[ -f "$py" ]]; then
    NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
      python3 "$py" json 2>/dev/null && return 0
  fi
  if [[ -s "$cache" ]]; then
    python3 -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null
    return 0
  fi
  printf '{"schema":"signals-field/v1","stats":{"antenna_fields":0},"antennas":[],"pulse_channels":[]}'
}