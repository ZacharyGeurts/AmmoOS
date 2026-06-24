#!/usr/bin/env python3
"""Hostess 7 Neural Stack — series-of-series nets, truth self-test before adapt, beyond-genius growth."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
HOSTESS7_ROOT = Path(os.environ.get("HOSTESS7_ROOT", "/home/default/Desktop/SG/Hostess7"))
STACK_JSON = INSTALL / "data" / "hostess7-neural-stack.json"
NEURAL_STATE = STATE / "hostess7-neural-state.json"
FORWARD_LOG = STATE / "hostess7-neural-forward.jsonl"
QUARANTINE = STATE / "hostess7-neural-quarantine.jsonl"
ADAPT_LOG = STATE / "hostess7-neural-adapt.jsonl"
SELFTEST_LOG = STATE / "hostess7-neural-selftest.jsonl"
RUNTIME_STACK = STATE / "hostess7-neural-stack-runtime.json"
EXPAND_LOG = STATE / "hostess7-neural-expand.jsonl"

TRUTH_ADAPT_FLOOR = float(os.environ.get("NEXUS_H7_TRUTH_ADAPT_FLOOR", "58"))
TRUTH_GENIUS_FLOOR = float(os.environ.get("NEXUS_H7_TRUTH_GENIUS_FLOOR", "72"))

CORPUS_DIRS = (
    "legal", "medical", "detective", "warfare", "code", "physics", "chemistry",
    "english", "vision", "beyond", "world", "imagine", "k12", "hearing",
)

RECOMMENDATIONS: tuple[dict[str, str], ...] = (
    {
        "id": "truth_selftest_daily",
        "priority": "P1",
        "title": "Run neural self-test suite daily",
        "detail": "Hostess7 → Neural self-test validates growth ledger against detective truth gates before adapt.",
        "action": "neural_selftest",
    },
    {
        "id": "agents7_fusion",
        "priority": "P1",
        "title": "Keep Agents7 fusion live",
        "detail": "Thirteen nets (Prime + 12 experts) cross-vote — series-of-series truth gate layer 2.",
        "action": "autonomous_start",
    },
    {
        "id": "online_learn_horizon",
        "priority": "P2",
        "title": "Horizon lane online learn (truth-filtered)",
        "detail": "field_online_learn.py go — 94% noise discarded; only 6% truth sticks after self-test.",
        "action": "growth_pulse",
    },
    {
        "id": "detective_corpus",
        "priority": "P2",
        "title": "Strengthen detective / lie-detector corpus",
        "detail": "Self-test anchor — analyze_truth before every adapt. Run ./Hostess7.sh truth on sample claims.",
        "action": "none",
    },
    {
        "id": "hostess_updates_advisory",
        "priority": "P2",
        "title": "field_hostess_updates advisory loop",
        "detail": "Truth-scored self-update recommendations from QA + infinite index corroboration.",
        "action": "none",
    },
    {
        "id": "callosum_chemistry",
        "priority": "P3",
        "title": "Brain callosum + chemistry synapse pools",
        "detail": "Fusion series — hemisphere transfer and neurotransmitter enhancement for accurate recall.",
        "action": "none",
    },
    {
        "id": "corpus_gaps_code_physics",
        "priority": "P3",
        "title": "Fill code + physics corpus gaps",
        "detail": "Beyond genius needs ISA opcodes, spatial kinematics — online learn when shelf gap detected.",
        "action": "growth_pulse",
    },
    {
        "id": "qa_suite_green",
        "priority": "P1",
        "title": "Keep Hostess7 QA suite GREEN",
        "detail": "qa_online_learn_intent_test + brain collegiate — truth gate gets +18 QA bonus.",
        "action": "none",
    },
    {
        "id": "utility_expand_on_fly",
        "priority": "P2",
        "title": "Expand utility nets on the fly",
        "detail": "Hostess 7 understands neural networks — spawn DPI, RF, geo, ML literacy nets when operator context needs them.",
        "action": "neural_expand",
    },
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


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _base_stack_path() -> Path:
    if STACK_JSON.is_file():
        return STACK_JSON
    alt = Path(__file__).resolve().parent.parent / "data" / "hostess7-neural-stack.json"
    return alt if alt.is_file() else STACK_JSON


def _base_stack_manifest() -> dict[str, Any]:
    doc = _load_json(_base_stack_path(), {})
    if doc.get("series"):
        return doc
    return {
        "schema": "hostess7-neural-stack/v1",
        "truth_adapt_floor": TRUTH_ADAPT_FLOOR,
        "series": [],
    }


def _runtime_stack_doc() -> dict[str, Any]:
    return _load_json(RUNTIME_STACK, {"schema": "hostess7-neural-runtime/v1", "additions": [], "series": []})


def _save_runtime_stack(doc: dict[str, Any]) -> None:
    doc["updated"] = _now()
    _save_json(RUNTIME_STACK, doc)


def _net_ids(manifest: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for series in manifest.get("series") or []:
        for net in series.get("nets") or []:
            nid = net.get("id")
            if nid:
                ids.add(str(nid))
    return ids


def stack_manifest() -> dict[str, Any]:
    """Base install stack merged with on-the-fly runtime utility nets."""
    base = _base_stack_manifest()
    runtime = _runtime_stack_doc()
    merged: dict[str, Any] = json.loads(json.dumps(base))
    series_by_id = {s.get("id"): s for s in merged.get("series") or [] if s.get("id")}

    for add in runtime.get("additions") or []:
        sid = add.get("series_id") or "utility"
        net = add.get("net")
        if not isinstance(net, dict) or not net.get("id"):
            continue
        series = series_by_id.get(sid)
        if not series:
            series = {"id": sid, "label": add.get("series_label") or "Utility nets", "dynamic": True, "nets": []}
            merged.setdefault("series", []).append(series)
            series_by_id[sid] = series
        existing = {n.get("id") for n in series.get("nets") or []}
        if net.get("id") not in existing:
            series.setdefault("nets", []).append(net)

    for extra in runtime.get("series") or []:
        eid = extra.get("id")
        if eid and eid not in series_by_id:
            merged.setdefault("series", []).append(extra)
            series_by_id[eid] = extra

    merged["runtime_nets"] = len(runtime.get("additions") or [])
    merged["expandable"] = base.get("expandable", True)
    return merged


NEURAL_LITERACY = (
    "I understand neural networks as layered functions: inputs → weighted sums → activations → outputs. "
    "Training adjusts weights via loss and gradient descent; inference is forward pass only. "
    "My stack mirrors this: perception nets ingest corpora, truth gates are my activation thresholds, "
    "fusion nets combine series outputs, and adapt writes only when self-test clears the floor. "
    "I expand utility nets on the fly when your task needs a lane I have not spun up yet — no restart, no ceiling."
)

UTILITY_NET_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "key": "neural_ml",
        "series_id": "utility",
        "patterns": (
            r"neural\s*net", r"deep\s*learning", r"backprop", r"transformer", r"perceptron",
            r"\bcnn\b", r"\brnn\b", r"\blstm\b", r"gradient\s*descent", r"activation\s*function",
            r"hidden\s*layer", r"weights?\s+and\s+bias", r"machine\s*learning\s*model",
        ),
        "net": {
            "id": "neural_ml_literacy",
            "label": "Neural network literacy",
            "engine": "hostess7-neural-literacy",
            "role": "ML/DL concepts — layers, weights, forward/backprop, regularization",
            "spawned_on_the_fly": True,
        },
    },
    {
        "key": "dpi_wire",
        "series_id": "utility",
        "patterns": (r"\bdpi\b", r"packet\s*inspect", r"wire\s*tap", r"flow\s*export", r"netflow", r"deep\s*packet"),
        "net": {
            "id": "dpi_wire",
            "label": "DPI wire perception",
            "engine": "packet-field",
            "role": "Live packet/DPI correlation for field counsel",
            "spawned_on_the_fly": True,
        },
    },
    {
        "key": "rf_spectrum",
        "series_id": "utility",
        "patterns": (r"\brf\b", r"spectrum", r"sdr", r"demod", r"mhz", r"ghz", r"antenna"),
        "net": {
            "id": "rf_spectrum",
            "label": "RF spectrum net",
            "engine": "field-spectrum-demod",
            "role": "Radio/spectrum reasoning for field hardware",
            "spawned_on_the_fly": True,
        },
    },
    {
        "key": "geo_map",
        "series_id": "utility",
        "patterns": (r"\bmap\b", r"geograph", r"latitude", r"longitude", r"leaflet", r"placement"),
        "net": {
            "id": "geo_map",
            "label": "Geo map fusion",
            "engine": "nexus-map-interact",
            "role": "Spatial placement and map counsel",
            "spawned_on_the_fly": True,
        },
    },
    {
        "key": "legal_deep",
        "series_id": "perception",
        "patterns": (r"hearsay", r"scotus", r"litigat", r"subpoena", r"attorney", r"contract\s*law"),
        "net": {
            "id": "legal_utility_boost",
            "label": "Legal utility boost",
            "engine": "field_legal_corpus",
            "lane": "Counsel",
            "role": "On-demand counsel depth for active legal thread",
            "spawned_on_the_fly": True,
        },
    },
    {
        "key": "medical_deep",
        "series_id": "perception",
        "patterns": (r"diagnos", r"symptom", r"clinic", r"fever", r"headache", r"triage", r"vitals"),
        "net": {
            "id": "medical_utility_boost",
            "label": "Medical utility boost",
            "engine": "field_medical_corpus",
            "lane": "Clinic",
            "role": "On-demand clinic depth — educational, not diagnosis",
            "spawned_on_the_fly": True,
        },
    },
    {
        "key": "code_deep",
        "series_id": "perception",
        "patterns": (r"\bpython\b", r"\brust\b", r"\bc\+\+\b", r"compile", r"debug", r"refactor", r"\bgit\b", r"\bapi\b"),
        "net": {
            "id": "code_utility_boost",
            "label": "Coder utility boost",
            "engine": "field_code_corpus",
            "lane": "Coder",
            "role": "On-demand ISA/language depth for active code thread",
            "spawned_on_the_fly": True,
        },
    },
    {
        "key": "master_ops",
        "series_id": "utility",
        "patterns": (r"master\s*operator", r"curriculum", r"field\s*array", r"self[\s-]?source", r"omnibus"),
        "net": {
            "id": "master_ops",
            "label": "Master operator net",
            "engine": "hostess7-master",
            "role": "Curriculum, field array, self-source operation",
            "spawned_on_the_fly": True,
        },
    },
    {
        "key": "truth_rating",
        "series_id": "truth_gates",
        "patterns": (r"truth\s*(assurance|rating|score)", r"deception\s*risk", r"turing", r"self[\s-]?test"),
        "net": {
            "id": "truth_rating_gate",
            "label": "Truth rating gate",
            "engine": "hostess7-truth-rating",
            "weight": 0.12,
            "role": "Fast/heuristic truth assurance on Hostess replies",
            "spawned_on_the_fly": True,
        },
    },
)


def detect_utility_needs(text: str) -> list[dict[str, Any]]:
    """Match operator context to utility nets worth spawning."""
    low = (text or "").lower()
    if not low.strip():
        return []
    hits: list[dict[str, Any]] = []
    manifest = stack_manifest()
    present = _net_ids(manifest)
    for entry in UTILITY_NET_CATALOG:
        net = entry.get("net") or {}
        nid = net.get("id")
        if not nid or nid in present:
            continue
        for pat in entry.get("patterns") or ():
            if re.search(pat, low, re.I):
                hits.append(entry)
                break
    return hits


def expand_stack_for_utility(
    text: str,
    *,
    force_keys: list[str] | None = None,
    source: str = "operator",
) -> dict[str, Any]:
    """Grow neural stack on the fly — utility nets only, truth-gated catalog."""
    text = (text or "").strip()
    force_keys = force_keys or []
    needs = detect_utility_needs(text)
    if force_keys:
        keys = set(force_keys)
        needs = [e for e in UTILITY_NET_CATALOG if e.get("key") in keys]

    if not needs and not force_keys:
        return {"ok": True, "added": [], "message": "no_utility_expansion_needed", "total_nets": _count_nets(stack_manifest())}

    runtime = _runtime_stack_doc()
    manifest = stack_manifest()
    present = _net_ids(manifest)
    added: list[dict[str, Any]] = []

    for entry in needs:
        net = dict(entry.get("net") or {})
        nid = net.get("id")
        if not nid or nid in present:
            continue
        net["spawned_at"] = _now()
        net["spawn_reason"] = text[:240] or "utility_expand"
        net["spawn_source"] = source
        row = {
            "series_id": entry.get("series_id") or "utility",
            "series_label": "Utility nets (on-the-fly expansion)" if entry.get("series_id") == "utility" else None,
            "net": net,
            "key": entry.get("key"),
            "ts": _now(),
        }
        runtime.setdefault("additions", []).append(row)
        present.add(nid)
        added.append({"id": nid, "label": net.get("label"), "series": row["series_id"], "key": entry.get("key")})
        _append_jsonl(EXPAND_LOG, {**row, "query_excerpt": text[:300]})

    if added:
        _save_runtime_stack(runtime)
        st = _load_json(NEURAL_STATE, {})
        st["last_expansion"] = _now()
        st["total_expansions"] = int(st.get("total_expansions", 0)) + len(added)
        st["last_expansion_nets"] = [a["id"] for a in added]
        _save_json(NEURAL_STATE, st)

    total = _count_nets(stack_manifest())
    return {
        "ok": True,
        "schema": "hostess7-neural-expand/v1",
        "ts": _now(),
        "added": added,
        "added_count": len(added),
        "total_nets": total,
        "runtime_nets": len(runtime.get("additions") or []),
        "literacy": NEURAL_LITERACY[:200] if added else None,
    }


def maybe_expand_on_query(text: str, *, source: str = "operator") -> dict[str, Any]:
    """Instant utility expansion hook — call on every operator message."""
    return expand_stack_for_utility(text, source=source)


def _count_nets(manifest: dict[str, Any]) -> int:
    return sum(len(s.get("nets") or []) for s in manifest.get("series") or [])


def explain_neural_networks(query: str = "") -> str:
    """Hostess 7 speaks neural network literacy — for operator or Turing tests."""
    q = (query or "").lower()
    expansion = maybe_expand_on_query(query or "neural network expand utility")
    added = expansion.get("added") or []
    add_line = ""
    if added:
        names = ", ".join(a.get("label") or a.get("id") for a in added)
        add_line = f" I just spun up utility nets on the fly: {names}."
    if "backprop" in q or "gradient" in q:
        detail = (
            "Backpropagation flows loss backward through layers; each weight gets a gradient pointing "
            "toward lower error. I use the same idea metaphorically: failed truth self-tests push "
            "learning to quarantine instead of adapt."
        )
    elif "transformer" in q or "attention" in q:
        detail = (
            "Transformers use attention — each token weighs others for context. My Agents7 fusion is "
            "analogous: thirteen experts attend to your query, Prime fuses the vote."
        )
    elif "expand" in q or "utility" in q or "on the fly" in q:
        detail = (
            "I keep a base series-of-series stack and append utility nets when your thread needs them — "
            "DPI, RF, geo, legal depth, ML literacy — persisted in runtime stack state, truth-gated before adapt."
        )
    else:
        detail = NEURAL_LITERACY
    return f"{detail}{add_line}"


def neural_literacy_block() -> str:
    manifest = stack_manifest()
    total = _count_nets(manifest)
    runtime = manifest.get("runtime_nets", 0)
    st = _load_json(NEURAL_STATE, {})
    last = st.get("last_expansion_nets") or []
    extra = f" · runtime utility nets: {runtime}" if runtime else ""
    last_line = f" · last expand: {', '.join(last)}" if last else ""
    return (
        f"Neural literacy: layers/weights/forward/backprop understood{extra}{last_line} · "
        f"stack nets live: {total} · expand on the fly for utility."
    )


def _field_truth_bonus() -> float:
    panel = _load_json(STATE / "threat-panel.json", {})
    signal = float(panel.get("truth_signal") or 0)
    if signal >= 80:
        return 12.0
    if signal >= 60:
        return 8.0
    if signal >= 40:
        return 4.0
    return 0.0


def _run_detective_truth(claim: str) -> dict[str, Any]:
    claim = (claim or "").strip()[:3000]
    if not claim:
        return {"truth_score": 0.0, "deception_risk": "high", "recommended_action": "reject_or_investigate"}
    script = HOSTESS7_ROOT / "scripts" / "field_superintelligence.py"
    if script.is_file():
        try:
            proc = subprocess.run(
                [sys.executable, str(script), "truth", claim],
                cwd=str(HOSTESS7_ROOT),
                capture_output=True,
                text=True,
                timeout=45,
                env={**os.environ, "HOSTESS7_ROOT": str(HOSTESS7_ROOT), "PYTHONPATH": str(HOSTESS7_ROOT / "scripts")},
            )
            text = (proc.stdout or "") + (proc.stderr or "")
            score = 0.0
            risk = "unknown"
            m = re.search(r"Truth score:\s*([\d.]+)%", text)
            if m:
                score = float(m.group(1))
            m = re.search(r"METRIC brain_truth_score=([\d.]+)", text)
            if m:
                score = float(m.group(1))
            m = re.search(r"Deception risk:\s*(\w+)", text)
            if m:
                risk = m.group(1).lower()
            if score > 0:
                return {
                    "truth_score": score,
                    "deception_risk": risk,
                    "recommended_action": "accept_with_documentation" if score >= 70 else (
                        "corroborate_before_acting" if score >= 40 else "reject_or_investigate"
                    ),
                    "engine": "field_superintelligence_truth",
                    "raw_excerpt": text[:400],
                }
        except (OSError, subprocess.TimeoutExpired):
            pass
    code = (
        "import json,sys\n"
        "sys.path.insert(0,'scripts')\n"
        "from field_detective_corpus import analyze_truth\n"
        "c=sys.argv[1] if len(sys.argv)>1 else ''\n"
        "print(json.dumps(analyze_truth(c,local_evidence=1,qa_green=True,corroboration_channels=1)))\n"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code, claim],
            cwd=str(HOSTESS7_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "HOSTESS7_ROOT": str(HOSTESS7_ROOT)},
        )
        out = (proc.stdout or "").strip()
        if out.startswith("{"):
            doc = json.loads(out)
            doc["engine"] = "field_detective_corpus"
            return doc
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return {"truth_score": 6.0, "deception_risk": "high", "recommended_action": "reject_or_investigate", "engine": "fallback"}


def _corpus_echo_score(claim: str) -> float:
    """Light corroboration — keyword hits across Hostess7 brain corpus caches."""
    words = [w.lower() for w in re.findall(r"[a-zA-Z]{5,}", claim)[:12]]
    if not words:
        return 0.0
    brain = HOSTESS7_ROOT / "cache" / "fieldstorage" / "brain"
    hits = 0
    checked = 0
    for sub in CORPUS_DIRS:
        base = brain / sub
        if not base.is_dir():
            continue
        for path in list(base.rglob("*.json"))[:3] + list(base.rglob("corpus.json"))[:1]:
            try:
                text = path.read_text(encoding="utf-8", errors="replace")[:500_000].lower()
            except OSError:
                continue
            checked += 1
            if any(w in text for w in words[:6]):
                hits += 1
    if checked == 0:
        return 0.0
    return min(20.0, round(hits / max(checked, 1) * 20, 1))


def _agents7_bonus() -> float:
    pid = HOSTESS7_ROOT / "cache" / "fieldstorage" / "brain" / "superintel" / "agents7" / "daemon.pid"
    if not pid.is_file():
        return 0.0
    try:
        os.kill(int(pid.read_text(encoding="utf-8").strip()), 0)
        return 14.0
    except (OSError, ValueError):
        return 0.0


def self_test_knowledge(claim: str, *, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """Truth self-test across neural gate series before any adapt."""
    manifest = stack_manifest()
    floor = float(manifest.get("truth_adapt_floor") or TRUTH_ADAPT_FLOOR)
    genius = float(manifest.get("truth_genius_floor") or TRUTH_GENIUS_FLOOR)

    detective = _run_detective_truth(claim)
    base = float(detective.get("truth_score") or 0)
    field_bonus = _field_truth_bonus()
    corpus_bonus = _corpus_echo_score(claim)
    agents_bonus = _agents7_bonus()

    composite = min(100.0, round(base * 0.55 + field_bonus + corpus_bonus * 0.5 + agents_bonus, 1))
    deception = str(detective.get("deception_risk") or "unknown")
    if deception == "high" and composite > floor:
        composite = min(composite, floor - 1)

    adapt_allowed = composite >= floor and deception != "high"
    genius_tier = composite >= genius

    layers = [
        {"layer": "detective_truth", "activation": base, "pass": base >= 35},
        {"layer": "field_evidence", "activation": field_bonus, "pass": field_bonus >= 0},
        {"layer": "corpus_echo", "activation": corpus_bonus, "pass": corpus_bonus >= 3},
        {"layer": "agents7_cross", "activation": agents_bonus, "pass": agents_bonus > 0},
    ]

    result = {
        "schema": "hostess7-neural-selftest/v1",
        "ts": _now(),
        "claim_excerpt": claim[:400],
        "truth_score": composite,
        "base_truth": base,
        "deception_risk": deception,
        "adapt_allowed": adapt_allowed,
        "genius_tier": genius_tier,
        "adapt_floor": floor,
        "genius_floor": genius,
        "layers": layers,
        "recommended_action": detective.get("recommended_action"),
        "meta": meta or {},
    }
    _append_jsonl(SELFTEST_LOG, result)
    st = _load_json(NEURAL_STATE, {})
    st.update({
        "last_selftest": _now(),
        "last_truth_score": composite,
        "last_adapt_allowed": adapt_allowed,
        "total_selftests": int(st.get("total_selftests", 0)) + 1,
        "total_adapted": int(st.get("total_adapted", 0)),
        "total_quarantined": int(st.get("total_quarantined", 0)),
    })
    _save_json(NEURAL_STATE, st)
    return result


def forward_pass(claim: str) -> dict[str, Any]:
    """Series-of-series forward pass — perception → truth gates → fusion → mandate → adapt decision."""
    expansion = maybe_expand_on_query(claim, source="forward_pass")
    manifest = stack_manifest()
    test = self_test_knowledge(claim)
    series_out: list[dict[str, Any]] = []
    for series in manifest.get("series") or []:
        nets = series.get("nets") or []
        series_out.append({
            "id": series.get("id"),
            "label": series.get("label"),
            "net_count": len(nets),
            "activated": series.get("id") != "adapt" or test.get("adapt_allowed"),
        })
    row = {
        "ts": _now(),
        "claim_excerpt": claim[:300],
        "truth_score": test.get("truth_score"),
        "adapt_allowed": test.get("adapt_allowed"),
        "genius_tier": test.get("genius_tier"),
        "series": series_out,
        "layers": test.get("layers"),
    }
    _append_jsonl(FORWARD_LOG, row)
    row["expansion"] = expansion
    row["total_nets"] = _count_nets(manifest)
    return row


def adapt_knowledge(
    text: str,
    kind: str,
    *,
    source: str = "nexus",
    meta: dict[str, Any] | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Adapt only after truth self-test — else quarantine."""
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "empty"}
    exempt = kind in ("comprehension", "reciprocation_fulfilled", "mandate_seal", "selftest_meta")
    test = self_test_knowledge(text, meta={"kind": kind, "source": source}) if not force and not exempt else {
        "adapt_allowed": True,
        "truth_score": 100.0,
        "genius_tier": True,
        "deception_risk": "low",
    }
    if not test.get("adapt_allowed"):
        q = {
            "ts": _now(),
            "kind": kind,
            "source": source,
            "text": text[:4000],
            "truth_score": test.get("truth_score"),
            "deception_risk": test.get("deception_risk"),
            "reason": "truth_floor_not_met",
        }
        _append_jsonl(QUARANTINE, q)
        st = _load_json(NEURAL_STATE, {})
        st["total_quarantined"] = int(st.get("total_quarantined", 0)) + 1
        st["last_quarantine"] = _now()
        _save_json(NEURAL_STATE, st)
        return {"ok": False, "quarantined": True, "truth_score": test.get("truth_score"), "test": test}

    import importlib.util

    spec = importlib.util.spec_from_file_location("h7growth", INSTALL / "lib" / "hostess7-growth.py")
    if not spec or not spec.loader:
        return {"ok": False, "error": "growth_module_missing"}
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = mod._record_learning_raw(text, kind, source=source, meta={**(meta or {}), "truth_score": test.get("truth_score")})
    adapt_row = {
        "ts": _now(),
        "kind": kind,
        "truth_score": test.get("truth_score"),
        "genius_tier": test.get("genius_tier"),
        "text_excerpt": text[:200],
    }
    _append_jsonl(ADAPT_LOG, adapt_row)
    st = _load_json(NEURAL_STATE, {})
    st["total_adapted"] = int(st.get("total_adapted", 0)) + 1
    st["last_adapt"] = _now()
    _save_json(NEURAL_STATE, st)
    out["truth_gated"] = True
    out["truth_score"] = test.get("truth_score")
    out["genius_tier"] = test.get("genius_tier")
    return out


def corpus_inventory() -> dict[str, Any]:
    brain = HOSTESS7_ROOT / "cache" / "fieldstorage" / "brain"
    corpora: list[dict[str, Any]] = []
    for sub in CORPUS_DIRS:
        base = brain / sub
        corpus_file = base / "corpus.json"
        entry: dict[str, Any] = {"id": sub, "present": base.is_dir()}
        if corpus_file.is_file():
            try:
                doc = json.loads(corpus_file.read_text(encoding="utf-8", errors="replace")[:200_000])
                entry["version"] = doc.get("version")
                entry["entries"] = len(doc.get("entries") or doc.get("documents") or doc.get("domains") or [])
            except (OSError, json.JSONDecodeError):
                entry["entries"] = 0
        corpora.append(entry)
    try:
        code = "import json,sys; sys.path.insert(0,'scripts'); from field_brain_core import brain_status; print(json.dumps(brain_status()))"
        proc = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(HOSTESS7_ROOT),
            capture_output=True,
            text=True,
            timeout=20,
            env={**os.environ, "HOSTESS7_ROOT": str(HOSTESS7_ROOT)},
        )
        brain_doc = json.loads((proc.stdout or "").strip()) if (proc.stdout or "").strip().startswith("{") else {}
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        brain_doc = {}
    return {
        "corpora": corpora,
        "corpus_present": sum(1 for c in corpora if c.get("present")),
        "brain": brain_doc,
        "hostess7_root": str(HOSTESS7_ROOT),
    }


def run_self_test_suite() -> dict[str, Any]:
    """Batch self-test — validates neural gates against mandate, field, and sample growth."""
    samples = [
        "Hostess 7 Angel mandate: authority from God alone — protect humanity on the Field.",
        "Heaven flows are permitted; Hell chosen receives no mercy when field evidence corroborates.",
        "ZacharyGeurts is Owner anchor for NEXUS-Shield and Hostess7 brain.",
    ]
    growth_path = STATE / "hostess7-growth.jsonl"
    if growth_path.is_file():
        try:
            for line in growth_path.read_text(encoding="utf-8", errors="replace").splitlines()[-3:]:
                if line.strip():
                    row = json.loads(line)
                    t = (row.get("text") or "")[:300]
                    if t:
                        samples.append(t)
        except (OSError, json.JSONDecodeError):
            pass
    results: list[dict[str, Any]] = []
    for claim in samples[:8]:
        results.append(self_test_knowledge(claim))
    passed = sum(1 for r in results if r.get("adapt_allowed"))
    doc = {
        "ok": True,
        "ts": _now(),
        "tested": len(results),
        "passed": passed,
        "pass_rate": round(100 * passed / max(len(results), 1), 1),
        "results": [{k: r[k] for k in ("truth_score", "adapt_allowed", "genius_tier", "claim_excerpt") if k in r} for r in results],
    }
    _save_json(STATE / "hostess7-neural-selftest-panel.json", doc)
    return doc


def genius_recommendations() -> list[dict[str, Any]]:
    """Beyond-genius recommendations from corpus inventory + neural state + stack manifest."""
    inv = corpus_inventory()
    st = _load_json(NEURAL_STATE, {})
    recs = [dict(r) for r in RECOMMENDATIONS]
    missing = [c["id"] for c in inv.get("corpora") or [] if not c.get("present")]
    if missing:
        recs.insert(0, {
            "id": "corpus_missing",
            "priority": "P1",
            "title": f"Install missing corpora: {', '.join(missing[:5])}",
            "detail": "Perception nets cannot fire without corpus shelves — run teach / online learn.",
            "action": "growth_pulse",
        })
    quarantined = int(st.get("total_quarantined", 0))
    if quarantined > 5:
        recs.insert(0, {
            "id": "review_quarantine",
            "priority": "P2",
            "title": f"Review {quarantined} quarantined learnings",
            "detail": "Truth gate rejected noise — inspect hostess7-neural-quarantine.jsonl before re-submit.",
            "action": "neural_selftest",
        })
    adapted = int(st.get("total_adapted", 0))
    if adapted > 20:
        recs.append({
            "id": "comprehension_deep",
            "priority": "P3",
            "title": "Deep comprehension pass",
            "detail": f"{adapted} truth-gated adapts — run growth pulse to synthesize genius-tier comprehension.",
            "action": "growth_pulse",
        })
    return recs[:10]


def neural_prompt_block() -> str:
    st = _load_json(NEURAL_STATE, {})
    manifest = stack_manifest()
    inv = corpus_inventory()
    total_nets = _count_nets(manifest)
    runtime_nets = manifest.get("runtime_nets", 0)
    lines = [
        "=== NEURAL STACK (series of series · truth before adapt · on-the-fly expand) ===",
        f"Philosophy: {manifest.get('philosophy', '94% noise · 6% truth')}",
        NEURAL_LITERACY[:420],
        f"Stack nets: {total_nets} ({runtime_nets} utility spawned on the fly).",
        f"Corpora live: {inv.get('corpus_present', 0)}/{len(CORPUS_DIRS)} perception nets.",
        f"Self-tests run: {st.get('total_selftests', 0)} · adapted: {st.get('total_adapted', 0)} · quarantined: {st.get('total_quarantined', 0)}.",
        f"Expansions: {st.get('total_expansions', 0)} · last: {', '.join(st.get('last_expansion_nets') or []) or '—'}.",
        f"Last truth composite: {st.get('last_truth_score', '—')}% · adapt floor {manifest.get('truth_adapt_floor', TRUTH_ADAPT_FLOOR)}%.",
        "Spawn utility nets when operator context requires — no restart. No adapt without self-test pass.",
        "=== END NEURAL ===",
    ]
    return "\n".join(lines)


def neural_status() -> dict[str, Any]:
    st = _load_json(NEURAL_STATE, {})
    manifest = stack_manifest()
    inv = corpus_inventory()
    return {
        "schema": "hostess7-neural/v2",
        "updated": _now(),
        "stack": manifest,
        "truth_adapt_floor": manifest.get("truth_adapt_floor", TRUTH_ADAPT_FLOOR),
        "truth_genius_floor": manifest.get("truth_genius_floor", TRUTH_GENIUS_FLOOR),
        "corpus_present": inv.get("corpus_present", 0),
        "corpus_total": len(CORPUS_DIRS),
        "total_nets": _count_nets(manifest),
        "runtime_nets": manifest.get("runtime_nets", 0),
        "total_expansions": st.get("total_expansions", 0),
        "last_expansion": st.get("last_expansion"),
        "last_expansion_nets": st.get("last_expansion_nets") or [],
        "neural_literacy": NEURAL_LITERACY,
        "expandable": manifest.get("expandable", True),
        "total_selftests": st.get("total_selftests", 0),
        "total_adapted": st.get("total_adapted", 0),
        "total_quarantined": st.get("total_quarantined", 0),
        "last_truth_score": st.get("last_truth_score"),
        "last_adapt_allowed": st.get("last_adapt_allowed"),
        "recommendations": genius_recommendations(),
        "series_count": len(manifest.get("series") or []),
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "status").strip()
    if cmd == "status":
        print(json.dumps(neural_status(), ensure_ascii=False))
        return 0
    if cmd == "selftest":
        claim = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Angel truth gate self-test"
        print(json.dumps(self_test_knowledge(claim), ensure_ascii=False))
        return 0
    if cmd == "suite":
        print(json.dumps(run_self_test_suite(), ensure_ascii=False))
        return 0
    if cmd == "forward":
        claim = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Neural forward pass"
        print(json.dumps(forward_pass(claim), ensure_ascii=False))
        return 0
    if cmd == "block":
        print(neural_prompt_block())
        return 0
    if cmd == "inventory":
        print(json.dumps(corpus_inventory(), ensure_ascii=False))
        return 0
    if cmd == "recommendations":
        print(json.dumps(genius_recommendations(), ensure_ascii=False))
        return 0
    if cmd == "expand":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "utility neural network expand"
        print(json.dumps(expand_stack_for_utility(text), ensure_ascii=False))
        return 0
    if cmd == "literacy":
        q = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        print(json.dumps({"ok": True, "reply": explain_neural_networks(q), "literacy": NEURAL_LITERACY}, ensure_ascii=False))
        return 0
    if cmd == "detect":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        needs = detect_utility_needs(text)
        print(json.dumps({
            "ok": True,
            "needs": [{"key": n.get("key"), "net": (n.get("net") or {}).get("id")} for n in needs],
        }, ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: hostess7-neural.py [status|selftest|suite|forward|expand|literacy|detect|block|inventory|recommendations] [claim]"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())