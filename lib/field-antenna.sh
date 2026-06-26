#!/bin/bash
# Field antenna orchestrator — RF + audio + laser + BLE + sub-µm blaster cycle.

nexus_field_antenna_publish() {
  [[ "${NEXUS_FIELD_ANTENNA:-1}" == "1" ]] || return 0
  command -v pythong >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-antenna-orchestrator.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    pythong "$py" build >/dev/null 2>&1 || true
}

nexus_field_antenna_cycle() {
  [[ "${NEXUS_FIELD_ANTENNA:-1}" == "1" ]] || return 0
  command -v pythong >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-antenna-orchestrator.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    pythong "$py" cycle >/dev/null 2>&1 || true
}

nexus_field_antenna_json() {
  if declare -f nexus_field_antenna_publish >/dev/null 2>&1; then
    nexus_field_antenna_publish
  fi
  local py="${NEXUS_INSTALL_ROOT}/lib/field-antenna-orchestrator.py"
  local cache="${NEXUS_STATE_DIR}/field-antenna-panel.json"
  if [[ -f "$py" ]]; then
    NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
      pythong "$py" json 2>/dev/null && return 0
  fi
  if [[ -s "$cache" ]]; then
    pythong -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null
    return 0
  fi
  printf '{"schema":"field-antenna/v1","readiness":{"blaster_ready":false,"score":0},"frequency_knowledge":{"modalities":[]}}'
}