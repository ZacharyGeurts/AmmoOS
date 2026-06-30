#!/usr/bin/env pythong
"""G16 field linker — macOS, Android, ARM, x86. Every point to the silicon."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GROK16 = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
STATE = GROK16 / ".grok16-state"
DOCTRINE = GROK16 / "data" / "g16-linker-doctrine.json"
PANEL = STATE / "g16-linker-panel.json"
LEDGER = STATE / "g16-linker-ledger.jsonl"

_ARCH_ALIASES = {
    "amd64": "x86_64",
    "x64": "x86_64",
    "arm64": "aarch64",
    "armv7l": "arm",
    "armv8l": "aarch64",
    "i686": "i386",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _save(path: Path, doc: dict[str, Any]) -> None:
    import tempfile

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    fd, tmp_name = tempfile.mkstemp(
        prefix=f"{path.stem}.",
        suffix=".tmp",
        dir=path.parent,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(payload)
        os.replace(tmp_name, path)
    except OSError:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def _append_ledger(row: dict[str, Any]) -> None:
    try:
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _mod(path: Path, name: str) -> Any | None:
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _prefix() -> Path:
    return Path(os.environ.get("G16_PREFIX", GROK16))


def _norm_arch(machine: str) -> str:
    m = machine.lower()
    return _ARCH_ALIASES.get(m, m)


def _android_env() -> bool:
    return bool(
        os.environ.get("ANDROID_NDK_ROOT")
        or os.environ.get("ANDROID_NDK")
        or os.environ.get("NDK_ROOT")
        or os.environ.get("G16_LINK_TARGET", "").startswith("android")
    )


def _host_target() -> str:
    env = os.environ.get("G16_LINK_TARGET", "").strip()
    if env:
        return env
    if _android_env():
        arch = _norm_arch(platform.machine())
        if arch == "x86_64":
            return "android-x86_64"
        if arch in ("arm", "armv7"):
            return "android-arm"
        return f"android-{arch}"
    machine = _norm_arch(platform.machine())
    sysname = platform.system().lower()
    if sysname == "linux":
        return f"linux-gnu-{machine}"
    if sysname == "darwin":
        return f"darwin-{machine}"
    if sysname == "windows":
        return f"win32-{machine}" if machine != "x86_64" else "win32-x86_64"
    return f"linux-gnu-{machine}"


def _target_from_triple(triple: str) -> str | None:
    t = triple.lower()
    doctrine = _load(DOCTRINE, {})
    for row in doctrine.get("targets") or []:
        if str(row.get("triple", "")).lower() == t:
            return str(row.get("id"))
    if "android" in t:
        if "aarch64" in t:
            return "android-aarch64"
        if "arm" in t:
            return "android-arm"
        if "x86_64" in t:
            return "android-x86_64"
    if "apple-macos" in t or "apple-darwin" in t:
        return "darwin-aarch64" if "arm64" in t or "aarch64" in t else "darwin-x86_64"
    if "apple-ios" in t:
        return "ios-aarch64"
    if "windows" in t:
        return "win32-aarch64" if "aarch64" in t or "arm64" in t else "win32-x86_64"
    if "linux" in t:
        arch = "x86_64"
        for a in ("aarch64", "arm", "riscv64", "i386", "x86_64"):
            if a in t:
                arch = a
                break
        return f"linux-gnu-{arch}"
    return None


def _target_from_argv(argv: list[str]) -> str | None:
    for i, arg in enumerate(argv):
        if arg in ("-target", "--target") and i + 1 < len(argv):
            hit = _target_from_triple(argv[i + 1])
            if hit:
                return hit
        if arg == "-m" and i + 1 < len(argv):
            emu = argv[i + 1]
            doctrine = _load(DOCTRINE, {})
            for t in doctrine.get("targets") or []:
                if t.get("emulation") == emu:
                    return str(t.get("id"))
        if arg.startswith("-m") and len(arg) > 2:
            emu = arg[2:]
            doctrine = _load(DOCTRINE, {})
            for t in doctrine.get("targets") or []:
                if t.get("emulation") == emu:
                    return str(t.get("id"))
        if arg.startswith("--sysroot=") and "android" in arg.lower():
            arch = os.environ.get("G16_ANDROID_ARCH", "aarch64")
            return f"android-{arch}"
    cc = os.environ.get("CC", "") + os.environ.get("CXX", "")
    if "android" in cc.lower():
        if "aarch64" in cc:
            return "android-aarch64"
        if "arm" in cc:
            return "android-arm"
        if "x86_64" in cc:
            return "android-x86_64"
    return None


def discern_target(argv: list[str] | None = None) -> dict[str, Any]:
    argv = argv or []
    doctrine = _load(DOCTRINE, {})
    targets = {str(t.get("id")): t for t in doctrine.get("targets") or [] if t.get("id")}
    tid = _target_from_argv(argv) or _host_target()
    target = targets.get(tid)
    if not target:
        machine = tid.split("-")[-1] if "-" in tid else "x86_64"
        page_sizes = doctrine.get("silicon", {}).get("page_sizes", {})
        return {
            "id": tid,
            "target": {},
            "format": "elf",
            "backend": "bfd",
            "page_size": page_sizes.get(machine, 4096),
            "active": True,
            "unknown": True,
        }
    page_sizes = doctrine.get("silicon", {}).get("page_sizes", {})
    arch = str(target.get("arch") or "x86_64")
    return {
        "id": tid,
        "target": target,
        "format": target.get("format", "elf"),
        "backend": target.get("backend", "bfd"),
        "triple": target.get("triple"),
        "page_size": target.get("page_size") or page_sizes.get(arch, 4096),
        "active": bool(target.get("active", True)),
    }


def _no_field_files_witness(argv: list[str]) -> dict[str, Any]:
    nf = _mod(Path(__file__).resolve().parent / "g16-no-field-files.py", "g16_linker_no_field")
    if not nf or not hasattr(nf, "gate_link_outputs"):
        return {"ok": True, "skipped": "g16_no_field_files_missing"}
    return nf.gate_link_outputs(argv)


def _ammocode_field_witness() -> dict[str, Any]:
    instill = _mod(Path(__file__).resolve().parent.parent / "lib" / "g16-ammocode-field-instill.py", "g16_linker_ammocode")
    if not instill or not hasattr(instill, "meld_slice"):
        return {"ok": False, "error": "ammocode_instill_missing"}
    slice_doc = instill.meld_slice()
    return {
        "ok": bool(slice_doc.get("absorbed")) and slice_doc.get("no_subfields") is True,
        "instilled": bool(slice_doc.get("instilled")),
        "posture": slice_doc.get("posture"),
        "field": slice_doc.get("field"),
        "no_subfields": True,
        "citation": slice_doc.get("citation") or "ammocode:field:no_subfields",
        "meld_citation": slice_doc.get("meld_citation") or "ironclad:meld:2",
        "ammocode_field": slice_doc,
    }


def _ironclad_witness() -> dict[str, Any]:
    ic = _mod(Path(__file__).resolve().parent / "g16-ironclad.py", "g16_linker_ironclad")
    fs = _mod(Path(__file__).resolve().parent / "g16-field-sanity.py", "g16_linker_sanity")
    se = _mod(Path(__file__).resolve().parent / "g16-spatial-existence.py", "g16_linker_spatial")
    iron = ic.meld_slice() if ic and hasattr(ic, "meld_slice") else {"ok": False}
    sanity = fs.meld_slice() if fs and hasattr(fs, "meld_slice") else {"ok": False}
    spatial = se.meld_slice() if se and hasattr(se, "meld_slice") else {"absorbed": False}
    spatial_ok = bool(spatial.get("absorbed")) and bool(spatial.get("pass_ok", True))
    return {
        "ok": bool(iron.get("absorbed")) and bool(sanity.get("ok")) and spatial_ok,
        "ironclad_sealed": bool(iron.get("ironclad_sealed")),
        "meld_citation": iron.get("meld_citation") or "ironclad:meld:2",
        "citation": spatial.get("citation") or sanity.get("citation") or iron.get("citation") or "ironclad:spatial_existence:5",
        "canonical_hash": iron.get("canonical_hash"),
        "ironclad": iron,
        "field_sanity": sanity,
        "spatial_existence": spatial,
        "this_one": spatial.get("this_one"),
        "that_one": spatial.get("that_one"),
    }


def _flatten_mandate_flags(target: dict[str, Any], *, for_ld: bool = True) -> list[str]:
    fmt = str(target.get("format") or "elf")
    os_name = str(target.get("os") or "")
    if fmt == "mach-o":
        return ["-dead_strip"] if for_ld else ["-Wl,-dead_strip"]
    if fmt == "pe":
        return []
    if os_name == "android" or fmt == "elf":
        # BFD ld wants -zrelro not split -z relro (split form treats relro as input file)
        zflags = ["-zrelro", "-znow", "-znoexecstack"]
        pie: list[str] = []
        if os.environ.get("G16_LINKER_NO_PIE", "").strip().lower() not in ("1", "true", "yes"):
            pie = ["-pie"]
        if for_ld:
            return zflags + pie
        return [f"-Wl,{f}" for f in zflags + pie]
    return []


def linker_pass(argv: list[str] | None = None, *, witness_only: bool = False) -> dict[str, Any]:
    argv = argv or []
    doctrine = _load(DOCTRINE, {})
    disc = discern_target(argv)
    target = disc.get("target") or {}
    witness = _ironclad_witness()
    ammocode = _ammocode_field_witness()
    no_field = _no_field_files_witness(argv)
    mandate = _flatten_mandate_flags(target, for_ld=True)
    material = {
        "target": disc.get("id"),
        "format": disc.get("format"),
        "backend": disc.get("backend"),
        "triple": disc.get("triple"),
        "page_size": disc.get("page_size"),
        "mandate": mandate,
        "witness_ok": witness.get("ok"),
        "ammocode_field_ok": ammocode.get("ok"),
        "ammocode_no_subfields": ammocode.get("no_subfields"),
        "no_field_files_ok": no_field.get("ok"),
        "argv_len": len(argv),
    }
    chain = hashlib.sha256(json.dumps(material, sort_keys=True, default=str).encode()).hexdigest()
    ok = (
        bool(witness.get("ok"))
        and bool(ammocode.get("ok"))
        and bool(no_field.get("ok"))
        and disc.get("active", True)
    )
    doc = {
        "schema": "g16-linker-pass/v1",
        "updated": _now(),
        "ok": ok,
        "pass_ok": ok,
        "witness": witness,
        "ammocode_field": ammocode,
        "no_field_files": no_field,
        "never_poison_the_well": bool(no_field.get("ok")),
        "discern": disc,
        "mandate_flags": mandate,
        "chain_hash": chain,
        "meld_citation": witness.get("meld_citation"),
        "citation": witness.get("citation"),
        "silicon": doctrine.get("silicon"),
        "pass": doctrine.get("pass"),
        "targets_supported": len(doctrine.get("targets") or []),
    }
    if witness_only:
        doc.pop("pass", None)
    return doc


def _link_kind(argv: list[str]) -> str:
    """Classify link invocation so mandate flags do not break -shared/-r links."""
    if "-shared" in argv:
        return "shared"
    if "-r" in argv or "-relocatable" in argv:
        return "relocatable"
    if "-static" in argv or "-static-pie" in argv:
        return "static"
    return "executable"


def _mandate_for_argv(mandate: list[str], argv: list[str]) -> list[str]:
    kind = _link_kind(argv)
    if kind == "shared":
        # -pie turns ET_DYN shared objects into PIE executables (breaks libgcc_s et al.)
        return [f for f in mandate if f != "-pie"]
    if kind in ("relocatable", "static"):
        return []
    return list(mandate)


def _link_output(argv: list[str]) -> Path | None:
    if "-o" not in argv:
        return None
    idx = argv.index("-o")
    if idx + 1 >= len(argv):
        return None
    return Path(argv[idx + 1])


def _instill_link_output(argv: list[str]) -> dict[str, Any] | None:
    out = _link_output(argv)
    if not out or not out.is_file():
        return None
    instill = _mod(Path(__file__).resolve().parent.parent / "lib" / "g16-ammocode-field-instill.py", "g16_linker_instill")
    if not instill or not hasattr(instill, "instill_binary"):
        return None
    try:
        surface = os.environ.get("G16_AMMOCODE_SURFACE", "").strip() or None
        return instill.instill_binary(out, surface=surface, meta={"lane": "link"})
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:160]}


def _inject_flags(argv: list[str], extra: list[str]) -> list[str]:
    extra = _mandate_for_argv(extra, argv)
    if not extra:
        return argv
    present = set(argv)
    injected = [f for f in extra if f not in present]
    if not injected:
        return argv
    out = list(argv)
    if "-o" in out:
        idx = out.index("-o")
        out[idx:idx] = injected
    else:
        out[1:1] = injected
    return out


def _bfd_backend() -> Path:
    for candidate in (
        _prefix() / "libexec" / "grok16" / "g16-ld-bfd",
        _prefix() / "bin" / "g16-ld-bfd",
    ):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return _prefix() / "libexec" / "grok16" / "g16-ld-bfd"


def _ndk_root() -> Path | None:
    for key in ("ANDROID_NDK_ROOT", "ANDROID_NDK", "NDK_ROOT"):
        val = os.environ.get(key, "").strip()
        if val and Path(val).is_dir():
            return Path(val)
    return None


def _ndk_ld(target: dict[str, Any]) -> Path | None:
    ndk = _ndk_root()
    if not ndk:
        return None
    api = int(target.get("api") or os.environ.get("ANDROID_API", 33))
    triple = str(target.get("triple") or "")
    prebuilt = ndk / "toolchains" / "llvm" / "prebuilt"
    if not prebuilt.is_dir():
        return None
    hosts = sorted(prebuilt.iterdir())
    if not hosts:
        return None
    bindir = hosts[0] / "bin"
    for name in (
        f"ld.{triple}{api}",
        f"{triple}{api}-ld",
        "ld.lld",
        "ld",
    ):
        candidate = bindir / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None


def _macho_ld() -> Path | None:
    env = os.environ.get("G16_MACHO_LD", "").strip()
    if env and Path(env).is_file():
        return Path(env)
    for cmd in (
        ["xcrun", "--find", "ld"],
        ["which", "ld"],
    ):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
            if proc.returncode == 0 and proc.stdout.strip():
                p = Path(proc.stdout.strip())
                if p.is_file():
                    return p
        except (OSError, subprocess.TimeoutExpired):
            pass
    for fixed in ("/usr/bin/ld", "/Library/Developer/CommandLineTools/usr/bin/ld"):
        if Path(fixed).is_file():
            return Path(fixed)
    return None


def _pe_ld() -> Path | None:
    env = os.environ.get("G16_PE_LD", "").strip()
    if env and Path(env).is_file():
        return Path(env)
    for name in ("lld-link", "lld", "ld.lld"):
        found = shutil.which(name)
        if found:
            return Path(found)
    return None


def _cross_ld(target: dict[str, Any]) -> Path | None:
    prefix = os.environ.get("G16_CROSS_PREFIX", "").strip()
    if not prefix:
        triple = str(target.get("triple") or "")
        if triple:
            found = shutil.which(f"{triple}-ld")
            if found:
                return Path(found)
        return None
    p = Path(prefix)
    if p.is_file():
        return p
    candidate = Path(f"{prefix}ld") if not str(prefix).endswith("-") else Path(f"{prefix}ld")
    return candidate if candidate.is_file() else None


def resolve_backend(disc: dict[str, Any]) -> dict[str, Any]:
    target = disc.get("target") or {}
    backend = str(disc.get("backend") or "bfd")
    path: Path | None = None
    if backend == "bfd":
        path = _cross_ld(target) or _bfd_backend()
    elif backend == "android-ndk":
        path = _ndk_ld(target) or _cross_ld(target) or _bfd_backend()
    elif backend == "mach-o":
        path = _macho_ld()
    elif backend == "pe":
        path = _pe_ld()
    return {
        "backend": backend,
        "path": str(path) if path else "",
        "resolved": bool(path and path.is_file()),
    }


def _run_backend(path: Path, argv: list[str]) -> int:
    try:
        proc = subprocess.run([str(path), *argv[1:]], check=False)
        return int(proc.returncode)
    except OSError as exc:
        sys.stderr.write(f"g16-linker: exec {path} failed: {exc}\n")
        return 127


def _dispatch(argv: list[str], disc: dict[str, Any], mandate: list[str]) -> int:
    target = disc.get("target") or {}
    resolved = resolve_backend(disc)
    path_s = resolved.get("path") or ""
    if not path_s:
        sys.stderr.write(
            f"g16-linker: no backend for {disc.get('id')} ({disc.get('backend')}/{disc.get('format')})\n"
            f"  hint: set ANDROID_NDK_ROOT, G16_MACHO_LD, G16_PE_LD, or G16_CROSS_PREFIX\n"
        )
        return 127
    path = Path(path_s)
    nargv = _inject_flags(list(argv), mandate)
    emu = target.get("emulation")
    if emu and disc.get("backend") == "bfd":
        joined = " ".join(nargv)
        if "-m" not in nargv and f"-m{emu}" not in joined:
            nargv[1:1] = ["-m", str(emu)]
    ndk = _ndk_root()
    if disc.get("backend") == "android-ndk" and ndk and "--sysroot" not in nargv:
        sysroot = ndk / "toolchains" / "llvm" / "prebuilt"
        hosts = sorted(sysroot.iterdir()) if sysroot.is_dir() else []
        if hosts:
            triple = str(target.get("triple") or "aarch64-linux-android")
            api = int(target.get("api") or 33)
            root = hosts[0] / "sysroot"
            if root.is_dir():
                nargv[1:1] = [f"--sysroot={root}", f"-dynamic-linker=/system/bin/linker64"]
    return _run_backend(path, nargv)


def link(argv: list[str]) -> int:
    if not argv:
        sys.stderr.write("g16-linker: usage: g16-linker.py link [ld args...]\n")
        return 2
    doc = linker_pass(argv)
    resolved = resolve_backend(doc.get("discern") or {})
    doc["backend_resolve"] = resolved
    _save(PANEL, {**doc, "panel_schema": "g16-linker-panel/v1", "argv_head": argv[:8]})
    _append_ledger({
        "ts": doc.get("updated"),
        "ok": doc.get("ok"),
        "target": (doc.get("discern") or {}).get("id"),
        "backend": resolved.get("backend"),
        "chain_hash": doc.get("chain_hash"),
        "citation": doc.get("citation"),
    })
    if not doc.get("pass_ok") and os.environ.get("G16_LINKER_ALLOW_UNWITNESSED", "").strip().lower() not in ("1", "true", "yes"):
        sys.stderr.write("g16-linker: link pass blocked — unwittnessed (set G16_LINKER_ALLOW_UNWITNESSED=1 to override)\n")
        return 2
    if not resolved.get("resolved"):
        sys.stderr.write(
            f"g16-linker: backend unresolved for {(doc.get('discern') or {}).get('id')} "
            f"({resolved.get('backend')})\n"
        )
        return 127
    rc = _dispatch(argv, doc.get("discern") or {}, doc.get("mandate_flags") or [])
    if rc == 0:
        instill = _instill_link_output(argv)
        if instill and instill.get("ok"):
            doc["ammocode_field_instill"] = instill
            _save(PANEL, {**doc, "panel_schema": "g16-linker-panel/v1", "argv_head": argv[:8]})
        elif instill and not instill.get("ok"):
            sys.stderr.write(f"g16-linker: ammocode field instill failed: {instill.get('error', instill)}\n")
    return rc


def list_targets() -> dict[str, Any]:
    doctrine = _load(DOCTRINE, {})
    return {
        "schema": "g16-linker-targets/v1",
        "updated": _now(),
        "host": _host_target(),
        "targets": doctrine.get("targets") or [],
    }


def meld_slice() -> dict[str, Any]:
    cached = _load(PANEL, {})
    if cached.get("schema") == "g16-linker-pass/v1":
        disc = cached.get("discern") or {}
        return {
            "id": "g16_linker",
            "absorbed": bool(cached.get("ok")),
            "pass_ok": bool(cached.get("pass_ok")),
            "target": disc.get("id"),
            "format": disc.get("format"),
            "backend": disc.get("backend"),
            "targets_supported": cached.get("targets_supported"),
            "citation": cached.get("citation"),
            "meld_citation": cached.get("meld_citation"),
            "chain_hash": cached.get("chain_hash"),
            "updated": cached.get("updated"),
        }
    doc = linker_pass(witness_only=True)
    return {
        "id": "g16_linker",
        "absorbed": bool(doc.get("ok")),
        "pass_ok": bool(doc.get("pass_ok")),
        "target": (doc.get("discern") or {}).get("id"),
        "format": (doc.get("discern") or {}).get("format"),
        "backend": (doc.get("discern") or {}).get("backend"),
        "targets_supported": doc.get("targets_supported"),
        "citation": doc.get("citation"),
        "meld_citation": doc.get("meld_citation"),
        "chain_hash": doc.get("chain_hash"),
        "updated": doc.get("updated"),
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "panel", "status"):
        doc = linker_pass(witness_only=True)
        doc["panel_schema"] = "g16-linker-panel/v1"
        doc["backend_resolve"] = resolve_backend(doc.get("discern") or {})
        _save(PANEL, doc)
        print(json.dumps(doc, ensure_ascii=False))
        return 0
    if cmd == "pass":
        print(json.dumps(linker_pass(sys.argv[2:], witness_only=True), ensure_ascii=False))
        return 0
    if cmd == "slice":
        print(json.dumps(meld_slice(), ensure_ascii=False))
        return 0
    if cmd == "discern":
        print(json.dumps(discern_target(sys.argv[2:]), ensure_ascii=False))
        return 0
    if cmd == "targets":
        print(json.dumps(list_targets(), ensure_ascii=False))
        return 0
    if cmd == "resolve":
        disc = discern_target(sys.argv[2:])
        print(json.dumps(resolve_backend(disc), ensure_ascii=False))
        return 0
    if cmd == "link":
        return link(sys.argv[1:])
    print(json.dumps({"error": "usage: g16-linker.py [json|pass|slice|discern|targets|resolve|link ARGS...]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())