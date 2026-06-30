#!/usr/bin/env bash
# ZNetwork release — gates, source tarball, platform packs, GitHub.
# Usage: ./scripts/znetwork-release.sh [version] [--push]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG_ROOT="${SG_ROOT:-$(cd "$ROOT/.." && pwd)}"
VERSION="${1:-2.1.0}"
TAG="v${VERSION}"
PUSH=0
shift || true
for arg in "$@"; do [[ "$arg" == "--push" ]] && PUSH=1; done

DIST="$ROOT/dist"
SRC_TAR="$DIST/znetwork-${VERSION}-src.tar.gz"
PLAT_MD="$DIST/znetwork-${VERSION}-PLATFORMS.md"
NOTES="$ROOT/RELEASE-${VERSION}.md"

log() { printf '[%s] znetwork-release %s\n' "$(date +%H:%M:%S)" "$*"; }

run_gates() {
  log "gates: build host"
  bash "$ROOT/scripts/znetwork-build-host.sh"
  log "gates: test battery"
  bash "$ROOT/scripts/znetwork-test-battery.sh" 2>&1 | tail -15
}

write_platforms_md() {
  python3 - <<PY
import json
from pathlib import Path
root = Path("$ROOT")
dist = Path("$DIST")
ver = "$VERSION"
data = json.loads((root / "data/znetwork-platform-release.json").read_text())
lines = [
    f"# ZNetwork {ver} — platform matrix",
    "",
    f"**Tag:** \`v{ver}\` · **Canonical:** NewLatest/ZNetwork · **Grok16:** {data.get('grok16_pair')}",
    "",
    "| Platform | OS | Arch | Binary |",
    "|----------|-----|------|--------|",
]
for p in data.get("platforms", []):
    lines.append(f"| {p['id']} | {p['os']} | {p['arch']} | {p.get('build', 'cmake')} |")
(dist / f"znetwork-{ver}-PLATFORMS.md").write_text("\\n".join(lines) + "\\n")
PY
}

build_tarball() {
  rm -f "$SRC_TAR"
  mkdir -p "$DIST"
  tar -C "$ROOT" --exclude='./dist' --exclude='./build' --exclude='./.lab-state' --exclude='./.git' \
    -czf "$SRC_TAR" .
  log "wrote $SRC_TAR ($(du -h "$SRC_TAR" | awk '{print $1}'))"
}

git_release() {
  cd "$ROOT"
  [[ -d .git ]] || git init -b main
  git config user.email "gzac5314@users.noreply.github.com" 2>/dev/null || true
  git config user.name "ZacharyGeurts" 2>/dev/null || true
  git add -A
  git diff --cached --quiet || git commit -m "ZNetwork ${VERSION} Stack — NewLatest canonical"
  git tag -a "$TAG" -m "ZNetwork ${VERSION}" 2>/dev/null || git tag -f "$TAG" -m "ZNetwork ${VERSION}"
  if [[ "$PUSH" -eq 1 ]]; then
    REMOTE="https://github.com/ZacharyGeurts/ZNetwork.git"
    gh repo view ZacharyGeurts/ZNetwork >/dev/null 2>&1 || \
      gh repo create ZNetwork --public --description "ZNetwork smart relayer — field stack pipe on loopback"
    git remote remove origin 2>/dev/null || true
    git remote add origin "$REMOTE"
    git push -u origin main --force
    git push origin "$TAG" --force
  fi
}

gh_release() {
  [[ "$PUSH" -eq 0 ]] && return 0
  local assets=("$SRC_TAR" "$PLAT_MD" "$ROOT/data/znetwork-version.json" "$ROOT/data/znetwork-platform-release.json")
  for a in "$DIST"/znetwork-${VERSION}-linux-gnu-*.tar.gz "$DIST"/znetwork-${VERSION}-win32-*.tar.gz; do
    [[ -f "$a" ]] && assets+=("$a")
  done
  if gh release view "$TAG" >/dev/null 2>&1; then
    gh release edit "$TAG" --title "ZNetwork ${VERSION} — Stack" --notes-file "$NOTES"
    gh release upload "$TAG" "${assets[@]}" --clobber 2>/dev/null || true
  else
    gh release create "$TAG" --title "ZNetwork ${VERSION} — Stack" --notes-file "$NOTES" "${assets[@]}"
  fi
}

main() {
  log "ZNetwork ${VERSION} (${TAG})"
  run_gates
  bash "$ROOT/scripts/znetwork-pack-platform.sh" "$VERSION"
  write_platforms_md
  build_tarball
  git_release
  gh_release
  log "release ${VERSION} complete"
}

main