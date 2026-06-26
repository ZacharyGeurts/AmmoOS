#!/bin/bash
# NEXUS AI Integration Hook — field compiler + Grok build; human integration forbidden.

nexus_ai_integration_hook_enabled() {
  [[ "${NEXUS_AI_INTEGRATION_HOOK:-1}" == "1" ]]
}

nexus_ai_integration_hook_board() {
  nexus_ai_integration_hook_enabled || return 0
  mkdir -p "${NEXUS_STATE_DIR}" 2>/dev/null || true
  local ts
  ts="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/ai-integration-hook.py" ]]; then
    NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
      pythong "${NEXUS_INSTALL_ROOT}/lib/ai-integration-hook.py" board >/dev/null 2>&1 || true
  else
    cat >"${NEXUS_STATE_DIR}/ai-integration-hook.json" <<EOF
{"schema":"nexus-ai-integration-hook/v1","owner":"nexus","boarded":true,"policy":"ai_only_never_human","human_integration":false,"updated":"${ts}"}
EOF
  fi
  nexus_log "INFO" "ai-integration-hook" "BOARD_HIT policy=ai_only_never_human field_compiler=1 grok_build=1"
}