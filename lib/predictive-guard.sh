#!/bin/bash
# Predictive guard — correlate recent alerts to pre-tighten before escalation.

NEXUS_PREDICTIVE_STATE="${NEXUS_PREDICTIVE_STATE:-${NEXUS_STATE_DIR}/predictive.state}"

nexus_predictive_init() {
  [[ "${NEXUS_PREDICTIVE:-1}" == "1" ]] || return 0
  mkdir -p "$(dirname "$NEXUS_PREDICTIVE_STATE")"
  [[ -f "$NEXUS_PREDICTIVE_STATE" ]] || echo "score=0" >"$NEXUS_PREDICTIVE_STATE"
}

nexus_predictive_record() {
  local module="$1"
  local weight=1
  case "$module" in
    entropy-oracle) weight=2 ;;
    behavior-symphony) weight=3 ;;
    shadow-reality|privacy-guard) weight=2 ;;
    packet-oracle|threat-vectors|firewall-sentinel) weight=4 ;;
    self-defense) weight=5 ;;
  esac
  local score
  score="$(grep '^score=' "$NEXUS_PREDICTIVE_STATE" 2>/dev/null | cut -d= -f2)"
  score=$(( ${score:-0} + weight ))
  sed -i "s/^score=.*/score=${score}/" "$NEXUS_PREDICTIVE_STATE" 2>/dev/null || echo "score=${score}" >"$NEXUS_PREDICTIVE_STATE"
  if [[ "$score" -ge 6 ]]; then
    nexus_vigil_record_alert "predictive-guard"
    nexus_log "INFO" "predictive-guard" "PREDICTIVE_TIGHTEN score=${score} modules_correlated"
  fi
}

nexus_predictive_decay() {
  local score
  score="$(grep '^score=' "$NEXUS_PREDICTIVE_STATE" 2>/dev/null | cut -d= -f2)"
  score=$(( ${score:-0} > 0 ? score - 1 : 0 ))
  sed -i "s/^score=.*/score=${score}/" "$NEXUS_PREDICTIVE_STATE" 2>/dev/null || true
}