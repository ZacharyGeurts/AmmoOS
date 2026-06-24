#!/bin/bash
# NEXUS Field DNS — truth resolver publish, multipoint local capture, resolv override.

nexus_field_dns_publish() {
  [[ "${NEXUS_FIELD_DNS:-1}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-dns.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$py" build >/dev/null 2>&1 || true
  local mid="${NEXUS_INSTALL_ROOT}/lib/dns-multipoint-identity.py"
  [[ -f "$mid" ]] && NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$mid" build >/dev/null 2>&1 || true
}

nexus_field_dns_json() {
  if declare -f nexus_field_dns_publish >/dev/null 2>&1; then
    nexus_field_dns_publish
  fi
  local py="${NEXUS_INSTALL_ROOT}/lib/field-dns.py"
  local cache="${NEXUS_STATE_DIR}/field-dns-panel.json"
  if [[ -f "$py" ]]; then
    NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
      python3 "$py" json 2>/dev/null && return 0
  fi
  if [[ -s "$cache" ]]; then
    python3 -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null
    return 0
  fi
  printf '{"schema":"field-dns/v1","running":false,"rfc_matrix":[],"legal_framework":[],"zones":[]}'
}

nexus_field_dns_serve_loop() {
  [[ "${NEXUS_FIELD_DNS:-1}" == "1" ]] || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-dns.py"
  [[ -f "$py" ]] || return 0
  declare -f nexus_field_dns_enforce_resolv >/dev/null 2>&1 && nexus_field_dns_enforce_resolv || true
  declare -f nexus_field_dns_local_capture >/dev/null 2>&1 && nexus_field_dns_local_capture || true
  while true; do
    NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
      NEXUS_FIELD_DNS_BINDS_IPV4="${NEXUS_FIELD_DNS_BINDS_IPV4:-127.0.0.1,127.0.0.53}" \
      NEXUS_FIELD_DNS_BINDS_IPV6="${NEXUS_FIELD_DNS_BINDS_IPV6:-::1}" \
      python3 "$py" serve 2>/dev/null || true
    sleep 5
  done
}

nexus_field_dns_enforce_resolv() {
  [[ "${NEXUS_FIELD_DNS_ENFORCE_RESOLV:-1}" == "1" ]] || return 0
  local port="${NEXUS_FIELD_DNS_PORT:-53}"
  local stub="${NEXUS_STATE_DIR}/resolv.conf.nexus-stub"
  local backup="${NEXUS_STATE_DIR}/resolv.conf.nexus-backup"
  if [[ ! -f "$backup" && -f /etc/resolv.conf && ! -L /etc/resolv.conf ]]; then
    cp -a /etc/resolv.conf "$backup" 2>/dev/null || true
  elif [[ ! -f "$backup" && -L /etc/resolv.conf ]]; then
    cp -a "$(readlink -f /etc/resolv.conf 2>/dev/null || echo /etc/resolv.conf)" "$backup" 2>/dev/null || true
  fi
  {
    echo "# NEXUS Truth DNS — all local queries use our resolver (RFC 1035, RFC 6761, RFC 9520)"
    echo "# User DNS settings overridden — multipoint secure identification"
    echo "nameserver 127.0.0.1"
    echo "nameserver ::1"
    echo "options edns0 trust-ad single-request-reopen"
    echo "# NEXUS_FIELD_DNS_PORT=${port}"
    echo "# NEXUS_FIELD_DNS_BINDS=${NEXUS_FIELD_DNS_BINDS_IPV4:-127.0.0.1,127.0.0.53}"
  } >"$stub"
  if [[ "$(id -u)" -eq 0 ]]; then
    if [[ "${NEXUS_FIELD_DNS_BREAK_RESOLV_SYMLINK:-1}" == "1" && -L /etc/resolv.conf ]]; then
      rm -f /etc/resolv.conf 2>/dev/null || true
    fi
    cp -f "$stub" /etc/resolv.conf 2>/dev/null || true
    chmod 644 /etc/resolv.conf 2>/dev/null || true
  fi
  nexus_log "INFO" "field-dns" "resolv override active (127.0.0.1 + ::1 truth resolver)"
}

nexus_field_dns_local_capture() {
  [[ "${NEXUS_FIELD_DNS_LOCAL_CAPTURE:-1}" == "1" ]] || return 0
  command -v nft >/dev/null 2>&1 || return 0
  local port="${NEXUS_FIELD_DNS_PORT:-53}"
  local table="${NEXUS_FIREWALL_TABLE:-nexus}"
  if nft list chain inet "$table" output 2>/dev/null | grep -q 'nexus-dns-local'; then
    return 0
  fi
  # Block egress DNS to foreign resolvers — never add untrusted (RFC 9520)
  local foreign="8.8.8.8, 8.8.4.4, 1.1.1.1, 1.0.0.1, 9.9.9.9, 71.10.216.1, 71.10.216.2"
  nft add rule inet "$table" output \
    ip daddr "{ ${foreign} }" udp dport "${port}" drop comment "nexus-dns-local" 2>/dev/null || true
  nft add rule inet "$table" output \
    ip daddr "{ ${foreign} }" tcp dport "${port}" drop comment "nexus-dns-local" 2>/dev/null || true
  nft add rule inet "$table" output \
    udp dport 853 drop comment "nexus-dns-local-dot" 2>/dev/null || true
  nexus_log "INFO" "field-dns" "local DNS capture — foreign resolver egress blocked"
}

nexus_field_dns_enforce_cycle() {
  [[ "${NEXUS_FIELD_DNS:-1}" == "1" ]] || return 0
  declare -f nexus_field_dns_enforce_resolv >/dev/null 2>&1 && nexus_field_dns_enforce_resolv || true
  declare -f nexus_field_dns_local_capture >/dev/null 2>&1 && nexus_field_dns_local_capture || true
  declare -f nexus_field_dns_publish >/dev/null 2>&1 && nexus_field_dns_publish || true
}