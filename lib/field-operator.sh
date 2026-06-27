#!/bin/bash
# Operator — field workhorse (IRQ, DMA, Smart Connective Iron Plate).
set -euo pipefail

nexus_field_operator_once() {
  [[ "${NEXUS_FIELD_OPERATOR:-1}" == "1" ]] || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-operator.py"
  [[ -f "$py" ]] || return 0
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}" \
    SG_ROOT="${SG_ROOT:-}" pythong "$py" tick >/dev/null 2>&1 || true
}

nexus_field_operator_loop() {
  [[ "${NEXUS_FIELD_OPERATOR:-1}" == "1" ]] || return 0
  local interval="${NEXUS_FIELD_OPERATOR_INTERVAL:-300}"
  while true; do
    nexus_field_operator_once
    sleep "$interval"
  done
}