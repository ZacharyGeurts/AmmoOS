#!/usr/bin/env python3
"""Write full textbook body fragments for chapters 07-12."""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "content" / "chapters"


def wc(text: str) -> int:
    return len(text.split())


CHAPTERS = {}

# Chapter content will be loaded from separate files written by this script's main block
# We write each chapter inline below for maintainability.