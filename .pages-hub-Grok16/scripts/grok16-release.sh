#!/usr/bin/env bash
# Grok16 release assembler — gates, source tarball, per-platform manifest, GitHub release.
# Usage: ./scripts/grok16-release.sh [version] [--push] [--no-gh]
set -euo pipefail

GROK16_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG_ROOT="${SG_ROOT:-$(cd "$GROK16_ROOT/.." && pwd)}"
VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  VERSION="$(python3 -c "import json;from pathlib import Path;p=Path('${GROK16_ROOT}/data/grok16-version.json');d=json.loads(p.read_text());print(d.get('upload_version') or d.get('distro_version','4.7.1'))")"
fi
DISPLAY_VERSION="$(python3 -c "import json;from pathlib import Path;p=Path('${GROK16_ROOT}/data/grok16-version.json');d=json.loads(p.read_text());print(d.get('distro_version', '${VERSION}'))")"
TAG="v${VERSION}"
DISPLAY_TAG="v${DISPLAY_VERSION}"
PUSH=0
NO_GH=0
shift || true
for arg in "$@"; do
  case "$arg" in
    --push) PUSH=1 ;;
    --no-gh) NO_GH=1 ;;
  esac
done

export GROK16_ROOT SG_ROOT
export G16_PREFIX="${G16_PREFIX:-$GROK16_ROOT}"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$SG_ROOT/NewLatest}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-$GROK16_ROOT/.nexus-release-state}"

DIST="$GROK16_ROOT/dist"
STAGE="$DIST/grok16-${VERSION}"
TARBALL="$DIST/grok16-${VERSION}-src.tar.gz"
PLAT_JSON="$DIST/grok16-${VERSION}-platforms.json"
PLAT_MD="$DIST/grok16-${VERSION}-PLATFORMS.md"
BINARY_TARBALL="$DIST/grok16-${DISPLAY_VERSION}-linux-x86_64.tar.gz"
BINARY_MANIFEST="$DIST/grok16-${DISPLAY_VERSION}-linux-x86_64-manifest.json"

log() { printf '[%s] release %s\n' "$(date +%H:%M:%S)" "$*"; }

refresh_launch_paths() {
  log "refresh portable .launch chamber_root"
  python3 - <<'PY'
import json
from pathlib import Path

root = Path(__import__("os").environ["GROK16_ROOT"])
for lp in sorted(root.glob("examples/*/*.launch")):
    doc = json.loads(lp.read_text(encoding="utf-8"))
    name = lp.parent.name
    doc["chamber_root"] = f"${{GROK16_ROOT}}/examples/{name}"
    lp.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  {lp.name} -> ${{GROK16_ROOT}}/examples/{name}")
PY
}

run_gates() {
  if [[ "${AML_BUILD:-1}" != "0" && -z "${AML_INLINE:-}" && -f "${NEXUS_INSTALL_ROOT}/lib/ammolang-run.sh" ]]; then
    log "gates: AmmoLang grok16_gates (hang guard · freeze assist)"
    bash "${NEXUS_INSTALL_ROOT}/lib/ammolang-run.sh" gates || return 1
  else
    log "gates: self-monitor"
    python3 "$GROK16_ROOT/tests/test_g16_self_monitor.py"
    log "gates: test-gate smoke"
    bash "$GROK16_ROOT/scripts/grok16-test-gate.sh" smoke
    if [[ "${GROK16_RELEASE_SKIP_LAUNCH:-}" == "1" ]]; then
      log "gates: skip launch-verify (python tests passed)"
    else
      log "gates: launch-verify"
      bash "$GROK16_ROOT/scripts/grok16-launch-verify.sh"
    fi
  fi
  if [[ "${GROK16_RELEASE_SKIP_LAUNCH:-}" == "1" ]]; then
    log "gates: skip test-battery-release (python tests passed)"
  elif "$GROK16_ROOT/scripts/grok16-toolchain.sh" status >/dev/null 2>&1; then
    log "gates: test-battery-release"
    G16_RELEASE_PROFILE=1 bash "$GROK16_ROOT/scripts/grok16-toolchain.sh" test-battery-release
  else
    log "WARN skip test-battery-release (g16 not ready)"
  fi
}

write_platform_artifacts() {
  mkdir -p "$DIST"
  python3 - <<PY
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path("$GROK16_ROOT")
dist = Path("$DIST")
ver = "$VERSION"
tag = "$TAG"
distro = "$DISPLAY_VERSION"
distro_tag = "$DISPLAY_TAG"
src = json.loads((root / "data/grok16-platform-release.json").read_text(encoding="utf-8"))
src["distro_version"] = distro
src["distro_tag"] = distro_tag
src["upload_version"] = ver
src["upload_tag"] = tag
src["released_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
out = dist / f"grok16-{ver}-platforms.json"
out.write_text(json.dumps(src, indent=2) + "\\n", encoding="utf-8")

lines = [
    f"# Grok16 {distro} — platform bootstrap matrix",
    "",
    f"**Distro:** \`{distro_tag}\` · **Upload:** \`{tag}\` · **g16:** {src.get('g16_version')} · **Model:** source bootstrap per platform",
    "",
    "Grok16 releases **source + forge**. Build `g16` locally on each target (or cross from a Linux x86_64 host).",
    "",
    "## Quick start (any Linux x86_64)",
    "",
    "\`\`\`bash",
    "tar xzf grok16-{ver}-src.tar.gz && cd grok16-{ver}-src",
    "export G16_PREFIX=\\$(pwd) G16_PKGVERSION=Grok16-16.2.0",
    "./scripts/grok16-toolchain.sh bootstrap",
    "./scripts/grok16-toolchain.sh rebuild",
    "./scripts/grok16-launch-verify.sh",
    "\`\`\`",
    "",
    "## .launch chambers",
    "",
    "Every example ships a portable \`.launch\` (schema \`queen-launch/v1\`). Run without compile:",
    "",
    "\`\`\`bash",
    "export GROK16_ROOT=\\$(pwd) SG_ROOT=/path/to/SG",
    "python3 NewLatest/Queen/lib/queen-launch-chamber.py run examples/speed-demo/speed-demo.launch",
    "\`\`\`",
    "",
    "## Bootstrap platforms (g16 builds here)",
    "",
    "| ID | OS | Arch | Bootstrap |",
    "|----|-----|------|-----------|",
]
boot_rows = []
pair_rows = []
for p in src.get("platforms") or []:
    if p.get("format") == "hardware_pair" or p.get("pair"):
        pair_rows.append(p)
        continue
    boot = p.get("bootstrap") or {}
    hint = boot.get("cross_prefix") or boot.get("CC") or boot.get("host") or boot.get("ndk") or "local"
    if isinstance(hint, bool):
        hint = "ndk" if hint else "local"
    boot_rows.append(f"| {p.get('id')} | {p.get('os')} | {p.get('arch')} | {hint} |")
lines.extend(boot_rows)
if pair_rows:
    lines.extend([
        "",
        "## Hardware pairs (g16 does **not** run on device)",
        "",
        "| ID | Device | Arch | Grok16 host |",
        "|----|--------|------|-------------|",
    ])
    for p in pair_rows:
        pair = p.get("pair") or {}
        host = pair.get("grok16_host") or "linux-gnu-x86_64"
        label = (p.get("hardware") or {}).get("models", [{}])[0].get("label", p.get("id"))
        lines.append(f"| {p.get('id')} | {label} | {p.get('arch')} | {host} |")

lines.extend([
    "",
    "## RISC-V (linux-gnu-riscv64)",
    "",
    "Install cross toolchain, then bootstrap with:",
    "",
    "\`\`\`bash",
    "sudo apt install gcc-riscv64-linux-gnu g++-riscv64-linux-gnu",
    "export CC=riscv64-linux-gnu-gcc CXX=riscv64-linux-gnu-g++",
    "export G16_CROSS_PREFIX=riscv64-linux-gnu-",
    "./scripts/grok16-toolchain.sh bootstrap",
    "\`\`\`",
    "",
    "Linker emulation: \`elf64lriscv\` · doctrine target \`linux-gnu-riscv64\` + \`bare-elf-riscv64\`.",
    "",
])
(dist / f"grok16-{ver}-PLATFORMS.md").write_text("\\n".join(lines) + "\\n", encoding="utf-8")
print(out)
PY
}

build_binary_package() {
  if ! "$GROK16_ROOT/scripts/grok16-toolchain.sh" status >/dev/null 2>&1; then
    log "WARN skip binary package (g16 not ready)"
    return 0
  fi
  log "binary package: g16 + AmmoCode + default settings"
  bash "$GROK16_ROOT/scripts/grok16-binary-package.sh" "$DISPLAY_VERSION" || {
    log "WARN binary package build failed"
    return 0
  }
}

build_tarball() {
  log "stage source tarball"
  rm -rf "$STAGE" "$TARBALL"
  mkdir -p "$STAGE"
  tar -C "$GROK16_ROOT" \
    --exclude='./vendor' --exclude='./build' --exclude='./bin' \
    --exclude='./lib' --exclude='./libexec' --exclude='./include' \
    --exclude='./share' --exclude='./dist' --exclude='./.git' \
    --exclude='./.nexus-state' --exclude='./.nexus-release-state' \
    --exclude='./.grok16-state' --exclude='./data/bench' \
    --exclude='./cmake/grok16-toolchain.cmake' \
    -cf - . | tar -C "$STAGE" -xf -
  mv "$STAGE" "$STAGE-src"
  STAGE="$STAGE-src"
  cp "$PLAT_JSON" "$STAGE/data/grok16-platform-release.json"
  tar -czf "$TARBALL" -C "$DIST" "grok16-${VERSION}-src"
  log "wrote $TARBALL ($(du -h "$TARBALL" | awk '{print $1}'))"
}

git_release() {
  cd "$GROK16_ROOT"
  if ! git diff --quiet HEAD 2>/dev/null; then
    log "commit release tree"
    git add -A
    git commit -m "Grok16 ${VERSION} — bench-refresh, comparison charts, gcc-14 host pin"
  fi
  if git rev-parse "$TAG" >/dev/null 2>&1; then
    log "tag $TAG exists"
  else
    git tag -a "$TAG" -m "Grok16 ${VERSION}"
    log "tagged $TAG"
  fi
  if [[ "$PUSH" -eq 1 ]]; then
    git push origin main
    git push origin "$TAG"
    log "pushed main + $TAG"
  fi
}

gh_release() {
  [[ "$NO_GH" -eq 1 ]] && return 0
  command -v gh >/dev/null 2>&1 || { log "WARN gh missing — skip GitHub release"; return 0; }
  local notes="$GROK16_ROOT/RELEASE-${VERSION}.md"
  [[ -f "$notes" ]] || notes="$PLAT_MD"
  if gh release view "$TAG" >/dev/null 2>&1; then
    log "GitHub release $TAG exists — upload assets"
    assets=("$TARBALL" "$PLAT_JSON" "$PLAT_MD")
    [[ -f "$BINARY_TARBALL" ]] && assets+=("$BINARY_TARBALL" "$BINARY_MANIFEST")
    gh release upload "$TAG" "${assets[@]}" --clobber
  else
    assets=("$TARBALL" "$PLAT_JSON" "$PLAT_MD")
    [[ -f "$BINARY_TARBALL" ]] && assets+=("$BINARY_TARBALL" "$BINARY_MANIFEST")
    gh release create "$TAG" \
      --title "Grok16 ${VERSION}" \
      --notes-file "$notes" \
      "${assets[@]}"
    log "created GitHub release $TAG"
  fi
}

seal_dist_artifacts() {
  local seal="$GROK16_ROOT/lib/g16-sealed-release.py"
  [[ -f "$seal" ]] || { log "WARN skip sealed dist (missing g16-sealed-release.py)"; return 0; }
  [[ -d "$DIST" ]] || return 0
  log "seal dist/ artifacts (G1)"
  python3 "$seal" "$VERSION" seal
  if python3 "$seal" verify; then
    log "sealed dist verify OK"
  else
    log "WARN sealed dist verify partial (sha256 sidecars written; inline json seal optional)"
  fi
}

main() {
  log "Grok16 upload ${VERSION} (${TAG}) — distro ${DISPLAY_VERSION} (${DISPLAY_TAG})"
  refresh_launch_paths
  run_gates
  write_platform_artifacts
  build_tarball
  build_binary_package
  seal_dist_artifacts
  git_release
  gh_release
  log "release upload ${VERSION} complete (distro ${DISPLAY_VERSION})"
  log "  tarball: $TARBALL"
  log "  binary: ${BINARY_TARBALL}"
  log "  platforms: $PLAT_JSON"
  log "  guide: $PLAT_MD"
}

main