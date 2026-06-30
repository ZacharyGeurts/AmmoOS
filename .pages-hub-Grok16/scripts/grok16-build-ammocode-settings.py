#!/usr/bin/env python3
"""Build signed AmmoCode default settings for Grok16 binary package."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

GROK16_ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
SG_ROOT = Path(os.environ.get("SG_ROOT", GROK16_ROOT.parent))
AMMOCODE = Path(os.environ.get("AMMOCODE_ROOT", SG_ROOT / "AmmoCode"))
OUT_DIR = Path(os.environ.get("GROK16_AMMOCODE_SHARE", GROK16_ROOT / "share" / "ammocode"))

PACKAGE_KEY_SEED = os.environ.get(
    "AMMOCODE_PACKAGE_KEY_SEED",
    "grok16-ammocode-package-key-v1",
)


def _package_key() -> bytes:
    ver = json.loads((GROK16_ROOT / "data" / "grok16-version.json").read_text(encoding="utf-8"))
    distro = ver.get("distro_version", "5.0.0")
    seed = f"{PACKAGE_KEY_SEED}:{distro}".encode()
    return hashlib.sha256(seed).digest()


def _canonical(values: dict) -> bytes:
    return json.dumps(values, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sign(schema_version: int, values: dict, settings_version: str, key: bytes) -> str:
    payload = f"{schema_version}:{settings_version}:".encode() + _canonical(values)
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def main() -> int:
    schema_path = AMMOCODE / "data" / "ammocode-settings-schema.json"
    defaults_path = AMMOCODE / "data" / "ammocode-settings-package-defaults.json"
    if not schema_path.is_file():
        print(f"missing schema: {schema_path}", file=sys.stderr)
        return 1
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    pkg = json.loads(defaults_path.read_text(encoding="utf-8")) if defaults_path.is_file() else {}
    raw_values = dict(pkg.get("values") or {})
    options = schema.get("options") or {}

    values: dict = {}
    for key, spec in options.items():
        if key in raw_values:
            values[key] = raw_values[key]
        else:
            values[key] = spec.get("default")

    portable = os.environ.get("AMMOCODE_PACKAGE_PORTABLE", "").lower() in ("1", "true", "yes")
    if portable:
        values["grok16Root"] = "${GROK16_ROOT}"
    else:
        gr = str(values.get("grok16Root") or "").replace("${GROK16_ROOT}", str(GROK16_ROOT))
        values["grok16Root"] = gr or str(GROK16_ROOT)
    values["bundledGrok16"] = True
    values["memoryVault"] = values.get("memoryVault", True)
    values["profile"] = values.get("profile") or "belt_2_0"

    sv = int(schema.get("schema_version") or 1)
    settings_version = str(schema.get("settings_version") or "5.0.0")
    key = _package_key()
    doc = {
        "schema": "ammocode-settings-secure/v1",
        "schema_version": sv,
        "settings_version": settings_version,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "package": True,
        "grok16_distro": pkg.get("grok16_distro", "5.0.0"),
        "g16_version": pkg.get("g16_version", "16.2.0"),
        "values": values,
        "signature": "",
    }
    doc["signature"] = _sign(sv, values, settings_version, key)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    settings_out = OUT_DIR / "ammocode-settings.secure.json"
    key_out = OUT_DIR / "ammocode-settings.package.key"
    settings_out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    key_out.write_bytes(key)
    try:
        os.chmod(settings_out, 0o644)
        os.chmod(key_out, 0o600)
    except OSError:
        pass

    manifest = {
        "schema": "grok16-ammocode-package-settings/v1",
        "settings": str(settings_out),
        "package_key": str(key_out),
        "options_count": len(values),
        "profile": values.get("profile"),
        "memory_vault": values.get("memoryVault"),
    }
    (OUT_DIR / "ammocode-settings.manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps({"ok": True, **manifest}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())