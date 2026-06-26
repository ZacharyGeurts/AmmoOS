#!/bin/bash
# Immediate Home Protector — 3-bedroom home airspace publish helpers.

nexus_home_protector_publish() {
  [[ "${NEXUS_HOME_PROTECTOR:-1}" == "1" ]] || return 0
  command -v pythong >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/home-protector.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    pythong "$py" build >/dev/null 2>&1 || true
}

nexus_home_protector_json() {
  if declare -f nexus_home_protector_publish >/dev/null 2>&1; then
    nexus_home_protector_publish
  fi
  local py="${NEXUS_INSTALL_ROOT}/lib/home-protector.py"
  local cache="${NEXUS_STATE_DIR}/home-protector-panel.json"
  if [[ -f "$py" ]]; then
    NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
      pythong "$py" json 2>/dev/null && return 0
  fi
  if [[ -s "$cache" ]]; then
    pythong -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null
    return 0
  fi
  printf '{"schema":"home-protector/v1","stats":{"total":0},"entities":[],"table":[]}'
}