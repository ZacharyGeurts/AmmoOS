#!/bin/bash
# Field radio catcher — 1940s GPS-scoped broadcast menu · tower GPS · red pirates.

nexus_field_radio_publish() {
  [[ "${NEXUS_FIELD_RADIO:-1}" == "1" ]] || return 0
  command -v pythong >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-radio-catcher.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    pythong "$py" build >/dev/null 2>&1 || true
}

nexus_field_radio_json() {
  if declare -f nexus_field_radio_publish >/dev/null 2>&1; then
    nexus_field_radio_publish
  fi
  local py="${NEXUS_INSTALL_ROOT}/lib/field-radio-catcher.py"
  local cache="${NEXUS_STATE_DIR}/field-radio-panel.json"
  if [[ -f "$py" ]]; then
    NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
      pythong "$py" json 2>/dev/null && return 0
  fi
  if [[ -s "$cache" ]]; then
    pythong -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null
    return 0
  fi
  printf '{"schema":"field-radio-catcher/v1","station_menu":[],"illegal_frequencies":[],"stats":{"menu_count":0}}'
}