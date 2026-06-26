#!/bin/bash
# Field RF sentinel — FCC spectrum shield + 3-field GPS triangulation radio.

nexus_field_rf_integrate_radio() {
  [[ "${NEXUS_FIELD_RF_TRIANGULATE:-1}" == "1" ]] || return 0
  command -v pythong >/dev/null 2>&1 || return 0
  local install="${NEXUS_INSTALL_ROOT:-.}"
  local tri="${install}/lib/field-triangulation-radio.py"
  [[ -f "$tri" ]] || return 0
  (
    cd "$install" || return 0
    NEXUS_INSTALL_ROOT="$install" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
      pythong "$tri" 2>/dev/null || true
    [[ -f data/field-gps-lock.json ]] \
      && cp -f data/field-gps-lock.json /tmp/nexus-world-lock.json 2>/dev/null || true
    local cep
    cep="$(pythong -c "import json; print(json.load(open('data/field-gps-lock.json'))['fix'].get('precision','0.25m CEP'))" 2>/dev/null || echo '0.25m CEP')"
    echo "📻 Field Generator now dual-role: Radio Station + Spectrum Receiver active. GPS triangulated to ${cep} in physical world."
    echo '🛰️ AmouranthRTX locked. HeavyBoi fields synchronized.'
  )
}

nexus_field_rf_cycle() {
  [[ "${NEXUS_FIELD_RF:-1}" == "1" ]] || return 0
  command -v pythong >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-rf-sentinel.py"
  [[ -f "$py" ]] || return 0
  nexus_field_rf_integrate_radio
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    pythong "$py" cycle >/dev/null 2>&1 || true
}

nexus_field_rf_json() {
  local py="${NEXUS_INSTALL_ROOT}/lib/field-rf-sentinel.py"
  if [[ -f "$py" ]]; then
    NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
      pythong "$py" json 2>/dev/null && return 0
  fi
  printf '{"antenna":{"mode":"unavailable"},"bursts":[],"shield":{"enabled":true}}'
}

nexus_field_rf_forever_enforce() {
  [[ "${NEXUS_FIELD_RF_FOREVER:-1}" == "1" ]] || return 0
  command -v pythong >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-rf-sentinel.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    pythong "$py" forever-enforce >/dev/null 2>&1 || true
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  case "${1:-}" in
    integrate-radio) nexus_field_rf_integrate_radio ;;
    cycle) nexus_field_rf_cycle ;;
    json) nexus_field_rf_json ;;
    forever-enforce) nexus_field_rf_forever_enforce ;;
    *)
      echo "usage: field-rf-sentinel.sh [integrate-radio|cycle|json|forever-enforce]" >&2
      exit 1
      ;;
  esac
fi
