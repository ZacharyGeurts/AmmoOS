#!/usr/bin/env bash
# NXF installer — compact GitHub-driven install/update (replaces legacy wizard paths).
set -euo pipefail

_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${_LIB}/.." && pwd)"
MODE="portable"
FROM_GITHUB=0
NXF_FILE=""
TARGET_VERSION=""

usage() {
  cat <<'EOF'
NEXUS Field NXF installer

  ./install.sh                    Portable (no sudo)
  ./install.sh --system           Full system install (one admin approval)
  ./install-remote.sh             Fetch latest.nxf from GitHub, install portable
  ./lib/nxf-install.sh --from-github [--mode system|portable]

NXF manifest: nxf/latest.nxf — version, tarball URLs, entry scripts.
Update: Queen browser UPDATE button or panel INSTALL UPDATE when online.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --system|--full|-s) MODE="system" ;;
    --portable|-p) MODE="portable" ;;
    --from-github|--github|-g) FROM_GITHUB=1 ;;
    --nxf) NXF_FILE="${2:-}"; shift ;;
    --version) TARGET_VERSION="${2:-}"; shift ;;
    *) echo "Unknown arg: $1" >&2; usage >&2; exit 1 ;;
  esac
  shift
done

# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-common.sh"
nexus_init_runtime_paths 2>/dev/null || true
# shellcheck source=/dev/null
source "${ROOT}/lib/installer.sh"

if ! nexus_install_check_deps; then
  echo "Install python3 and curl, then re-run." >&2
  exit 1
fi

_resolve_pythong() {
  if command -v pythong >/dev/null 2>&1; then
    command -v pythong
    return 0
  fi
  command -v python3
}

PY="$(_resolve_pythong)"
STAGING="${NEXUS_STATE_DIR:-${ROOT}/.nexus-state}/nxf-staging"
mkdir -p "$STAGING"

_fetch_nxf() {
  local dest="$1"
  if [[ -n "$NXF_FILE" && -f "$NXF_FILE" ]]; then
    cp -f "$NXF_FILE" "$dest"
    return 0
  fi
  if [[ -f "${ROOT}/nxf/latest.nxf" && "$FROM_GITHUB" != "1" ]]; then
    cp -f "${ROOT}/nxf/latest.nxf" "$dest"
    return 0
  fi
  local repo url ver
  repo="${NEXUS_GITHUB_REPO:-ZacharyGeurts/NEXUS-Shield}"
  if [[ -n "$TARGET_VERSION" ]]; then
    ver="${TARGET_VERSION#v}"
    url="https://github.com/${repo}/releases/download/v${ver}/nexus-shield-${ver}.nxf"
    curl -fsSL --retry 3 -o "$dest" "$url" 2>/dev/null && return 0
  fi
  for url in \
    "https://github.com/${repo}/releases/latest/download/latest.nxf" \
    "https://raw.githubusercontent.com/${repo}/main/nxf/latest.nxf"; do
    if curl -fsSL --retry 3 -o "$dest" "$url" 2>/dev/null; then
      return 0
    fi
  done
  if [[ -f "${ROOT}/nxf/latest.nxf" ]]; then
    cp -f "${ROOT}/nxf/latest.nxf" "$dest"
    return 0
  fi
  echo "BLOCKER: could not fetch NXF manifest from GitHub" >&2
  return 1
}

_read_nxf_field() {
  local nxf="$1" field="$2"
  "$PY" -c "
import json, sys
doc = json.load(open(sys.argv[1], encoding='utf-8'))
keys = sys.argv[2].split('.')
val = doc
for k in keys:
    val = val.get(k) if isinstance(val, dict) else None
    if val is None:
        break
print(val or '')
" "$nxf" "$field"
}

_download_pack() {
  local url="$1" dest="$2"
  echo "NXF download: $url"
  curl -fsSL --retry 3 --retry-delay 2 -o "$dest" "$url"
}

_extract_source() {
  local archive="$1" dest="$2"
  mkdir -p "$dest"
  tar -xzf "$archive" -C "$dest"
  local found ver
  found="$(find "$dest" -maxdepth 2 -name install-all.sh -print -quit 2>/dev/null || true)"
  if [[ -n "$found" ]]; then
    dirname "$found"
    return 0
  fi
  ver="$(_read_nxf_field "$NXF_MANIFEST" version)"
  for c in "${dest}/nexus-shield-${ver}" "${dest}/nexus-shield-v${ver}"; do
    [[ -f "${c}/install-all.sh" ]] && printf '%s' "$c" && return 0
  done
  return 1
}

_install_tree() {
  local tree="$1"
  export NEXUS_INSTALL_SRC="$tree"
  export SG_ROOT="${SG_ROOT:-$tree}"
  case "$MODE" in
    system)
      export NEXUS_INSTALL_ROOT=/usr/local/lib/nexus-shield
      export NEXUS_STATE_DIR=/var/lib/nexus-shield
      # shellcheck source=/dev/null
      source "${tree}/lib/nexus-elevate.sh"
      nexus_elevate_acquire "${tree}/install-all.sh"
      bash "${tree}/genius_shield.sh"
      ;;
    portable)
      nexus_install_portable "$tree"
      ;;
  esac
}

NXF_MANIFEST="${STAGING}/active.nxf"
_fetch_nxf "$NXF_MANIFEST"

VER="$(_read_nxf_field "$NXF_MANIFEST" version)"
TAG="$(_read_nxf_field "$NXF_MANIFEST" tag)"
SOURCE_URL="$(_read_nxf_field "$NXF_MANIFEST" pack.source.url)"
ENTRY="$(_read_nxf_field "$NXF_MANIFEST" entry)"

echo "=== NEXUS NXF install (${MODE}) v${VER} (${TAG}) ==="

if [[ "$FROM_GITHUB" == "1" || ! -f "${ROOT}/${ENTRY}" ]]; then
  [[ -n "$SOURCE_URL" ]] || { echo "NXF missing pack.source.url" >&2; exit 1; }
  ARCHIVE="${STAGING}/nexus-shield-${VER}-source.tar.gz"
  _download_pack "$SOURCE_URL" "$ARCHIVE"
  EXTRACT="${STAGING}/tree-${VER}"
  rm -rf "$EXTRACT"
  TREE="$(_extract_source "$ARCHIVE" "$EXTRACT")" || {
    echo "Extract failed — install-all.sh not found" >&2
    exit 1
  }
  cp -f "$NXF_MANIFEST" "${TREE}/nxf/latest.nxf" 2>/dev/null || mkdir -p "${TREE}/nxf" && cp -f "$NXF_MANIFEST" "${TREE}/nxf/latest.nxf"
  _install_tree "$TREE"
else
  cp -f "$NXF_MANIFEST" "${ROOT}/nxf/latest.nxf" 2>/dev/null || mkdir -p "${ROOT}/nxf" && cp -f "$NXF_MANIFEST" "${ROOT}/nxf/latest.nxf"
  _install_tree "$ROOT"
fi

IMPORTS="${NEXUS_STATE_DIR:-${ROOT}/.nexus-state}/imports"
mkdir -p "$IMPORTS"
chmod 700 "${NEXUS_STATE_DIR:-${ROOT}/.nexus-state}" 2>/dev/null || true
chmod 700 "$IMPORTS" 2>/dev/null || true

if [[ -f "${ROOT}/Queen/scripts/queen-icon-kit.py" ]]; then
  python3 "${ROOT}/Queen/scripts/queen-icon-kit.py" >/dev/null 2>&1 \
    || pythong "${ROOT}/Queen/scripts/queen-icon-kit.py" >/dev/null 2>&1 || true
fi
if [[ -x "${ROOT}/Queen/scripts/queen-browser-primary.sh" ]]; then
  bash "${ROOT}/Queen/scripts/queen-browser-primary.sh" >/dev/null 2>&1 || true
fi

echo ""
echo "=== NXF install complete ==="
echo "Queen browser: http://127.0.0.1:9481/world/browser.html"
echo "NEXUS panel:   http://127.0.0.1:9477/field"
echo "Launcher:      ./nexus.sh  or  ./Queen/scripts/run-queen.sh"
echo "Import drop:   ${IMPORTS}/  (bookmarks.html · passwords.csv)"
echo "Report:        ${NEXUS_STATE_DIR:-${ROOT}/.nexus-state}/install-report.json"