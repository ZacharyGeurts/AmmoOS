#!/bin/bash
# Panel browser detection and localhost open helpers.

nexus_panel_url() {
  local port="${NEXUS_THREAT_PANEL_PORT:-9477}"
  if [[ "${NEXUS_PANEL_TLS:-1}" == "1" ]]; then
    printf 'https://127.0.0.1:%s/field' "$port"
  else
    printf 'http://127.0.0.1:%s/field' "$port"
  fi
}

nexus_panel_app_url() {
  local port="${NEXUS_THREAT_PANEL_PORT:-9477}"
  if [[ "${NEXUS_PANEL_TLS:-1}" == "1" ]]; then
    printf 'https://127.0.0.1:%s/app' "$port"
  else
    printf 'http://127.0.0.1:%s/app' "$port"
  fi
}

nexus_panel_wait_ready() {
  local url="${1:-$(nexus_panel_url)}"
  local tries="${2:-30}"
  local i
  for i in $(seq 1 "$tries"); do
    curl -sk --connect-timeout 1 "$url" >/dev/null 2>&1 && return 0
    sleep 1
  done
  return 1
}

nexus_panel_detect_browsers() {
  local c
  for c in \
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
  ready_url="$(nexus_panel_app_url)"

  if ! nexus_panel_wait_ready "$ready_url" 30; then
    nexus_panel_wait_ready "${url%/field}/" 10 || true
  fi
  if ! curl -sk --connect-timeout 1 "$url" >/dev/null 2>&1 \
    && ! curl -sk --connect-timeout 1 "$ready_url" >/dev/null 2>&1; then
    nexus_log "WARN" "panel-browser" "PANEL_NOT_READY url=${url}"
    return 1
  fi

  while IFS= read -r browser; do
    [[ -n "$browser" ]] || continue
    if [[ "$browser" == "xdg-open" ]]; then
      DISPLAY="${DISPLAY:-:0}" xdg-open "$url" >/dev/null 2>&1 &
    elif [[ "$browser" == "google-chrome-stable" || "$browser" == "google-chrome" || "$browser" == "chromium-browser" || "$browser" == "chromium" ]]; then
      DISPLAY="${DISPLAY:-:0}" "$browser" --app="$url" --window-size=1440,900 --new-window >/dev/null 2>&1 \
        || DISPLAY="${DISPLAY:-:0}" "$browser" --new-window "$url" >/dev/null 2>&1 &
    elif [[ "$browser" == "firefox" ]]; then
      DISPLAY="${DISPLAY:-:0}" "$browser" --new-window "$url" >/dev/null 2>&1 &
    else
      DISPLAY="${DISPLAY:-:0}" "$browser" --new-window "$url" >/dev/null 2>&1 \
        || DISPLAY="${DISPLAY:-:0}" "$browser" "$url" >/dev/null 2>&1 &
    fi
    opened=1
    nexus_log "INFO" "panel-browser" "FIELD_WINDOW_OPENED url=${url} via=${browser}"
    return 0
  done < <(nexus_panel_detect_browsers)

  [[ "$opened" -eq 1 ]]
}

nexus_panel_open_help() {
  local url="${1:-$(nexus_panel_url)}"
  cat <<EOF
NEXUS panel URL: ${url}

Browser could not be opened automatically. Try one of these:

  xdg-open '${url}'
  firefox '${url}'
  google-chrome-stable '${url}'

Or use the CLI (no browser needed):

  nexus status
  nexus connections
  nexus trust <ip> [label]
  nexus block <ip> [--forever]
  nexus unblock <ip>

If the panel is offline:

  sudo systemctl start nexus-genius.service
  nexus panel --wait
EOF
}