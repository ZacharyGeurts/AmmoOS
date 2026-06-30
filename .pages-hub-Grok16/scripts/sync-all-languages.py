#!/usr/bin/env pythong
"""Sync every combinatoric language into grok16-languages.json + uncompiled .launch packages."""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
SG = Path(os.environ.get("SG_ROOT", ROOT.parent))
SEED = SG / "NewLatest" / "data" / "field-program-combinatronic-seed.json"
QUEEN_LANG = SG / "NewLatest" / "Queen" / "data" / "queen-code-languages.json"
LANG_JSON = ROOT / "data" / "grok16-languages.json"
LAUNCH_ROOT = ROOT / "examples" / "languages"

# Existing native / compiler-backed entries (preserved fields)
NATIVE: dict[str, dict[str, Any]] = {
    "c": {
        "extensions": [".c", ".h"],
        "driver": "g16-cc",
        "backend": "libexec/grok16/g16-cc",
        "std": "gnu17",
        "memory": "manual",
        "belt": "belt_2_0",
        "uncompiled": False,
        "launch_packaging": True,
    },
    "cxx": {
        "extensions": [".cpp", ".cxx", ".cc", ".C", ".hpp", ".hh", ".ixx"],
        "driver": "g16-cxx",
        "backend": "libexec/grok16/g16-cxx",
        "std": "gnu++26",
        "memory": "manual+RAII",
        "belt": "belt_2_0",
        "uncompiled": False,
        "launch_packaging": True,
    },
    "python": {
        "extensions": [".py", ".gpy"],
        "driver": "gpy-16",
        "tree": "python/",
        "pair": "GPY-16",
        "builtin": True,
        "memory": "gc",
        "secure": "truth_floor_58",
        "belt": "ai_agent",
        "uncompiled": True,
        "launch_packaging": True,
        "runtime": "python",
    },
    "asm": {
        "extensions": [".s", ".S", ".asm"],
        "driver": "g16-as",
        "memory": "manual",
        "belt": "field_opt",
        "uncompiled": False,
        "launch_packaging": True,
    },
    "fortran": {
        "extensions": [".f", ".f90", ".f95", ".f03", ".for"],
        "driver": "g16-gfortran",
        "memory": "manual",
        "belt": "belt_2_0",
        "uncompiled": False,
        "launch_packaging": True,
    },
    "rust": {
        "extensions": [".rs"],
        "driver": "g16-rust",
        "memory": "ownership",
        "secure_flags": "-D warnings -C overflow-checks=on",
        "belt": "memory_safe",
        "uncompiled": False,
        "launch_packaging": True,
    },
    "go": {
        "extensions": [".go"],
        "driver": "g16-go",
        "memory": "gc",
        "belt": "memory_safe",
        "uncompiled": False,
        "launch_packaging": True,
    },
    "zig": {
        "extensions": [".zig"],
        "driver": "g16-zig",
        "memory": "manual+comptime",
        "belt": "memory_safe",
        "uncompiled": False,
        "launch_packaging": True,
    },
    "d": {
        "extensions": [".d"],
        "driver": "g16-gdc",
        "memory": "gc_optional",
        "belt": "belt_2_0",
        "uncompiled": False,
        "launch_packaging": True,
    },
    "objc": {
        "extensions": [".m", ".mm"],
        "driver": "g16-objc",
        "memory": "arc",
        "belt": "belt_2_0",
        "uncompiled": False,
        "launch_packaging": True,
    },
    "ada": {
        "extensions": [".adb", ".ads"],
        "driver": "g16-gnat",
        "memory": "manual",
        "secure": "spark_subset",
        "belt": "memory_safe",
        "uncompiled": False,
        "launch_packaging": True,
    },
    "basic": {
        "extensions": [".bas", ".inc"],
        "driver": "g16-qbasic",
        "memory": "manual",
        "combinatronic": True,
        "belt": "belt_1_0",
        "universal_isa": ["x86", "m6502", "m6809", "z80", "coco"],
        "uncompiled": True,
        "launch_packaging": True,
        "runtime": "basic",
    },
    "qbasic": {
        "extends": "basic",
        "extensions": [".qb", ".qbs"],
        "driver": "g16-qbasic",
        "memory": "manual",
        "combinatronic": True,
        "belt": "belt_1_0",
        "universal_isa": ["x86"],
        "uncompiled": True,
        "launch_packaging": True,
        "runtime": "qbasic",
    },
    "pascal": {
        "extensions": [".pas", ".pp"],
        "driver": "g16-fpc",
        "memory": "manual",
        "combinatronic": True,
        "belt": "belt_2_0",
        "universal_isa": ["x86"],
        "uncompiled": True,
        "launch_packaging": True,
        "runtime": "pascal",
    },
    "turbo_pascal": {
        "extends": "pascal",
        "extensions": [".tp", ".tpu"],
        "driver": "g16-fpc",
        "memory": "manual",
        "combinatronic": True,
        "belt": "belt_2_0",
        "dialect": "turbo",
        "universal_isa": ["x86", "cyrix"],
        "uncompiled": True,
        "launch_packaging": True,
        "runtime": "turbo_pascal",
    },
    "ammolang": {
        "extensions": [".aml"],
        "driver": "g16-aml",
        "memory": "gc",
        "combinatronic": True,
        "belt": "belt_2_0",
        "product": "AmmoOS",
        "runtime": "ammolang",
        "universal_isa": ["x86", "arm", "riscv", "combinatronics"],
        "uncompiled": True,
        "launch_packaging": True,
    },
}

# Pascal family + retro — FPC driver, uncompiled launch
PASCAL_FAMILY = {
    "quickbasic": {"extends": "qbasic", "extensions": [".qbi"], "belt": "belt_1_0"},
    "freebasic": {"extends": "quickbasic", "extensions": [".bi", ".fb", ".fbi"], "belt": "belt_2_0", "driver": "g16-fpc"},
    "delphi": {"extends": "pascal", "extensions": [".dpr", ".dfm"], "belt": "belt_2_0"},
    "modula2": {"extends": "pascal", "extensions": [".mod"], "belt": "belt_2_0"},
    "visual_basic": {"extends": "basic", "extensions": [".vb", ".vbs"], "belt": "belt_1_0", "driver": "g16-interp"},
    "vba": {"extends": "visual_basic", "extensions": [".vba"], "belt": "belt_1_0"},
}

# Interpreted / uncompiled launch — g16-interp (no compile on launch)
INTERP: dict[str, dict[str, Any]] = {
    "javascript": {"extensions": [".js", ".mjs", ".cjs", ".jsx"], "belt": "belt_1_0", "runtime": "javascript"},
    "typescript": {"extends": "javascript", "extensions": [".ts", ".tsx"], "belt": "belt_2_0"},
    "java": {"extensions": [".java", ".kt", ".kts"], "belt": "belt_2_0", "runtime": "java"},
    "sql": {"extensions": [".sql"], "belt": "belt_1_0", "runtime": "sql"},
    "shell": {"extensions": [".sh", ".bash", ".zsh", ".ps1"], "belt": "belt_1_0", "runtime": "shell"},
    "haskell": {"extensions": [".hs", ".lhs"], "belt": "belt_2_0", "runtime": "haskell"},
    "lisp": {"extensions": [".lisp", ".lsp", ".cl"], "belt": "belt_1_0", "runtime": "lisp"},
    "ruby": {"extensions": [".rb"], "belt": "belt_1_0", "runtime": "ruby"},
    "php": {"extensions": [".php"], "belt": "belt_1_0", "runtime": "php"},
    "lua": {"extensions": [".lua"], "belt": "belt_1_0", "runtime": "lua"},
    "csharp": {"extensions": [".cs"], "belt": "belt_2_0", "runtime": "csharp"},
    "swift": {"extensions": [".swift"], "belt": "memory_safe", "runtime": "swift"},
    "kotlin": {"extends": "java", "extensions": [".kt", ".kts"], "belt": "memory_safe"},
    "cobol": {"extensions": [".cob", ".cbl"], "belt": "belt_1_0", "runtime": "cobol"},
    "prolog": {"extensions": [".pl", ".pro"], "belt": "belt_1_0", "runtime": "prolog"},
    "verilog": {"extensions": [".v", ".sv"], "belt": "belt_2_0", "runtime": "verilog"},
    "elixir": {"extensions": [".ex", ".exs"], "belt": "belt_1_0", "runtime": "elixir"},
    "erlang": {"extensions": [".erl", ".hrl"], "belt": "belt_1_0", "runtime": "erlang"},
    "scala": {"extensions": [".scala", ".sc"], "belt": "belt_2_0", "runtime": "scala"},
    "perl": {"extensions": [".pl", ".pm"], "belt": "belt_1_0", "runtime": "perl"},
    "r": {"extensions": [".r", ".R"], "belt": "belt_1_0", "runtime": "r"},
    "julia": {"extensions": [".jl"], "belt": "belt_2_0", "runtime": "julia"},
    "ocaml": {"extensions": [".ml", ".mli"], "belt": "belt_2_0", "runtime": "ocaml"},
    "clojure": {"extensions": [".clj", ".cljs", ".cljc"], "belt": "belt_1_0", "runtime": "clojure"},
    "matlab": {"extensions": [".m"], "belt": "belt_2_0", "runtime": "matlab"},
    "nim": {"extensions": [".nim"], "belt": "belt_2_0", "runtime": "nim"},
    "dart": {"extensions": [".dart"], "belt": "belt_1_0", "runtime": "dart"},
    "field": {"extensions": [".fld"], "belt": "belt_2_0", "runtime": "field", "combinatronic": True},
    "smalltalk": {"extensions": [".st"], "belt": "belt_1_0", "runtime": "smalltalk"},
    "forth": {"extensions": [".fs", ".fth"], "belt": "belt_1_0", "runtime": "forth"},
    "apl": {"extensions": [".apl"], "belt": "belt_1_0", "runtime": "apl"},
    "algol": {"extensions": [".alg"], "belt": "belt_1_0", "runtime": "algol"},
    "snobol": {"extensions": [".sno"], "belt": "belt_1_0", "runtime": "snobol"},
    "yaml": {"extensions": [".yaml", ".yml"], "belt": "belt_1_0", "runtime": "yaml"},
    "json": {"extensions": [".json", ".jsonc"], "belt": "belt_1_0", "runtime": "json"},
    "html": {"extensions": [".html", ".htm"], "belt": "belt_1_0", "runtime": "html"},
    "css": {"extensions": [".css"], "belt": "belt_1_0", "runtime": "css"},
    "markdown": {"extensions": [".md", ".markdown"], "belt": "belt_1_0", "runtime": "markdown"},
    "toml": {"extensions": [".toml"], "belt": "belt_1_0", "runtime": "toml"},
    "xml": {"extensions": [".xml"], "belt": "belt_1_0", "runtime": "xml"},
    "dockerfile": {"extensions": [], "belt": "belt_1_0", "runtime": "dockerfile"},
    "makefile": {"extensions": [], "belt": "belt_1_0", "runtime": "makefile"},
    "cmake": {"extensions": [".cmake"], "belt": "belt_2_0", "runtime": "cmake"},
    "glsl": {"extensions": [".glsl", ".frag", ".vert"], "belt": "belt_2_0", "runtime": "glsl"},
    "graphql": {"extensions": [".graphql", ".gql"], "belt": "belt_1_0", "runtime": "graphql"},
    "ini": {"extensions": [".ini", ".cfg"], "belt": "belt_1_0", "runtime": "ini"},
    "log": {"extensions": [".log"], "belt": "belt_1_0", "runtime": "log"},
    "diff": {"extensions": [".diff", ".patch"], "belt": "belt_1_0", "runtime": "diff"},
    "plaintext": {"extensions": [".txt"], "belt": "belt_1_0", "runtime": "plaintext"},
    "wasm": {"extensions": [".wasm"], "belt": "belt_2_0", "runtime": "wasm"},
    "wat": {"extensions": [".wat"], "belt": "belt_2_0", "runtime": "wat"},
    "scss": {"extensions": [".scss"], "belt": "belt_1_0", "runtime": "scss"},
    "powershell": {"extensions": [".ps1", ".psm1"], "belt": "belt_1_0", "runtime": "powershell"},
    "vbscript": {"extensions": [".vbs"], "belt": "belt_1_0", "runtime": "vbscript"},
    "cobol_copy": {"extends": "cobol", "extensions": [".cpy"], "belt": "belt_1_0", "runtime": "cobol_copy"},
}

HELLO: dict[str, tuple[str, str]] = {
    "python": ("hello.py", '#!/usr/bin/env pythong\nprint("grok16 python interpreter")\n'),
    "c": ("hello.c", '#include <stdio.h>\nint main(void){puts("grok16 c");return 0;}\n'),
    "cxx": ("hello.cpp", '#include <iostream>\nint main(){std::cout<<"grok16 cxx\\n";}\n'),
    "rust": ("hello.rs", 'fn main(){println!("grok16 rust");}\n'),
    "go": ("hello.go", 'package main\nimport "fmt"\nfunc main(){fmt.Println("grok16 go")}\n'),
    "javascript": ("hello.js", 'console.log("grok16 javascript interpreter");\n'),
    "typescript": ("hello.ts", 'console.log("grok16 typescript interpreter");\n'),
    "java": ("hello.java", 'public class Hello{public static void main(String[]a){System.out.println("grok16 java");}}\n'),
    "shell": ("hello.sh", '#!/bin/sh\necho "grok16 shell interpreter"\n'),
    "sql": ("hello.sql", 'SELECT \'grok16 sql\' AS msg;\n'),
    "ruby": ("hello.rb", 'puts "grok16 ruby"\n'),
    "php": ("hello.php", '<?php echo "grok16 php\\n";\n'),
    "lua": ("hello.lua", 'print("grok16 lua")\n'),
    "haskell": ("hello.hs", 'main = putStrLn "grok16 haskell"\n'),
    "lisp": ("hello.lisp", '(format t "grok16 lisp~%")\n'),
    "perl": ("hello.pl", 'print "grok16 perl\\n";\n'),
    "basic": ("hello.bas", '10 PRINT "grok16 basic"\n'),
    "qbasic": ("hello.qb", 'PRINT "grok16 qbasic"\n'),
    "pascal": ("hello.pas", 'program Hello; begin writeln(\'grok16 pascal\'); end.\n'),
    "turbo_pascal": ("hello.tp", 'program Hello; begin writeln(\'grok16 turbo pascal\'); end.\n'),
    "ammolang": ("hello.aml", 'combinator observe { source "grok16" }\n'),
    "field": ("hello.fld", 'plate meld\nverdict ok\n'),
    "fortran": ("hello.f90", 'program hello\nprint *, "grok16 fortran"\nend program\n'),
    "asm": ("hello.s", '.section .data\nmsg: .asciz "grok16 asm\\n"\n'),
    "zig": ("hello.zig", 'const std=@import("std");pub fn main()!void{try std.io.getStdOut().writer().print("grok16 zig\\n",.{});}\n'),
    "d": ("hello.d", 'import std; void main(){writeln("grok16 d");}\n'),
    "ada": ("hello.adb", 'with Ada.Text_IO; procedure Hello is begin Ada.Text_IO.Put_Line("grok16 ada"); end Hello;\n'),
    "objc": ("hello.mm", '#import <Foundation/Foundation.h>\nint main(int argc,const char*argv[]){@autoreleasepool{puts("grok16 objc");}return 0;}\n'),
    "csharp": ("hello.cs", 'class H{static void Main(){System.Console.WriteLine("grok16 csharp");}}\n'),
    "swift": ("hello.swift", 'print("grok16 swift")\n'),
    "kotlin": ("hello.kt", 'fun main(){println("grok16 kotlin")}\n'),
    "cobol": ("hello.cob", '       IDENTIFICATION DIVISION.\n       PROGRAM-ID. HELLO.\n       PROCEDURE DIVISION.\n           DISPLAY "grok16 cobol".\n'),
    "prolog": ("hello.pl", 'main :- write("grok16 prolog"), nl.\n'),
    "verilog": ("hello.v", 'module hello; initial $display("grok16 verilog"); endmodule\n'),
    "elixir": ("hello.exs", 'IO.puts("grok16 elixir")\n'),
    "erlang": ("hello.erl", '-module(hello). -export([main/0]). main() -> io:format("grok16 erlang~n").\n'),
    "scala": ("hello.scala", 'object Hello extends App { println("grok16 scala") }\n'),
    "r": ("hello.r", 'cat("grok16 r\\n")\n'),
    "julia": ("hello.jl", 'println("grok16 julia")\n'),
    "ocaml": ("hello.ml", 'let () = print_endline "grok16 ocaml"\n'),
    "clojure": ("hello.clj", '(println "grok16 clojure")\n'),
    "matlab": ("hello.m", 'disp("grok16 matlab")\n'),
    "nim": ("hello.nim", 'echo "grok16 nim"\n'),
    "dart": ("hello.dart", 'void main(){print("grok16 dart");}\n'),
    "smalltalk": ("hello.st", 'Transcript show: \'grok16 smalltalk\'; cr.\n'),
    "forth": ("hello.fs", ': HELLO ." grok16 forth" CR ; HELLO\n'),
    "apl": ("hello.apl", '← \'grok16 apl\'\n'),
    "algol": ("hello.alg", 'begin printstring("grok16 algol") end\n'),
    "snobol": ("hello.sno", 'OUTPUT = "grok16 snobol"\nEND\n'),
    "cobol_copy": ("hello.cob", '       IDENTIFICATION DIVISION.\n       PROGRAM-ID. HELLOCP.\n       PROCEDURE DIVISION.\n           DISPLAY "grok16 cobol copy".\n'),
    "yaml": ("hello.yaml", '# grok16 yaml\nmessage: grok16 yaml\n'),
    "json": ("hello.json", '{"message": "grok16 json"}\n'),
    "html": ("hello.html", '<!DOCTYPE html><html><body><p>grok16 html</p></body></html>\n'),
    "css": ("hello.css", '/* grok16 css */\nbody::before{content:"grok16 css";}\n'),
    "markdown": ("hello.md", '# grok16 markdown\n'),
    "toml": ("hello.toml", 'message = "grok16 toml"\n'),
    "xml": ("hello.xml", '<?xml version="1.0"?><msg>grok16 xml</msg>\n'),
    "dockerfile": ("hello.dockerfile", 'FROM scratch\n# grok16 dockerfile\n'),
    "makefile": ("hello.makefile", 'all:\n\t@echo grok16 makefile\n'),
    "cmake": ("hello.cmake", 'message(STATUS "grok16 cmake")\n'),
    "glsl": ("hello.glsl", 'void main(){gl_FragColor=vec4(1.0);}\n'),
    "graphql": ("hello.graphql", 'query { __typename }\n'),
    "ini": ("hello.ini", '[grok16]\nmessage=grok16 ini\n'),
    "log": ("hello.log", 'grok16 log sample\n'),
    "diff": ("hello.diff", '--- a\n+++ b\n@@\n+grok16 diff\n'),
    "plaintext": ("hello.txt", 'grok16 plaintext\n'),
    "wasm": ("hello.wat", '(module (func (export "run") (result i32) i32.const 42))\n'),
    "wat": ("hello.wat", '(module (func (export "run") (result i32) i32.const 42))\n'),
    "scss": ("hello.scss", '$g16: "grok16 scss"; body::before{content:$g16;}\n'),
    "powershell": ("hello.ps1", 'Write-Host "grok16 powershell"\n'),
    "vbscript": ("hello.vbs", 'WScript.Echo "grok16 vbscript"\n'),
    "delphi": ("hello.dpr", 'program Hello; begin Writeln(\'grok16 delphi\'); end.\n'),
    "modula2": ("hello.mod", 'MODULE Hello; FROM InOut IMPORT WriteString; BEGIN WriteString("grok16 modula2") END Hello.\n'),
    "quickbasic": ("hello.qb", 'PRINT "grok16 quickbasic"\n'),
    "freebasic": ("hello.bas", 'PRINT "grok16 freebasic"\n'),
    "visual_basic": ("hello.vb", 'Module H\nSub Main()\nConsole.WriteLine("grok16 visual basic")\nEnd Sub\nEnd Module\n'),
    "vba": ("hello.vba", 'Sub Main()\nDebug.Print "grok16 vba"\nEnd Sub\n'),
}


def _load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _merge_lang(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    row = dict(base)
    for k, v in extra.items():
        if k == "extends":
            row[k] = v
        elif k == "extensions" and k in row:
            row[k] = sorted(set(row[k]) | set(v))
        else:
            row[k] = v
    return row


def _build_languages(seed_packs: set[str]) -> dict[str, dict[str, Any]]:
    langs: dict[str, dict[str, Any]] = {}
    for lid, spec in NATIVE.items():
        langs[lid] = dict(spec)
    for lid, extra in PASCAL_FAMILY.items():
        parent = str(extra.get("extends", "pascal"))
        base = dict(langs.get(parent, NATIVE.get("pascal", {})))
        row = _merge_lang(base, extra)
        row.setdefault("driver", "g16-fpc" if parent in ("pascal", "turbo_pascal") else "g16-qbasic")
        row.setdefault("memory", "manual")
        row.setdefault("combinatronic", True)
        row.setdefault("uncompiled", True)
        row.setdefault("launch_packaging", True)
        row.setdefault("runtime", lid)
        langs[lid] = row
    for lid, extra in INTERP.items():
        row = {
            "driver": "g16-interp",
            "memory": "gc",
            "combinatronic": True,
            "uncompiled": True,
            "launch_packaging": True,
            "runtime": extra.get("runtime", lid),
            **extra,
        }
        if extra.get("extends") and extra["extends"] in langs:
            row = _merge_lang(langs[extra["extends"]], row)
        langs[lid] = row
    # Ensure every seed pack has an entry
    for pack_id in sorted(seed_packs):
        pid = pack_id.lower()
        if pid not in langs:
            langs[pid] = {
                "extensions": [f".{pid}"],
                "driver": "g16-interp",
                "memory": "gc",
                "combinatronic": True,
                "uncompiled": True,
                "launch_packaging": True,
                "runtime": pid,
                "belt": "belt_1_0",
                "inferred": True,
            }
    return langs


def _launch_doc(lang_id: str, meta: dict[str, Any], entry: str) -> dict[str, Any]:
    runtime = str(meta.get("runtime") or lang_id)
    uncompiled = bool(meta.get("uncompiled", True))
    return {
        "schema": "queen-launch/v1",
        "title": lang_id,
        "chamber_root": f"${{GROK16_ROOT}}/examples/languages/{lang_id}",
        "entry": entry,
        "runtime": runtime,
        "cwd": ".",
        "env": {},
        "chamber": {
            "mode": "folder_mirror",
            "include": ["**/*"],
            "exclude": [
                "*.a", "*.o", "*.pyc", "*.so", "*.tmp", ".git", ".nexus-state",
                ".venv", "__pycache__", "build", "dist", "node_modules",
            ],
        },
        "uncompiled": uncompiled,
        "launch_packaging": True,
        "organized_field": {
            "schema": "queen-organized-field/v1",
            "field_depth": 0,
            "inspect_files": True,
            "compile": False,
            "compile_gate": False,
            "free_meld": True,
            "trim_excess": True,
            "runner_policy": {
                "python": "interpreter",
                "native": "bsp_reuse",
                "cmake": "staged_binary",
                "shell": "interpreter",
                runtime: "interpreter",
                "iron_exec_when_free_meld": True,
            },
        },
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scan": "fast",
    }


def _write_launches(langs: dict[str, dict[str, Any]]) -> list[str]:
    written: list[str] = []
    LAUNCH_ROOT.mkdir(parents=True, exist_ok=True)
    for lang_id in sorted(langs.keys()):
        meta = langs[lang_id]
        if not meta.get("launch_packaging"):
            continue
        hello = HELLO.get(lang_id)
        if not hello:
            ext = (meta.get("extensions") or [f".{lang_id}"])[0]
            if not str(ext).startswith("."):
                ext = f".{ext}"
            hello = (f"hello{ext}", f'// grok16 {lang_id} uncompiled launch\n')
        fname, body = hello
        lang_dir = LAUNCH_ROOT / lang_id
        lang_dir.mkdir(parents=True, exist_ok=True)
        entry_path = lang_dir / fname
        if not entry_path.is_file() or entry_path.read_text(encoding="utf-8") != body:
            entry_path.write_text(body, encoding="utf-8")
        launch_path = lang_dir / f"{lang_id}.launch"
        doc = _launch_doc(lang_id, meta, fname)
        launch_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(str(launch_path.relative_to(ROOT)))
    return written


def _write_grok16_json(langs: dict[str, Any]) -> dict[str, Any]:
    memory_safe = ["rust", "go", "zig", "ada", "swift", "kotlin", "python"]
    retro = ["basic", "qbasic", "quickbasic", "freebasic", "pascal", "turbo_pascal", "visual_basic", "vba"]
    doc = {
        "schema": "grok16-languages/v1",
        "product": "Grok16",
        "rule": "Unified g16 discerns every field language — uncompiled launch by default",
        "memory_safe": memory_safe,
        "manual_memory": ["c", "cxx", "asm", "fortran", "d", "pascal", "turbo_pascal", "basic", "qbasic", "forth", "verilog"],
        "retro_classic": retro,
        "combinatorics_native": ["ammolang", "field"],
        "uncompiled_default": True,
        "launch_packaging": True,
        "languages": langs,
        "hostess7": _load(LANG_JSON).get("hostess7") or {
            "truth_adapt_floor": 58,
            "mandate_cmake": "cmake/g16-field-mandate.cmake",
            "secure_profile": "hostess_secure",
            "forever_profile": "forever",
            "probe_cmd": "Hostess7.sh queen-grok16-probe",
        },
    }
    LANG_JSON.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc


def _update_queen_discern(langs: dict[str, Any]) -> None:
    queen = _load(QUEEN_LANG)
    if not queen:
        return
    queen["g16_discern"] = sorted(langs.keys())
    ext_map: dict[str, str] = dict(queen.get("extensions") or {})
    for lid, meta in langs.items():
        for e in meta.get("extensions") or []:
            ext_map[str(e).lower()] = lid
    queen["extensions"] = dict(sorted(ext_map.items()))
    profiles = dict(queen.get("profiles") or {})
    for lid, meta in langs.items():
        profiles.setdefault(lid, meta.get("belt") or "belt_1_0")
    queen["profiles"] = profiles
    QUEEN_LANG.write_text(json.dumps(queen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    seed = _load(SEED)
    packs = set((seed.get("language_packs") or {}).keys())
    langs = _build_languages(packs)
    doc = _write_grok16_json(langs)
    launches = _write_launches(langs)
    _update_queen_discern(langs)
    print(json.dumps({
        "ok": True,
        "languages": len(langs),
        "launches": len(launches),
        "seed_packs": len(packs),
        "grok16_languages": str(LANG_JSON),
        "launch_root": str(LAUNCH_ROOT),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())