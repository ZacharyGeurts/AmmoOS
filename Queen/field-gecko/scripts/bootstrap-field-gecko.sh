#!/usr/bin/env bash
# Bootstrap stripped Field Gecko from Mozilla Firefox source (MPL 2.0).
# Does not download unless --fetch is passed. Documents g16 build lane.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUEEN="$(cd "${ROOT}/.." && pwd)"
SG="$(cd "${QUEEN}/../.." && pwd)"
GROK16="${GROK16_ROOT:-${SG}/Grok16}"
TAG="${1:-FIREFOX_ESR_128_BASE}"
FETCH=0
[[ "${1:-}" == "--fetch" ]] && FETCH=1 && TAG="${2:-FIREFOX_ESR_128_BASE}"

SRC="${ROOT}/vendor/mozilla"
BUILD="${ROOT}/build"

cat <<EOF
Queen Field Gecko bootstrap
  Source tag: ${TAG}
  Vendor dir: ${SRC}
  g16 root:   ${GROK16}
  License:    MPL-2.0 — offer corresponding source on distribution

Strip goals (AI operator):
  - Telemetry / Normandy / Pocket off at compile where possible
  - Single-window kiosk to Queen Webbrowser shell
  - g16 toolchain for engine compile (future): QUEEN_FIELD_GECKO_BUILD=1

EOF

if [[ "${FETCH}" != "1" ]]; then
  echo "Dry run. To clone Mozilla source:"
  echo "  $0 --fetch ${TAG}"
  echo "Then configure with Mozilla ./mach bootstrap and wire g16 in build/mozconfig."
  exit 0
fi

mkdir -p "${ROOT}/vendor"
if [[ ! -d "${SRC}/.git" ]]; then
  git clone --depth 1 --branch "${TAG}" https://github.com/mozilla-firefox/firefox.git "${SRC}"
fi

mkdir -p "${BUILD}"
cat >"${BUILD}/mozconfig.queen" <<MOZ
# Queen Field Gecko — stripped operator build (template)
ac_add_options --enable-application=browser
ac_add_options --disable-telemetry
ac_add_options --disable-default-browser-agent
ac_add_options --disable-maintenance-service
# Wire g16: export CC CXX from Grok16 after mach bootstrap
MOZ

echo "Cloned to ${SRC}. Next: cd ${SRC} && ./mach bootstrap && mach build"