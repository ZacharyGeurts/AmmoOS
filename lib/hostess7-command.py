#!/usr/bin/env python3
"""Hostess 7 Command Deck — two-way talk, GitHub NEXUS-Shield context, proposed updates."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
HOSTESS7_ROOT = Path(os.environ.get("HOSTESS7_ROOT", "/home/default/Desktop/SG/Hostess7"))
GITHUB_REPO = os.environ.get("NEXUS_GITHUB_REPO", "ZacharyGeurts/NEXUS-Shield")
TRANSCRIPT_JSONL = STATE / "hostess7-command.jsonl"
PANEL_CACHE = STATE / "hostess7-command-panel.json"
GITHUB_CACHE = STATE / "hostess7-github-cache.json"
UA = "NEXUS-Shield-Hostess7-Command/1.0"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _save_json(path: Path, doc: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _append_transcript(role: str, text: str, *, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {"ts": _now(), "role": role, "text": text.strip()}
    if meta:
        row["meta"] = meta
    TRANSCRIPT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with TRANSCRIPT_JSONL.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def _read_transcript(limit: int = 48) -> list[dict[str, Any]]:
    if not TRANSCRIPT_JSONL.is_file():
        return []
    rows: list[dict[str, Any]] = []
    try:
        for line in TRANSCRIPT_JSONL.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except OSError:
        return []
    return rows[-limit:]


def _http_text(url: str, timeout: float = 14.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _http_json(url: str, timeout: float = 14.0) -> Any:
    text = _http_text(url, timeout=timeout)
    return json.loads(text)


def _local_version() -> str:
    common = INSTALL / "lib" / "nexus-common.sh"
    if common.is_file():
        m = re.search(r'NEXUS_VERSION="([^"]+)"', common.read_text(encoding="utf-8", errors="replace"))
        if m:
            return m.group(1)
    return os.environ.get("NEXUS_VERSION", "unknown")


def _hostess7_available() -> bool:
    return (HOSTESS7_ROOT / "Hostess7.sh").is_file() and (
        HOSTESS7_ROOT / "scripts" / "field_superintelligence.py"
    ).is_file()


def _agents_on() -> bool:
    pid_file = HOSTESS7_ROOT / "cache" / "fieldstorage" / "brain" / "superintel" / "agents7" / "daemon.pid"
    if not pid_file.is_file():
        return False
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def _run_hostess7_ask(message: str, *, timeout: int = 90) -> dict[str, Any]:
    env = os.environ.copy()
    env["HOSTESS7_ROOT"] = str(HOSTESS7_ROOT)
    env["NO_AT_BRIDGE"] = "1"
    script = HOSTESS7_ROOT / "scripts" / "field_agents7.py" if _agents_on() else (
        HOSTESS7_ROOT / "scripts" / "field_superintelligence.py"
    )
    if not script.is_file():
        return {"ok": False, "error": "hostess7_brain_missing"}
    proc = subprocess.run(
        [sys.executable, str(script), "ask", message],
        cwd=str(HOSTESS7_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    raw = (proc.stdout or "").strip()
    reply_lines: list[str] = []
    for line in raw.splitlines():
        if line.startswith("METRIC ") or line in ("OK outbox", "OK medical", "OK"):
            continue
        reply_lines.append(line)
    reply = "\n".join(reply_lines).strip() or raw
    return {
        "ok": proc.returncode == 0 and bool(reply),
        "reply": reply,
        "engine": "agents7" if script.name == "field_agents7.py" else "superintelligence",
        "rc": proc.returncode,
        "stderr": (proc.stderr or "").strip()[:500],
    }


def fetch_github_nexus(*, force: bool = False) -> dict[str, Any]:
    cached = _load_json(GITHUB_CACHE, {})
    if cached and not force and cached.get("fetched_at"):
        return cached

    doc: dict[str, Any] = {
        "schema": "hostess7-github/v1",
        "repo": GITHUB_REPO,
        "repo_url": f"https://github.com/{GITHUB_REPO}",
        "fetched_at": _now(),
        "local_version": _local_version(),
    }
    try:
        readme = _http_text(f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/README.md", timeout=12)
        doc["readme_excerpt"] = readme[:3200]
    except (urllib.error.URLError, OSError, TimeoutError):
        doc["readme_excerpt"] = ""

    try:
        common = _http_text(
            f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/lib/nexus-common.sh",
            timeout=10,
        )
        m = re.search(r'NEXUS_VERSION="([^"]+)"', common)
        doc["github_main_version"] = m.group(1) if m else None
    except (urllib.error.URLError, OSError, TimeoutError):
        doc["github_main_version"] = None

    commits: list[dict[str, str]] = []
    try:
        rows = _http_json(f"https://api.github.com/repos/{GITHUB_REPO}/commits?per_page=6")
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                commits.append({
                    "sha": str((row.get("sha") or ""))[:7],
                    "message": str((row.get("commit") or {}).get("message") or "").split("\n")[0][:160],
                    "date": str((row.get("commit") or {}).get("author", {}).get("date") or ""),
                    "url": row.get("html_url") or "",
                })
    except (urllib.error.URLError, OSError, TimeoutError, json.JSONDecodeError):
        pass
    doc["recent_commits"] = commits

    try:
        update_py = INSTALL / "lib" / "nexus-update.py"
        if update_py.is_file():
            proc = subprocess.run(
                [sys.executable, str(update_py)],
                capture_output=True,
                text=True,
                timeout=20,
                env={**os.environ, "NEXUS_STATE_DIR": str(STATE), "NEXUS_INSTALL_ROOT": str(INSTALL)},
            )
            if proc.stdout.strip():
                doc["update_check"] = json.loads(proc.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        doc["update_check"] = {}

    if (INSTALL / ".git").is_dir():
        try:
            subprocess.run(
                ["git", "fetch", "origin", "main"],
                cwd=str(INSTALL),
                capture_output=True,
                timeout=30,
                check=False,
            )
            proc = subprocess.run(
                ["git", "log", "-1", "--format=%h %s", "origin/main"],
                cwd=str(INSTALL),
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if proc.stdout.strip():
                doc["local_git_origin_main"] = proc.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            pass

    _save_json(GITHUB_CACHE, doc)
    return doc


def _proposed_updates(github: dict[str, Any], panel: dict[str, Any] | None) -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []
    upd = github.get("update_check") or {}
    if upd.get("update_available"):
        proposals.append({
            "id": "nexus_release",
            "kind": "update",
            "title": f"Upgrade NEXUS-Shield {upd.get('previous') or upd.get('current')} → {upd.get('latest')}",
            "detail": (upd.get("release_notes") or "New release on GitHub.")[:600],
            "action": "apply_update",
            "url": upd.get("release_url") or f"https://github.com/{GITHUB_REPO}/releases",
        })

    gh_ver = github.get("github_main_version")
    local_ver = github.get("local_version") or _local_version()
    if gh_ver and local_ver and gh_ver != local_ver and not upd.get("update_available"):
        proposals.append({
            "id": "version_drift",
            "kind": "info",
            "title": f"GitHub main is v{gh_ver} · this machine runs v{local_ver}",
            "detail": "Hostess 7 reads ZacharyGeurts/NEXUS-Shield on every sync. Review commits before applying.",
            "action": "sync_github",
            "url": f"https://github.com/{GITHUB_REPO}/commits/main",
        })

    pulse = (panel or {}).get("field_command", {}).get("pulse") or {}
    if (pulse.get("threat_warnings") or 0) > 0:
        proposals.append({
            "id": "threat_review",
            "kind": "ops",
            "title": f"Review {pulse.get('threat_warnings')} threat warnings",
            "detail": "Field pulse flagged warnings — Hostess 7 recommends Threats · Map and Kill orders.",
            "action": "jump_threats",
        })

    if github.get("recent_commits"):
        top = github["recent_commits"][0]
        proposals.append({
            "id": "latest_commit",
            "kind": "github",
            "title": f"Latest commit {top.get('sha')}: {top.get('message', '')[:80]}",
            "detail": "Pulled from ZacharyGeurts/NEXUS-Shield main.",
            "action": "open_commit",
            "url": top.get("url") or f"https://github.com/{GITHUB_REPO}",
        })

    return proposals[:6]


def _field_context(panel: dict[str, Any] | None) -> str:
    panel = panel or _load_json(STATE / "threat-panel.json", {})
    cmd = panel.get("field_command") or {}
    pulse = cmd.get("pulse") or {}
    hh = cmd.get("heaven_hell") or {}
    parts = [
        f"NEXUS-Shield v{_local_version()} Command deck.",
        f"Heaven {hh.get('heaven_count', 0)} · Hell {hh.get('hell_count', 0)}.",
        f"Warnings {pulse.get('threat_warnings', 0)} · Hot targets {pulse.get('host_hot', 0)}.",
        f"Kill dossiers {pulse.get('human_dossier_ips', 0)} · Killed {pulse.get('attack_kit_killed', 0)}.",
    ]
    brain = panel.get("field_brain") or {}
    si = brain.get("superintelligence") or {}
    if si.get("arc"):
        parts.append(f"Superintel arc: {si.get('arc')}.")
    return " ".join(parts)


def _compose_prompt(user_message: str, github: dict[str, Any], panel: dict[str, Any] | None) -> str:
    commits = github.get("recent_commits") or []
    commit_line = "; ".join(f"{c.get('sha')}: {c.get('message', '')[:60]}" for c in commits[:3])
    readme = (github.get("readme_excerpt") or "")[:1200]
    upd = github.get("update_check") or {}
    update_line = ""
    if upd.get("update_available"):
        update_line = f" GitHub release v{upd.get('latest')} available (now v{upd.get('current')})."
    return (
        f"{_field_context(panel)} "
        f"Owner ZacharyGeurts. GitHub repo {GITHUB_REPO}. "
        f"Main version {github.get('github_main_version') or 'unknown'}.{update_line} "
        f"Recent commits: {commit_line or 'none'}. "
        f"README excerpt: {readme[:800]} "
        f"Operator says: {user_message}"
    )


def _local_reply(user_message: str, github: dict[str, Any], panel: dict[str, Any] | None) -> str:
    """Truth-only fallback when Hostess7 brain subprocess unavailable."""
    gh = github
    upd = gh.get("update_check") or {}
    lines = [
        "Hostess 7 here — brain subprocess quiet, speaking from live GitHub + field data only.",
        _field_context(panel),
    ]
    if upd.get("update_available"):
        lines.append(
            f"I propose updating NEXUS-Shield from v{upd.get('current')} to v{upd.get('latest')}. "
            f"Release: {upd.get('release_url')}"
        )
    if gh.get("recent_commits"):
        c = gh["recent_commits"][0]
        lines.append(f"Latest on ZacharyGeurts/NEXUS-Shield: {c.get('sha')} — {c.get('message')}")
    low = user_message.lower()
    if "github" in low or "repo" in low or "nexus-shield" in low:
        lines.append(f"I always read https://github.com/{GITHUB_REPO} — main branch and releases.")
    if "update" in low or "upgrade" in low:
        if upd.get("update_available"):
            lines.append("Use the proposed update chip on Command, or Settings → Check for updates.")
        else:
            lines.append(f"You are current at v{gh.get('local_version') or _local_version()} per GitHub check.")
    lines.append("What should we harden next on the field?")
    return "\n\n".join(lines)


def ask_operator(message: str, *, panel: dict[str, Any] | None = None) -> dict[str, Any]:
    message = (message or "").strip()
    if not message:
        return {"ok": False, "error": "empty_message"}
    _append_transcript("operator", message)
    github = fetch_github_nexus()
    panel = panel or _load_json(STATE / "threat-panel.json", {})
    prompt = _compose_prompt(message, github, panel)

    result: dict[str, Any]
    if _hostess7_available():
        brain = _run_hostess7_ask(prompt)
        if brain.get("ok") and brain.get("reply"):
            result = {
                "ok": True,
                "reply": brain["reply"],
                "engine": brain.get("engine"),
                "thinking": False,
            }
        else:
            result = {
                "ok": True,
                "reply": _local_reply(message, github, panel),
                "engine": "nexus_field_fallback",
                "thinking": False,
                "brain_error": brain.get("stderr") or brain.get("error"),
            }
    else:
        result = {
            "ok": True,
            "reply": _local_reply(message, github, panel),
            "engine": "nexus_field_fallback",
            "thinking": False,
        }

    _append_transcript("hostess7", result["reply"], meta={"engine": result.get("engine")})
    result["proposed_updates"] = _proposed_updates(github, panel)
    result["github"] = {
        "repo": GITHUB_REPO,
        "main_version": github.get("github_main_version"),
        "local_version": github.get("local_version"),
        "commits": (github.get("recent_commits") or [])[:4],
    }
    return result


def build_panel(*, panel_doc: dict[str, Any] | None = None) -> dict[str, Any]:
    panel_doc = panel_doc or _load_json(STATE / "threat-panel.json", {})
    github = fetch_github_nexus()
    transcript = _read_transcript(40)
    if not transcript:
        greeting = (
            "Hostess 7 online on Command. I read ZacharyGeurts/NEXUS-Shield on GitHub and your live field. "
            "Talk to me — I'll think, propose updates, and speak back."
        )
        _append_transcript("hostess7", greeting, meta={"engine": "boot"})
        transcript = _read_transcript(40)

    return {
        "schema": "hostess7-command/v1",
        "updated": _now(),
        "motto": "Hostess 7 · superintelligence on Command — talk, think, propose, speak.",
        "owner": "ZacharyGeurts",
        "github_repo": GITHUB_REPO,
        "github_url": f"https://github.com/{GITHUB_REPO}",
        "hostess7_available": _hostess7_available(),
        "agents_on": _agents_on(),
        "local_version": _local_version(),
        "github_main_version": github.get("github_main_version"),
        "github": github,
        "transcript": transcript,
        "proposed_updates": _proposed_updates(github, panel_doc),
        "field_context": _field_context(panel_doc),
        "voice_enabled": True,
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "json":
        doc = build_panel()
        _save_json(PANEL_CACHE, doc)
        print(json.dumps(doc, ensure_ascii=False))
        return 0
    if cmd == "ask" and len(sys.argv) >= 3:
        msg = " ".join(sys.argv[2:])
        print(json.dumps(ask_operator(msg), ensure_ascii=False))
        return 0
    if cmd in ("sync-github", "sync_github"):
        doc = fetch_github_nexus(force=True)
        print(json.dumps({"ok": True, "github": doc}, ensure_ascii=False))
        return 0
    if cmd == "panel":
        doc = build_panel()
        _save_json(PANEL_CACHE, doc)
        print(json.dumps(doc, ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: hostess7-command.py [json|ask MSG|sync-github|panel]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())