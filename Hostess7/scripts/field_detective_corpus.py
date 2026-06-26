#!/usr/bin/env pythong
"""Field detective & lie-detector corpus — investigation, forensics, deception analysis.

Educational synthesis. Hostess 7 truth filter: 94% noise / 6% signal — corroborate before believe.
Not a substitute for licensed investigators, polygraph examiners, or court proceedings.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORPUS_CACHE = ROOT / "cache" / "fieldstorage" / "brain" / "detective" / "corpus.json"
DETECTIVE_CORPUS_VERSION = 1

NOISE_RATIO = 0.94
TRUTH_RATIO = 0.06

DETECTIVE_DOMAINS: tuple[dict[str, str | tuple[str, ...]], ...] = (
    {
        "id": "detective_foundations",
        "title": "Detective foundations — method & mindset",
        "tags": ("detective", "investigation", "inquiry", "deduction", "holmes", "sherlock"),
        "body": (
            "Investigation is structured doubt: observe → hypothesize → test → corroborate. "
            "Deduction: if premises true, conclusion necessary. Induction: best explanation from evidence. "
            "Abduction (inference to best explanation): rank hypotheses by parsimony, predictive power, fit. "
            "Never confuse story coherence with truth — liars optimize for plausibility, not verifiability. "
            "Hostess 7 method: local file evidence, QA GREEN, infinite drive index, git HEAD — "
            "multiple independent channels before advising an update."
        ),
    },
    {
        "id": "crime_scene",
        "title": "Crime scene investigation",
        "tags": ("crime scene", "csi", "evidence", "chain of custody", "trace", "scene"),
        "body": (
            "Secure scene → document → photograph → sketch → collect → preserve chain of custody. "
            "Locard exchange: every contact leaves a trace. "
            "Contamination destroys cases — gloves, logs, sealed containers, documented transfers. "
            "Reconstruct timeline: entry, activity, exit; align witness statements to physical layout. "
            "Digital scene parallel: preserve logs, disk images, memory dumps before power-off."
        ),
    },
    {
        "id": "forensic_science",
        "title": "Forensic science — physical & digital",
        "tags": ("forensic", "fingerprint", "dna", "ballistics", "toxicology", "digital forensics"),
        "body": (
            "Fingerprints: class characteristics + individual minutiae; AFIS database comparison. "
            "DNA: STR profiling, mixture deconvolution, CODIS; probabilistic genotyping. "
            "Ballistics: toolmarks, rifling, NIBIN cartridge case correlation. "
            "Digital: write-blocked imaging, hash verification (SHA-256), metadata vs content, "
            "timeline from MFT/event logs. "
            "Expert testimony: Daubert/Frye reliability — method, error rate, peer review, general acceptance."
        ),
    },
    {
        "id": "interview_interrogation",
        "title": "Interview & interrogation",
        "tags": ("interview", "interrogation", "witness", "suspect", "miranda", "statement"),
        "body": (
            "Cognitive interview: context reinstatement, varied recall, witness-generated detail. "
            "PEACE model: Preparation, Engage, Account, Closure, Evaluate — non-accusatory. "
            "Reid technique: controversial — risk of false confession; document voluntariness, recording mandatory. "
            "Miranda before custodial interrogation in US criminal context. "
            "Best practice: separate witnesses early; avoid contaminating memory with leading questions."
        ),
    },
    {
        "id": "lie_detection_verbal",
        "title": "Lie detection — verbal & statement analysis",
        "tags": ("lie", "deception", "statement analysis", "scan", "cbcb", "verbal", "truth"),
        "body": (
            "No single verbal cue proves deception — base rates and context matter. "
            "Statement Analysis (SCAN): unexpected structure shifts, missing emotions, altered time order, "
            "extraneous information, passive voice distancing, lack of experiential detail in critical segments. "
            "CBCA (Criteria-Based Content Analysis): structured criteria for statement credibility in some jurisdictions. "
            "Liars often over-specify irrelevant detail and under-specify sensory memory of core events. "
            "Truth tellers correct themselves; coached stories stay rigid. "
            "Hostess 7: compare claim against grep evidence, corpus version, infinite index — inconsistency flags."
        ),
    },
    {
        "id": "lie_detection_nonverbal",
        "title": "Lie detection — nonverbal & physiological",
        "tags": ("nonverbal", "microexpression", "polygraph", "physiological", "baseline", "stress"),
        "body": (
            "Ekman microexpressions: fleeting universal affect leakage — training improves detection modestly; "
            "not courtroom-proof alone. Baseline deviation: compare subject's normal speech rate, gesture rate, "
            "pause pattern under low-stakes vs high-stakes topics. "
            "Polygraph: measures arousal (GSR, BP, respiration) — not direct lie detection; "
            "inadmissible in most US federal courts (Daubert); high false-positive risk on anxious innocents. "
            "Voice stress analysis: weak scientific support for courtroom use. "
            "Best detector stack: corroborating documents + timeline + independent witnesses + forensics."
        ),
    },
    {
        "id": "corroboration_truth",
        "title": "Corroboration — infinite out the truth",
        "tags": ("corroboration", "truth", "verify", "source", "independent", "94", "6 percent"),
        "body": (
            "Fast internet: ~94% noise, ~6% verifiable signal — Hostess 7 infinite-drives truth only after corroboration. "
            "Independent sources: two+ channels that cannot both be fooled by same fabrication (file hash + QA + git). "
            "Triangulation: document, witness, physical, digital, statistical. "
            "Falsification: actively seek disconfirming evidence (Popper). "
            "Red flags: single anonymous source, no chain of custody, retroactive timestamps, "
            "magic-byte mismatch (filename lies — probe bytes in FieldFormatHistory). "
            "Truth score floor 30% before Hostess advises an update; 100% only on self-advisory loop with full brain scan."
        ),
    },
    {
        "id": "digital_investigation",
        "title": "Digital investigation & OSINT",
        "tags": ("osint", "digital", "metadata", "log", "timeline", "malware", "attribution"),
        "body": (
            "OSINT: public records, WHOIS, social graph, archived pages — verify provenance, not screenshot alone. "
            "Log correlation: auth failures, process creation, network flows — UTC normalized timeline. "
            "Malware attribution: TTP clustering, infrastructure reuse — probability not certainty. "
            "AMOURANTHRTX parallel: monolith_audit, ingest_index.json, thoughts.jsonl — detective read of codebase state. "
            "Field magic probe: ExtensionMap vs hex signature — detect when declared type contradicts bytes."
        ),
    },
    {
        "id": "hostess_lie_detector",
        "title": "Hostess 7 computational lie detector",
        "tags": ("hostess", "lie detector", "truth score", "smart boss", "advisory", "filter"),
        "body": (
            "Hostess 7 lie detector is computational corroboration — not a polygraph. "
            "Inputs: claim text, local evidence paths, corpus versions, infinite drive counts, QA script presence. "
            "Outputs: truth_score 0–100, deception_risk low|medium|high, inconsistency_flags[], "
            "recommended_action (reject|investigate|corroborate|accept). "
            "Commands: `./Hostess7.sh detect \"claim\"` · `./Hostess7.sh truth <text>` · `./Hostess7.sh updates`. "
            "Workspace: `HOSTESS7_WORKSPACE=detective ./Hostess7.sh` — bilateral L↔R investigation fusion."
        ),
    },
    {
        "id": "legal_admissibility",
        "title": "Legal framing — evidence & deception science",
        "tags": ("admissible", "hearsay", "expert", "daubert", "court", "privilege"),
        "body": (
            "Detective findings must meet jurisdiction rules: hearsay exceptions, authentication FRE 901, "
            "expert reliability Daubert. Polygraph results generally excluded in federal criminal trials. "
            "Private investigator licensure varies by state. "
            "Hostess 7 output is educational synthesis — not admissible expert testimony; "
            "counsel workspace handles formal court framing. "
            "Attorney-Client Privilege may attach to investigation strategy with licensed counsel."
        ),
    },
)


def build_corpus() -> dict:
    return {
        "version": DETECTIVE_CORPUS_VERSION,
        "domains": [dict(entry) for entry in DETECTIVE_DOMAINS],
        "domain_count": len(DETECTIVE_DOMAINS),
        "noise_ratio": NOISE_RATIO,
        "truth_ratio": TRUTH_RATIO,
        "disclaimer": (
            "Detective/lie-detector corpus is educational. Not licensed PI, polygraph, or legal advice. "
            "Corroborate all claims with independent evidence."
        ),
    }


def ensure_corpus() -> Path:
    CORPUS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    refresh = True
    if CORPUS_CACHE.is_file():
        try:
            data = json.loads(CORPUS_CACHE.read_text(encoding="utf-8"))
            refresh = int(data.get("version", 0)) < DETECTIVE_CORPUS_VERSION
        except (json.JSONDecodeError, TypeError, ValueError):
            refresh = True
    if refresh:
        CORPUS_CACHE.write_text(json.dumps(build_corpus(), indent=2) + "\n", encoding="utf-8")
    return CORPUS_CACHE


def _tokens(query: str) -> list[str]:
    return [t for t in re.split(r"\W+", query.lower()) if len(t) > 2]


def search_detective(query: str, *, limit: int = 6) -> list[dict]:
    ensure_corpus()
    try:
        doc = json.loads(CORPUS_CACHE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        doc = build_corpus()
    domains = doc.get("domains") or []
    toks = _tokens(query)
    q = query.lower()
    scored: list[tuple[int, dict]] = []
    for d in domains:
        tags = " ".join(d.get("tags") or []).lower()
        body = str(d.get("body", "")).lower()
        title = str(d.get("title", "")).lower()
        blob = f"{title} {tags} {body[:2000]}"
        score = sum(5 if t in tags else 2 if t in blob else 0 for t in toks)
        if any(k in q for k in ("lie", "deception", "deceive", "lying", "polygraph")):
            if d.get("id") in ("lie_detection_verbal", "lie_detection_nonverbal", "hostess_lie_detector"):
                score += 18
        if any(k in q for k in ("detective", "investigate", "investigation", "sherlock")):
            if d.get("id") in ("detective_foundations", "crime_scene"):
                score += 15
        if any(k in q for k in ("forensic", "fingerprint", "dna", "digital")):
            if d.get("id") in ("forensic_science", "digital_investigation"):
                score += 15
        if any(k in q for k in ("truth", "corroborate", "94", "verify")):
            if d.get("id") in ("corroboration_truth", "hostess_lie_detector"):
                score += 15
        if score > 0:
            scored.append((score, d))
    scored.sort(key=lambda x: -x[0])
    return [d for _, d in scored[:limit]]


def _deception_flags(text: str) -> list[str]:
    """Heuristic inconsistency flags — educational, not definitive."""
    flags: list[str] = []
    low = text.lower()
    if re.search(r"\b(always|never|everyone|no one|100%|guaranteed)\b", low):
        flags.append("absolute_language")
    if re.search(r"\b(trust me|believe me|to be honest|frankly)\b", low):
        flags.append("credibility_appeal")
    if len(text.split()) > 40 and not re.search(r"\b(because|since|therefore|evidence|document|log|file)\b", low):
        flags.append("long_claim_no_evidence_anchor")
    if re.search(r"\b(they said|someone told|rumor|heard that)\b", low) and "source" not in low:
        flags.append("hearsay_without_source")
    if re.search(r"\b(probably|maybe|might have|sort of)\b", low) and re.search(r"\b(definitely|certainly|proved)\b", low):
        flags.append("confidence_inconsistency")
    return flags


def analyze_truth(
    claim: str,
    *,
    local_evidence: int = 0,
    qa_green: bool = False,
    infinite_indexed: bool = False,
    corroboration_channels: int = 0,
) -> dict[str, Any]:
    """Hostess 7 computational lie detector — corroboration-weighted truth score."""
    flags = _deception_flags(claim)
    score = TRUTH_RATIO * 100
    if local_evidence:
        score += min(25, local_evidence * 8)
    if qa_green:
        score += 18
    if infinite_indexed:
        score += 15
    score += min(20, corroboration_channels * 6)
    score -= len(flags) * 8
    score = max(0.0, min(100.0, round(score, 1)))

    if score >= 70:
        risk = "low"
        action = "accept_with_documentation"
    elif score >= 40:
        risk = "medium"
        action = "corroborate_before_acting"
    else:
        risk = "high"
        action = "reject_or_investigate"

    return {
        "claim_preview": claim[:200],
        "truth_score": score,
        "deception_risk": risk,
        "inconsistency_flags": flags,
        "noise_ratio": NOISE_RATIO,
        "truth_ratio": TRUTH_RATIO,
        "recommended_action": action,
        "verdict": (
            f"Truth {score}% — deception risk {risk}. "
            f"{len(flags)} verbal flags. Corroborate: grep + QA + infinite index."
        ),
    }


def synthesize_detective_paragraphs(query: str) -> list[str]:
    hits = search_detective(query, limit=5)
    if not hits:
        hits = search_detective("detective lie deception corroboration truth", limit=4)
    paras: list[str] = []
    pro = os.environ.get("AMOURANTHRTX_HOSTESS") == "1" and os.environ.get("HOSTESS7_PRO", "1") == "1"
    if pro:
        paras.append(
            "Investigation note: educational synthesis — corroborate with independent evidence; "
            "not licensed PI or admissible polygraph."
        )
    else:
        paras.append(
            "Detective note: Hostess 7 holds investigation method, forensics, interview science, "
            "verbal/nonverbal deception cues, and computational truth scoring — "
            "94% noise / 6% truth until corroborated."
        )
    for h in hits:
        title = h.get("title", "Detective")
        body = str(h.get("body", "")).strip()
        if len(body) > 1150:
            body = body[:1150] + "… [truncated — cache/fieldstorage/brain/detective/corpus.json]"
        paras.append(f"{title}: {body}")
    return paras


def corpus_stats() -> dict:
    ensure_corpus()
    doc = json.loads(CORPUS_CACHE.read_text(encoding="utf-8"))
    return {
        "version": doc.get("version", DETECTIVE_CORPUS_VERSION),
        "domains": doc.get("domain_count", len(DETECTIVE_DOMAINS)),
    }


if __name__ == "__main__":
    ensure_corpus()
    import sys
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "lie detector deception corroboration"
    for p in synthesize_detective_paragraphs(q):
        print(p)
        print()
    if "--analyze" in sys.argv:
        claim = " ".join(a for a in sys.argv[1:] if a != "--analyze")
        print(json.dumps(analyze_truth(claim, local_evidence=2, qa_green=True), indent=2))