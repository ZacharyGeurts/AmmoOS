#!/bin/bash
# Pack NEXUS-Shield release archives for GitHub upload.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-common.sh"

VER="${NEXUS_VERSION}"
DIST="${ROOT}/dist"
STAGE="${DIST}/nexus-shield-${VER}"
PKG_NAME="nexus-shield-${VER}-source.tar.gz"
INST_NAME="nexus-shield-${VER}-installers.tar.gz"

mkdir -p "$DIST"
rm -rf "$STAGE"
mkdir -p "$STAGE"

echo "=== staging ${VER} ==="
rsync -a \
  --exclude='.git' \
  --exclude='.nexus-state' \
  --exclude='.nexus-state-test' \
  --exclude='dist' \
  --exclude='Hostess7/cache' \
  --exclude='Hostess7/zac' \
  --exclude='Queen/build' \
  --exclude='Queen/build-*' \
  --exclude='Queen/vendor' \
  --exclude='Queen/cache' \
  --exclude='Queen/.venv*' \
  --exclude='*.log' \
  --exclude='AMOURANTHRTX' \
  --exclude='Grok16' \
  --exclude='GrokPy' \
  --exclude='PythonG' \
  --exclude='KILROY' \
  --exclude='Final_Eye' \
  --exclude='Final_Ear' \
  --exclude='ZNEWOCR' \
  --exclude='ZOCR' \
  --exclude='ZNetwork' \
  --exclude='World_Redata' \
  --exclude='World_Repack' \
  --exclude='Field_Primer' \
  --exclude='Spiderweb' \
  "${ROOT}/" "${STAGE}/"

echo "=== source tarball ==="
tar -czf "${DIST}/${PKG_NAME}" -C "${DIST}" "nexus-shield-${VER}"

echo "=== installers tarball ==="
INSTALL_STAGE="${DIST}/nexus-shield-${VER}-installers"
rm -rf "$INSTALL_STAGE"
mkdir -p "$INSTALL_STAGE/scripts" "$INSTALL_STAGE/install"
for f in install-all.sh genius_shield.sh nexus.sh stealth_install.sh install.sh INSTALL-README.md assets/nexus-field.png; do
  [[ -f "${ROOT}/${f}" ]] && cp "${ROOT}/${f}" "$INSTALL_STAGE/"
done
cp -a "${ROOT}/scripts/nexus-boot-impl.sh" "${ROOT}/scripts/wire-stack.sh" \
  "${ROOT}/scripts/migrate-nexus-state.sh" "${ROOT}/scripts/release.sh" \
  "$INSTALL_STAGE/scripts/" 2>/dev/null || true
[[ -d "${ROOT}/install" ]] && cp -a "${ROOT}/install/." "$INSTALL_STAGE/install/"
tar -czf "${DIST}/${INST_NAME}" -C "${DIST}" "nexus-shield-${VER}-installers"

ls -lh "${DIST}/${PKG_NAME}" "${DIST}/${INST_NAME}"
echo "packed: ${DIST}/${PKG_NAME}"
echo "packed: ${DIST}/${INST_NAME}"