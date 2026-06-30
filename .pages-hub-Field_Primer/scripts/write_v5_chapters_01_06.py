#!/usr/bin/env python3
"""Write Field Technology v5 chapter body fragments 01-06 to content/chapters/."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "content" / "chapters"


def wc(s: str) -> int:
    return len(s.split())


def write(name: str, body: str) -> int:
    path = OUT_DIR / name
    path.write_text(body.strip() + "\n", encoding="utf-8")
    n = wc(body)
    print(f"{name}: {n} words")
    return n


# Import chapter bodies from companion module
from chapter_bodies_01_06 import (  # noqa: E402
    BODY_01,
    BODY_02,
    BODY_03,
    BODY_04,
    BODY_05,
    BODY_06,
)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bodies = [
        ("01.html", BODY_01),
        ("02.html", BODY_02),
        ("03.html", BODY_03),
        ("04.html", BODY_04),
        ("05.html", BODY_05),
        ("06.html", BODY_06),
    ]
    total = 0
    for name, body in bodies:
        total += write(name, body)
    print(f"TOTAL: {total} words across {len(bodies)} chapters")


if __name__ == "__main__":
    main()