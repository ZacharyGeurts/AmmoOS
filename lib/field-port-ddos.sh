#!/bin/bash
# Port & WiFi DDoS shield — wave view thermals + entropy at network edge.

nexus_port_ddos_enabled() {
  [[ "${NEXUS_PORT_DDOS_SHIELD:-1}" == "1" ]]
}

nexus_port_ddos_cycle() {
  nexus_port_ddos_enabled || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-port-ddos-shield.py"
  [[ -f "$py" ]] || return 0
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    NEXUS_PORT_DDOS_ENFORCE="${NEXUS_PORT_DDOS_ENFORCE:-1}" \
    pythong "$py" cycle >/dev/null 2>&1 || true
}