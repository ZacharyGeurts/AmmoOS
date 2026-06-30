"""Grok16 forge engine — logging and subprocess dispatch."""
from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class ForgeContext:
    """Grok16 repo root — vendor/, build/, bin/ live here."""

    queen: Path
    install: Path
    state: Path
    jobs: int = field(default_factory=lambda: max(1, os.cpu_count() or 4))

    @classmethod
    def from_env(cls) -> ForgeContext:
        root = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
        jobs = int(os.environ.get("GROK16_BUILD_JOBS", os.environ.get("QUEEN_BUILD_JOBS", max(1, os.cpu_count() or 4))))
        return cls(
            queen=root,
            install=root,
            state=root / ".grok16-state",
            jobs=jobs,
        )

    @property
    def vendor(self) -> Path:
        return self.queen / "vendor"

    @property
    def forge_log(self) -> Path:
        return self.queen / ".grok16-forge.log"

    @property
    def state_log(self) -> Path:
        return self.state / "build.log"

    def env(self) -> dict[str, str]:
        return {
            **os.environ,
            "GROK16_ROOT": str(self.queen),
            "GROK16_BUILD_JOBS": str(self.jobs),
        }


@dataclass
class ForgeResult:
    ok: bool
    tool: str
    message: str = ""
    returncode: int = 0
    tail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "tool": self.tool,
            "message": self.message,
            "returncode": self.returncode,
            "tail": self.tail[-4000:] if self.tail else "",
        }


ToolFn = Callable[[ForgeContext, "ForgeEngine"], ForgeResult]
CheckFn = Callable[[ForgeContext], bool]


class ForgeEngine:
    def __init__(self, ctx: ForgeContext | None = None) -> None:
        self.ctx = ctx or ForgeContext.from_env()
        self._buffers: list[str] = []

    def log(self, line: str) -> None:
        stamp = f"[{_now()}] {line}"
        self._buffers.append(stamp)
        print(stamp, file=sys.stderr, flush=True)
        for path in (self.ctx.forge_log, self.ctx.state_log):
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(stamp + "\n")

    def run_stream(
        self,
        cmd: list[str],
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> int:
        self.log(f"$ {' '.join(cmd)}")
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd or self.ctx.queen),
            env=env or self.ctx.env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert proc.stdout is not None
        try:
            for line in proc.stdout:
                self.log(line.rstrip("\n"))
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            self.log("TIMEOUT — process killed")
            return 124
        return proc.returncode or 0

    def tail_buffer(self, n: int = 4000) -> str:
        text = "\n".join(self._buffers)
        return text[-n:] if len(text) > n else text