#!/bin/bash
# NEXUS vector scour — classify active peers; populate intel cache for gatekeeper.

nexus_vector_scour_publish() {
  [[ "${NEXUS_VECTOR_INTEL:-1}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  local script="${NEXUS_INSTALL_ROOT}/lib/vector-intel.py"
  [[ -f "$script" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$script" scour >/dev/null 2>&1 || true
  if declare -f nexus_angel_dossier_publish >/dev/null 2>&1; then
    nexus_angel_dossier_publish
  elif [[ -f "${NEXUS_INSTALL_ROOT}/lib/angel-dossier.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/angel-dossier.sh"
    nexus_angel_dossier_publish
  fi
}

nexus_vector_intel_json() {
  local scour="${NEXUS_STATE_DIR}/vector-scour.json"
  if [[ -s "$scour" ]]; then
    python3 -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$scour" 2>/dev/null
  else
    printf '{"active_count":0,"pest_count":0,"active_vectors":[],"pests":[],"never_unknown":true}'
  fi
}