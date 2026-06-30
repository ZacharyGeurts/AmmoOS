#!/usr/bin/env python3
"""Grok16 sealed output — every durable artifact self-verifies SHA-256; silent unless mismatch."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

SCHEMA = "g16-sealed-output/v1"
SEAL_KEY = "_g16_seal"
ALGORITHM = "sha256"
SIDE_SUFFIX = ".sha256"
ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _emit(msg: str, *, stream: Any = None) -> None:
    print(msg, file=stream or sys.stderr, flush=True)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _body_without_seal(doc: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in doc.items() if k != SEAL_KEY}


def _canonical_json(doc: dict[str, Any]) -> str:
    return json.dumps(doc, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _g1id_meld_slice() -> dict[str, Any] | None:
    """G15 — optional sovereign-time slice for cold identity files."""
    if os.environ.get("G16_SEAL_G1ID_MELD", "1").strip().lower() in ("0", "false", "no"):
        return None
    forge = ROOT / "forge" / "g16-g1id.py"
    if not forge.is_file():
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location("g16_g1id", forge)
    if not spec or not spec.loader:
        return None
    try:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "meld_slice"):
            sl = mod.meld_slice()
            if isinstance(sl, dict) and sl.get("ok", True):
                return sl
    except Exception:
        pass
    return None


def attach_seal(doc: dict[str, Any], *, path: str = "", g1id_meld: bool | None = None) -> dict[str, Any]:
    body = _body_without_seal(doc)
    digest = sha256_text(_canonical_json(body))
    sealed = dict(body)
    seal_doc: dict[str, Any] = {
        "schema": SCHEMA,
        "algorithm": ALGORITHM,
        "digest": digest,
        "sealed_at": _now(),
    }
    if path:
        seal_doc["path"] = str(path)
    use_meld = g1id_meld if g1id_meld is not None else bool(path and str(path).endswith((".g1id", ".json")))
    if use_meld:
        sl = _g1id_meld_slice()
        if sl:
            seal_doc["g1id_meld"] = sl
    sealed[SEAL_KEY] = seal_doc
    return sealed


def seal_row(row: dict[str, Any]) -> dict[str, Any]:
    return attach_seal(row)


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def sealed_write_json(path: Path | str, doc: dict[str, Any]) -> dict[str, Any]:
    """Write JSON with embedded _g16_seal — only durable Grok16 output path."""
    p = Path(path)
    sealed = attach_seal(doc, path=str(p))
    _atomic_write(p, json.dumps(sealed, ensure_ascii=False, indent=2) + "\n")
    return sealed


def sealed_write_text(path: Path | str, text: str) -> str:
    """Write text + sidecar .sha256 for non-JSON artifacts."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(p)
    digest = sha256_file(p) or sha256_text(text)
    side = Path(str(p) + SIDE_SUFFIX)
    side.write_text(f"{ALGORITHM}:{digest}  {p.name}\n", encoding="utf-8")
    return digest


def sealed_write_bytes(path: Path | str, data: bytes) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(p)
    digest = sha256_bytes(data)
    Path(str(p) + SIDE_SUFFIX).write_text(f"{ALGORITHM}:{digest}  {p.name}\n", encoding="utf-8")
    return digest


def sealed_append_jsonl(path: Path | str, row: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(seal_row(row), ensure_ascii=False, separators=(",", ":")) + "\n"
    with p.open("a", encoding="utf-8") as fh:
        fh.write(line)


def _verify_json(path: Path, doc: dict[str, Any]) -> tuple[bool, str]:
    seal = doc.get(SEAL_KEY)
    if not isinstance(seal, dict) or not seal.get("digest"):
        return False, "missing_seal"
    body = _body_without_seal(doc)
    expect = str(seal.get("digest"))
    got = sha256_text(_canonical_json(body))
    if got != expect:
        return False, f"digest_mismatch expected={expect} got={got}"
    if seal.get("algorithm") and seal.get("algorithm") != ALGORITHM:
        return False, f"algorithm_mismatch {seal.get('algorithm')}"
    return True, "match"


def _verify_sidecar(path: Path) -> tuple[bool, str]:
    side = Path(str(path) + SIDE_SUFFIX)
    if not side.is_file():
        return False, "missing_sidecar"
    line = side.read_text(encoding="utf-8", errors="replace").strip().splitlines()[0]
    prefix = f"{ALGORITHM}:"
    if not line.startswith(prefix):
        return False, "bad_sidecar_format"
    digest = line[len(prefix) :].split(None, 1)[0]
    got = sha256_file(path)
    if not got:
        return False, "read_failed"
    if got != digest:
        return False, f"digest_mismatch expected={digest} got={got}"
    return True, "match"


def verify(
    path: Path | str,
    *,
    silent: bool = True,
    skip_unsealed: bool = False,
) -> bool:
    """Verify sealed artifact. Silent on match; stderr only on mismatch."""
    p = Path(path)
    if not p.is_file():
        if not silent:
            _emit(f"g16-seal MISMATCH {p}: not_found")
        return False
    ok, reason = False, "unknown"
    if p.suffix.lower() == ".json":
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            ok, reason = False, "invalid_json"
        else:
            if SEAL_KEY not in doc:
                if skip_unsealed:
                    return True
                ok, reason = False, "missing_seal"
            else:
                ok, reason = _verify_json(p, doc)
    elif p.suffix.lower() == ".jsonl":
        try:
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                if SEAL_KEY not in row:
                    if skip_unsealed:
                        continue
                    ok, reason = False, f"line_{i}_missing_seal"
                    break
                ok, reason = _verify_json(p, row)
                if not ok:
                    reason = f"line_{i}_{reason}"
                    break
            else:
                ok, reason = True, "match"
        except json.JSONDecodeError as exc:
            ok, reason = False, f"invalid_jsonl:{exc}"
    else:
        ok, reason = _verify_sidecar(p)
    if ok:
        return True
    _emit(f"g16-seal MISMATCH {p}: {reason}")
    return False


def verify_tree(
    root: Path | str,
    *,
    patterns: tuple[str, ...] = ("*.json", "*.jsonl"),
    silent: bool = True,
    skip_unsealed: bool = True,
) -> dict[str, Any]:
    base = Path(root)
    checked = 0
    failed: list[str] = []
    for pat in patterns:
        for path in sorted(base.rglob(pat)):
            if path.name.startswith(".") or ".tmp" in path.name or path.name.endswith(SIDE_SUFFIX):
                continue
            checked += 1
            if not verify(path, silent=silent, skip_unsealed=skip_unsealed):
                failed.append(str(path))
    return {
        "schema": SCHEMA,
        "ok": not failed,
        "root": str(base),
        "checked": checked,
        "failed": failed,
        "failed_count": len(failed),
    }


def reseal_json(path: Path | str) -> bool:
    p = Path(path)
    doc = json.loads(p.read_text(encoding="utf-8"))
    sealed_write_json(p, doc)
    return True


def main() -> int:
    args = sys.argv[1:]
    if not args:
        _emit("usage: g16-sealed-output.py verify <path>... | verify-tree <dir> | reseal <path>...")
        return 2
    cmd = args[0].lower()
    if cmd == "verify":
        rc = 0
        for raw in args[1:]:
            if not verify(raw, silent=True, skip_unsealed=False):
                rc = 1
        return rc
    if cmd == "verify-tree":
        root = args[1] if len(args) > 1 else str(ROOT / "data")
        rep = verify_tree(root, silent=True, skip_unsealed=True)
        if not rep["ok"]:
            _emit(f"g16-seal tree FAIL checked={rep['checked']} failed={rep['failed_count']}")
            for f in rep["failed"][:20]:
                _emit(f"  {f}")
            return 1
        return 0
    if cmd == "reseal":
        for raw in args[1:]:
            reseal_json(raw)
        return 0
    _emit(f"unknown command: {cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())