#!/usr/bin/env python3
"""G11 — Grok16 MCP-style compile stdio: check / compile / run / discern (sealed JSON responses)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _uni() -> Any:
    spec = importlib.util.spec_from_file_location("g16_uni", ROOT / "lib" / "g16-universal-compiler.py")
    if not spec or not spec.loader:
        raise ImportError("g16-universal-compiler.py missing")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sealed_response(doc: dict[str, Any]) -> str:
    spec = importlib.util.spec_from_file_location("g16_sealed_output", ROOT / "lib" / "g16-sealed-output.py")
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sealed = mod.attach_seal(doc)
        return json.dumps(sealed, ensure_ascii=False) + "\n"
    return json.dumps(doc, ensure_ascii=False) + "\n"


def handle(msg: dict[str, Any]) -> dict[str, Any]:
    uni = _uni()
    action = str(msg.get("action") or msg.get("method") or "").lower()
    profile = str(msg.get("profile") or msg.get("params", {}).get("profile") or "belt_2_0")
    if action in ("ping", "status"):
        return {"ok": True, "mcp": "g16-compile", "schema": "g16-mcp-compile/v1", **uni.status()}
    path = str(msg.get("path") or msg.get("params", {}).get("path") or "")
    content = str(msg.get("content") or msg.get("params", {}).get("content") or "")
    lang = str(msg.get("language") or msg.get("lang") or msg.get("params", {}).get("language") or "")
    mime = str(msg.get("mime") or msg.get("params", {}).get("mime") or "")
    if action in ("discern",):
        return {"ok": True, "language": uni.discern(path, mime=mime, content=content)}
    if action in ("check", "g16_check"):
        return uni.check(content, lang=lang, path=path, profile=profile)
    if action in ("compile", "g16_build", "build"):
        return uni.compile_source(content, lang=lang, path=path, profile=profile)
    if action in ("run", "g16_run"):
        if path:
            return uni.run_file(path, lang=lang, profile=profile)
        return {"ok": False, "error": "run_requires_path"}
    return {"ok": False, "error": "unknown_action", "actions": ["ping", "discern", "check", "compile", "run"]}


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as exc:
            sys.stdout.write(_sealed_response({"ok": False, "error": str(exc)}))
            sys.stdout.flush()
            continue
        rep = handle(msg)
        sys.stdout.write(_sealed_response(rep))
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())