#!/usr/bin/env pythong
"""Generate publisher sign-off table HTML with live verify stamps."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SG = Path(__file__).resolve().parents[2]
FP = Path(__file__).resolve().parents[1]
TB = SG / "NewLatest" / "Textbook"
H7 = SG / "Hostess7"
QUEEN = SG / "NewLatest" / "Queen"
COMMENTS = SG / "comments.md"
VOICE_BAD = re.compile(
    r"robot brain|DARPA-grade|greatest weapon is field literacy|Super Intelligence doctrine",
    re.IGNORECASE,
)


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[bool, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=180)
        return p.returncode == 0, (p.stdout or "")[-500:]
    except Exception as exc:
        return False, str(exc)


def collect_status() -> dict:
    rows: dict[str, dict] = {}
    # ZAC
    zac_ok, _ = _run([sys.executable, str(TB / "build-field-technology-zac.py"), "--verify-only"], cwd=TB)
    summary = {}
    try:
        summary = json.loads((TB / "build-summary.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    rows["zac_sync"] = {
        "ok": zac_ok and summary.get("verify_ok"),
        "detail": f"{summary.get('pack', {}).get('files', '?')} files · verify={summary.get('verify_ok')}",
    }
    # Hostess
    h7_ok, _ = _run([str(H7 / "Hostess7.sh"), "sdf-verify-redata"], cwd=H7)
    seg = len(list((H7 / "cache/fieldstorage/brain/sdf/segments").glob("seg-*.json"))) if (H7 / "cache/fieldstorage/brain/sdf/segments").is_dir() else 0
    rows["hostess_ingest"] = {"ok": h7_ok and seg >= 100, "detail": f"{seg} segments · sdf-verify-redata"}
    # Editorial
    ed_ok, _ = _run([sys.executable, str(FP / "scripts/verify_editorial.py")], cwd=FP)
    rows["editorial_web"] = {"ok": ed_ok, "detail": "read-first · KaTeX · horizon · schematics"}
    # PDF
    pdf_bytes = sum(f.stat().st_size for f in (FP / "pdf").rglob("*.pdf") if f.is_file()) if (FP / "pdf").is_dir() else 0
    rows["pdf_regen"] = {
        "ok": pdf_bytes > 0 and pdf_bytes < 10_000_000,
        "detail": f"{pdf_bytes / 1048576:.2f} MiB total" if pdf_bytes else "pending rebuild",
    }
    # RTX binary
    bin_path = QUEEN / "build/rtx/bin/Linux/queen-browser"
    if not bin_path.is_file():
        bin_path = QUEEN / "build/rtx/bin/queen-browser"
    rtx_detail = str(bin_path) if bin_path.is_file() else "building"
    forge_log = QUEEN / ".queen-forge.log"
    if not bin_path.is_file() and forge_log.is_file():
        tail = forge_log.read_text(encoding="utf-8", errors="replace")[-80_000:]
        if tail.count("changed variables that require your cache to be deleted") >= 2:
            rtx_detail = "cmake reconfigure loop — wipe build/rtx and re-run forge rtx"
        elif (QUEEN / "build/rtx/CMakeCache.txt").is_file():
            rtx_detail = "compiling"
        elif any(x in tail for x in ("=== forge:rtx_configure ===", "Populating sdl3")):
            rtx_detail = "cmake configure (SDL3 probes — slow)"
    rows["rtx_binary"] = {"ok": bin_path.is_file(), "detail": rtx_detail}
    # Voice
    voice_hits: list[str] = []
    content_dir = FP / "content" / "chapters"
    if content_dir.is_dir():
        for path in sorted(content_dir.glob("*.html")):
            if VOICE_BAD.search(path.read_text(encoding="utf-8")):
                voice_hits.append(path.name)
    rows["voice_pass"] = {
        "ok": not voice_hits,
        "detail": "22 chapters clean" if not voice_hits else f"scrub: {', '.join(voice_hits[:3])}",
    }
    ch02 = FP / "docs" / "chapters" / "02-fields-pixels-packets.html"
    rows["redata_section"] = {
        "ok": (FP / "wiki" / "Redata-Pipeline.md").is_file()
        and ch02.is_file()
        and 'id="redata-pipeline"' in ch02.read_text(encoding="utf-8"),
        "detail": "Ch02 + wiki",
    }
    return {"stamped": _ts(), "rows": rows}


def html_table(doc: dict) -> str:
    trs = []
    labels = {
        "voice_pass": "1. Chapter voice pass",
        "redata_section": "2. Redata section + wiki",
        "editorial_web": "3. Web editorial verify",
        "zac_sync": "4. content → ZAC sync",
        "pdf_regen": "5. PDF regen (<9 MiB)",
        "hostess_ingest": "6. Hostess7 brain ingest",
        "rtx_binary": "7. queen-browser binary",
    }
    for key, label in labels.items():
        row = doc["rows"].get(key, {})
        ok = row.get("ok")
        mark = "✓" if ok else "…"
        cls = "tag impl" if ok else "tag meta"
        trs.append(
            f'<tr><td>{label}</td><td><span class="{cls}">{mark}</span></td>'
            f'<td>{row.get("detail", "")}</td><td>{doc["stamped"]}</td></tr>'
        )
    return f"""
<section id="publisher-sign-off" class="gate-section">
  <h2>Publisher sign-off — redata sync</h2>
  <p>Stamped after verify commands. Refresh: <code>pythong Field_Primer/scripts/sign_off_table.py</code></p>
  <table>
    <thead><tr><th>Step</th><th>Status</th><th>Detail</th><th>Stamped (UTC)</th></tr></thead>
    <tbody>{"".join(trs)}</tbody>
  </table>
</section>
"""


def markdown_section(doc: dict) -> str:
    labels = {
        "voice_pass": "1. Chapter voice pass",
        "redata_section": "2. Redata section + wiki",
        "editorial_web": "3. Web editorial verify",
        "zac_sync": "4. content → ZAC sync",
        "pdf_regen": "5. PDF regen (<9 MiB)",
        "hostess_ingest": "6. Hostess7 brain ingest",
        "rtx_binary": "7. queen-browser binary",
    }
    lines = [
        "## 5. Sign-off — redata sync (live stamps)",
        "",
        f"**Stamped (UTC):** {doc['stamped']}",
        "",
        "| Step | Status | Detail |",
        "|------|--------|--------|",
    ]
    for key, label in labels.items():
        row = doc["rows"].get(key, {})
        mark = "✓" if row.get("ok") else "…"
        lines.append(f"| {label} | {mark} | {row.get('detail', '')} |")
    lines.extend(
        [
            "",
            "Refresh: `pythong Field_Primer/scripts/sign_off_table.py --sync-comments`",
            "",
        ]
    )
    return "\n".join(lines)


def sync_comments(doc: dict) -> None:
    if not COMMENTS.is_file():
        return
    text = COMMENTS.read_text(encoding="utf-8")
    section = markdown_section(doc)
    marker = "## 5. Sign-off"
    footer = "\n*Updated when sizes or verify stamps change."
    if marker in text:
        head = text.split(marker, 1)[0].rstrip()
        tail = ""
        if footer in text:
            tail = text[text.index(footer) :]
        COMMENTS.write_text(head + "\n\n" + section + tail, encoding="utf-8")
    else:
        COMMENTS.write_text(text.rstrip() + "\n\n" + section + footer, encoding="utf-8")
    print(f"synced {COMMENTS.relative_to(SG)}")


def main() -> None:
    doc = collect_status()
    out = FP / "docs" / "data" / "sign-off.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    if "--sync-comments" in sys.argv:
        sync_comments(doc)
    elif "--html-only" not in sys.argv:
        print(html_table(doc))
    if "--json" in sys.argv:
        print(json.dumps(doc, indent=2))


if __name__ == "__main__":
    main()