#!/usr/bin/env bash
# Publish stack Pages — AmmoOS manual is canonical; siblings get redirect hubs only.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VER="${STACK_VERSION:-2.0.0-beta3.1}"
GROK_VER="${GROK16_VERSION:-5.2.0}"

log() { echo "==> $*"; }

log "AmmoOS manual (canonical) → gh-pages"
bash "${ROOT}/scripts/publish-ammoos-pages.sh" --version "$VER"

log "Stack redirect hubs → sibling repos link to AmmoOS manual"
AMMOOS_VERSION="$VER" bash "${ROOT}/scripts/publish-ammoos-hub-pages.sh"

log "Profile stack hub → ZacharyGeurts/docs (links to AmmoOS pages)"
bash "${ROOT}/scripts/publish-profile-pages.sh"

if [[ -d "${ROOT}/Grok16" ]]; then
  log "Grok16 wiki source (no duplicate manual — hub points to AmmoOS)"
  (cd "${ROOT}/Grok16" && bash scripts/publish-wiki.sh "$GROK_VER") || true
fi

log "AmmoOS wiki"
AMMOOS_VERSION="$VER" bash "${ROOT}/scripts/publish-ammoos-wiki.sh" || true

log "Stack companion releases (link back to AmmoOS code)"
STACK_VERSION="$VER" bash "${ROOT}/scripts/publish-stack-releases.sh" || true

log "done — canonical manual + hubs:"
echo "  https://zacharygeurts.github.io/AmmoOS/"
echo "  https://zacharygeurts.github.io/AmmoOS/stack-hub.html"
echo "  https://zacharygeurts.github.io/Queen/  → redirects to AmmoOS manual"
echo "  https://zacharygeurts.github.io/Grok16/  → redirects to AmmoOS manual"
echo "  https://zacharygeurts.github.io/ZacharyGeurts/stack.html"