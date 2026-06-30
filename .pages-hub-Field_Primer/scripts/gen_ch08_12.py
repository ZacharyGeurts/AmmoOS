#!/usr/bin/env python3
"""Generate chapters 08-12 body fragments (4500+ words each)."""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "content" / "chapters"


def wc(t: str) -> int:
    return len(t.split())


def write(name: str, body: str) -> None:
    path = OUT / name
    path.write_text(body.strip() + "\n", encoding="utf-8")
    print(f"{name}: {wc(body)} words")


# Import chapter bodies from companion module
from gen_ch08_12_bodies import CH08, CH09, CH10, CH11, CH12  # noqa: E402

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for fname, body in [
        ("08.html", CH08),
        ("09.html", CH09),
        ("10.html", CH10),
        ("11.html", CH11),
        ("12.html", CH12),
    ]:
        write(fname, body)