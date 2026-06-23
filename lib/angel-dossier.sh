#!/bin/bash
# NEXUS Angel Dossier — publish attack-path dossiers and research tables.

nexus_angel_dossier_publish() {
  [[ "${NEXUS_ANGEL_DOSSIER:-1}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  local script="${NEXUS_INSTALL_ROOT}/lib/angel-dossier.py"
  [[ -f "$script" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$script" build >/dev/null 2>&1 || true
}

nexus_angel_dossiers_json() {
  local f="${NEXUS_STATE_DIR}/angel-dossiers.json"
  if [[ -s "$f" ]]; then
    python3 -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$f" 2>/dev/null
  else
    printf '{"dossier_count":0,"dossiers":[],"motto":"Let'\''s Be Angels"}'
  fi
}

nexus_angel_research_json() {
  local f="${NEXUS_STATE_DIR}/angel-research.json"
  if [[ -s "$f" ]]; then
    python3 -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$f" 2>/dev/null
  else
    printf '{"tables":{"mac_vendors":[],"ip_intel":[],"exploit_cve_map":[],"attack_paths":[]},"motto":"Let'\''s Be Angels"}'
  fi
}