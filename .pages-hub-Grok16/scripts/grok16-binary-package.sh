#!/usr/bin/env bash
# Grok16 binary package — full g16 prefix + AmmoCode executable + default settings.
# Usage: ./scripts/grok16-binary-package.sh [version] [--skip-ammocode-build]
set -euo pipefail

GROK16_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG_ROOT="${SG_ROOT:-$(cd "$GROK16_ROOT/.." && pwd)}"
AMMOCODE_ROOT="${AMMOCODE_ROOT:-$SG_ROOT/AmmoCode}"
# shellcheck source=grok16-config.sh
source "$GROK16_ROOT/scripts/grok16-config.sh"

VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  VERSION="$(python3 -c "import json;from pathlib import Path;p=Path('${GROK16_ROOT}/data/grok16-version.json');d=json.loads(p.read_text());print(d.get('distro_version','5.0.0'))")"
fi
DISPLAY_VERSION="$VERSION"
SKIP_AMMO=0
shift || true
for arg in "$@"; do
  case "$arg" in
    --skip-ammocode-build) SKIP_AMMO=1 ;;
  esac
done

export GROK16_ROOT SG_ROOT AMMOCODE_ROOT G16_PREFIX="${G16_PREFIX:-$GROK16_ROOT}"

DIST="$GROK16_ROOT/dist"
PKG_NAME="grok16-${VERSION}-linux-x86_64"
STAGE="$DIST/$PKG_NAME"
TARBALL="$DIST/${PKG_NAME}.tar.gz"
MANIFEST="$DIST/${PKG_NAME}-manifest.json"

log() { printf '[%s] binary-package %s\n' "$(date +%H:%M:%S)" "$*"; }

require_g16() {
  if ! "$GROK16_ROOT/scripts/grok16-toolchain.sh" status >/dev/null 2>&1; then
    log "ERROR: g16 not ready — run: ./scripts/grok16-toolchain.sh rebuild"
    exit 1
  fi
  log "g16: $("$GROK16_ROOT/bin/g16" --version | head -1)"
}

stage_ammocode_launcher() {
  mkdir -p "$AMMOCODE_ROOT/dist"
  cat >"$AMMOCODE_ROOT/dist/ammocode" <<'LAUNCH'
#!/usr/bin/env bash
# Grok16 package launcher — runs bundled AmmoCode tree (PyInstaller optional).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
BUNDLE="$HERE/bundle"
export GROK16_ROOT="${GROK16_ROOT:-$(cd "$HERE/../.." && pwd)}"
export AMMOCODE_FROZEN=1
if [[ -f "$BUNDLE/ammocode.py" ]]; then
  exec python3 "$BUNDLE/ammocode.py" "$@"
fi
if [[ -x "$HERE/ammocode.bin" ]]; then
  exec "$HERE/ammocode.bin" "$@"
fi
echo "ammocode: missing bundle — reinstall Grok16 binary package" >&2
exit 1
LAUNCH
  chmod +x "$AMMOCODE_ROOT/dist/ammocode"
}

build_ammocode_exe() {
  if [[ "$SKIP_AMMO" -eq 1 && -x "$AMMOCODE_ROOT/dist/ammocode" ]]; then
    log "ammocode: reuse $AMMOCODE_ROOT/dist/ammocode"
    return 0
  fi
  if [[ ! -d "$AMMOCODE_ROOT" ]]; then
    log "ERROR: AmmoCode not found at $AMMOCODE_ROOT"
    exit 1
  fi
  log "ammocode: build secured executable"
  set +e
  (
    cd "$AMMOCODE_ROOT"
    export GROK16_ROOT AMMOCODE_FROZEN=1
    bash scripts/build-executable.sh
  )
  local rc=$?
  set -e
  if [[ $rc -ne 0 || ! -x "$AMMOCODE_ROOT/dist/ammocode" ]]; then
    log "WARN: PyInstaller unavailable — staging launcher + bundle tree"
    stage_ammocode_launcher
    mkdir -p "$AMMOCODE_ROOT/dist/bundle"
    rsync -a --delete \
      --exclude '.git' --exclude 'dist/build' --exclude 'dist/*.spec' \
      --exclude '__pycache__' --exclude '*.pyc' \
      "$AMMOCODE_ROOT/" "$AMMOCODE_ROOT/dist/bundle/" 2>/dev/null || \
      cp -a "$AMMOCODE_ROOT/ammocode.py" "$AMMOCODE_ROOT/server" "$AMMOCODE_ROOT/lib" \
            "$AMMOCODE_ROOT/data" "$AMMOCODE_ROOT/assets" "$AMMOCODE_ROOT/index.html" \
            "$AMMOCODE_ROOT/tab.html" "$AMMOCODE_ROOT/dist/bundle/" 2>/dev/null || true
  elif file "$AMMOCODE_ROOT/dist/ammocode" | grep -q ELF; then
    cp -a "$AMMOCODE_ROOT/dist/ammocode" "$AMMOCODE_ROOT/dist/ammocode.bin"
    stage_ammocode_launcher
  fi
}

build_default_settings() {
  log "ammocode: package default settings"
  export GROK16_ROOT SG_ROOT AMMOCODE_ROOT AMMOCODE_PACKAGE_PORTABLE=1
  python3 "$GROK16_ROOT/scripts/grok16-build-ammocode-settings.py"
}

stage_prefix() {
  log "stage g16 prefix → $STAGE"
  rm -rf "$STAGE"
  mkdir -p "$STAGE/share/ammocode"

  for part in bin libexec lib lib64 include share x86_64-pc-linux-gnu; do
    if [[ -d "$G16_PREFIX/$part" ]]; then
      mkdir -p "$STAGE/$part"
      cp -a "$G16_PREFIX/$part/." "$STAGE/$part/" 2>/dev/null || cp -a "$G16_PREFIX/$part" "$STAGE/" 2>/dev/null || true
    fi
  done

  for f in VERSION SELFHOST.json; do
    [[ -f "$G16_PREFIX/$f" ]] && cp -a "$G16_PREFIX/$f" "$STAGE/"
  done

  cp -a "$GROK16_ROOT/cmake" "$STAGE/" 2>/dev/null || true
  mkdir -p "$STAGE/scripts"
  cp -a "$GROK16_ROOT/scripts/grok16-toolchain.sh" "$GROK16_ROOT/scripts/grok16-config.sh" "$STAGE/scripts/"
  cp -a "$GROK16_ROOT/scripts/g16-build-env.sh" "$STAGE/scripts/" 2>/dev/null || true

  cp -a "$AMMOCODE_ROOT/dist/ammocode" "$STAGE/share/ammocode/ammocode"
  chmod +x "$STAGE/share/ammocode/ammocode"
  if [[ -d "$AMMOCODE_ROOT/dist/bundle" ]]; then
    cp -a "$AMMOCODE_ROOT/dist/bundle" "$STAGE/share/ammocode/"
  fi
  if [[ -f "$AMMOCODE_ROOT/dist/ammocode.bin" ]]; then
    cp -a "$AMMOCODE_ROOT/dist/ammocode.bin" "$STAGE/share/ammocode/"
  fi

  if [[ -d "$GROK16_ROOT/share/ammocode" ]]; then
    cp -a "$GROK16_ROOT/share/ammocode/." "$STAGE/share/ammocode/"
  fi

  cat >"$STAGE/share/ammocode/README.txt" <<EOF
Grok16 ${DISPLAY_VERSION} binary package — AmmoCode bundle

  share/ammocode/ammocode              Secured AmmoCode GUI (replacement-only updates)
  share/ammocode/ammocode-settings.secure.json   Default settings (all options pre-set)
  share/ammocode/ammocode-settings.package.key   Package signing key (first-run import)

First run:
  export GROK16_ROOT="\$(pwd)"
  export PATH="\$GROK16_ROOT/bin:\$PATH"
  ./share/ammocode/ammocode

Settings copy to ~/.config/ammocode/ on first launch when bundledGrok16=true.
g16: ./bin/g16 --version
EOF

  cat >"$STAGE/grok16-env.sh" <<'ENV'
#!/usr/bin/env bash
# Source after extracting the binary package.
export GROK16_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export G16_PREFIX="$GROK16_ROOT"
export PATH="$GROK16_ROOT/bin:$GROK16_ROOT/libexec/grok16:$PATH"
export LD_LIBRARY_PATH="$GROK16_ROOT/lib:$GROK16_ROOT/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
[[ -f "$GROK16_ROOT/scripts/g16-build-env.sh" ]] && source "$GROK16_ROOT/scripts/g16-build-env.sh"
ENV
  chmod +x "$STAGE/grok16-env.sh"
}

write_manifest() {
  python3 - <<PY
import json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path

root = Path("$STAGE")
g16 = root / "bin" / "g16"
ammo = root / "share" / "ammocode" / "ammocode"
settings = root / "share" / "ammocode" / "ammocode-settings.secure.json"
ver = {}
try:
    ver = json.loads((Path("$GROK16_ROOT") / "data" / "grok16-version.json").read_text())
except Exception:
    pass
g16_ver = ""
if g16.is_file():
    try:
        g16_ver = subprocess.check_output([str(g16), "-dumpversion"], text=True).strip()
    except Exception:
        pass
doc = {
    "schema": "grok16-binary-package/v1",
    "distro_version": "$DISPLAY_VERSION",
    "g16_version": ver.get("g16_version", g16_ver),
    "pkgversion": ver.get("pkgversion", "Grok16-$DISPLAY_VERSION"),
    "built": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "platform": "linux-x86_64",
    "contents": {
        "g16_prefix": True,
        "ammocode_executable": ammo.is_file(),
        "default_settings": settings.is_file(),
        "cmake": (root / "cmake").is_dir(),
    },
    "ammocode": {
        "path": "share/ammocode/ammocode",
        "settings": "share/ammocode/ammocode-settings.secure.json",
        "package_key": "share/ammocode/ammocode-settings.package.key",
    },
    "usage": "source grok16-env.sh && ./share/ammocode/ammocode",
}
out = Path("$MANIFEST")
out.write_text(json.dumps(doc, indent=2) + "\\n", encoding="utf-8")
print(out)
PY
}

build_tarball() {
  log "tarball $TARBALL"
  tar -czf "$TARBALL" -C "$DIST" "$PKG_NAME"
  log "wrote $TARBALL ($(du -h "$TARBALL" | awk '{print $1}'))"
}

main() {
  log "Grok16 ${DISPLAY_VERSION} binary package (g16 + AmmoCode + defaults)"
  require_g16
  build_ammocode_exe
  build_default_settings
  stage_prefix
  write_manifest
  build_tarball
  log "complete: $TARBALL"
  log "  manifest: $MANIFEST"
  log "  extract: tar xzf $(basename "$TARBALL") && source grok16-env.sh"
}

main