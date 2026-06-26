#!/usr/bin/env pythong
"""Wireframe graph builder + connected model probes for Training Viewer."""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _save(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def level_from_track(track: dict[str, Any] | None) -> str:
    if not track:
        return "pending"
    return str(track.get("level") or ("mastered" if track.get("mastered") else "complete" if track.get("complete") else "training" if track.get("ok") else "pending"))


def _status_color(level: str) -> str:
    lv = (level or "pending").lower()
    if lv in ("mastered", "g16_master"):
        return "#c084fc"
    if lv in ("complete", "fluent"):
        return "#4ade80"
    if lv in ("training", "online"):
        return "#38bdf8"
    if lv in ("error", "offline"):
        return "#f87171"
    return "#64748b"


def probe_model(model: dict[str, Any], *, install: Path, state: Path, hostess7: Path) -> dict[str, Any]:
    kind = str(model.get("kind") or "panel_file")
    mid = str(model.get("id") or "unknown")
    out: dict[str, Any] = {
        "id": mid,
        "label": model.get("label") or mid,
        "kind": kind,
        "online": False,
        "level": "pending",
        "score": 0.0,
        "detail": "",
        "probed_at": _now(),
    }
    try:
        if kind == "nexus_module":
            mod = str(model.get("module") or "")
            args = [str(a) for a in (model.get("args") or ["json"])]
            py = install / "lib" / mod
            if not py.is_file():
                out["level"] = "error"
                out["detail"] = f"missing {mod}"
                return out
            proc = subprocess.run(
                [sys.executable, str(py), *args],
                cwd=str(install),
                capture_output=True,
                text=True,
                timeout=int(model.get("timeout") or 45),
                env={**os.environ, "NEXUS_INSTALL_ROOT": str(install), "NEXUS_STATE_DIR": str(state), "HOSTESS7_ROOT": str(hostess7)},
            )
            text = (proc.stdout or "").strip()
            if text.startswith("{"):
                doc = json.loads(text)
                out["online"] = proc.returncode == 0
                out["payload"] = {k: doc.get(k) for k in (model.get("summary_keys") or ["tier", "score", "ok", "verdict", "g16_score", "programming_score"]) if k in doc}
                score_key = str(model.get("score_key") or "")
                if score_key and doc.get(score_key) is not None:
                    sc = float(doc[score_key])
                    out["score"] = sc if sc <= 1 else sc / 100.0
                tier = doc.get("tier") or doc.get("verdict")
                if tier:
                    out["level"] = str(tier)
                elif out["online"]:
                    out["level"] = "complete"
                out["detail"] = text[:400]
            else:
                out["online"] = proc.returncode == 0
                out["level"] = "complete" if out["online"] else "error"
                out["detail"] = text[:400] or (proc.stderr or "")[:200]

        elif kind == "panel_file":
            rel = str(model.get("path") or "")
            fp = state / rel if not rel.startswith("/") else Path(rel)
            if not fp.is_file():
                out["level"] = "pending"
                out["detail"] = f"no panel: {rel}"
                return out
            doc = _load(fp, {})
            out["online"] = True
            out["payload"] = {k: doc.get(k) for k in (model.get("summary_keys") or ["tier", "verdict", "ok"]) if k in doc}
            ready_key = model.get("ready_key")
            if ready_key and doc.get(ready_key):
                out["level"] = "complete"
            score_key = str(model.get("score_key") or "")
            if score_key and doc.get(score_key) is not None:
                sc = float(doc[score_key])
                out["score"] = sc if sc <= 1 else sc / 100.0
            if doc.get("mastered"):
                out["level"] = "mastered"
            elif doc.get("fluent") or doc.get("better_than_assistant"):
                out["level"] = "complete"
            out["detail"] = json.dumps(out.get("payload") or {}, ensure_ascii=False)[:300]

        elif kind == "install_data":
            rel = str(model.get("path") or "")
            fp = install / rel if not rel.startswith("/") else Path(rel)
            if not fp.is_file():
                out["level"] = "error"
                out["detail"] = f"missing {rel}"
                return out
            doc = _load(fp, {})
            out["online"] = True
            ready_key = str(model.get("ready_key") or "ready")
            if doc.get(ready_key) or doc.get("ready_g16") or doc.get("ready"):
                out["level"] = "complete"
            ver = (doc.get("toolchain") or {}).get("g16_version") or doc.get("g16_version")
            if ver:
                out["detail"] = f"v{ver}"
            tc = doc.get("toolchain") or doc
            if tc.get("dumpversion"):
                out["detail"] = f"g16 {tc.get('dumpversion')}"
            out["score"] = 0.92 if out["level"] == "complete" else 0.4
            out["payload"] = {"ready_g16": doc.get("ready_g16"), "version": ver or tc.get("dumpversion")}

        elif kind == "http_json":
            url = str(model.get("url") or "")
            req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Hostess7TrainingViewer/1.0"})
            with urllib.request.urlopen(req, timeout=int(model.get("timeout") or 8)) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
            doc = json.loads(raw) if raw.strip().startswith("{") else {"raw": raw[:200]}
            out["online"] = True
            out["level"] = "complete" if doc.get("ok", True) else "training"
            out["score"] = float(doc.get("overall_score") or doc.get("completion_level") == "mastered" and 1.0 or 0.75 if doc.get("solid") else 0.5)
            out["payload"] = {k: doc.get(k) for k in ("completion_level", "overall_score", "solid", "tracks_complete") if k in doc}
            out["detail"] = json.dumps(out["payload"], ensure_ascii=False)[:240]

        elif kind == "path_exists":
            p = Path(str(model.get("path") or ""))
            out["online"] = p.exists()
            out["level"] = "complete" if out["online"] else "offline"
            out["score"] = 1.0 if out["online"] else 0.0
            out["detail"] = str(p)

        else:
            out["level"] = "error"
            out["detail"] = f"unknown kind {kind}"
    except (OSError, subprocess.TimeoutExpired, urllib.error.URLError, json.JSONDecodeError, ValueError) as exc:
        out["level"] = "offline" if kind == "http_json" else "error"
        out["detail"] = str(exc)[:200]
    out["color"] = model.get("color") or _status_color(out["level"])
    return out


def _ring_pos(i: int, n: int, radius: float, y: float, phase: float = 0.0) -> tuple[float, float, float]:
    if n <= 0:
        return 0.0, y, 0.0
    a = (2 * math.pi * i / n) + phase
    return radius * math.cos(a), y, radius * math.sin(a)


def build_wireframe_graph(
    bundle: dict[str, Any],
    models_doc: dict[str, Any],
    *,
    install: Path,
    state: Path,
    hostess7: Path,
) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    node_ids: set[str] = set()

    def add_node(**kw: Any) -> str:
        nid = str(kw["id"])
        if nid in node_ids:
            return nid
        node_ids.add(nid)
        level = str(kw.get("level") or "pending")
        nodes.append({
            "id": nid,
            "label": kw.get("label") or nid,
            "group": kw.get("group") or "misc",
            "level": level,
            "score": float(kw.get("score") or 0),
            "color": kw.get("color") or _status_color(level),
            "x": float(kw.get("x") or 0),
            "y": float(kw.get("y") or 0),
            "z": float(kw.get("z") or 0),
            "detail": kw.get("detail") or "",
            "payload": kw.get("payload") or {},
            "kind": kw.get("kind") or "builtin",
        })
        return nid

    def add_edge(frm: str, to: str, kind: str = "meld") -> None:
        if frm in node_ids and to in node_ids:
            edges.append({"from": frm, "to": to, "kind": kind})

    assessment = bundle.get("assessment") or {}
    tracks = assessment.get("tracks") or {}
    a_overall = float(assessment.get("overall_score") or 0)
    a_level = str(assessment.get("completion_level") or "pending")

    add_node(
        id="hostess7_core",
        label="Hostess 7",
        group="core",
        level=a_level,
        score=a_overall,
        x=0, y=0, z=0,
        detail=bundle.get("training_panel", {}).get("reason") or "Super Intelligence core",
        kind="core",
    )

    mastery = assessment.get("mastery_facets") or bundle.get("training_panel", {}).get("mastery_facets") or {}
    facet_defs = [
        ("flexibility", "Flexibility", "#38bdf8", 0.0),
        ("adaptability", "Adaptability", "#f4a261", 2.094),
        ("confidence", "Confidence", "#c084fc", 4.189),
    ]
    for fid, flabel, fcolor, phase in facet_defs:
        facet = (mastery.get("facets") or {}).get(fid) or {}
        flv = str(facet.get("level") or "pending")
        fsc = float(facet.get("score") or 0)
        fx, fy, fz = _ring_pos(0, 1, 2.2, 0.0, phase)
        add_node(
            id=f"facet_{fid}",
            label=flabel,
            group="mastery_facet",
            level=flv,
            score=fsc,
            x=fx, y=fy, z=fz,
            color=fcolor,
            detail=str(facet.get("definition") or "")[:120],
            kind="mastery_facet",
            payload={"signals": facet.get("signals") or {}, "mastered": facet.get("mastered")},
        )
        add_edge(f"facet_{fid}", "hostess7_core", "mastery")

    stack = _load(install / "data" / "hostess7-neural-stack.json", {})
    series_phase = 0.0
    for si, series in enumerate(stack.get("series") or []):
        sid = str(series.get("id") or f"series_{si}")
        nets = series.get("nets") or []
        radius = 4.5 + si * 1.8
        y = (si - 3) * 1.4
        ring_id = f"ring_{sid}"
        rx, ry, rz = _ring_pos(0, 1, radius * 0.55, y)
        add_node(
            id=ring_id,
            label=str(series.get("label") or sid)[:32],
            group="series_ring",
            level="complete",
            score=0.85,
            x=rx, y=ry, z=rz,
            kind="series",
            detail=f"{len(nets)} nets",
        )
        add_edge("hostess7_core", ring_id, "series")

        for ni, net in enumerate(nets):
            nid = str(net.get("id") or f"net_{si}_{ni}")
            engine = str(net.get("engine") or net.get("corpus") or "")
            px, py, pz = _ring_pos(ni, max(len(nets), 1), radius, y, series_phase)
            lv = "pending"
            sc = 0.5
            track_map = {
                "hostess7_brain_guard": "brain_guard",
                "hostess7_brain": "brain_guard",
                "programming_chamber": "programming",
                "g16_chamber": "g16",
                "training_chamber": "master_curriculum",
                "calculator_chamber": "calculator",
                "biology_chamber": "biology",
                "engineering_chamber": "engineering",
                "combat_chamber": "combat",
                "mos_chamber": "mos",
            }
            if nid == "calculator_chamber":
                add_edge("vision", nid, "ocr_feed")
            if nid == "biology_chamber":
                add_edge("vision", nid, "ocr_feed")
                add_edge("medical", nid, "corpus_feed")
            if nid == "engineering_chamber":
                add_edge("vision", nid, "ocr_feed")
                add_edge("physics", nid, "corpus_feed")
            if nid == "combat_chamber":
                add_edge("vision", nid, "ocr_feed")
                add_edge("warfare", nid, "corpus_feed")
                add_edge("motion_chamber", nid, "motion_feed")
            if nid == "mos_chamber":
                add_edge("warfare", nid, "corpus_feed")
                add_edge("combat_chamber", nid, "combat_feed")
                add_edge("medical", nid, "medical_feed")
            if nid in track_map and track_map[nid] in tracks:
                t = tracks[track_map[nid]]
                lv = level_from_track(t)
                sc = float(t.get("score") or 0)
                if sc > 1:
                    sc /= 100.0
            elif "programming" in engine:
                t = tracks.get("programming")
                if t:
                    lv, sc = level_from_track(t), float(t.get("score") or 0.5)
            elif "g16" in engine:
                t = tracks.get("g16")
                if t:
                    lv, sc = level_from_track(t), float(t.get("score") or 0.5)
            elif "brain" in engine or "brain" in nid:
                t = tracks.get("brain_guard")
                if t:
                    lv, sc = level_from_track(t), float(t.get("score") or 0.5)

            add_node(
                id=nid,
                label=nid.replace("_", " ")[:22],
                group="think_tank" if sid == "think_tanks" else sid,
                level=lv,
                score=sc if sc <= 1 else sc / 100.0,
                x=px, y=py, z=pz,
                detail=str(net.get("role") or engine)[:120],
                kind="chamber",
                payload={"engine": engine},
            )
            add_edge(ring_id, nid, "chamber")
            if sid == "think_tanks":
                add_edge(nid, "hostess7_core", "meld")

        series_phase += 0.4

    track_order = list(tracks.keys())
    for ti, tid in enumerate(track_order):
        t = tracks[tid]
        tx, ty, tz = _ring_pos(ti, max(len(track_order), 1), 2.8, -3.5, 0.8)
        add_node(
            id=f"track_{tid}",
            label=str(t.get("label") or tid)[:24],
            group="training_track",
            level=level_from_track(t),
            score=float(t.get("score") or 0) if float(t.get("score") or 0) <= 1 else float(t.get("score") or 0) / 100.0,
            x=tx, y=ty, z=tz,
            detail=json.dumps({k: t.get(k) for k in ("tier", "verdict", "fluent", "mastered") if t.get(k) is not None}, ensure_ascii=False)[:160],
            kind="track",
        )
        add_edge("hostess7_core", f"track_{tid}", "training")

    steps = bundle.get("curriculum_steps") or []
    done = sum(1 for s in steps if s.get("completed"))
    cx, cy, cz = _ring_pos(0, 1, 3.2, 3.8)
    add_node(
        id="master_curriculum_hub",
        label=f"Curriculum {done}/{len(steps)}",
        group="curriculum",
        level="mastered" if done >= len(steps) and len(steps) else "training" if done else "pending",
        score=done / max(len(steps), 1),
        x=cx, y=cy, z=cz,
        kind="curriculum",
    )
    add_edge("hostess7_core", "master_curriculum_hub", "curriculum")
    for i, step in enumerate(steps[:18]):
        sid = str(step.get("id") or f"step_{i}")
        sx, sy, sz = _ring_pos(i, min(len(steps), 18), 5.2, 3.8, 1.2)
        add_node(
            id=f"cur_{sid}",
            label=sid[:18],
            group="curriculum_step",
            level="complete" if step.get("completed") else "pending",
            score=1.0 if step.get("completed") else 0.15,
            x=sx, y=sy, z=sz,
            detail=str(step.get("tip") or "")[:80],
            kind="curriculum_step",
        )
        add_edge("master_curriculum_hub", f"cur_{sid}", "step")

    fa = bundle.get("field_array") or {}
    slots = fa.get("slots") or []
    for i, slot in enumerate(slots[:16]):
        sid = str(slot.get("id") or f"slot_{i}")
        ox, oy, oz = _ring_pos(i, max(len(slots), 1), 8.5, -1.2, 2.0)
        add_node(
            id=f"omni_{sid}",
            label=str(slot.get("role") or sid)[:20],
            group="omnibus",
            level=str(slot.get("level") or "mastered"),
            score=0.95,
            x=ox, y=oy, z=oz,
            kind="omnibus",
        )
        add_edge("hostess7_core", f"omni_{sid}", "omnibus")

    probed_models: list[dict[str, Any]] = []
    for i, model in enumerate(models_doc.get("models") or []):
        probe = probe_model(model, install=install, state=state, hostess7=hostess7)
        probed_models.append({**model, "probe": probe})
        mid = str(model.get("id") or f"model_{i}")
        mx, my, mz = _ring_pos(i, max(len(models_doc.get("models") or []), 1), 10.5, 0.5, 0.5)
        saved = (models_doc.get("positions") or {}).get(mid)
        if saved:
            mx, my, mz = float(saved.get("x", mx)), float(saved.get("y", my)), float(saved.get("z", mz))
        add_node(
            id=f"ext_{mid}",
            label=str(model.get("label") or mid)[:22],
            group=str(model.get("group") or "connected"),
            level=probe.get("level") or "pending",
            score=float(probe.get("score") or 0),
            x=mx, y=my, z=mz,
            color=probe.get("color"),
            detail=probe.get("detail") or "",
            payload=probe.get("payload") or {},
            kind="connected",
        )
        for target in model.get("connect_to") or ["hostess7_core"]:
            tid = target if target in node_ids else target
            if tid not in node_ids:
                add_node(id=tid, label=target, group="link", level="pending", score=0.3, x=mx * 0.5, y=my * 0.5, z=mz * 0.5, kind="link")
            add_edge(f"ext_{mid}", tid, "connected")

    meld = _load(state / "field-plate-meld.json", {})
    if meld.get("chain_hash"):
        add_node(
            id="plate_meld",
            label="Plate meld",
            group="meld",
            level="complete",
            score=0.9,
            x=0, y=-4.2, z=0,
            detail=f"gen {meld.get('generation')} · {str(meld.get('chain_hash', ''))[:16]}…",
            kind="meld",
        )
        add_edge("plate_meld", "hostess7_core", "chain_hash")

    return {
        "schema": "hostess7-wireframe-graph/v1",
        "updated": _now(),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "connected_models": probed_models,
    }