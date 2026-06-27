#!/usr/bin/env bash
# Pack AmmoOS beta archives for all platform families.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-common.sh"

AMMOOS_VERSION="${AMMOOS_VERSION:-1.0.1-beta}"
VER="${AMMOOS_VERSION}"
DIST="${ROOT}/dist"
STAGE="${DIST}/ammoos-${VER}"
PKG_NAME="ammoos-${VER}-source.tar.gz"
INST_NAME="ammoos-${VER}-installers.tar.gz"
WIN_NAME="ammoos-${VER}-windows-x86_64.zip"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -v|--version) VER="$2"; shift 2 ;;
    *) echo "unknown: $1" >&2; exit 1 ;;
  esac
done

mkdir -p "$DIST"
rm -rf "$STAGE"
mkdir -p "$STAGE"

echo "=== staging AmmoOS ${VER} ==="
rsync -a \
  --exclude='.git' \
  --exclude='.nexus-state' \
  --exclude='.nexus-state-test' \
  --exclude='dist' \
  --exclude='cache' \
  --exclude='state' \
  --exclude='Hostess7/cache' \
  --exclude='Hostess7/zac' \
  --exclude='Queen/vendor' \
  --exclude='Queen/cache' \
  --exclude='Queen/.venv*' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='*.log' \
  --exclude='*.jsonl' \
  --exclude='.wiki-publish' \
  --exclude='.pages-publish' \
  --exclude='.github/workflows/ci.yml' \
  --exclude='.github/workflows/release-v10.yml' \
  --exclude='Hostess7/.github' \
  "${ROOT}/" "${STAGE}/"

# AmmoOS branding at export root
if [[ -f "${STAGE}/README-AMMOOS.md" ]]; then
  cp "${STAGE}/README-AMMOOS.md" "${STAGE}/README.md"
fi

echo "=== source tarball ==="
tar -czf "${DIST}/${PKG_NAME}" -C "${DIST}" "ammoos-${VER}"

echo "=== installers tarball ==="
INSTALL_STAGE="${DIST}/ammoos-${VER}-installers"
rm -rf "$INSTALL_STAGE"
mkdir -p "$INSTALL_STAGE/scripts"
for f in install-all.sh genius_shield.sh nexus.sh stealth_install.sh install.sh stealth.ps1 INSTALL-README.md assets/nexus-field.png README.md; do
  [[ -f "${STAGE}/${f}" ]] && cp "${STAGE}/${f}" "$INSTALL_STAGE/"
done
cp -a "${STAGE}/scripts/ammoos-"*.sh "${STAGE}/scripts/pack-ammoos-release.sh" \
  "${STAGE}/scripts/wire-stack.sh" "${STAGE}/scripts/nexus-boot-impl.sh" \
  "$INSTALL_STAGE/scripts/" 2>/dev/null || true
[[ -d "${STAGE}/install" ]] && cp -a "${STAGE}/install/." "$INSTALL_STAGE/install/"
tar -czf "${DIST}/${INST_NAME}" -C "${DIST}" "ammoos-${VER}-installers"

if command -v zip >/dev/null 2>&1 && [[ -f "${STAGE}/stealth.ps1" ]]; then
  echo "=== windows zip ==="
  WIN_STAGE="${DIST}/ammoos-${VER}-windows"
  rm -rf "$WIN_STAGE"
  mkdir -p "$WIN_STAGE"
  cp "${STAGE}/stealth.ps1" "${STAGE}/README.md" "${STAGE}/INSTALL-README.md" "$WIN_STAGE/" 2>/dev/null || true
  cp -a "${STAGE}/scripts/ammoos-launch-verify.sh" "$WIN_STAGE/" 2>/dev/null || true
  (cd "$WIN_STAGE" && zip -qr "${DIST}/${WIN_NAME}" .)
fi

echo "=== platform manifest ==="
python3 - <<PY
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path("${ROOT}")
dist = Path("${DIST}")
ver = "${VER}"
src = json.loads((root / "data/ammoos-platform-release.json").read_text(encoding="utf-8"))
src["version"] = ver
src["tag"] = f"v{ver}"
src["released_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
out = dist / f"ammoos-{ver}-platforms.json"
out.write_text(json.dumps(src, indent=2) + "\\n", encoding="utf-8")

lines = [
    f"# AmmoOS {ver} — platform bootstrap matrix",
    "",
    f"**Tag:** \`v{ver}\` · **Model:** source bootstrap per platform",
    "",
    "AmmoOS ships **source + installers**. Browser surfaces run on loopback; Queen shell builds on target.",
    "",
    "## Quick start (Linux x86_64)",
    "",
    "\`\`\`bash",
    f"tar xzf ammooos-{ver}-source.tar.gz && cd ammooos-{ver}",
    "sudo ./install-all.sh",
    "# browser opens http://127.0.0.1:9477/field",
    "\`\`\`",
    "",
    "## Platforms",
    "",
    "| ID | OS | Arch | Bootstrap |",
    "|----|-----|------|-----------|",
]
for p in src.get("platforms", []):
    boot = p.get("bootstrap", {})
    boot_s = ", ".join(f"{k}={v}" for k, v in boot.items() if not isinstance(v, dict))
    lines.append(f"| {p['id']} | {p['os']} | {p['arch']} | {boot_s} |")
(dist / f"ammoos-{ver}-PLATFORMS.md").write_text("\\n".join(lines) + "\\n", encoding="utf-8")
print(f"wrote {out.name}")
PY

echo "=== pack complete ==="
ls -lh "${DIST}"/ammoos-${VER}* 2>/dev/null || true