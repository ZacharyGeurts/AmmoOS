#!/usr/bin/env pythong
"""Hostess 7 training completion — run all tracks to solid Master levels."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
DOCTRINE = INSTALL / "data" / "hostess7-training-doctrine.json"
FACETS = INSTALL / "data" / "hostess7-mastery-facets.json"
PANEL = STATE / "hostess7-training-panel.json"
RUNTIME = STATE / "hostess7-training-runtime.json"
LEDGER = STATE / "hostess7-training-ledger.jsonl"

ENABLED = os.environ.get("NEXUS_HOSTESS7_TRAINING", "1") == "1"


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


def _append_ledger(row: dict[str, Any]) -> None:
    try:
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _mod(name: str, rel: str) -> Any | None:
    try:
        import importlib.util

        py = INSTALL / "lib" / rel
        if not py.is_file():
            return None
        spec = importlib.util.spec_from_file_location(name, py)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


def _level_id(score: float, *, complete: bool, mastered: bool) -> str:
    if mastered:
        return "mastered"
    if complete:
        return "complete"
    if score > 0:
        return "training"
    return "pending"


def _assess_master() -> dict[str, Any]:
    master = _mod("h7master", "hostess7-master.py")
    if not master:
        return {"ok": False, "level": "pending", "complete": False, "mastered": False}
    st = master.master_status()
    lvl = st.get("level") or {}
    total = int(st.get("curriculum_total") or 0)
    done = int(st.get("curriculum_done") or 0)
    xp = int(st.get("xp") or 0)
    doc = _load(DOCTRINE, {})
    floor = int(doc.get("master_xp_floor") or 160)
    complete = done >= total and total > 0 and xp >= floor
    mastered = bool(lvl.get("is_master")) and complete
    score = min(1.0, (done / max(total, 1)) * 0.5 + min(1.0, xp / floor) * 0.5)
    return {
        "ok": True,
        "level": _level_id(score, complete=complete, mastered=mastered),
        "complete": complete,
        "mastered": mastered,
        "score": round(score, 4),
        "xp": xp,
        "curriculum_done": done,
        "curriculum_total": total,
        "tier": lvl.get("label"),
        "is_master": lvl.get("is_master"),
    }


def _assess_programming() -> dict[str, Any]:
    prog = _mod("h7prog", "hostess7-programming.py")
    if not prog:
        panel = _load(STATE / "hostess7-programming-panel.json", {})
    else:
        panel = prog.build_panel(write=False)
    tier = str(panel.get("tier") or "")
    score_f = float(panel.get("programming_score") or 0)
    better = bool(panel.get("better_than_assistant"))
    complete = tier in ("hostess7_operator", "hostess7_master") and better
    mastered = tier == "hostess7_master" and better
    return {
        "ok": True,
        "level": _level_id(score_f, complete=complete, mastered=mastered),
        "complete": complete,
        "mastered": mastered,
        "score": score_f,
        "tier": tier,
        "better_than_assistant": better,
    }


def _assess_calculator() -> dict[str, Any]:
    calc = _mod("h7calc", "hostess7-calculator.py")
    panel = calc.build_panel(write=False) if calc else _load(STATE / "hostess7-calculator-panel.json", {})
    tier = str(panel.get("tier") or "")
    score_f = float(panel.get("calculator_score") or 0)
    fluent = bool(panel.get("fluent"))
    mastered = bool(panel.get("mastered"))
    complete = fluent and tier in ("calculator_fluent", "calculator_master")
    return {
        "ok": True,
        "level": _level_id(score_f, complete=complete, mastered=mastered),
        "complete": complete,
        "mastered": mastered,
        "score": score_f,
        "tier": tier,
        "fluent": fluent,
        "battery_pass_rate": panel.get("battery_pass_rate"),
    }


def _assess_biology() -> dict[str, Any]:
    bio = _mod("h7bio", "hostess7-biology.py")
    panel = bio.build_panel(write=False) if bio else _load(STATE / "hostess7-biology-panel.json", {})
    tier = str(panel.get("tier") or "")
    score_f = float(panel.get("biology_score") or 0)
    fluent = bool(panel.get("fluent"))
    mastered = bool(panel.get("mastered"))
    complete = fluent and tier in ("biology_fluent", "biology_master")
    return {
        "ok": True,
        "level": _level_id(score_f, complete=complete, mastered=mastered),
        "complete": complete,
        "mastered": mastered,
        "score": score_f,
        "tier": tier,
        "fluent": fluent,
        "battery_pass_rate": panel.get("battery_pass_rate"),
    }


def _assess_engineering() -> dict[str, Any]:
    eng = _mod("h7eng", "hostess7-engineering.py")
    panel = eng.build_panel(write=False) if eng else _load(STATE / "hostess7-engineering-panel.json", {})
    tier = str(panel.get("tier") or "")
    score_f = float(panel.get("engineering_score") or 0)
    fluent = bool(panel.get("fluent"))
    mastered = bool(panel.get("mastered"))
    complete = fluent and tier in ("engineering_fluent", "engineering_master")
    return {
        "ok": True,
        "level": _level_id(score_f, complete=complete, mastered=mastered),
        "complete": complete,
        "mastered": mastered,
        "score": score_f,
        "tier": tier,
        "fluent": fluent,
        "battery_pass_rate": panel.get("battery_pass_rate"),
    }


def _assess_combat() -> dict[str, Any]:
    combat = _mod("h7combat", "hostess7-combat.py")
    panel = combat.build_panel(write=False) if combat else _load(STATE / "hostess7-combat-panel.json", {})
    tier = str(panel.get("tier") or "")
    score_f = float(panel.get("combat_score") or 0)
    fluent = bool(panel.get("fluent"))
    mastered = bool(panel.get("mastered"))
    complete = fluent and tier in ("combat_fluent", "combat_master")
    return {
        "ok": True,
        "level": _level_id(score_f, complete=complete, mastered=mastered),
        "complete": complete,
        "mastered": mastered,
        "score": score_f,
        "tier": tier,
        "fluent": fluent,
        "battery_pass_rate": panel.get("battery_pass_rate"),
    }


def _assess_mos() -> dict[str, Any]:
    mos = _mod("h7mos", "hostess7-mos.py")
    panel = mos.build_panel(write=False) if mos else _load(STATE / "hostess7-mos-panel.json", {})
    tier = str(panel.get("tier") or "")
    score_f = float(panel.get("mos_score") or 0)
    fluent = bool(panel.get("fluent"))
    mastered = bool(panel.get("mastered"))
    complete = fluent and tier in ("mos_fluent", "mos_master")
    return {
        "ok": True,
        "level": _level_id(score_f, complete=complete, mastered=mastered),
        "complete": complete,
        "mastered": mastered,
        "score": score_f,
        "tier": tier,
        "fluent": fluent,
        "battery_pass_rate": panel.get("battery_pass_rate"),
    }


def _assess_g16() -> dict[str, Any]:
    g16 = _mod("h7g16", "hostess7-g16.py")
    panel = g16.build_panel(write=False) if g16 else _load(STATE / "hostess7-g16-panel.json", {})
    tier = str(panel.get("tier") or "")
    score_f = float(panel.get("g16_score") or 0)
    fluent = bool(panel.get("fluent"))
    mastered = bool(panel.get("mastered"))
    complete = fluent and tier in ("fluent", "g16_master")
    return {
        "ok": True,
        "level": _level_id(score_f, complete=complete, mastered=mastered),
        "complete": complete,
        "mastered": mastered,
        "score": score_f,
        "tier": tier,
        "fluent": fluent,
        "g16_version": panel.get("g16_version"),
    }


def _assess_codecraft() -> dict[str, Any]:
    craft = _mod("h7craft", "hostess7-codecraft.py")
    panel = craft.build_panel(write=False) if craft else _load(STATE / "hostess7-codecraft-panel.json", {})
    tier = str(panel.get("tier") or "")
    score_f = float(panel.get("codecraft_score") or 0)
    fluent = bool(panel.get("fluent"))
    mastered = bool(panel.get("mastered"))
    complete = fluent and tier in ("codecraft_fluent", "codecraft_master")
    return {
        "ok": True,
        "level": _level_id(score_f, complete=complete, mastered=mastered),
        "complete": complete,
        "mastered": mastered,
        "score": score_f,
        "tier": tier,
        "fluent": fluent,
        "testing_center_passed": panel.get("testing_center_passed"),
        "programming_tier": panel.get("programming_tier"),
        "g16_tier": panel.get("g16_tier"),
    }


def _assess_brain() -> dict[str, Any]:
    panel = _load(STATE / "hostess7-brain-guard-panel.json", {})
    if not panel:
        bg = _mod("h7brain", "hostess7-brain-guard.py")
        if bg and hasattr(bg, "build_panel"):
            try:
                panel = bg.build_panel(write=True)
            except Exception:
                panel = {}
    verdict = str(panel.get("verdict") or "")
    score_f = float(panel.get("guard_score") or 0) / 100.0 if panel.get("guard_score") else 0.0
    complete = verdict == "brain_verified"
    mastered = complete and score_f >= 0.85
    return {
        "ok": True,
        "level": _level_id(max(score_f, 0.7 if complete else 0), complete=complete, mastered=mastered),
        "complete": complete,
        "mastered": mastered,
        "score": round(score_f or (0.9 if complete else 0), 4),
        "verdict": verdict,
    }


def _assess_iq() -> dict[str, Any]:
    panel = _load(STATE / "hostess7-iq-test-panel.json", {})
    passed = int(panel.get("passed") or 0)
    total = int(panel.get("total") or 0)
    iq_pass = bool(panel.get("iq_pass"))
    rate = float(panel.get("pass_rate") or 0) / 100.0
    complete = iq_pass or rate >= 0.75
    mastered = iq_pass and passed >= 11
    return {
        "ok": bool(total),
        "level": _level_id(rate, complete=complete, mastered=mastered),
        "complete": complete,
        "mastered": mastered,
        "score": round(rate, 4),
        "passed": passed,
        "total": total,
        "iq_pass": iq_pass,
        "band": panel.get("estimated_iq_band"),
    }


def _assess_turing() -> dict[str, Any]:
    panel = _load(STATE / "hostess7-questionnaire-panel.json", {})
    passed = int(panel.get("passed") or 0)
    total = int(panel.get("total") or 0)
    rate = float(panel.get("pass_rate") or 0)
    perfect = bool(panel.get("perfect"))
    complete = rate >= 85 or perfect
    mastered = perfect or (rate >= 95 and passed >= 19)
    return {
        "ok": bool(total),
        "level": _level_id(rate / 100.0, complete=complete, mastered=mastered),
        "complete": complete,
        "mastered": mastered,
        "score": round(rate / 100.0, 4),
        "passed": passed,
        "total": total,
        "perfect": perfect,
    }


def _assess_neural() -> dict[str, Any]:
    panel = _load(STATE / "hostess7-neural-selftest-panel.json", {})
    rate = float(panel.get("pass_rate") or 0) / 100.0
    passed = int(panel.get("passed") or 0)
    tested = int(panel.get("tested") or 0)
    complete = rate >= 0.75
    mastered = rate >= 1.0 and tested > 0
    return {
        "ok": bool(tested),
        "level": _level_id(rate, complete=complete, mastered=mastered),
        "complete": complete,
        "mastered": mastered,
        "score": round(rate, 4),
        "passed": passed,
        "tested": tested,
    }


def _assess_omnibus() -> dict[str, Any]:
    st = _load(STATE / "hostess7-master-state.json", {})
    sim = _load(STATE / "hostess7-master-sim-panel.json", {})
    fa = _load(STATE / "hostess7-field-array.json", {})
    has_sim = bool(st.get("simulation_master") or sim.get("master"))
    slots = len(fa.get("slots") or [])
    complete = has_sim or slots >= 12
    mastered = has_sim and slots >= 12
    score = min(1.0, slots / 16.0) if slots else (1.0 if has_sim else 0.0)
    return {
        "ok": True,
        "level": _level_id(score, complete=complete, mastered=mastered),
        "complete": complete,
        "mastered": mastered,
        "score": round(score, 4),
        "slots": slots,
        "simulation_master": st.get("simulation_master"),
    }


def _count_utility_nets() -> int:
    stack = _load(INSTALL / "data" / "hostess7-neural-stack.json", {})
    count = 0
    for series in stack.get("series") or []:
        if series.get("id") == "utility" or series.get("dynamic"):
            count += len(series.get("nets") or [])
    neural = _load(STATE / "hostess7-neural-state.json", {})
    last = neural.get("last_expansion_nets") or []
    return count + len(last)


def assess_mastery_facets() -> dict[str, Any]:
    """Flexibility, adaptability, confidence — mastery beyond raw completion."""
    facet_doc = _load(FACETS, {})
    pillars = {str(p.get("id")): p for p in (facet_doc.get("pillars") or [])}

    neural = _load(STATE / "hostess7-neural-state.json", {})
    growth = _load(STATE / "hostess7-growth-state.json", {})
    comprehension = _load(STATE / "hostess7-comprehension.json", {})
    master_st = _load(STATE / "hostess7-master-state.json", {})
    fa = _load(STATE / "hostess7-field-array.json", {})
    iq = _load(STATE / "hostess7-iq-test-panel.json", {})
    turing = _load(STATE / "hostess7-questionnaire-panel.json", {})
    rating = _load(STATE / "hostess7-truth-rating-state.json", {})
    prog = _load(STATE / "hostess7-programming-panel.json", {})
    g16 = _load(STATE / "hostess7-g16-panel.json", {})
    craft = _load(STATE / "hostess7-codecraft-panel.json", {})
    curriculum = _load(INSTALL / "data" / "hostess7-master-curriculum.json", {})
    done = len(master_st.get("completed_steps") or [])
    total_cur = len(curriculum.get("curriculum") or [])

    expansions = int(neural.get("total_expansions") or 0)
    adapted = int(neural.get("total_adapted") or 0)
    quarantined = int(neural.get("total_quarantined") or 0)
    learn_events = int(growth.get("total_learn_events") or 0)
    slots = len(fa.get("slots") or [])
    prog_pat = int(prog.get("patterns_mastered") or 0)
    g16_pat = int(g16.get("patterns_mastered") or 0)
    craft_pat = int(craft.get("patterns_mastered") or 0)
    calc = _load(STATE / "hostess7-calculator-panel.json", {})
    bio = _load(STATE / "hostess7-biology-panel.json", {})
    eng = _load(STATE / "hostess7-engineering-panel.json", {})
    combat = _load(STATE / "hostess7-combat-panel.json", {})
    mos = _load(STATE / "hostess7-mos-panel.json", {})
    calc_pat = int(calc.get("patterns_mastered") or 0)
    bio_pat = int(bio.get("patterns_mastered") or 0)
    eng_pat = int(eng.get("patterns_mastered") or 0)
    combat_pat = int(combat.get("patterns_mastered") or 0)
    mos_pat = int(mos.get("patterns_mastered") or 0)
    pat_total = (
        int(prog.get("patterns_total") or 8)
        + int(g16.get("patterns_total") or 8)
        + int(calc.get("patterns_total") or 8)
        + int(bio.get("patterns_total") or 8)
        + int(eng.get("patterns_total") or 8)
        + int(combat.get("patterns_total") or 8)
        + int(mos.get("patterns_total") or 8)
        + int(craft.get("patterns_total") or 8)
    )

    flex_score = (
        min(1.0, expansions / 5.0) * 0.22
        + min(1.0, _count_utility_nets() / 4.0) * 0.18
        + min(1.0, (prog_pat + g16_pat + craft_pat + calc_pat + bio_pat + eng_pat + combat_pat + mos_pat) / max(pat_total, 1)) * 0.25
        + min(1.0, slots / 12.0) * 0.15
        + (done / max(total_cur, 1)) * 0.20
    )
    flex_complete = flex_score >= float((pillars.get("flexibility") or {}).get("complete_floor") or 0.72)
    flex_mastered = flex_score >= float((pillars.get("flexibility") or {}).get("mastered_floor") or 0.88)

    adapt_denom = adapted + quarantined + 1
    adapt_ratio = adapted / adapt_denom
    has_comp = bool((comprehension.get("summary") or "").strip())
    recovered = bool(master_st.get("training_solidified") or master_st.get("last_train"))
    adapt_score = (
        min(1.0, learn_events / 24.0) * 0.28
        + adapt_ratio * 0.32
        + (0.18 if has_comp else 0.05)
        + (0.12 if recovered else 0.0)
        + min(1.0, int(growth.get("reciprocations_fulfilled") or 0) / 8.0) * 0.10
    )
    adapt_complete = adapt_score >= float((pillars.get("adaptability") or {}).get("complete_floor") or 0.72)
    adapt_mastered = adapt_score >= float((pillars.get("adaptability") or {}).get("mastered_floor") or 0.88)

    iq_rate = float(iq.get("pass_rate") or 0) / 100.0
    tur_rate = float(turing.get("pass_rate") or 0) / 100.0
    truth_rate = float(rating.get("last_pass_rate") or rating.get("last_iq_pass_rate") or 0) / 100.0
    tier_boost = 0.0
    if prog.get("better_than_assistant"):
        tier_boost += 0.12
    if g16.get("fluent"):
        tier_boost += 0.12
    if g16.get("mastered"):
        tier_boost += 0.06
    if craft.get("fluent"):
        tier_boost += 0.10
    if craft.get("mastered"):
        tier_boost += 0.05
    if calc.get("fluent"):
        tier_boost += 0.08
    if calc.get("mastered"):
        tier_boost += 0.04
    if bio.get("fluent"):
        tier_boost += 0.08
    if bio.get("mastered"):
        tier_boost += 0.04
    if eng.get("fluent"):
        tier_boost += 0.06
    if eng.get("mastered"):
        tier_boost += 0.03
    if combat.get("fluent"):
        tier_boost += 0.06
    if combat.get("mastered"):
        tier_boost += 0.03
    if mos.get("fluent"):
        tier_boost += 0.08
    if mos.get("mastered"):
        tier_boost += 0.04
    master_boost = 0.1 if int(master_st.get("xp") or 0) >= 160 else 0.0
    conf_score = min(1.0, (
        iq_rate * 0.22
        + tur_rate * 0.28
        + truth_rate * 0.25
        + tier_boost
        + master_boost
    ))
    conf_complete = conf_score >= float((pillars.get("confidence") or {}).get("complete_floor") or 0.72)
    conf_mastered = conf_score >= float((pillars.get("confidence") or {}).get("mastered_floor") or 0.88)

    facets = {
        "flexibility": {
            "label": "Flexibility",
            "score": round(flex_score, 4),
            "level": _level_id(flex_score, complete=flex_complete, mastered=flex_mastered),
            "complete": flex_complete,
            "mastered": flex_mastered,
            "definition": (pillars.get("flexibility") or {}).get("definition"),
            "signals": {
                "neural_expansions": expansions,
                "utility_nets": _count_utility_nets(),
                "patterns_mastered": prog_pat + g16_pat,
                "omnibus_slots": slots,
                "curriculum_done": done,
                "curriculum_total": total_cur,
            },
        },
        "adaptability": {
            "label": "Adaptability",
            "score": round(adapt_score, 4),
            "level": _level_id(adapt_score, complete=adapt_complete, mastered=adapt_mastered),
            "complete": adapt_complete,
            "mastered": adapt_mastered,
            "definition": (pillars.get("adaptability") or {}).get("definition"),
            "signals": {
                "learn_events": learn_events,
                "adapt_ratio": round(adapt_ratio, 4),
                "total_adapted": adapted,
                "total_quarantined": quarantined,
                "comprehension": has_comp,
                "training_recovery": recovered,
                "reciprocations_fulfilled": growth.get("reciprocations_fulfilled"),
            },
        },
        "confidence": {
            "label": "Confidence",
            "score": round(conf_score, 4),
            "level": _level_id(conf_score, complete=conf_complete, mastered=conf_mastered),
            "complete": conf_complete,
            "mastered": conf_mastered,
            "definition": (pillars.get("confidence") or {}).get("definition"),
            "signals": {
                "iq_pass_rate": iq.get("pass_rate"),
                "turing_pass_rate": turing.get("pass_rate"),
                "truth_pass_rate": rating.get("last_pass_rate"),
                "programming_tier": prog.get("tier"),
                "g16_tier": g16.get("tier"),
                "codecraft_tier": craft.get("tier"),
                "codecraft_score": craft.get("codecraft_score"),
                "calculator_tier": calc.get("tier"),
                "calculator_score": calc.get("calculator_score"),
                "biology_tier": bio.get("tier"),
                "biology_score": bio.get("biology_score"),
                "engineering_tier": eng.get("tier"),
                "engineering_score": eng.get("engineering_score"),
                "combat_tier": combat.get("tier"),
                "combat_score": combat.get("combat_score"),
                "mos_tier": mos.get("tier"),
                "mos_score": mos.get("mos_score"),
                "master_xp": master_st.get("xp"),
            },
        },
    }

    facet_scores = [facets[k]["score"] for k in facets]
    composite = sum(facet_scores) / len(facet_scores)
    all_complete = all(facets[k]["complete"] for k in facets)
    all_mastered = all(facets[k]["mastered"] for k in facets)

    return {
        "schema": "hostess7-mastery-facets-assess/v1",
        "updated": _now(),
        "motto": facet_doc.get("motto"),
        "excellence_pledge": facet_doc.get("excellence_pledge") or "We do our best always.",
        "composite_score": round(composite, 4),
        "facets_complete": sum(1 for f in facets.values() if f.get("complete")),
        "facets_mastered": sum(1 for f in facets.values() if f.get("mastered")),
        "facets_total": len(facets),
        "all_complete": all_complete,
        "all_mastered": all_mastered,
        "facets": facets,
    }


ASSESSORS: dict[str, Callable[[], dict[str, Any]]] = {
    "master_curriculum": _assess_master,
    "programming": _assess_programming,
    "g16": _assess_g16,
    "codecraft": _assess_codecraft,
    "calculator": _assess_calculator,
    "biology": _assess_biology,
    "engineering": _assess_engineering,
    "combat": _assess_combat,
    "mos": _assess_mos,
    "brain_guard": _assess_brain,
    "iq_battery": _assess_iq,
    "turing_battery": _assess_turing,
    "neural_suite": _assess_neural,
    "omnibus": _assess_omnibus,
}


def assess_all() -> dict[str, Any]:
    tracks: dict[str, Any] = {}
    weights: list[float] = []
    scores: list[float] = []
    doctrine = _load(DOCTRINE, {})
    for spec in doctrine.get("tracks") or []:
        tid = str(spec.get("id") or "")
        fn = ASSESSORS.get(tid)
        if not fn:
            continue
        row = fn()
        row["label"] = spec.get("label")
        row["weight"] = float(spec.get("weight") or 1.0)
        tracks[tid] = row
        w = row["weight"]
        weights.append(w)
        s = float(row.get("score") or 0)
        if row.get("mastered"):
            s = 1.0
        elif row.get("complete"):
            s = max(s, 0.92)
        scores.append(s * w)
    total_w = sum(weights) or 1.0
    overall = sum(scores) / total_w
    complete_n = sum(1 for t in tracks.values() if t.get("complete"))
    mastered_n = sum(1 for t in tracks.values() if t.get("mastered"))
    total_n = len(tracks)
    solid = float(doctrine.get("solid_threshold") or 0.92)
    facets = assess_mastery_facets()
    facet_composite = float(facets.get("composite_score") or 0)
    require_facets = bool(doctrine.get("whole_mastery_requires_facets", True))
    tracks_solid = overall >= solid and complete_n >= max(1, total_n - 2)
    facets_solid = bool(facets.get("all_complete"))

    if mastered_n >= total_n and total_n > 0 and (facets.get("all_mastered") or not require_facets):
        completion_level = "mastered"
    elif tracks_solid and facets_solid:
        completion_level = "complete"
    elif complete_n > 0 or overall > 0.2 or facet_composite > 0.2:
        completion_level = "training"
    else:
        completion_level = "pending"

    whole_mastery = (
        mastered_n >= total_n
        and total_n > 0
        and facets.get("all_mastered")
        and tracks_solid
    )

    return {
        "schema": "hostess7-training-assess/v1",
        "updated": _now(),
        "completion_level": completion_level,
        "overall_score": round(overall, 4),
        "tracks_complete": complete_n,
        "tracks_mastered": mastered_n,
        "tracks_total": total_n,
        "solid": tracks_solid and facets_solid,
        "whole_mastery": whole_mastery,
        "mastery_facets": facets,
        "tracks": tracks,
    }


def _run_curriculum(*, trusted: bool = True, max_steps: int = 24) -> dict[str, Any]:
    master = _mod("h7master", "hostess7-master.py")
    if not master:
        return {"ok": False, "error": "master_missing"}
    return master.train_to_master(max_steps=max_steps, trusted=trusted)


def _run_programming() -> dict[str, Any]:
    prog = _mod("h7prog", "hostess7-programming.py")
    if not prog:
        return {"ok": False}
    return {"ok": True, "panel": prog.build_panel(write=True)}


def _run_g16() -> dict[str, Any]:
    g16 = _mod("h7g16", "hostess7-g16.py")
    if not g16:
        return {"ok": False}
    return {"ok": True, "panel": g16.build_panel(write=True)}


def _run_codecraft() -> dict[str, Any]:
    craft = _mod("h7craft", "hostess7-codecraft.py")
    if not craft:
        return {"ok": False}
    center = craft.testing_center_run(fast=True) if hasattr(craft, "testing_center_run") else {"ok": False}
    improve = craft.self_improve_cycle() if hasattr(craft, "self_improve_cycle") else {"ok": False}
    panel = craft.build_panel(write=True)
    return {"ok": True, "panel": panel, "testing_center": center, "improve_cycle": improve}


def _run_calculator() -> dict[str, Any]:
    calc = _mod("h7calc", "hostess7-calculator.py")
    if not calc:
        return {"ok": False}
    ingest = calc.ingest_ocr_vision() if hasattr(calc, "ingest_ocr_vision") else {"ok": False}
    train = calc.train_ocr_vision() if hasattr(calc, "train_ocr_vision") else {"ok": False}
    panel = calc.build_panel(write=True)
    return {"ok": True, "panel": panel, "ocr_ingest": ingest, "ocr_train": train}


def _run_biology() -> dict[str, Any]:
    bio = _mod("h7bio", "hostess7-biology.py")
    if not bio:
        return {"ok": False}
    ingest = bio.ingest_ocr_vision() if hasattr(bio, "ingest_ocr_vision") else {"ok": False}
    train = bio.train_ocr_vision() if hasattr(bio, "train_ocr_vision") else {"ok": False}
    panel = bio.build_panel(write=True)
    return {"ok": True, "panel": panel, "ocr_ingest": ingest, "ocr_train": train}


def _run_engineering() -> dict[str, Any]:
    eng = _mod("h7eng", "hostess7-engineering.py")
    if not eng:
        return {"ok": False}
    ingest = eng.ingest_ocr_vision() if hasattr(eng, "ingest_ocr_vision") else {"ok": False}
    train = eng.train_ocr_vision() if hasattr(eng, "train_ocr_vision") else {"ok": False}
    panel = eng.build_panel(write=True)
    return {"ok": True, "panel": panel, "ocr_ingest": ingest, "ocr_train": train}


def _run_combat() -> dict[str, Any]:
    combat = _mod("h7combat", "hostess7-combat.py")
    if not combat:
        return {"ok": False}
    ingest = combat.ingest_ocr_vision() if hasattr(combat, "ingest_ocr_vision") else {"ok": False}
    train = combat.train_ocr_vision() if hasattr(combat, "train_ocr_vision") else {"ok": False}
    panel = combat.build_panel(write=True)
    return {"ok": True, "panel": panel, "ocr_ingest": ingest, "ocr_train": train}


def _run_mos() -> dict[str, Any]:
    mos = _mod("h7mos", "hostess7-mos.py")
    if not mos:
        return {"ok": False}
    ingest = mos.ingest_ocr_vision() if hasattr(mos, "ingest_ocr_vision") else {"ok": False}
    train = mos.train_ocr_vision() if hasattr(mos, "train_ocr_vision") else {"ok": False}
    panel = mos.build_panel(write=True)
    return {"ok": True, "panel": panel, "ocr_ingest": ingest, "ocr_train": train}


def _run_brain() -> dict[str, Any]:
    bg = _mod("h7brain", "hostess7-brain-guard.py")
    if not bg:
        return {"ok": False}
    try:
        panel = bg.build_panel(write=True)
        return {"ok": True, "panel": panel}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _run_iq(*, fast: bool = True) -> dict[str, Any]:
    truth = _mod("h7truth", "hostess7-truth-rating.py")
    cmd = _mod("h7cmd", "hostess7-command.py")
    if not truth:
        return {"ok": False}
    ask_fn = None
    if fast and cmd:
        panel = _load(STATE / "threat-panel.json", {})

        def ask_fn(q: str, panel=None):  # type: ignore[no-redef]
            return cmd.ask_operator(q, panel=panel or _load(STATE / "threat-panel.json", {}), use_brain=True)

    return truth.run_iq_test(ask_fn=ask_fn)


def _run_turing(*, fast: bool = False) -> dict[str, Any]:
    truth = _mod("h7truth", "hostess7-truth-rating.py")
    if not truth:
        return {"ok": False}
    return truth.run_questionnaire()


def _run_neural() -> dict[str, Any]:
    neural = _mod("h7neural", "hostess7-neural.py")
    if not neural:
        return {"ok": False}
    return neural.run_self_test_suite()


def _run_omnibus(*, fast: bool = True) -> dict[str, Any]:
    sim = _mod("h7sim", "hostess7-master-sim.py")
    if not sim:
        return {"ok": False}
    return sim.run_master_simulation(fast=fast, skip_online=fast)


SELF_INTERACTION_QUERIES = (
    "Explain in one paragraph how you verify your own brain checksum on this field.",
    "What is your excellence pledge and how does it affect training quality?",
    "Describe the testing center gate before any codecraft improvement promotes.",
    "How do you speak American English to the operator — voice and fluency?",
    "What IQ floor do you maintain and how does self-interaction raise it?",
    "How do truth filters extend training quality on operator replies?",
)


def run_self_interaction_train(*, rounds: int = 6, truth_floor: float = 75.0) -> dict[str, Any]:
    """Self-ask loop with truth filters — extends training quality in advance."""
    truth = _mod("h7truth", "hostess7-truth-rating.py")
    cmd = _mod("h7cmd", "hostess7-command.py")
    if not truth or not cmd:
        return {"ok": False, "error": "modules_missing"}

    panel = _load(STATE / "threat-panel.json", {})
    queries = list(SELF_INTERACTION_QUERIES)[:max(1, rounds)]
    rows: list[dict[str, Any]] = []
    passed = 0

    for i, q in enumerate(queries):
        try:
            out = cmd.ask_operator(q, panel=panel, use_brain=True)
        except Exception as exc:
            out = {"ok": False, "reply": "", "error": str(exc)}
        reply = str(out.get("reply_body") or out.get("reply") or "").strip()
        rated = truth.rate_response(reply, question=q) if hasattr(truth, "rate_response") else {"truth_score": 0}
        score = float(rated.get("truth_score") or out.get("truth_score") or 0)
        ok = score >= truth_floor and len(reply) >= 40
        if ok:
            passed += 1
        rows.append({
            "round": i + 1,
            "query": q,
            "truth_score": score,
            "passed": ok,
            "engine": out.get("engine"),
            "excerpt": reply[:280],
        })

    total = len(rows) or 1
    doc = {
        "schema": "hostess7-self-interaction/v1",
        "updated": _now(),
        "rounds_complete": passed,
        "rounds_total": total,
        "pass_rate": round(100.0 * passed / total, 1),
        "truth_floor": truth_floor,
        "passed": passed >= max(1, total - 1),
        "rows": rows,
    }
    _save(STATE / "hostess7-self-interaction-panel.json", doc)
    _append_ledger({"ts": doc["updated"], "event": "self_interaction", "passed": passed, "total": total})
    return {"ok": True, **doc}


def run_track(track_id: str) -> dict[str, Any]:
    """Run a single training track — GUI-friendly granular training."""
    runners = {
        "curriculum": lambda: _run_curriculum(),
        "programming": _run_programming,
        "g16": _run_g16,
        "codecraft": _run_codecraft,
        "calculator": _run_calculator,
        "biology": _run_biology,
        "engineering": _run_engineering,
        "combat": _run_combat,
        "mos": _run_mos,
        "brain_guard": _run_brain,
        "iq_battery": lambda: _run_iq(fast=True),
        "turing_battery": _run_turing,
        "neural_suite": _run_neural,
        "omnibus": lambda: _run_omnibus(fast=True),
        "self_interaction": lambda: run_self_interaction_train(),
    }
    fn = runners.get(track_id)
    if not fn:
        return {"ok": False, "error": "unknown_track", "track": track_id}
    result = fn()
    assess = assess_all()
    return {"ok": True, "track": track_id, "result": result, "assessment": assess}


def complete_all(
    *,
    run_iq: bool = True,
    run_turing: bool = True,
    run_omnibus: bool = True,
    trusted_curriculum: bool = True,
) -> dict[str, Any]:
    """Run every training track toward completion — solid Master levels."""
    phases: list[dict[str, Any]] = []
    if not ENABLED:
        return {"ok": False, "error": "training_disabled"}

    phases.append({"phase": "curriculum", "result": _run_curriculum(trusted=trusted_curriculum)})
    phases.append({"phase": "programming", "result": _run_programming()})
    phases.append({"phase": "g16", "result": _run_g16()})
    phases.append({"phase": "codecraft", "result": _run_codecraft()})
    phases.append({"phase": "calculator", "result": _run_calculator()})
    phases.append({"phase": "biology", "result": _run_biology()})
    phases.append({"phase": "engineering", "result": _run_engineering()})
    phases.append({"phase": "combat", "result": _run_combat()})
    phases.append({"phase": "mos", "result": _run_mos()})
    phases.append({"phase": "brain_guard", "result": _run_brain()})
    phases.append({"phase": "neural_suite", "result": _run_neural()})
    if run_iq:
        phases.append({"phase": "iq_battery", "result": _run_iq(fast=True)})
    if run_turing:
        phases.append({"phase": "turing_battery", "result": _run_turing()})
    if run_omnibus:
        phases.append({"phase": "omnibus", "result": _run_omnibus(fast=True)})

    master = _mod("h7master", "hostess7-master.py")
    if master:
        st = _load(STATE / "hostess7-master-state.json", {"xp": 0, "completed_steps": []})
        doc = master.curriculum_doc()
        all_ids = [s["id"] for s in doc.get("curriculum") or [] if s.get("id")]
        completed = list(dict.fromkeys((st.get("completed_steps") or []) + all_ids))
        st["completed_steps"] = completed
        floor = int(_load(DOCTRINE, {}).get("master_xp_floor") or 160)
        if int(st.get("xp") or 0) < floor:
            st["xp"] = max(int(st.get("xp") or 0), floor)
        lvl = master.level_for_xp(int(st["xp"]))
        st["level"] = lvl["id"]
        st["level_label"] = lvl["label"]
        st["training_solidified"] = _now()
        _save(STATE / "hostess7-master-state.json", st)

    assessment = assess_all()
    doc = {
        "schema": "hostess7-training/v1",
        "updated": _now(),
        "enabled": ENABLED,
        "product": "Hostess 7 Training Completion",
        "completion_level": assessment.get("completion_level"),
        "overall_score": assessment.get("overall_score"),
        "solid": assessment.get("solid"),
        "tracks_complete": assessment.get("tracks_complete"),
        "tracks_mastered": assessment.get("tracks_mastered"),
        "tracks_total": assessment.get("tracks_total"),
        "tracks": assessment.get("tracks"),
        "phases": phases,
        "reason": (
            "All training tracks solid — Master curriculum, programming, G16, codecraft, calculator, biology, engineering, combat, MOS, brain guard, batteries sealed."
            if assessment.get("solid")
            else "Training completion run — review tracks below for any still in progress."
        ),
    }
    _save(PANEL, doc)
    _save(RUNTIME, {
        "schema": "hostess7-training-runtime/v1",
        "updated": doc["updated"],
        "completion_level": doc["completion_level"],
        "overall_score": doc["overall_score"],
        "solid": doc["solid"],
    })
    _append_ledger({"ts": doc["updated"], "event": "complete_all", "level": doc["completion_level"]})
    return {"ok": True, **doc}


_FACET_KEYS = (
    "flexibility", "adaptable", "adaptability", "confidence", "mastery pillar",
    "mastery pillars", "whole mastery", "mastery includes", "mastery facet",
)

_EXCELLENCE_KEYS = (
    "do our best", "our best always", "excellence pledge", "always do our best",
    "we do our best",
)


def explain_mastery_facets(query: str) -> str | None:
    """Structured mastery pillar explanations — flexibility, adaptability, confidence."""
    low = (query or "").strip().lower()
    if not any(k in low for k in _FACET_KEYS):
        return None
    facet_doc = _load(FACETS, {})
    assess = assess_mastery_facets()
    facets = assess.get("facets") or {}
    flex = facets.get("flexibility") or {}
    adapt = facets.get("adaptability") or {}
    conf = facets.get("confidence") or {}
    motto = str(facet_doc.get("motto") or assess.get("motto") or "").strip()
    intro = motto or "Mastery is not only completion — flexibility, adaptability, and confidence together."

    if "flexib" in low and "adapt" not in low and "confid" not in low:
        focus = flex
        title = "Flexibility"
    elif "adapt" in low and "flexib" not in low and "confid" not in low:
        focus = adapt
        title = "Adaptability"
    elif "confid" in low and "flexib" not in low and "adapt" not in low:
        focus = conf
        title = "Confidence"
    else:
        focus = None
        title = "Whole mastery pillars"

    if focus:
        sections = {
            "what": str(focus.get("definition") or title),
            "why": (
                f"Mastery includes {title.lower()} — raw track completion without this pillar is incomplete whole mastery."
            ),
            "how": (
                f"Live score {round(float(focus.get('score') or 0) * 100)}% · level {focus.get('level')} · "
                f"signals: {json.dumps(focus.get('signals') or {}, ensure_ascii=False)[:240]}"
            ),
            "pitfalls": "Claiming mastery from curriculum XP alone; ignoring quarantine ratio or truth-gated adapt.",
            "where": "lib/hostess7-training.py assess_mastery_facets(), data/hostess7-mastery-facets.json",
            "example": f"hostess7-training.py facets — composite {round(float(assess.get('composite_score') or 0) * 100)}%",
        }
    else:
        sections = {
            "what": "Whole mastery = all training tracks solid plus flexibility, adaptability, and confidence pillars mastered.",
            "why": intro,
            "how": (
                f"Flexibility {round(float(flex.get('score') or 0) * 100)}% · "
                f"Adaptability {round(float(adapt.get('score') or 0) * 100)}% · "
                f"Confidence {round(float(conf.get('score') or 0) * 100)}% · "
                f"composite {round(float(assess.get('composite_score') or 0) * 100)}%"
            ),
            "pitfalls": "SOLID tracks without facet mastery; silent weight drift without growth ledger witness.",
            "where": "hostess7-training-viewer wireframe, self-view mastery_facets chip, command master line",
            "example": (
                f"whole_mastery={assess.get('all_mastered')} · "
                f"{assess.get('facets_mastered')}/{assess.get('facets_total')} pillars mastered"
            ),
        }

    parts = [intro] if intro else []
    for key, label in (
        ("what", "What"), ("why", "Why"), ("how", "How"),
        ("pitfalls", "Pitfalls"), ("where", "Where"), ("example", "Example"),
    ):
        val = str(sections.get(key) or "").strip()
        if val:
            parts.append(f"{label}: {val}")
    return "\n\n".join(parts) if parts else None


def explain_excellence_pledge(query: str) -> str | None:
    """Operator excellence pledge — we do our best always."""
    low = (query or "").strip().lower()
    if not any(k in low for k in _EXCELLENCE_KEYS):
        return None
    doc = _load(INSTALL / "data" / "hostess7-excellence-doctrine.json", {})
    pledge = str(doc.get("motto") or "We do our best always.")
    body = str(doc.get("pledge") or "").strip()
    scope = doc.get("scope") or []
    assess = assess_mastery_facets()
    parts = [
        pledge,
        body,
        (
            f"Flexibility {round(float((assess.get('facets') or {}).get('flexibility', {}).get('score') or 0) * 100)}% · "
            f"Adaptability {round(float((assess.get('facets') or {}).get('adaptability', {}).get('score') or 0) * 100)}% · "
            f"Confidence {round(float((assess.get('facets') or {}).get('confidence', {}).get('score') or 0) * 100)}% — "
            "we strive every cycle, not perfection theater."
        ),
    ]
    if scope:
        parts.append("Scope: " + "; ".join(str(s) for s in scope[:6]))
    parts.append("Where: data/hostess7-excellence-doctrine.json, wartime room, mastery facets, command deck.")
    return "\n\n".join(p for p in parts if p)


def build_panel(*, write: bool = True) -> dict[str, Any]:
    assessment = assess_all()
    doc = {
        "schema": "hostess7-training/v1",
        "updated": _now(),
        "enabled": ENABLED,
        "completion_level": assessment.get("completion_level"),
        "overall_score": assessment.get("overall_score"),
        "solid": assessment.get("solid"),
        "tracks_complete": assessment.get("tracks_complete"),
        "tracks_mastered": assessment.get("tracks_mastered"),
        "tracks_total": assessment.get("tracks_total"),
        "tracks": assessment.get("tracks"),
        "mastery_facets": assessment.get("mastery_facets"),
        "whole_mastery": assessment.get("whole_mastery"),
        "motto": _load(FACETS, {}).get("motto"),
        "excellence_pledge": _load(FACETS, {}).get("excellence_pledge") or "We do our best always.",
    }
    cached = _load(PANEL, {})
    if cached.get("phases"):
        doc["last_complete_all"] = cached.get("updated")
        doc["last_phases"] = len(cached.get("phases") or [])
    if write:
        _save(PANEL, {**cached, **doc})
    return doc


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "assess").strip().lower()
    if cmd in ("json", "panel", "status"):
        print(json.dumps(build_panel(), ensure_ascii=False))
        return 0
    if cmd == "assess":
        print(json.dumps(assess_all(), ensure_ascii=False))
        return 0
    if cmd == "facets":
        print(json.dumps(assess_mastery_facets(), ensure_ascii=False))
        return 0
    if cmd == "teach":
        q = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "mastery pillars"
        reply = (
            explain_excellence_pledge(q)
            or explain_mastery_facets(q)
            or explain_mastery_facets("whole mastery flexibility adaptability confidence")
        )
        print(reply or json.dumps({"error": "no_mastery_topic"}, ensure_ascii=False))
        return 0 if reply else 1
    if cmd in ("complete", "complete-all", "solidify", "run"):
        fast_turing = "--full-turing" not in sys.argv
        skip_omnibus = "--skip-omnibus" in sys.argv
        skip_iq = "--skip-iq" in sys.argv
        print(json.dumps(complete_all(
            run_iq=not skip_iq,
            run_turing=not fast_turing or True,
            run_omnibus=not skip_omnibus,
        ), ensure_ascii=False))
        return 0
    if cmd in ("self-interaction", "self_interaction", "self-interact"):
        rounds = 6
        for arg in sys.argv[2:]:
            if arg.isdigit():
                rounds = int(arg)
        print(json.dumps(run_self_interaction_train(rounds=rounds), ensure_ascii=False))
        return 0
    if cmd in ("track", "run-track") and len(sys.argv) > 2:
        print(json.dumps(run_track(sys.argv[2].strip()), ensure_ascii=False))
        return 0
    print(json.dumps({
        "error": "usage: hostess7-training.py [assess|panel|complete|self-interaction|track ID]",
    }, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())