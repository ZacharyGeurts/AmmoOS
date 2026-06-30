#!/usr/bin/env pythong
"""CHIPs universal compiler design — write every G16 language front-end from ISA graph."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1])).resolve()
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", ROOT.parent))
LANGS_PATH = ROOT / "data" / "grok16-languages.json"
DOCTRINE_PATH = ROOT / "data" / "g16-chips-compiler-doctrine.json"
EXAMPLES = ROOT / "examples" / "languages"
CHIPS_MANIFEST = INSTALL / "Queen" / "data" / "chips-g16-manifest.json"

_NATIVE_MODULES = frozenset({
    "java", "kotlin", "fortran", "cobol", "cobol_copy",
    "basic", "qbasic", "quickbasic", "freebasic", "visual_basic", "vba",
    "pascal", "turbo_pascal", "delphi",
})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _save(path: Path, doc: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _invert_isa_map(isa_lang: dict[str, list[str]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for isa, langs in (isa_lang or {}).items():
        for lang in langs:
            lid = str(lang).lower()
            out.setdefault(lid, [])
            if isa not in out[lid]:
                out[lid].append(isa)
    return out


def _resolve_isas(lang_id: str, meta: dict[str, Any], lang_to_isa: dict[str, list[str]], doctrine: dict[str, Any]) -> list[str]:
    if meta.get("universal_isa"):
        return list(meta["universal_isa"])
    parent = str(meta.get("extends") or "").lower()
    if parent and parent in lang_to_isa:
        return list(lang_to_isa[parent])
    if lang_id in lang_to_isa:
        return list(lang_to_isa[lang_id])
    return list(doctrine.get("default_isa") or ["x86"])


def _compiler_lane(driver: str, lang_id: str, doctrine: dict[str, Any]) -> str:
    lanes = doctrine.get("driver_lane") or {}
    if lang_id in ("ammolang", "field"):
        return "combinatronics_native"
    if lang_id in _NATIVE_MODULES:
        return "chips_native"
    return str(lanes.get(driver or "", "chips_lower"))


def _chip_hints(isas: list[str], doctrine: dict[str, Any]) -> list[str]:
    hints = doctrine.get("isa_chip_hints") or {}
    out: list[str] = []
    for isa in isas:
        for chip in hints.get(isa, []):
            if chip not in out:
                out.append(chip)
    manifest = _load(CHIPS_MANIFEST, {})
    if manifest.get("hot_paths"):
        for row in manifest["hot_paths"][:6]:
            chip = str(row.get("chip") or "")
            if chip and chip not in out:
                out.append(chip)
    return out[:12]


def design_for_language(lang_id: str, meta: dict[str, Any], *, doctrine: dict[str, Any] | None = None) -> dict[str, Any]:
    doc = doctrine or _load(DOCTRINE_PATH, {})
    lang_to_isa = _invert_isa_map(doc.get("isa_lang") or {})
    driver = str(meta.get("driver") or "g16-interp")
    isas = _resolve_isas(lang_id, meta, lang_to_isa, doc)
    lane = _compiler_lane(driver, lang_id, doc)
    frontends = doc.get("frontend_modules") or {}
    primary = isas[0] if isas else "x86"
    chips = _chip_hints(isas, doc)
    return {
        "schema": "g16-chips-compiler-design/v1",
        "lang": lang_id,
        "driver": driver,
        "compiler_lane": lane,
        "universal_isa": isas,
        "chips": {
            "primary_isa": primary,
            "target_chips": chips,
            "universal": True,
            "manifest": str(CHIPS_MANIFEST.relative_to(INSTALL)) if CHIPS_MANIFEST.is_file() else None,
            "design_note": (
                f"CHIPs universal — {primary} ISA informs lowering, dispatch tables, and field_opt hot paths."
            ),
        },
        "frontend": frontends.get(lane, "lib/g16-lang-lower.py"),
        "lowering": "lib/g16-lang-lower.py" if lane in ("chips_lower", "chips_native") else None,
        "native_module": "lib/g16-native-compile.py" if lang_id in _NATIVE_MODULES else None,
        "profile": meta.get("belt") or "field_opt",
        "written": True,
        "updated": _now(),
    }


def write_compiler_design(lang_id: str, meta: dict[str, Any], *, doctrine: dict[str, Any] | None = None) -> Path:
    design = design_for_language(lang_id, meta, doctrine=doctrine)
    folder = EXAMPLES / lang_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "compiler.design.json"
    _save(path, design)
    return path


def ensure_all_compilers_written(*, update_langs: bool = True) -> dict[str, Any]:
    """Write compiler.design.json for every language; stamp grok16-languages.json."""
    doctrine = _load(DOCTRINE_PATH, {})
    langs_doc = _load(LANGS_PATH, {})
    languages = dict(langs_doc.get("languages") or {})
    written: list[str] = []
    errors: list[dict[str, str]] = []

    for lang_id in sorted(languages.keys()):
        meta = dict(languages[lang_id])
        try:
            design = design_for_language(lang_id, meta, doctrine=doctrine)
            write_compiler_design(lang_id, meta, doctrine=doctrine)
            if update_langs:
                meta["universal_isa"] = design["universal_isa"]
                meta["compiler_written"] = True
                meta["compiler_lane"] = design["compiler_lane"]
                meta["chips_primary_isa"] = design["chips"]["primary_isa"]
                if not meta.get("combinatronic"):
                    meta["combinatronic"] = True
                languages[lang_id] = meta
            written.append(lang_id)
        except Exception as exc:
            errors.append({"lang": lang_id, "error": type(exc).__name__})

    if update_langs:
        langs_doc["languages"] = languages
        langs_doc["chips_universal"] = {
            "schema": "g16-chips-universal/v1",
            "updated": _now(),
            "compiler_written_count": len(written),
            "doctrine": str(DOCTRINE_PATH.relative_to(ROOT)),
            "motto": doctrine.get("motto"),
        }
        _save(LANGS_PATH, langs_doc)

    return {
        "schema": "g16-chips-compiler-ensure/v1",
        "ok": len(errors) == 0,
        "written": len(written),
        "total": len(languages),
        "errors": errors,
        "languages": written,
        "updated": _now(),
    }


def posture() -> dict[str, Any]:
    langs = _load(LANGS_PATH, {}).get("languages") or {}
    written = sum(1 for m in langs.values() if m.get("compiler_written"))
    designs = sum(1 for lid in langs if (EXAMPLES / lid / "compiler.design.json").is_file())
    return {
        "schema": "g16-chips-compiler-design/v1",
        "ok": written == len(langs) and designs == len(langs),
        "languages_total": len(langs),
        "compiler_written": written,
        "design_files": designs,
        "doctrine": str(DOCTRINE_PATH),
        "motto": "CHIPs universal — every language has a written compiler design",
    }


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "posture"):
        print(json.dumps(posture(), ensure_ascii=False, indent=2))
        return 0
    if cmd in ("ensure", "write", "write-all"):
        out = ensure_all_compilers_written()
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if out.get("ok") else 1
    if cmd == "design" and len(sys.argv) > 2:
        lang = sys.argv[2].lower()
        langs = _load(LANGS_PATH, {}).get("languages") or {}
        if lang not in langs:
            print(json.dumps({"error": "unknown_lang", "lang": lang}, indent=2))
            return 1
        design = design_for_language(lang, langs[lang])
        print(json.dumps(design, ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({"usage": "g16-chips-compiler-design.py [json|ensure|design LANG]"}, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())