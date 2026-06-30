#!/usr/bin/env python3
"""Generate 4500+ word HTML chapter fragments for Field Technology v5 ch 01-06."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "content" / "chapters"


def p(*xs: str) -> str:
    return "\n".join(f"<p>{x}</p>" for x in xs)


def h2(title: str, *blocks: str) -> str:
    return f"<h2>{title}</h2>\n" + "\n".join(blocks)


def h3(title: str, *blocks: str) -> str:
    return f"<h3>{title}</h3>\n" + "\n".join(blocks)


def wc(s: str) -> int:
    return len(s.split())


def write_chapter(num: str, body: str) -> int:
    path = OUT / f"{num}.html"
    path.write_text(body.strip() + "\n", encoding="utf-8")
    n = wc(body)
    print(f"{num}.html: {n} words")
    return n


# Shared prose blocks reused with variation where noted
def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    total += write_chapter("01", body_01())
    total += write_chapter("02", body_02())
    total += write_chapter("03", body_03())
    total += write_chapter("04", body_04())
    total += write_chapter("05", body_05())
    total += write_chapter("06", body_06())
    print(f"TOTAL: {total}")


def body_01() -> str:
    parts: list[str] = []
    parts.append('<p class="eyebrow">Chapter 1 · Read this before you dispatch anything</p>')
    parts.append("""<div class="objectives">
<h2>Learning objectives</h2>
<ol>
<li>State the implemented definition of a <em>field</em> used throughout Field Technology v5.</li>
<li>Name the three axioms and give one stack example for each.</li>
<li>Distinguish <span class="tag impl">Implemented</span>, <span class="tag meta">Metaphor</span>, <span class="tag phil">Philosophy</span>, and <span class="tag vis">Visual</span> on every claim.</li>
<li>Locate Phi, Thermo, Flow (bindings 8–10) and FieldX86Die (binding 1).</li>
<li>Explain packet-field locality and planetary-weave <span class="tag vis">Visual</span> honesty.</li>
<li>Articulate God as Truth, Math, Existence without substituting philosophy for <code>grep</code>.</li>
<li>Map chapters 2–12 engineering core and bookmark chapter 12 rocks.</li>
</ol>
</div>""")

    parts.append(h2("What this book is",
        p(
            "This is <strong>Field Technology</strong> — a serious textbook for operators who build and defend continuous state on their own machines. It is not a marketing deck. It is not a substitute for reading headers. It is the long-form explanation of why AMOURANTHRTX, NEXUS-Shield, Queen, and KILROY exist, written so a patient reader can learn the stack the way you would learn thermodynamics or networking: definitions first, mechanisms second, honesty labels always.",
            "We write for the human at the keyboard. Daemons assist. Shaders evolve. Panels display. None of them inherit your conscience. If you remember only one sentence from this chapter, remember this: <strong>the greatest offensive and defensive weapon you will know is field literacy</strong> — reading continuous state, imposing boundary conditions, and refusing to let someone else narrate your perimeter.",
            "Field Technology v5 is the 2026 edition of that literacy. Earlier site versions taught the same spine with shorter chapters. This edition expands every engineering chapter to textbook depth: learning objectives, operator drills, failure modes, study questions, and explicit rocks beside every poetic name. The wiki beside this book remains a quick reference; these chapters are where you sit down with tea and learn the machine.",
            "The stack you will study is real software. AMOURANTHRTX is a Vulkan Field Die engine with analog fabric channels, a 64 MiB guest address space on the GPU, and thermodynamic accounting that prints to stderr. NEXUS-Shield is a local-first endpoint security layer that turns sockets into sentences in <code>field jsonl</code>. Queen is the sovereign RTX browser that holds every web gate — WebRTC through the Connection Gatekeeper, MP4 mandatory in-tree, EME held not omitted. KILROY is the Field OS kernel path when you need syscall-boundary field discipline.",
            "This primer ties the products together without pretending they are one monolithic binary. When you grep AMOURANTHRTX for gatekeeper verdicts you will not find them — that is NEXUS. When you search NEXUS for <code>vkCmdDispatch</code> you will not find it — that is AMOURANTHRTX. Field literacy includes knowing which repository owns which writable surface.",
        ),
        h3("Why a textbook, not a README",
            p(
                "README files answer how do I build it tonight. Textbooks answer what world am I entering, and what mistakes will hurt me in week six. The Field stack punishes category errors: treating shader art as instrumentation, treating proxy entropy as joules, treating a JSON verdict as physics, treating a visual ionosphere as a spectrum analyzer.",
                "We borrow the pedagogical shape of classical engineering texts: axioms, mechanisms, lab exercises, failure catalogs, summaries, questions. We refuse the shape of vendor whitepapers: unnamed metaphors, conflated layers, screenshots without stderr. When you finish Chapter 12, you should hold conversations with skeptical physicists and security engineers simultaneously — because you label every claim before you defend it.",
                "Long chapters are intentional. Field operators routinely debug across GPU dispatch, guest die addresses, and local socket archives in a single afternoon. The book length mirrors that cross-layer reality. You are not expected to memorize every knob on first read; you are expected to know where the honest sentence lives when a knob misbehaves.",
            ),
        ),
    ))

    # ... truncated in file - will append rest via StrReplace
    return "\n\n".join(parts)


if __name__ == "__main__":
    build()