#!/bin/bash
# Field Outside Talk — egress gate panel payload (SSH, telnet, mail, custom ports).

[[ -f "${NEXUS_INSTALL_ROOT}/lib/field-outside-asm.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/field-outside-asm.sh"

nexus_field_outside_talk_publish() {
  [[ "${NEXUS_FIELD_OUTSIDE_TALK:-1}" == "1" ]] || return 0
  if declare -f nexus_field_outside_asm_build >/dev/null 2>&1; then
    nexus_field_outside_asm_build >/dev/null 2>&1 || true
  fi
  command -v python3 >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-outside-talk.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$py" build >/dev/null 2>&1 || true
}

nexus_field_outside_talk_json() {
  if declare -f nexus_field_outside_talk_publish >/dev/null 2>&1; then
    nexus_field_outside_talk_publish
  fi
  local py="${NEXUS_INSTALL_ROOT}/lib/field-outside-talk.py"
  local cache="${NEXUS_STATE_DIR}/field-outside-talk-panel.json"
  if [[ -f "$py" ]]; then
    NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
      python3 "$py" json 2>/dev/null && return 0
  fi
  if [[ -s "$cache" ]]; then
    python3 -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null
    return 0
  fi
  printf '{"schema":"field-outside-talk/v1","tools":[],"firewall":{"active":false},"recent_sessions":[]}'
}