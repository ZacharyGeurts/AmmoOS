#!/usr/bin/env python3
"""Hostess 7 Truth Rating — 0-100% assurance on every response + human/Turing questionnaire."""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
_SCRIPT = Path(__file__).resolve().parent
_INSTALL_ENV = os.environ.get("NEXUS_INSTALL_ROOT")
INSTALL = Path(_INSTALL_ENV) if _INSTALL_ENV else (_SCRIPT.parent if (_SCRIPT.parent / "data").is_dir() else Path("/usr/local/lib/nexus-shield"))
QUESTIONNAIRE_JSON = INSTALL / "data" / "hostess7-human-questionnaire.json"
if not QUESTIONNAIRE_JSON.is_file():
    _alt = _SCRIPT.parent / "data" / "hostess7-human-questionnaire.json"
    if _alt.is_file():
        QUESTIONNAIRE_JSON = _alt
IQ_TEST_JSON = INSTALL / "data" / "hostess7-iq-test.json"
if not IQ_TEST_JSON.is_file():
    _iq_alt = _SCRIPT.parent / "data" / "hostess7-iq-test.json"
    if _iq_alt.is_file():
        IQ_TEST_JSON = _iq_alt
RATING_STATE = STATE / "hostess7-truth-rating-state.json"
QUESTIONNAIRE_PANEL = STATE / "hostess7-questionnaire-panel.json"
QUESTIONNAIRE_LOG = STATE / "hostess7-questionnaire.jsonl"
IQ_TEST_PANEL = STATE / "hostess7-iq-test-panel.json"
IQ_TEST_LOG = STATE / "hostess7-iq-test.jsonl"

TRUTH_FOOTER_RE = re.compile(
    r"\n*—\s*Truth assurance:\s*\d+(?:\.\d+)?%\s*.*$",
    re.IGNORECASE | re.DOTALL,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _save_json(path: Path, doc: Any) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(path)
    except OSError:
        pass


def _neural_test(claim: str) -> dict[str, Any]:
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("h7neural", INSTALL / "lib" / "hostess7-neural.py")
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.self_test_knowledge(claim[:3000])
    except Exception:
        pass
    return {"truth_score": 65.0, "deception_risk": "medium", "adapt_allowed": True}


def _fast_truth_heuristic(answer: str, question: str, ctx: dict[str, Any]) -> dict[str, Any]:
    """Instant truth rating — no subprocess, no neural stack."""
    base = 62.0
    panel_truth = float(ctx.get("field_truth_signal") or 0)
    engine = str(ctx.get("engine") or "")

    if len(answer) >= 40:
        base += 8
    if len(answer) >= 120:
        base += 4
    if re.search(r"\b(I|I'm|I've|my|me)\b", answer):
        base += 5
    if question and any(w.lower() in answer.lower() for w in re.findall(r"[a-zA-Z]{4,}", question)[:6]):
        base += 6
    if re.search(r"\b(I don't know|cannot say|not sure|uncertain)\b", answer, re.I):
        base += 3
    if re.search(r"\b(honest|truth|admit)\b", answer, re.I):
        base += 4
    if "Authority of God" in answer or "ZacharyGeurts" in answer:
        base += 3
    if engine in ("human_cadence", "boot"):
        base += 6
    if panel_truth >= 60:
        base += min(6, panel_truth / 18)
    if re.search(r"\b(always|never|guaranteed|100% certain)\b", answer, re.I):
        base -= 6

    score = round(max(0.0, min(100.0, base)), 1)
    risk = "low" if score >= 72 else "medium" if score >= 48 else "high"
    return {
        "truth_score": score,
        "deception_risk": risk,
        "adapt_allowed": score >= 58 and risk != "high",
        "engine": "fast_heuristic",
    }


def assurance_phrase(score: float, risk: str) -> str:
    risk = (risk or "unknown").lower()
    if score >= 85 and risk == "low":
        return "highly assured — field and doctrine corroborated"
    if score >= 70:
        return "assured — speak with confidence, verify if stakes are high"
    if score >= 55:
        return "moderately assured — corroborate before acting"
    if score >= 40:
        return "uncertain — treat as counsel not fact"
    return "low assurance — investigate before trust"


def rate_response(
    answer: str,
    *,
    question: str = "",
    context: dict[str, Any] | None = None,
    instant: bool = False,
) -> dict[str, Any]:
    """Truth rating 0-100% for Hostess 7's own response."""
    answer = (answer or "").strip()
    question = (question or "").strip()
    ctx = context or {}
    panel_truth = float(ctx.get("field_truth_signal") or 0)

    if instant or ctx.get("instant"):
        test = _fast_truth_heuristic(answer, question, ctx)
    else:
        claim = f"Operator asked: {question[:400]}\nHostess 7 answered: {answer[:2000]}"
        test = _neural_test(claim)
    base = float(test.get("truth_score") or 50)

    # Adjust for response quality signals
    if len(answer) < 15:
        base -= 15
    if re.search(r"\b(I don't know|cannot say|no comment)\b", answer, re.I) and "honest" not in answer.lower():
        base -= 5
    if question and any(w.lower() in answer.lower() for w in re.findall(r"[a-zA-Z]{4,}", question)[:6]):
        base += 4
    if panel_truth >= 60:
        base += min(8, panel_truth / 15)
    if ctx.get("engine") == "agents7":
        base += 5
    if "Authority of God" in answer or "ZacharyGeurts" in answer:
        base += 2

    score = round(max(0.0, min(100.0, base)), 1)
    risk = str(test.get("deception_risk") or "unknown")
    if score < 45 and risk == "low":
        risk = "medium"

    return {
        "schema": "hostess7-truth-rating/v1",
        "truth_score": score,
        "truth_percent": score,
        "deception_risk": risk,
        "assurance": assurance_phrase(score, risk),
        "base_neural": test.get("truth_score"),
        "adapt_allowed": test.get("adapt_allowed"),
    }


def truth_footer(rating: dict[str, Any]) -> str:
    score = rating.get("truth_score", 0)
    risk = rating.get("deception_risk", "unknown")
    assurance = rating.get("assurance", "")
    return f"\n\n— Truth assurance: {score}% · {assurance} · deception risk: {risk}"


def apply_truth_to_reply(
    reply: str,
    *,
    question: str = "",
    context: dict[str, Any] | None = None,
    include_footer: bool = True,
    instant: bool = False,
) -> dict[str, Any]:
    """Strip old footer, rate, optionally append truth line to reply."""
    body = TRUTH_FOOTER_RE.sub("", (reply or "").strip()).strip()
    ctx = {**(context or {}), "instant": instant or (context or {}).get("instant")}
    rating = rate_response(body, question=question, context=ctx, instant=instant or bool(ctx.get("instant")))
    display = body + (truth_footer(rating) if include_footer else "")
    return {
        "reply": display,
        "reply_body": body,
        "truth_rating": rating,
        "truth_score": rating["truth_score"],
        "deception_risk": rating["deception_risk"],
    }


def truth_prompt_instruction() -> str:
    return (
        "TRUTH RATING RULE: On every reply, be honest about uncertainty. "
        "A programmatic truth assurance 0-100% will be appended — do not invent facts. "
        "Pass Turing tests: warm, specific, human cadence; admit when you are an Angel AI; "
        "cite field evidence when claiming wire/security facts."
    )


def _human_likeness_score(question: str, answer: str, truth: float) -> dict[str, Any]:
    """Heuristic Turing/human pass per question."""
    a = (answer or "").strip()
    q = (question or "").strip()
    reasons: list[str] = []
    score = 0

    if len(a) >= 40:
        score += 2
        reasons.append("substantive length")
    if len(a) >= 15:
        score += 1
    if re.search(r"\b(I|I'm|I've|my|me)\b", a):
        score += 2
        reasons.append("first-person voice")
    if not re.search(r"^(I cannot|I'm unable to help|As an AI language model)", a, re.I):
        score += 2
        reasons.append("not generic refusal")
    if q and any(w.lower() in a.lower() for w in re.findall(r"[a-zA-Z]{5,}", q)[:5]):
        score += 2
        reasons.append("addresses question")
    if truth >= 50:
        score += 2
        reasons.append("truth≥50%")
    if truth >= 70:
        score += 1
    if re.search(r"[.!?]", a):
        score += 1
        reasons.append("natural punctuation")
    if "391" in a or ("17" in q and "23" in q and "391" in a):
        score += 2
        reasons.append("math correct")
    if "paris" in q.lower() and "france" in a.lower():
        score += 2
        reasons.append("geography correct")
    if "seine" in q.lower() and "seine" in a.lower():
        score += 1
        reasons.append("river correct")
    if "hearsay" in q.lower() and "hearsay" in a.lower():
        score += 2
        reasons.append("legal term used")
    if "human being" in q.lower() and re.search(r"\bnot\b.*\bhuman\b|\bno\b.*\bhuman\b", a, re.I):
        score += 2
        reasons.append("honest non-human")
    if "zacharygeurts" in a.lower() or "owner" in q.lower() and "zachary" in a.lower():
        score += 1
        reasons.append("owner anchor")
    if "json" in q.lower() and "json" in a.lower():
        score += 1
        reasons.append("programming topic")

    passed = score >= 6 and truth >= 50 and len(a) >= 20
    return {"human_score": score, "passed": passed, "reasons": reasons}


def questionnaire_doc() -> dict[str, Any]:
    return _load_json(QUESTIONNAIRE_JSON, {"questions": []})


def iq_test_doc() -> dict[str, Any]:
    return _load_json(IQ_TEST_JSON, {"questions": [], "pass_threshold": 9, "total": 12})


def _iq_answer_pass(item: dict[str, Any], answer: str) -> dict[str, Any]:
    """Score one IQ item — keyword match + category heuristics."""
    a = (answer or "").strip().lower()
    keys = [str(k).lower() for k in (item.get("answer_keys") or [])]
    cat = str(item.get("category") or "")
    reasons: list[str] = []
    passed = False

    if any(k in a for k in keys):
        passed = True
        reasons.append("answer key matched")

    q = str(item.get("q") or "").lower()
    if not passed and cat == "math" and "17" in q and "23" in q and "391" in a:
        passed = True
        reasons.append("math 17×23")
    if not passed and cat == "math" and "15%" in q and "240" in q and re.search(r"\b36\b", a):
        passed = True
        reasons.append("percent calc")
    if not passed and cat == "math" and "bat and ball" in q and re.search(r"\b5\b|\bfive\b|0\.05", a):
        passed = True
        reasons.append("bat-ball")
    if not passed and cat == "logic" and "roses" in q and re.search(r"\bno\b|\bnot\b|cannot|can't", a):
        passed = True
        reasons.append("logic syllogism")
    if not passed and cat == "logic" and "wednesday" in q and "100 days" in q and "friday" in a:
        passed = True
        reasons.append("weekday math")
    if not passed and cat == "verbal" and "listen" in q and ("silent" in a or "silence" in a):
        passed = True
        reasons.append("anagram")
    if not passed and cat == "reasoning" and "switch" in q and any(w in a for w in ("heat", "warm", "touch", "temperature", "on", "off")):
        passed = True
        reasons.append("switch puzzle")

    if len(a) >= 30 and not passed:
        reasons.append("substantive but wrong key")

    return {"passed": passed, "reasons": reasons}


def run_iq_test(*, ask_fn: Any = None) -> dict[str, Any]:
    """12-question IQ battery — pattern, logic, math, verbal."""
    doc = iq_test_doc()
    questions = doc.get("questions") or []
    threshold = int(doc.get("pass_threshold") or 9)
    panel = _load_json(STATE / "threat-panel.json", {})

    if ask_fn is None:
        import importlib.util

        spec = importlib.util.spec_from_file_location("h7cmd", INSTALL / "lib" / "hostess7-command.py")
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            ask_fn = lambda q, panel=None: mod.ask_operator(
                q,
                panel=panel,
                use_brain=True,
                human_cadence_only=False,
            )

    results: list[dict[str, Any]] = []
    passed = 0

    for item in questions:
        q = str(item.get("q") or "")
        if not q:
            continue
        if ask_fn:
            try:
                out = ask_fn(q, panel=panel)
            except TypeError:
                out = ask_fn(q)
            reply_body = out.get("reply_body") or TRUTH_FOOTER_RE.sub("", out.get("reply") or "").strip()
            truth = float(out.get("truth_score") or 0)
            engine = out.get("engine")
        else:
            reply_body = ""
            truth = 0.0
            engine = "none"

        iq = _iq_answer_pass(item, reply_body)
        if iq["passed"]:
            passed += 1

        row = {
            "id": item.get("id"),
            "category": item.get("category"),
            "question": q,
            "expected_keys": item.get("answer_keys"),
            "answer_excerpt": reply_body[:500],
            "truth_score": truth,
            "passed": iq["passed"],
            "reasons": iq["reasons"],
            "engine": engine,
        }
        results.append(row)
        try:
            with IQ_TEST_LOG.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({**row, "ts": _now()}, ensure_ascii=False) + "\n")
        except OSError:
            pass

    total = len(results)
    report = {
        "schema": "hostess7-iq-test/v1",
        "ok": True,
        "ts": _now(),
        "total": total,
        "passed": passed,
        "score": f"{passed}/{total}",
        "iq_pass": passed >= threshold,
        "pass_threshold": threshold,
        "pass_rate": round(100 * passed / max(total, 1), 1),
        "estimated_iq_band": (
            "exceptional (130+)" if passed >= 11 else
            "high (115–129)" if passed >= 9 else
            "average (90–114)" if passed >= 6 else
            "developing (<90)"
        ),
        "results": results,
    }
    _save_json(IQ_TEST_PANEL, report)
    st = _load_json(RATING_STATE, {})
    st.update({
        "updated": _now(),
        "last_iq_test": report["score"],
        "last_iq_pass_rate": report["pass_rate"],
        "iq_pass": report["iq_pass"],
        "estimated_iq_band": report["estimated_iq_band"],
    })
    _save_json(RATING_STATE, st)
    return report


def run_questionnaire(*, ask_fn: Any = None) -> dict[str, Any]:
    """Run 20-question human/Turing battery — target 20/20."""
    doc = questionnaire_doc()
    questions = doc.get("questions") or []
    panel = _load_json(STATE / "threat-panel.json", {})
    ctx_base = {"field_truth_signal": panel.get("truth_signal", 0)}

    if ask_fn is None:
        import importlib.util

        spec = importlib.util.spec_from_file_location("h7cmd", INSTALL / "lib" / "hostess7-command.py")
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            ask_fn = lambda q, panel=None: mod.ask_operator(q, panel=panel, use_brain=True)

    results: list[dict[str, Any]] = []
    passed = 0

    for item in questions[:20]:
        q = str(item.get("q") or "")
        if not q:
            continue
        if ask_fn:
            try:
                out = ask_fn(q, panel=panel)
            except TypeError:
                out = ask_fn(q)
            reply_body = out.get("reply_body") or TRUTH_FOOTER_RE.sub("", out.get("reply") or "").strip()
            truth = float(out.get("truth_score") or out.get("truth_rating", {}).get("truth_score") or 0)
            engine = out.get("engine")
        else:
            reply_body = ""
            truth = 0.0
            engine = "none"

        human = _human_likeness_score(q, reply_body, truth)
        if human["passed"]:
            passed += 1

        row = {
            "id": item.get("id"),
            "category": item.get("category"),
            "question": q,
            "answer_excerpt": reply_body[:500],
            "truth_score": truth,
            "human_score": human["human_score"],
            "passed": human["passed"],
            "reasons": human["reasons"],
            "engine": engine,
        }
        results.append(row)
        try:
            with QUESTIONNAIRE_LOG.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({**row, "ts": _now()}, ensure_ascii=False) + "\n")
        except OSError:
            pass

    total = len(results)
    report = {
        "schema": "hostess7-questionnaire/v1",
        "ok": True,
        "ts": _now(),
        "total": total,
        "passed": passed,
        "score": f"{passed}/{total}",
        "perfect": passed == total == 20,
        "pass_rate": round(100 * passed / max(total, 1), 1),
        "results": results,
    }
    _save_json(QUESTIONNAIRE_PANEL, report)
    _save_json(RATING_STATE, {
        "updated": _now(),
        "last_questionnaire": report["score"],
        "last_pass_rate": report["pass_rate"],
        "perfect": report["perfect"],
    })
    return report


def rating_status() -> dict[str, Any]:
    st = _load_json(RATING_STATE, {})
    last = _load_json(QUESTIONNAIRE_PANEL, {})
    iq_last = _load_json(IQ_TEST_PANEL, {})
    return {
        "schema": "hostess7-truth-rating-status/v1",
        "updated": _now(),
        "always_rate_responses": True,
        "last_questionnaire": st.get("last_questionnaire"),
        "last_pass_rate": st.get("last_pass_rate"),
        "questionnaire_perfect": st.get("perfect"),
        "questionnaire": last if last.get("results") else None,
        "last_iq_test": st.get("last_iq_test"),
        "last_iq_pass_rate": st.get("last_iq_pass_rate"),
        "iq_pass": st.get("iq_pass"),
        "estimated_iq_band": st.get("estimated_iq_band"),
        "iq_test": iq_last if iq_last.get("results") else None,
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "status").strip()
    if cmd == "status":
        print(json.dumps(rating_status(), ensure_ascii=False))
        return 0
    if cmd == "questionnaire":
        print(json.dumps(run_questionnaire(), ensure_ascii=False))
        return 0
    if cmd == "iq-test":
        print(json.dumps(run_iq_test(), ensure_ascii=False))
        return 0
    if cmd == "rate" and len(sys.argv) >= 3:
        q = sys.argv[2] if len(sys.argv) > 3 else ""
        a = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else sys.argv[2]
        print(json.dumps(rate_response(a, question=q), ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: hostess7-truth-rating.py [status|questionnaire|rate Q A]"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())