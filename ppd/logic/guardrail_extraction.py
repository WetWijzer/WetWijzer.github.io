"""Formal guardrail extraction for PP&D requirement batches.

The extractor is intentionally deterministic. It accepts processor-backed
requirement batches represented as dictionaries and emits plain dictionaries so
callers can persist or compare results without importing internal classes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Iterable, Mapping


OBLIGATION_RE = re.compile(
    r"\b(shall|must|required|requires|may not|prohibited|is unlawful|no person)\b",
    re.IGNORECASE,
)
PREREQUISITE_RE = re.compile(r"\b(if|when|unless|before|after|provided that|where)\b", re.IGNORECASE)
EXACT_CONFIRMATION_RE = re.compile(
    r"\b(submit|certify|attest|pay|payment|file|appeal|cancel|withdraw|upload|sign|schedule inspection)\b",
    re.IGNORECASE,
)
REVERSIBLE_RE = re.compile(
    r"\b(view|read|draft|prepare|calculate|classify|estimate|compare|download blank|generate draft)\b",
    re.IGNORECASE,
)
PLACEHOLDER_RE = re.compile(r"\b(TBD|unknown|not provided|missing|unspecified|\?\?+)\b", re.IGNORECASE)
OFFICIAL_ACTION_RE = re.compile(
    r"\b(submit|certify|attest|pay|payment|file|appeal|cancel|withdraw|upload|sign|create account|login|mfa|captcha)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class LogicPredicate:
    id: str
    requirement_id: str
    text: str
    source: str


@dataclass(frozen=True)
class MissingFactQuestion:
    id: str
    requirement_id: str
    question: str
    source: str


@dataclass(frozen=True)
class StopGate:
    id: str
    requirement_id: str
    action: str
    reason: str
    source: str


def extract_guardrails(batch: Mapping[str, Any]) -> dict[str, Any]:
    """Extract formal guardrails from a processor-backed requirement batch."""

    obligations: list[LogicPredicate] = []
    prerequisites: list[LogicPredicate] = []
    missing_fact_questions: list[MissingFactQuestion] = []
    reversible_action_predicates: list[LogicPredicate] = []
    exact_confirmation_predicates: list[LogicPredicate] = []
    refused_official_action_stop_gates: list[StopGate] = []

    for index, requirement in enumerate(_iter_requirements(batch), start=1):
        req_id = str(requirement.get("id") or requirement.get("requirement_id") or f"requirement-{index}")
        text = _collapse_ws(str(requirement.get("text") or requirement.get("requirement") or ""))
        source = str(requirement.get("source") or batch.get("source") or "processor_batch")
        if not text:
            continue

        prefix = _stable_prefix(req_id)
        if OBLIGATION_RE.search(text):
            obligations.append(LogicPredicate(f"{prefix}:obligation", req_id, text, source))
        if PREREQUISITE_RE.search(text):
            prerequisites.append(LogicPredicate(f"{prefix}:prerequisite", req_id, _extract_prerequisite(text), source))
        if REVERSIBLE_RE.search(text) and not OFFICIAL_ACTION_RE.search(text):
            reversible_action_predicates.append(LogicPredicate(f"{prefix}:reversible", req_id, text, source))
        if EXACT_CONFIRMATION_RE.search(text):
            exact_confirmation_predicates.append(LogicPredicate(f"{prefix}:exact_confirmation", req_id, text, source))
        if OFFICIAL_ACTION_RE.search(text):
            refused_official_action_stop_gates.append(
                StopGate(
                    id=f"{prefix}:stop_gate",
                    requirement_id=req_id,
                    action=_official_action_label(text),
                    reason="Official PP&D actions require explicit human control and exact confirmation.",
                    source=source,
                )
            )

        for fact in _missing_facts(requirement, text):
            missing_fact_questions.append(
                MissingFactQuestion(
                    id=f"{prefix}:missing_fact:{len(missing_fact_questions) + 1}",
                    requirement_id=req_id,
                    question=f"What is the value for {fact}?",
                    source=source,
                )
            )

    return {
        "batch_id": str(batch.get("batch_id") or batch.get("id") or "unknown_batch"),
        "obligations": [asdict(item) for item in obligations],
        "prerequisites": [asdict(item) for item in prerequisites],
        "missing_fact_questions": [asdict(item) for item in missing_fact_questions],
        "reversible_action_predicates": [asdict(item) for item in reversible_action_predicates],
        "exact_confirmation_predicates": [asdict(item) for item in exact_confirmation_predicates],
        "refused_official_action_stop_gates": [asdict(item) for item in refused_official_action_stop_gates],
    }


def _iter_requirements(batch: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
    records = batch.get("requirements") or batch.get("items") or batch.get("records") or []
    if isinstance(records, Mapping):
        records = records.values()
    for record in records:
        if isinstance(record, Mapping):
            yield record


def _missing_facts(requirement: Mapping[str, Any], text: str) -> list[str]:
    facts: list[str] = []
    raw = requirement.get("missing_facts") or requirement.get("facts_needed") or []
    if isinstance(raw, str):
        raw = [raw]
    if isinstance(raw, Iterable):
        for fact in raw:
            if isinstance(fact, str) and fact.strip():
                facts.append(_collapse_ws(fact))
    if PLACEHOLDER_RE.search(text):
        facts.append("the unspecified requirement fact")
    return _dedupe(facts)


def _extract_prerequisite(text: str) -> str:
    match = PREREQUISITE_RE.search(text)
    if not match:
        return text
    return text[match.start() :]


def _official_action_label(text: str) -> str:
    match = OFFICIAL_ACTION_RE.search(text)
    return match.group(0).lower() if match else "official action"


def _stable_prefix(requirement_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.:-]+", "-", requirement_id).strip("-") or "requirement"


def _collapse_ws(value: str) -> str:
    return " ".join(value.split())


def _dedupe(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = value.casefold()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result
