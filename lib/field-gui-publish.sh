#!/bin/bash
# Field GUI publish — all panel slices originate from field modules (no orphan APIs).

[[ -f "${NEXUS_INSTALL_ROOT}/lib/packet-oracle.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/packet-oracle.sh"

nexus_field_py_json() {
  local script="$1"
  shift
  [[ -f "$script" ]] || return 1
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
    pythong "$script" "$@" 2>/dev/null
}

nexus_field_hardware_publish() {
  nexus_field_py_json "${NEXUS_INSTALL_ROOT}/lib/field-hardware-probe.py" json \
    >"${NEXUS_STATE_DIR}/field-hardware-panel.json.tmp" 2>/dev/null \
    && mv -f "${NEXUS_STATE_DIR}/field-hardware-panel.json.tmp" \
      "${NEXUS_STATE_DIR}/field-hardware-panel.json" 2>/dev/null || true
}

nexus_field_hazard_onset_publish() {
  nexus_field_py_json "${NEXUS_INSTALL_ROOT}/lib/field-hazard-onset.py" panel \
    >"${NEXUS_STATE_DIR}/field-hazard-onset-panel.json.tmp" 2>/dev/null \
    && mv -f "${NEXUS_STATE_DIR}/field-hazard-onset-panel.json.tmp" \
      "${NEXUS_STATE_DIR}/field-hazard-onset-panel.json" 2>/dev/null || true
}

nexus_lethal_enforcement_publish() {
  nexus_field_py_json "${NEXUS_INSTALL_ROOT}/lib/lethal-enforcement.py" panel \
    >"${NEXUS_STATE_DIR}/lethal-enforcement-panel.json.tmp" 2>/dev/null \
    && mv -f "${NEXUS_STATE_DIR}/lethal-enforcement-panel.json.tmp" \
      "${NEXUS_STATE_DIR}/lethal-enforcement-panel.json" 2>/dev/null || true
}

nexus_hostess7_lethal_insight_publish() {
  nexus_field_py_json "${NEXUS_INSTALL_ROOT}/lib/hostess7-lethal-insight.py" panel \
    >"${NEXUS_STATE_DIR}/hostess7-lethal-insight-panel.json.tmp" 2>/dev/null \
    && mv -f "${NEXUS_STATE_DIR}/hostess7-lethal-insight-panel.json.tmp" \
      "${NEXUS_STATE_DIR}/hostess7-lethal-insight-panel.json" 2>/dev/null || true
}

nexus_field_gui_publish_all() {
  if declare -f nexus_connection_gatekeeper_publish >/dev/null 2>&1; then
    nexus_connection_gatekeeper_publish
  fi
  nexus_field_hardware_publish
  nexus_field_hazard_onset_publish
  nexus_lethal_enforcement_publish
  nexus_hostess7_lethal_insight_publish
}

nexus_field_hardware_json() {
  local cache="${NEXUS_STATE_DIR}/field-hardware-panel.json"
  if [[ -s "$cache" ]]; then
    pythong -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null && return 0
  fi
  nexus_field_hardware_publish
  if [[ -s "$cache" ]]; then
    pythong -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null && return 0
  fi
  nexus_field_py_json "${NEXUS_INSTALL_ROOT}/lib/field-hardware-probe.py" json \
    || printf '{"schema":"field-hardware-probe/v1","standalone":true}'
}

nexus_field_hazard_onset_json() {
  local cache="${NEXUS_STATE_DIR}/field-hazard-onset-panel.json"
  if [[ -s "$cache" ]]; then
    pythong -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null && return 0
  fi
  nexus_field_hazard_onset_publish
  if [[ -s "$cache" ]]; then
    pythong -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null && return 0
  fi
  printf '{"schema":"field-hazard-onset-panel/v1","enabled":true}'
}

nexus_lethal_enforcement_json() {
  local cache="${NEXUS_STATE_DIR}/lethal-enforcement-panel.json"
  if [[ -s "$cache" ]]; then
    pythong -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null && return 0
  fi
  nexus_lethal_enforcement_publish
  if [[ -s "$cache" ]]; then
    pythong -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null && return 0
  fi
  printf '{"schema":"lethal-enforcement-panel/v1","status":"lethal","merciless":true}'
}

nexus_hostess7_lethal_insight_json() {
  local cache="${NEXUS_STATE_DIR}/hostess7-lethal-insight-panel.json"
  if [[ -s "$cache" ]]; then
    pythong -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null && return 0
  fi
  nexus_hostess7_lethal_insight_publish
  if [[ -s "$cache" ]]; then
    pythong -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null && return 0
  fi
  printf '{"schema":"hostess7-lethal-insight-panel/v1","available":false}'
}

nexus_field_antenna_catch_json() {
  local cache="${NEXUS_STATE_DIR}/field-antenna-catch.json"
  if [[ -s "$cache" ]]; then
    pythong -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null && return 0
  fi
  printf '{"schema":"field-antenna-catch/v1","caught":false}'
}