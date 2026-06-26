#!/bin/bash
# Truth ID human registry — prioritized above dossier; internet → people.

nexus_human_registry_publish() {
  [[ "${NEXUS_HUMAN_REGISTRY:-1}" == "1" ]] || return 0
  command -v pythong >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/human-registry.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    pythong "$py" build >/dev/null 2>&1 || true
}

nexus_human_registry_json() {
  if declare -f nexus_human_registry_publish >/dev/null 2>&1; then
    nexus_human_registry_publish
  fi
  local py="${NEXUS_INSTALL_ROOT}/lib/human-registry.py"
  local cache="${NEXUS_STATE_DIR}/human-registry-panel.json"
  if [[ -f "$py" ]]; then
    NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
      pythong "$py" json 2>/dev/null && return 0
  fi
  if [[ -s "$cache" ]]; then
    pythong -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null
    return 0
  fi
  printf '{"schema":"human-registry/v1","stats":{"total":0},"table":[],"humans":{}}'
}