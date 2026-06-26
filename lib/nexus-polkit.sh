#!/bin/bash
# NEXUS Field polkit — install, verify, and invoke hardened pkexec bridge.
set -euo pipefail

_NEXUS_POLKIT_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_NEXUS_POLKIT_ROOT="$(cd "${_NEXUS_POLKIT_LIB}/.." && pwd)"

nexus_polkit_policy_src() {
  local candidates=(
    "${NEXUS_INSTALL_SRC:-}/install/polkit/com.nexus.field.policy"
    "${_NEXUS_POLKIT_ROOT}/install/polkit/com.nexus.field.policy"
    "${SG_ROOT:-}/NewLatest/install/polkit/com.nexus.field.policy"
  )
  local c
  for c in "${candidates[@]}"; do
    [[ -f "$c" ]] && { printf '%s' "$c"; return 0; }
  done
  return 1
}

nexus_polkit_rules_src() {
  local candidates=(
    "${NEXUS_INSTALL_SRC:-}/install/polkit/49-com.nexus.field.rules"
    "${_NEXUS_POLKIT_ROOT}/install/polkit/49-com.nexus.field.rules"
    "${SG_ROOT:-}/NewLatest/install/polkit/49-com.nexus.field.rules"
  )
  local c
  for c in "${candidates[@]}"; do
    [[ -f "$c" ]] && { printf '%s' "$c"; return 0; }
  done
  return 1
}

nexus_polkit_bridge_path() {
  if [[ -x /usr/local/lib/nexus-shield/lib/nexus-pkexec-bridge.sh ]]; then
    printf '%s' /usr/local/lib/nexus-shield/lib/nexus-pkexec-bridge.sh
    return 0
  fi
  if [[ -x "${_NEXUS_POLKIT_LIB}/nexus-pkexec-bridge.sh" ]]; then
    printf '%s' "${_NEXUS_POLKIT_LIB}/nexus-pkexec-bridge.sh"
    return 0
  fi
  return 1
}

nexus_polkit_installed() {
  [[ -f /usr/share/polkit-1/actions/com.nexus.field.policy ]]
}

nexus_polkit_install() {
  local policy rules bridge
  policy="$(nexus_polkit_policy_src)" || return 0
  rules="$(nexus_polkit_rules_src)" || true
  bridge="${_NEXUS_POLKIT_LIB}/nexus-pkexec-bridge.sh"
  [[ -f "$bridge" ]] || bridge="/usr/local/lib/nexus-shield/lib/nexus-pkexec-bridge.sh"
  install -d -m 755 /usr/share/polkit-1/actions /etc/polkit-1/rules.d 2>/dev/null || return 0
  install -m 644 "$policy" /usr/share/polkit-1/actions/com.nexus.field.policy
  if [[ -n "${rules:-}" && -f "$rules" ]]; then
    install -m 644 "$rules" /etc/polkit-1/rules.d/49-com.nexus.field.rules
  fi
  if [[ -f "$bridge" ]]; then
    install -d -m 755 /usr/local/lib/nexus-shield/lib 2>/dev/null || true
    install -m 755 "$bridge" /usr/local/lib/nexus-shield/lib/nexus-pkexec-bridge.sh
  fi
  # Retire legacy single-action policy name if present.
  rm -f /usr/share/polkit-1/actions/com.nexus.field.install.policy 2>/dev/null || true
  command -v systemctl >/dev/null 2>&1 && systemctl reload polkit 2>/dev/null || true
}

nexus_polkit_bootstrap_if_cached_sudo() {
  nexus_polkit_installed && return 0
  if sudo -n true 2>/dev/null; then
    nexus_polkit_install || true
  fi
}

nexus_polkit_action_for() {
  local verb="${1:-install}"
  if nexus_polkit_installed; then
    case "$verb" in
      install) printf '%s' com.nexus.field.install ;;
      update)  printf '%s' com.nexus.field.update ;;
      harden)  printf '%s' com.nexus.field.harden ;;
      service) printf '%s' com.nexus.field.service ;;
      underlay) printf '%s' com.nexus.field.underlay ;;
      *)       printf '%s' com.nexus.field.install ;;
    esac
  else
    printf '%s' com.nexus.field.bootstrap
  fi
}

nexus_polkit_resolve_installer() {
  local name="${1:-install-all.sh}"
  local candidates=(
    "${NEXUS_INSTALL_SRC:-}/${name}"
    "${_NEXUS_POLKIT_ROOT}/${name}"
    "/usr/local/lib/nexus-shield/${name}"
  )
  local c
  for c in "${candidates[@]}"; do
    [[ -f "$c" ]] && { readlink -f "$c"; return 0; }
  done
  return 1
}

# pkexec via bridge — never pkexec bash directly.
nexus_polkit_pkexec() {
  local verb="$1"
  shift
  local bridge action
  bridge="$(nexus_polkit_bridge_path)" || {
    echo "nexus-polkit: pkexec bridge missing." >&2
    return 1
  }
  action="$(nexus_polkit_action_for "$verb")"
  pkexec --action "$action" "$bridge" "run-${verb}" "$@"
}

nexus_polkit_verify() {
  local ok=1
  local policy=/usr/share/polkit-1/actions/com.nexus.field.policy
  local rules=/etc/polkit-1/rules.d/49-com.nexus.field.rules
  local bridge=/usr/local/lib/nexus-shield/lib/nexus-pkexec-bridge.sh
  [[ -f "$policy" ]] || ok=0
  [[ -f "$rules" ]] || ok=0
  [[ -x "$bridge" && ! -w "$bridge" ]] || ok=0
  [[ ! -f /usr/share/polkit-1/actions/com.nexus.field.install.policy ]] || ok=0
  return $((ok == 1 ? 0 : 1))
}