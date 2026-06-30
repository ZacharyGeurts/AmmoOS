#!/usr/bin/env python3
"""Launch Grok16 build output window, then run every-language secure-chamber test matrix."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEXUS = Path(os.environ.get("NEXUS_INSTALL_ROOT", ROOT.parent.parent if ROOT.parent.name != "NewLatest" else ROOT.parent))
MATRIX = NEXUS / "lib" / "g16-language-test-matrix.py"


def main() -> int:
    port = os.environ.get("G16_TEST_WINDOW_PORT", "9488")
    argv = [sys.executable, str(MATRIX), "window", str(port)]
    env = {
        **os.environ,
        "NEXUS_INSTALL_ROOT": str(NEXUS),
        "GROK16_ROOT": os.environ.get("GROK16_ROOT", str(ROOT)),
        "SG_ROOT": os.environ.get("SG_ROOT", str(NEXUS.parent)),
        "NEXUS_STATE_DIR": os.environ.get("NEXUS_STATE_DIR", str(NEXUS / ".nexus-state")),
        "PYTHONPATH": os.pathsep.join(
            p for p in (str(NEXUS / "lib"), os.environ.get("PYTHONPATH", "")) if p
        ),
    }
    proc = subprocess.run(argv, env=env, check=False)
    return int(proc.returncode)


if __name__ == "__main__":
    raise SystemExit(main())