#!/usr/bin/env pythong
"""G16 code security — transparent vuln scan, insta-rewrite, no black box."""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "g16-vulnerability-registry.json"
AMMO_REGISTRY = ROOT.parent / "AmmoCode" / "data" / "vulnerability-registry.json"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _load_registry() -> dict[str, Any]:
    for path in (REGISTRY, AMMO_REGISTRY):
        if path.is_file():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
    return {"patterns": []}


def _line_no(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def scan(content: str, *, lang: str = "", path: str = "") -> dict[str, Any]:
    """Scan source for known vulnerabilities — transparent, no black box."""
    doc = _load_registry()
    findings: list[dict[str, Any]] = []
    blocked = False
    for row in doc.get("patterns") or []:
        langs = row.get("langs")
        if langs and lang and lang not in langs and "*" not in langs:
            continue
        pat = row.get("pattern")
        if not pat:
            continue
        try:
            rx = re.compile(pat, re.MULTILINE | re.IGNORECASE)
        except re.error:
            continue
        for m in rx.finditer(content):
            line = _line_no(content, m.start())
            col = m.start() - content.rfind("\n", 0, m.start())
            sev = str(row.get("severity") or "bad")
            finding = {
                "id": row.get("id"),
                "line": line,
                "column": col,
                "match": m.group(0)[:120],
                "severity": sev,
                "bad": True,
                "message": row.get("message") or "Unsafe pattern",
                "use_instead": row.get("use_instead") or row.get("alternative"),
                "rewrite": row.get("rewrite"),
                "cwe": row.get("cwe"),
                "transparent": True,
            }
            findings.append(finding)
            if sev in ("critical", "bad", "block") or row.get("block"):
                blocked = True
    return {
        "schema": "g16-code-security-scan/v1",
        "updated": _now(),
        "ok": not blocked,
        "blocked": blocked,
        "lang": lang,
        "path": path,
        "findings": findings,
        "finding_count": len(findings),
        "policy": doc.get("policy") or {"transparent": True, "no_black_box": True, "insta_rewrite": True},
        "motto": doc.get("motto") or "Bad code gets the red stop sign — use the safe alternative.",
    }


def insta_rewrite(content: str, *, lang: str = "") -> dict[str, Any]:
    """Apply transparent patches for known vulns — returns rewritten source."""
    doc = _load_registry()
    out = content
    applied: list[dict[str, Any]] = []
    for row in doc.get("patterns") or []:
        rewrite = row.get("rewrite")
        pat = row.get("pattern")
        if not rewrite or not pat:
            continue
        langs = row.get("langs")
        if langs and lang and lang not in langs and "*" not in langs:
            continue
        try:
            rx = re.compile(pat, re.MULTILINE | re.IGNORECASE)
            new_out, n = rx.subn(rewrite, out)
            if n:
                applied.append({"id": row.get("id"), "count": n, "use_instead": row.get("use_instead")})
                out = new_out
        except re.error:
            continue
    return {
        "schema": "g16-insta-rewrite/v1",
        "updated": _now(),
        "ok": True,
        "lang": lang,
        "applied": applied,
        "changed": out != content,
        "content": out,
    }


def gate(content: str, *, lang: str = "", path: str = "") -> dict[str, Any]:
    """Security gate — scan + optional rewrite suggestion."""
    s = scan(content, lang=lang, path=path)
    rewrite = insta_rewrite(content, lang=lang) if s.get("blocked") else {"changed": False, "content": content}
    return {
        "schema": "g16-code-security-gate/v1",
        "ok": s.get("ok", True),
        "blocked": s.get("blocked", False),
        "scan": s,
        "rewrite": rewrite,
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "scan").strip().lower()
    if cmd == "scan" and len(sys.argv) > 2:
        text = Path(sys.argv[2]).read_text(encoding="utf-8", errors="replace") if Path(sys.argv[2]).is_file() else sys.argv[2]
        lang = sys.argv[3] if len(sys.argv) > 3 else ""
        print(json.dumps(scan(text, lang=lang), ensure_ascii=False, indent=2))
        return 0
    if cmd == "rewrite" and len(sys.argv) > 2:
        text = Path(sys.argv[2]).read_text(encoding="utf-8", errors="replace") if Path(sys.argv[2]).is_file() else sys.argv[2]
        lang = sys.argv[3] if len(sys.argv) > 3 else ""
        print(json.dumps(insta_rewrite(text, lang=lang), ensure_ascii=False, indent=2))
        return 0
    if cmd == "gate":
        raw = sys.stdin.read() if len(sys.argv) <= 2 else (Path(sys.argv[2]).read_text(encoding="utf-8", errors="replace") if Path(sys.argv[2]).is_file() else sys.argv[2])
        lang = sys.argv[3] if len(sys.argv) > 3 else ""
        print(json.dumps(gate(raw, lang=lang), ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({"error": "usage", "cmds": ["scan <file|text> [lang]", "rewrite <file|text> [lang]", "gate"]}, ensure_ascii=False, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())