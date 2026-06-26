#!/bin/bash
# Panel browser detection and localhost open helpers.

nexus_panel_url() {
  local port="${NEXUS_THREAT_PANEL_PORT:-9477}"
  printf 'http://127.0.0.1:%s/field' "$port"
}

nexus_panel_app_url() {
  local port="${NEXUS_THREAT_PANEL_PORT:-9477}"
  printf 'http://127.0.0.1:%s/app' "$port"
}

nexus_panel_desired_version() {
  local common="${NEXUS_INSTALL_ROOT}/lib/nexus-common.sh"
  [[ -f "$common" ]] || return 1
  grep -o 'NEXUS_VERSION="[^"]*"' "$common" 2>/dev/null | head -1 | cut -d'"' -f2
}

nexus_panel_served_version() {
  local port="${NEXUS_THREAT_PANEL_PORT:-9477}"
  local html
  html="$(curl -s --connect-timeout 2 "http://127.0.0.1:${port}/field" 2>/dev/null)" || return 1
  [[ -n "$html" ]] || return 1
  if grep -q 'underlay-f9' <<<"$html" 2>/dev/null; then
    grep -oE 'NEXUS-Shield v[0-9]+\.[0-9]+\.[0-9]+' <<<"$html" 2>/dev/null | head -1 | sed 's/.*v//' && return 0
  fi
  grep -oE 'NEXUS-Shield v[0-9]+\.[0-9]+\.[0-9]+' <<<"$html" 2>/dev/null | head -1 | sed 's/.*v//'
}

nexus_panel_running_install_root() {
  local line
  line="$(pgrep -af 'threat-panel-http\.py' 2>/dev/null | head -1)" || return 1
  [[ -n "$line" ]] || return 1
  if [[ "$line" =~ threat-panel-http\.py[[:space:]]+[0-9]+[[:space:]]+([^[:space:]]+/panel) ]]; then
    dirname "${BASH_REMATCH[1]}"
    return 0
  fi
  awk '{
    for (i = 1; i <= NF; i++) {
      if ($i ~ /\/panel$/) { print $i; exit }
    }
  }' <<<"$line" | sed 's|/panel$||'
}

nexus_panel_stop() {
  local port="${NEXUS_THREAT_PANEL_PORT:-9477}"
  pkill -f "threat-panel-http.py.*${port}" 2>/dev/null || true
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" 2>/dev/null || true
  fi
  nexus_await_port_free "${port}" 5
}

nexus_panel_pick_port() {
  local want="${1:-$(nexus_panel_desired_version 2>/dev/null || true)}"
  local primary="${NEXUS_THREAT_PANEL_PORT:-9477}"
  local fallback="${NEXUS_THREAT_PANEL_FALLBACK_PORT:-9478}"
  local served

  if ! curl -s --connect-timeout 1 "http://127.0.0.1:${primary}/field" >/dev/null 2>&1; then
    printf '%s' "$primary"
    return 0
  fi

  served="$(NEXUS_THREAT_PANEL_PORT="$primary" nexus_panel_served_version 2>/dev/null || true)"
  if [[ -z "$want" || -z "$served" || "$served" == "$want" ]]; then
    printf '%s' "$primary"
    return 0
  fi

  nexus_panel_stop
  served="$(NEXUS_THREAT_PANEL_PORT="$primary" nexus_panel_served_version 2>/dev/null || true)"
  if [[ -z "$served" || "$served" == "$want" ]]; then
    printf '%s' "$primary"
    return 0
  fi

  nexus_log "WARN" "panel-browser" "PORT_FALLBACK primary=${primary} served=${served} want=${want} -> ${fallback}"
  printf '%s' "$fallback"
}

nexus_panel_needs_restart() {
  local want="${1:-$(nexus_panel_desired_version)}"
  local port="${NEXUS_THREAT_PANEL_PORT:-9477}"
  local running_root served want_root

  [[ -n "$want" ]] || return 0
  want_root="${NEXUS_INSTALL_ROOT}"

  if ! pgrep -f "threat-panel-http.py.*${port}" >/dev/null 2>&1; then
    return 0
  fi

  running_root="$(nexus_panel_running_install_root 2>/dev/null || true)"
  if [[ -n "$running_root" && "$running_root" != "$want_root" ]]; then
    return 0
  fi

  served="$(nexus_panel_served_version 2>/dev/null || true)"
  if [[ -n "$served" && "$served" != "$want" ]]; then
    return 0
  fi

  return 1
}

nexus_panel_wait_ready() {
  local url="${1:-$(nexus_panel_url)}"
  local tries="${2:-5}"
  nexus_await_curl_ready "$url" "$tries" "$tries"
}

nexus_panel_boot_id() {
  local bid
  bid="$(cat /proc/sys/kernel/random/boot_id 2>/dev/null || true)"
  [[ -n "$bid" ]] || bid="boot-$(date -u '+%Y%m%d%H%M%S' 2>/dev/null || date '+%Y%m%d%H%M%S')"
  printf '%s' "$bid"
}

nexus_panel_operator_user() {
  local user home
  user="${SUDO_USER:-}"
  [[ -z "$user" || "$user" == "root" ]] && user="$(logname 2>/dev/null || true)"
  [[ -z "$user" || "$user" == "root" ]] && user="${USER:-}"
  [[ -z "$user" || "$user" == "root" ]] && user="default"
  home="$(getent passwd "$user" 2>/dev/null | cut -d: -f6)"
  [[ -n "$home" ]] || home="/home/${user}"
  printf '%s:%s' "$user" "$home"
}

nexus_panel_tristate_url() {
  local port="${NEXUS_THREAT_PANEL_PORT:-9477}"
  printf 'http://127.0.0.1:%s/underlay-f9?sector=underlay' "$port"
}

nexus_panel_open_on_boot() {
  [[ "${NEXUS_PANEL_AUTO_OPEN:-1}" == "1" ]] || return 0
  local marker="${NEXUS_PANEL_LAUNCH_MARKER:-${NEXUS_STATE_DIR}/panel-launched.boot}"
  local boot_id url
  boot_id="$(nexus_panel_boot_id)"
  if [[ -f "$marker" ]] && grep -qFx "$boot_id" "$marker" 2>/dev/null; then
    return 0
  fi
  url="${1:-$(nexus_panel_url)}"
  if nexus_panel_open_browser "$url"; then
    printf '%s\n' "$boot_id" >"$marker"
    chmod 640 "$marker" 2>/dev/null || true
    return 0
  fi
  return 1
}

nexus_panel_detect_browsers() {
  local c
  for c in \
    fieldfox \
    field-queen \
    queen-browser \
    xdg-open \
    firefox \
    google-chrome-stable \
    google-chrome \
    chromium-browser \
    chromium \
    brave-browser \
    brave \
    microsoft-edge \
    msedge \
    opera \
    vivaldi; do
    command -v "$c" >/dev/null 2>&1 && printf '%s\n' "$c"
  done
}

nexus_panel_open_browser() {
  local url="${1:-$(nexus_panel_url)}"
  local browser opened=0
  local ready_url
  local ff_launch="${NEXUS_INSTALL_ROOT}/lib/fieldfox-launch.sh"
  local queen_launch="${QUEEN_ROOT:-${NEXUS_INSTALL_ROOT}/../Queen}/build/queen-browser"
  ready_url="$(nexus_panel_app_url)"

  if [[ "${NEXUS_QUEEN_SOVEREIGN:-1}" == "1" || "${NEXUS_FIELD_BROWSER_QUEEN:-1}" == "1" ]]; then
    if [[ -x "${queen_launch}" ]]; then
      DISPLAY="${DISPLAY:-:0}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
        "${queen_launch}" --sovereign --extended-field "${url}" >/dev/null 2>&1 &
      nexus_log "INFO" "panel-browser" "QUEEN_RTX_SOVEREIGN url=${url}"
      echo "Opened Queen RTX (sovereign): ${url}"
      return 0
    fi
  fi
  if [[ "${NEXUS_NO_OS_BROWSER_HOOK:-0}" == "1" ]]; then
    nexus_log "WARN" "panel-browser" "SOVEREIGN_NO_OS_HOOK url=${url}"
    return 1
  fi
  if [[ "${NEXUS_FIELD_BROWSER_QUEEN:-1}" == "1" && -x "${ff_launch}" ]]; then
    NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
      "${ff_launch}" "${url}" >/dev/null 2>&1 && {
      nexus_log "INFO" "panel-browser" "FIELD_WINDOW_OPENED url=${url}"
      echo "Opened Queen browser: ${url}"
      return 0
    }
  fi

  if ! nexus_panel_wait_ready "$ready_url" 5; then
    nexus_panel_wait_ready "$url" 5 || true
    nexus_panel_wait_ready "${url%/field}/" 5 || true
  fi
  if ! curl -s --connect-timeout 2 "$url" >/dev/null 2>&1 \
    && ! curl -s --connect-timeout 2 "$ready_url" >/dev/null 2>&1; then
    nexus_log "WARN" "panel-browser" "PANEL_NOT_READY url=${url}"
    return 1
  fi

  local op_user op_home op_uid
  IFS=: read -r op_user op_home <<<"$(nexus_panel_operator_user)"
  op_uid="$(getent passwd "$op_user" 2>/dev/null | cut -d: -f3)"

  while IFS= read -r browser; do
    [[ -n "$browser" ]] || continue
    if [[ "$(id -u)" -eq 0 && -n "$op_uid" && "$op_uid" != "0" ]]; then
      if [[ "$browser" == "xdg-open" ]]; then
        sudo -u "$op_user" DISPLAY="${DISPLAY:-:0}" XAUTHORITY="${XAUTHORITY:-${op_home}/.Xauthority}" \
          xdg-open "$url" >/dev/null 2>&1 &
      elif [[ "$browser" == "google-chrome-stable" || "$browser" == "google-chrome" || "$browser" == "chromium-browser" || "$browser" == "chromium" ]]; then
        sudo -u "$op_user" DISPLAY="${DISPLAY:-:0}" XAUTHORITY="${XAUTHORITY:-${op_home}/.Xauthority}" \
          "$browser" --app="$url" --window-size=1440,900 --new-window >/dev/null 2>&1 \
          || sudo -u "$op_user" DISPLAY="${DISPLAY:-:0}" "$browser" --new-window "$url" >/dev/null 2>&1 &
      else
        sudo -u "$op_user" DISPLAY="${DISPLAY:-:0}" XAUTHORITY="${XAUTHORITY:-${op_home}/.Xauthority}" \
          "$browser" --new-window "$url" >/dev/null 2>&1 \
          || sudo -u "$op_user" DISPLAY="${DISPLAY:-:0}" "$browser" "$url" >/dev/null 2>&1 &
      fi
    elif [[ "$browser" == "xdg-open" ]]; then
      DISPLAY="${DISPLAY:-:0}" xdg-open "$url" >/dev/null 2>&1 &
    elif [[ "$browser" == "google-chrome-stable" || "$browser" == "google-chrome" || "$browser" == "chromium-browser" || "$browser" == "chromium" ]]; then
      DISPLAY="${DISPLAY:-:0}" "$browser" --app="$url" --window-size=1440,900 --new-window >/dev/null 2>&1 \
        || DISPLAY="${DISPLAY:-:0}" "$browser" --new-window "$url" >/dev/null 2>&1 &
    else
      DISPLAY="${DISPLAY:-:0}" "$browser" --new-window "$url" >/dev/null 2>&1 \
        || DISPLAY="${DISPLAY:-:0}" "$browser" "$url" >/dev/null 2>&1 &
    fi
    opened=1
    nexus_log "INFO" "panel-browser" "FIELD_WINDOW_OPENED url=${url} via=${browser} user=${op_user:-self}"
    echo "Opened NEXUS panel: ${url}"
    return 0
  done < <(nexus_panel_detect_browsers)

  [[ "$opened" -eq 1 ]]
}

nexus_panel_open_help() {
  local url="${1:-$(nexus_panel_url)}"
  cat <<EOF
NEXUS panel URL: ${url}

Browser could not be opened automatically. Try one of:

  xdg-open '${url}'
  firefox '${url}'

Tray icon (right-click near clock → pick a tab):

  ./nexus.sh --tray
  ./nexus.sh --tab library

Or use the CLI (no browser needed):

  ./bin/nexus status
  ./bin/nexus test

If the panel is offline:

  ./nexus.sh --wait
  ./nexus.sh --no-browser
EOF
}