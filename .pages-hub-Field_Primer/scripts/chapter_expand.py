"""Helpers to render textbook sections from paragraph banks."""
from __future__ import annotations


def render_section(h2: str, paragraphs: list[str], h3_blocks: list[tuple[str, list[str]]] | None = None) -> str:
    parts = [f"<h2>{h2}</h2>"]
    parts.extend(f"<p>{p}</p>" for p in paragraphs)
    if h3_blocks:
        for h3, paras in h3_blocks:
            parts.append(f"<h3>{h3}</h3>")
            parts.extend(f"<p>{p}</p>" for p in paras)
    return "\n".join(parts)


def render_objectives(items: list[str]) -> str:
    lis = "\n".join(f"<li>{i}</li>" for i in items)
    return f"""<div class="objectives">
<h2>Learning objectives</h2>
<ol>
{lis}
</ol>
</div>"""


def render_study_questions(items: list[str], next_link: str = "") -> str:
    lis = "\n".join(f"<li>{i}</li>" for i in items)
    tail = f'\n<p><a href="{next_link}">Continue →</a></p>' if next_link else ""
    return f"<h2>Study questions</h2>\n<ol>\n{lis}\n</ol>{tail}"