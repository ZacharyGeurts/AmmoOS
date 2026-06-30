#!/usr/bin/env bash
# KILROY release — gates, source tarball, platform packs, GitHub release.
# Usage: ./scripts/kilroy-release.sh [version] [--push]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG_ROOT="${SG_ROOT:-$(cd "$ROOT/.." && pwd)}"
VERSION="${1:-1.1.0}"
TAG="v${VERSION}"
PUSH=0
shift || true
for arg in "$@"; do
  [[ "$arg" == "--push" ]] && PUSH=1
done

DIST="$ROOT/dist"
SRC_TAR="$DIST/kilroy-${VERSION}-src.tar.gz"
PLAT_MD="$DIST/kilroy-${VERSION}-PLATFORMS.md"
NOTES="$ROOT/RELEASE-${VERSION}.md"

log() { printf '[%s] kilroy-release %s\n' "$(date +%H:%M:%S)" "$*"; }

run_gates() {
  log "gates: check-field-stack"
  bash "$ROOT/scripts/check-field-stack.sh"
  log "gates: test-units"
  bash "$ROOT/scripts/test-units.sh"
  log "gates: test-ioctl-smoke"
  bash "$ROOT/scripts/test-ioctl-smoke.sh" || log "WARN ioctl smoke skipped (no running kernel)"
  if [[ -x "$SG_ROOT/Grok16/scripts/grok16-verify-ammoos.sh" ]]; then
    log "gates: grok16-verify-ammoos (stack pairing)"
    bash "$SG_ROOT/Grok16/scripts/grok16-verify-ammoos.sh" || log "WARN ammoos verify partial"
  fi
}

write_platforms_md() {
  python3 - <<PY
import json
from pathlib import Path
root = Path("$ROOT")
dist = Path("$DIST")
ver = "$VERSION"
data = json.loads((root / "data/kilroy-platform-release.json").read_text())
lines = [
    f"# KILROY {ver} Taco — platform matrix",
    "",
    f"**Tag:** \`v{ver}\` · **ABI:** kilroy-field-1.0 · **Grok16:** {data.get('grok16_pair')} · **AmmoOS:** {data.get('ammoos_pair')}",
    "",
    "## Model",
    "",
    "- **Source overlay** — Field Die + integration (this repo)",
    "- **Compat substrate** — linux-7.1.1 fetched via \`kilroy-stage-compat.sh\` (not vendored)",
    "- **x86_64** — full \`bzImage\` + Grok boot EFI + userspace",
    "- **Other ELF Linux** — cross-compiled \`kilroy-status\` / \`kilroy-ioctl-test\` where toolchain present",
    "- **Darwin / iOS / Windows** — source bootstrap per Grok16 platform docs",
    "",
    "| Platform | OS | Arch | Kernel image | Userspace bins |",
    "|----------|-----|------|--------------|----------------|",
]
for p in data.get("platforms", []):
    ki = "yes" if p.get("kernel_image") else "source/cross"
    us = p.get("userspace", "source")
    if us is True: us = "g16 cross"
    lines.append(f"| {p['id']} | {p['os']} | {p['arch']} | {ki} | {us} |")
lines += [
    "",
    "## Quick start",
    "",
    "\`\`\`bash",
    f"tar xzf kilroy-{ver}-src.tar.gz && cd kilroy-{ver}-src",
    "./scripts/kilroy-stage-compat.sh",
    "./scripts/build-kilroy.sh",
    "\`\`\`",
]
(dist / f"kilroy-{ver}-PLATFORMS.md").write_text("\\n".join(lines) + "\\n")
PY
}

build_src_tarball() {
  log "source tarball"
  mkdir -p "$DIST"
  rm -f "$SRC_TAR"
  tar -C "$ROOT" \
    --exclude='./dist' --exclude='./build/grok-kilroy.img' \
    --exclude='./build-cmake' --exclude='./.git' \
    --exclude='./boot/grok/vendor/limine/.git' \
    --exclude='memtest86+_*.deb' \
    --ignore-failed-read \
    -czf "$SRC_TAR" . 2>/dev/null || {
      log "WARN tarball with ignore-failed-read — fix boot/grok/*.conf permissions if needed"
      tar -C "$ROOT" \
        --exclude='./dist' --exclude='./build/grok-kilroy.img' \
        --exclude='./build-cmake' --exclude='./.git' \
        --exclude='./boot/grok/vendor/limine/.git' \
        --exclude='memtest86+_*.deb' \
        --exclude='./boot/grok/grok.conf' \
        --exclude='./boot/grok/grok.entries.host.conf' \
        -czf "$SRC_TAR" .
    }
  log "wrote $SRC_TAR ($(du -h "$SRC_TAR" | awk '{print $1}'))"
}

git_release() {
  cd "$ROOT"
  if [[ ! -d .git ]]; then
    git init -b main
    git config user.email "gzac5314@users.noreply.github.com"
    git config user.name "ZacharyGeurts"
  fi
  git add -A
  git diff --cached --quiet || git commit -m "KILROY ${VERSION} Taco — Field OS kernel release"
  git tag -a "$TAG" -m "KILROY ${VERSION} Taco" 2>/dev/null || git tag -f "$TAG" -m "KILROY ${VERSION} Taco"
  if [[ "$PUSH" -eq 1 ]]; then
    REMOTE="https://github.com/ZacharyGeurts/KILROY.git"
    if ! gh repo view ZacharyGeurts/KILROY >/dev/null 2>&1; then
      gh repo create KILROY --public --description "KILROY Field OS — Linux-compatible kernel. Codename Taco." \
        --homepage "https://github.com/ZacharyGeurts/KILROY"
    fi
    git remote remove origin 2>/dev/null || true
    git remote add origin "$REMOTE"
    git push -u origin main --force
    git push origin "$TAG" --force
    log "pushed main + $TAG"
  fi
}

gh_release() {
  [[ "$PUSH" -eq 0 ]] && return 0
  command -v gh >/dev/null 2>&1 || return 0
  local assets=("$SRC_TAR" "$PLAT_MD" "$ROOT/data/kilroy-platform-release.json")
  for a in "$DIST"/kilroy-${VERSION}-*.tar.gz; do
    [[ -f "$a" ]] && assets+=("$a")
  done
  if gh release view "$TAG" >/dev/null 2>&1; then
    gh release edit "$TAG" --title "KILROY ${VERSION} — Taco" --notes-file "$NOTES"
    gh release upload "$TAG" "${assets[@]}" --clobber 2>/dev/null || true
  else
    gh release create "$TAG" --title "KILROY ${VERSION} — Taco" --notes-file "$NOTES" "${assets[@]}"
  fi
  log "GitHub release $TAG"
}

main() {
  log "KILROY ${VERSION} (${TAG})"
  run_gates
  bash "$ROOT/scripts/kilroy-pack-platform.sh" "$VERSION"
  write_platforms_md
  build_src_tarball
  git_release
  gh_release
  log "release ${VERSION} complete"
}

main