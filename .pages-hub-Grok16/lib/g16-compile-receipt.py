#!/usr/bin/env python3
"""Grok16 compile receipt chain — source_sha → object_sha → binary_sha; silent verify."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
LEDGER = Path(os.environ.get("G16_RECEIPT_LEDGER", str(ROOT / "data" / "g16-compile-receipt.jsonl")))


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_file(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sealed_append(row: dict[str, Any]) -> None:
    path = ROOT / "lib" / "g16-sealed-output.py"
    spec = importlib.util.spec_from_file_location("g16_sealed_output", path)
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.sealed_append_jsonl(LEDGER, row)
        return
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def record(
    *,
    source_path: str = "",
    source_text: str = "",
    object_path: str = "",
    binary_path: str = "",
    profile: str = "",
    lang: str = "",
) -> dict[str, Any]:
    src_sha = sha256_file(Path(source_path)) if source_path and Path(source_path).is_file() else (
        sha256_text(source_text) if source_text else None
    )
    obj_sha = sha256_file(Path(object_path)) if object_path and Path(object_path).is_file() else None
    bin_sha = sha256_file(Path(binary_path)) if binary_path and Path(binary_path).is_file() else None
    row = {
        "schema": "g16-compile-receipt/v1",
        "ts": _now(),
        "profile": profile,
        "lang": lang,
        "source_sha256": src_sha,
        "object_sha256": obj_sha,
        "binary_sha256": bin_sha,
        "source_path": source_path or None,
        "object_path": object_path or None,
        "binary_path": binary_path or None,
    }
    chain = hashlib.sha256("|".join(filter(None, [src_sha, obj_sha, bin_sha])).encode()).hexdigest()
    row["chain_sha256"] = chain
    _sealed_append(row)
    return row


def verify_ledger(*, silent: bool = True) -> bool:
    if not LEDGER.is_file():
        return True
    spec = importlib.util.spec_from_file_location("g16_sealed_output", ROOT / "lib" / "g16-sealed-output.py")
    if not spec or not spec.loader:
        return True
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.verify(LEDGER, silent=silent, skip_unsealed=True)


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"usage": "record|verify", "ledger": str(LEDGER)}, indent=2))
        return 2
    if sys.argv[1] == "verify":
        return 0 if verify_ledger() else 1
    if sys.argv[1] == "record":
        body = json.loads(sys.stdin.read() or "{}")
        print(json.dumps(record(**body), indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())