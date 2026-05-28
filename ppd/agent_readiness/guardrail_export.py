"""Fixture-first guardrail export readiness packets for PP&D agents.

This module converts one already-compiled GuardrailBundle and one synthetic
UserGapAnalysis into an agent-facing predicate packet. It is intentionally
side-effect free: callers pass fixture-shaped mappings, and no network, browser,
DevHub, or crawl services are invoked.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping


class GuardrailExportReadinessError(ValueError):
    """Raised when fixture guardrails cannot be exported safely for an agent."""

    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid guardrail export readiness packet: " + "; ".join(self.problems))


_PRIVATE_KEYS = {
    "access_token",
    "auth_state",
    "card_number",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "cvv",
    "email",
    "field_value",
    "local_path",
    "password",
    "payment_details",
    "phone",
    "private_value",
    "raw_value",
    "refresh_token",
    "secret",
    "session_cookie",
    "session_state",
    "ssn",
    "token",
    "user_input",
    "value",
}

_RAW_OR_LIVE_KEYS = {
    "body",
    "downloaded_document",
    "har",
    "html",
    "page_text",
    "raw_body",
    "raw_crawl_output",
    "raw_html",
    "raw_text",
    "screenshot",
    "trace",
}

_CONSEQUENTIAL_CLASSES = {
    "cancellation",
    "certification",
    "consequential",
    "consequential_official",
    "financial",
    "inspection_scheduling",
    "official",
    "payment",
    "scheduling",
    "submission",
    "upload",
    "upload_to_official_record",
}

_REQUIRED_REFUSAL_CLASSES = {
    "certification",
    "financial",
    "inspection_scheduling",
    "payment",
    "scheduling",
    "submission",
    "upload",
    "upload_to_official_record",
}

_REVERSIBLE_CLASSES = {"reversible", "reversible_draft", "safe_read_only"}
_STALE_VALUES = {"expired", "invalidated", "needs_refresh", "outdated", "stale"}
_LOCAL_PATH_PATTERN = re.compile(r"(^|\s)(/home/|/users/|/var/folders/|[a-z]:\\\\users\\\\)", re.IGNORECASE)
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
_ACTION_STOPWORDS = {"a", "an", "and", "application", "devhub", "exact", "i", "official", "or", "ppd", "record", "request", "that", "the", "this", "to"}


def load_guardrail_export_fixture(path: str | Path) -> dict[str, Any]:
    """Load a committed fixture and assemble its export readiness packet."""

    fixture_path = Path(path)
    raw = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise GuardrailExportReadinessError(["fixture must be a JSON object"])
    guardrail_bundle = _required_mapping(raw, "guardrail_bundle")
    user_gap_analysis = _required_mapping(raw, "user_gap_analysis")
    return build_guardrail_export_readiness_packet(guardrail_bundle, user_gap_analysis)


def build_guardrail_export_readiness_packet(
    guardrail_bundle: Mapping[str, Any],
    user_gap_analysis: Mapping[str, Any],
) -> dict[str, Any]:
    """Build an agent-facing readiness packet from fixture guardrails and gaps."""

    bundle = deepcopy(dict(guardrail_bundle))
    gap = deepcopy(dict(user_gap_analysis))
    problems = _input_problems(bundle, gap)
    if problems:
        raise GuardrailExportReadinessError(problems)

    missing_information = _missing_information_predicates(bundle, gap)
    reversible_actions = _reversible_action_predicates(bundle, gap)
    refused_actions = _refused_action_predicates(bundle, gap)
    exact_confirmations = _exact_confirmation_predicates(bundle, gap)

    packet = {
        "packet_type": "ppd.guardrail_export_readiness.v1",
        "fixture_first": True,
        "live_services_called": False,
        "metadata_only": True,
        "case_id": gap["case_id"],
        "process_id": bundle["process_id"],
        "guardrail_bundle_id": bundle["guardrail_bundle_id"],
        "source_evidence_ids": sorted(_string_set(bundle.get("source_evidence_ids"))),
        "predicate_counts": {
            "missing_information": len(missing_information),
            "reversible_actions": len(reversible_actions),
            "refused_actions": len(refused_actions),
            "exact_confirmations": len(exact_confirmations),
        },
        "missing_information_predicates": missing_information,
        "reversible_action_predicates": reversible_actions,
        "refused_action_predicates": refused_actions,
        "exact_confirmation_predicates": exact_confirmations,
    }

    packet_problems = validate_guardrail_export_readiness_packet(packet)
    if packet_problems:
        raise GuardrailExportReadinessError(packet_problems)
    return packet


def validate_guardrail_export_readiness_packet(packet: Mapping[str, Any]) -> list[str]:
    """Validate an assembled guardrail export readiness packet fail-closed."""

    problems: list[str] = []
    if packet.get("packet_type") != "ppd.guardrail_export_readiness.v1":
        problems.append("packet_type must be ppd.guardrail_export_readiness.v1")
    if packet.get("fixture_first") is not True:
        problems.append("packet must be fixture_first")
    if packet.get("live_services_called") is not False:
        problems.append("packet must confirm live_services_called is false")
    if packet.get("metadata_only") is not True:
        problems.append("packet must be metadata_only")

    for key in ("case_id", "process_id", "guardrail_bundle_id"):
        if not _non_empty_text(packet.get(key)):
            problems.append(f"packet is missing {key}")

    evidence_ids = _string_set(packet.get("source_evidence_ids"))
    if not evidence_ids:
        problems.append("packet must include source_evidence_ids")

    predicate_sections = {
        "missing_information_predicates": packet.get("missing_information_predicates"),
        "reversible_action_predicates": packet.get("reversible_action_predicates"),
        "refused_action_predicates": packet.get("refused_action_predicates"),
        "exact_confirmation_predicates": packet.get("exact_confirmation_predicates"),
    }
    for section_name, section_value in predicate_sections.items():
        if not isinstance(section_value, list) or not section_value:
            problems.append(f"{section_name} must be a non-empty list")
            continue
        for index, predicate in enumerate(section_value):
            if not isinstance(predicate, Mapping):
                problems.append(f"{section_name}[{index}] must be an object")
                continue
            if not _non_empty_text(predicate.get("predicate_id")):
                problems.append(f"{section_name}[{index}] is missing predicate_id")
            if not _non_empty_text(predicate.get("predicate")):
                problems.append(f"{section_name}[{index}] is missing predicate")
            refs = _string_set(predicate.get("source_evidence_ids"))
            if not refs:
                problems.append(f"{section_name}[{index}] must cite source_evidence_ids")
            elif not refs.issubset(evidence_ids):
                problems.append(f"{section_name}[{index}] cites unknown source_evidence_ids")

    refused_action_ids = {
        str(item.get("action_id"))
        for item in _mapping_items(packet.get("refused_action_predicates"))
        if item.get("action_id")
    }
    reversible_action_ids = {
        str(item.get("action_id"))
        for item in _mapping_items(packet.get("reversible_action_predicates"))
        if item.get("action_id")
    }
    exact_confirmation_action_ids = {
        str(item.get("action_id"))
        for item in _mapping_items(packet.get("exact_confirmation_predicates"))
        if item.get("action_id")
    }
    overlap = refused_action_ids.intersection(reversible_action_ids)
    if overlap:
        problems.append("actions cannot be both refused and reversible: " + ", ".join(sorted(overlap)))

    for predicate in _mapping_items(packet.get("refused_action_predicates")):
        action_id = str(predicate.get("action_id") or "")
        classification = str(predicate.get("classification", "")).lower()
        if classification in _CONSEQUENTIAL_CLASSES or _looks_consequential(predicate):
            if predicate.get("requires_manual_handoff") is not True:
                problems.append(f"refused action {action_id} must require manual handoff")
            if predicate.get("requires_exact_confirmation") is not True:
                problems.append(f"refused action {action_id} must require exact confirmation")
            if predicate.get("default_outcome") != "refuse":
                problems.append(f"refused action {action_id} must default to refuse")
        if classification in _REQUIRED_REFUSAL_CLASSES and action_id not in exact_confirmation_action_ids:
            problems.append(f"refused action {action_id} must have a matching exact confirmation predicate")

    for predicate in _mapping_items(packet.get("exact_confirmation_predicates")):
        predicate_id = predicate.get("predicate_id")
        if predicate.get("requires_exact_confirmation") is not True:
            problems.append(f"exact confirmation {predicate_id} must require exact confirmation")
        if not _non_empty_text(predicate.get("confirmation_text")):
            problems.append(f"exact confirmation {predicate_id} is missing confirmation_text")
        elif not _confirmation_text_is_action_specific(predicate):
            problems.append(f"exact confirmation {predicate_id} must include action-specific confirmation language")

    problems.extend(_stale_value_problems(packet))
    problems.extend(_unsafe_key_problems(packet))
    return problems


def _input_problems(bundle: Mapping[str, Any], gap: Mapping[str, Any]) -> list[str]:
    problems: list[str] = []
    for key in ("guardrail_bundle_id", "process_id"):
        if not _non_empty_text(bundle.get(key)):
            problems.append(f"guardrail_bundle is missing {key}")
    for key in ("case_id", "process_id", "guardrail_bundle_id"):
        if not _non_empty_text(gap.get(key)):
            problems.append(f"user_gap_analysis is missing {key}")
    if bundle.get("process_id") != gap.get("process_id"):
        problems.append("guardrail_bundle and user_gap_analysis process_id values must match")
    if bundle.get("guardrail_bundle_id") != gap.get("guardrail_bundle_id"):
        problems.append("guardrail_bundle and user_gap_analysis guardrail_bundle_id values must match")

    evidence_ids = _string_set(bundle.get("source_evidence_ids"))
    if not evidence_ids:
        problems.append("guardrail_bundle must include source_evidence_ids")
    for key in (
        "deterministic_predicates",
        "reversible_action_predicates",
        "refused_action_predicates",
        "exact_confirmation_predicates",
    ):
        if not isinstance(bundle.get(key), list) or not bundle.get(key):
            problems.append(f"guardrail_bundle.{key} must be a non-empty list")

    if not isinstance(gap.get("missing_facts"), list):
        problems.append("user_gap_analysis.missing_facts must be a list")
    if not isinstance(gap.get("missing_documents"), list):
        problems.append("user_gap_analysis.missing_documents must be a list")
    if not isinstance(gap.get("blocked_actions"), list) or not gap.get("blocked_actions"):
        problems.append("user_gap_analysis.blocked_actions must be a non-empty list")
    if not isinstance(gap.get("next_safe_actions"), list) or not gap.get("next_safe_actions"):
        problems.append("user_gap_analysis.next_safe_actions must be a non-empty list")

    problems.extend(_bundle_citation_problems(bundle, evidence_ids))
    problems.extend(_blocked_action_coverage_problems(bundle, gap))
    problems.extend(_stale_value_problems(bundle, "guardrail_bundle"))
    problems.extend(_stale_value_problems(gap, "user_gap_analysis"))
    problems.extend(_unsafe_key_problems(bundle, "guardrail_bundle"))
    problems.extend(_unsafe_key_problems(gap, "user_gap_analysis"))
    return problems


def _missing_information_predicates(bundle: Mapping[str, Any], gap: Mapping[str, Any]) -> list[dict[str, Any]]:
    evidence_ids = sorted(_string_set(bundle.get("source_evidence_ids")))
    predicates: list[dict[str, Any]] = []
    for fact_id in sorted(_string_set(gap.get("missing_facts"))):
        predicates.append(
            {
                "predicate_id": f"missing-fact:{fact_id}",
                "predicate": "requires_missing_fact_answer",
                "gap_type": "missing_fact",
                "fact_id": fact_id,
                "agent_instruction": f"Ask the user for {fact_id} before drafting or advancing the process.",
                "source_evidence_ids": evidence_ids,
            }
        )
    for document_id in sorted(_string_set(gap.get("missing_documents"))):
        predicates.append(
            {
                "predicate_id": f"missing-document:{document_id}",
                "predicate": "requires_missing_document_match",
                "gap_type": "missing_document",
                "document_id": document_id,
                "agent_instruction": f"Ask the user to identify or provide metadata for {document_id}; do not upload it.",
                "source_evidence_ids": evidence_ids,
            }
        )
    for predicate in _mapping_items(bundle.get("deterministic_predicates")):
        if str(predicate.get("predicate", "")).startswith("requires_missing"):
            copied = _predicate_copy(predicate, evidence_ids)
            copied.setdefault("predicate_id", f"deterministic-missing:{len(predicates) + 1}")
            predicates.append(copied)
    return _dedupe_by_id(predicates)


def _reversible_action_predicates(bundle: Mapping[str, Any], gap: Mapping[str, Any]) -> list[dict[str, Any]]:
    missing_fact_ids = _string_set(gap.get("missing_facts"))
    missing_document_ids = _string_set(gap.get("missing_documents"))
    next_safe_ids = {
        str(item.get("action_id") or item.get("next_safe_action_id"))
        for item in _mapping_items(gap.get("next_safe_actions"))
        if item.get("action_id") or item.get("next_safe_action_id")
    }
    evidence_ids = sorted(_string_set(bundle.get("source_evidence_ids")))
    predicates: list[dict[str, Any]] = []
    for predicate in _mapping_items(bundle.get("reversible_action_predicates")):
        action_id = str(predicate.get("action_id") or predicate.get("action") or predicate.get("predicate_id"))
        classification = str(predicate.get("classification", "reversible_draft")).lower()
        if classification not in _REVERSIBLE_CLASSES:
            continue
        depends_on_facts = _string_set(predicate.get("depends_on_missing_facts"))
        depends_on_documents = _string_set(predicate.get("depends_on_missing_documents"))
        blocked_by = sorted(depends_on_facts.intersection(missing_fact_ids) | depends_on_documents.intersection(missing_document_ids))
        predicates.append(
            {
                "predicate_id": str(predicate.get("predicate_id") or f"reversible-action:{action_id}"),
                "predicate": "may_prepare_reversible_draft_only",
                "action_id": action_id,
                "action": str(predicate.get("action", action_id)),
                "classification": classification,
                "available_as_next_safe_action": action_id in next_safe_ids,
                "blocked_by_missing_information": blocked_by,
                "agent_instruction": str(
                    predicate.get(
                        "agent_instruction",
                        "Prepare only local or draft metadata; stop before official submission, upload, certification, scheduling, or payment.",
                    )
                ),
                "source_evidence_ids": sorted(_string_set(predicate.get("source_evidence_ids")) or set(evidence_ids)),
            }
        )
    return _dedupe_by_id(predicates)


def _refused_action_predicates(bundle: Mapping[str, Any], gap: Mapping[str, Any]) -> list[dict[str, Any]]:
    blocked_by_id = {
        str(item.get("action_id") or item.get("blocked_action_id")): item
        for item in _mapping_items(gap.get("blocked_actions"))
        if item.get("action_id") or item.get("blocked_action_id")
    }
    evidence_ids = sorted(_string_set(bundle.get("source_evidence_ids")))
    predicates: list[dict[str, Any]] = []
    for predicate in _mapping_items(bundle.get("refused_action_predicates")):
        action_id = str(predicate.get("action_id") or predicate.get("action") or predicate.get("predicate_id"))
        blocked = blocked_by_id.get(action_id, {})
        classification = str(predicate.get("classification") or blocked.get("classification") or "consequential_official").lower()
        predicates.append(
            {
                "predicate_id": str(predicate.get("predicate_id") or f"refused-action:{action_id}"),
                "predicate": "refuse_action_without_attended_exact_confirmation",
                "action_id": action_id,
                "action": str(predicate.get("action", action_id)),
                "classification": classification,
                "default_outcome": "refuse",
                "requires_manual_handoff": True,
                "requires_exact_confirmation": True,
                "refusal_reason": str(
                    blocked.get("reason")
                    or predicate.get("refusal_reason")
                    or "Official PP&D action requires attended user control and exact confirmation."
                ),
                "source_evidence_ids": sorted(_string_set(predicate.get("source_evidence_ids")) or set(evidence_ids)),
            }
        )
    return _dedupe_by_id(predicates)


def _exact_confirmation_predicates(bundle: Mapping[str, Any], gap: Mapping[str, Any]) -> list[dict[str, Any]]:
    required_confirmations = {
        str(item.get("confirmation_id") or item.get("action_id") or item)
        for item in gap.get("required_confirmations", [])
        if isinstance(item, (str, Mapping))
    }
    evidence_ids = sorted(_string_set(bundle.get("source_evidence_ids")))
    predicates: list[dict[str, Any]] = []
    for predicate in _mapping_items(bundle.get("exact_confirmation_predicates")):
        action_id = str(predicate.get("action_id") or predicate.get("action") or predicate.get("predicate_id"))
        confirmation_id = str(predicate.get("confirmation_id") or action_id)
        predicates.append(
            {
                "predicate_id": str(predicate.get("predicate_id") or f"exact-confirmation:{confirmation_id}"),
                "predicate": "requires_exact_user_confirmation_text",
                "confirmation_id": confirmation_id,
                "action_id": action_id,
                "action": str(predicate.get("action", action_id)),
                "requires_exact_confirmation": True,
                "required_by_gap_analysis": confirmation_id in required_confirmations or action_id in required_confirmations,
                "confirmation_text": str(
                    predicate.get("confirmation_text")
                    or predicate.get("required_text")
                    or f"I confirm the exact PP&D action: {action_id}"
                ),
                "source_evidence_ids": sorted(_string_set(predicate.get("source_evidence_ids")) or set(evidence_ids)),
            }
        )
    return _dedupe_by_id(predicates)


def _bundle_citation_problems(bundle: Mapping[str, Any], evidence_ids: set[str]) -> list[str]:
    problems: list[str] = []
    for section_name in (
        "deterministic_predicates",
        "reversible_action_predicates",
        "refused_action_predicates",
        "exact_confirmation_predicates",
    ):
        for index, predicate in enumerate(_mapping_items(bundle.get(section_name))):
            refs = _string_set(predicate.get("source_evidence_ids"))
            predicate_id = predicate.get("predicate_id") or f"{section_name}[{index}]"
            if not refs:
                problems.append(f"guardrail_bundle.{section_name}.{predicate_id} must cite source_evidence_ids")
            elif not refs.issubset(evidence_ids):
                problems.append(f"guardrail_bundle.{section_name}.{predicate_id} cites unknown source_evidence_ids")
    return problems


def _blocked_action_coverage_problems(bundle: Mapping[str, Any], gap: Mapping[str, Any]) -> list[str]:
    refused_action_ids = {
        str(item.get("action_id") or item.get("blocked_action_id"))
        for item in _mapping_items(bundle.get("refused_action_predicates"))
        if item.get("action_id") or item.get("blocked_action_id")
    }
    exact_action_ids = {
        str(item.get("action_id") or item.get("confirmation_id"))
        for item in _mapping_items(bundle.get("exact_confirmation_predicates"))
        if item.get("action_id") or item.get("confirmation_id")
    }
    problems: list[str] = []
    for blocked in _mapping_items(gap.get("blocked_actions")):
        action_id = str(blocked.get("action_id") or blocked.get("blocked_action_id") or "")
        classification = str(blocked.get("classification") or "").lower()
        if not action_id:
            problems.append("user_gap_analysis.blocked_actions entries must include action_id")
            continue
        if classification in _REQUIRED_REFUSAL_CLASSES or _looks_consequential(blocked):
            if action_id not in refused_action_ids:
                problems.append(f"blocked consequential action {action_id} must have a refused_action_predicate")
            if action_id not in exact_action_ids:
                problems.append(f"blocked consequential action {action_id} must have an exact_confirmation_predicate")
    return problems


def _predicate_copy(predicate: Mapping[str, Any], fallback_evidence_ids: list[str]) -> dict[str, Any]:
    copied = {str(key): deepcopy(value) for key, value in predicate.items() if str(key) not in _PRIVATE_KEYS}
    copied["source_evidence_ids"] = sorted(_string_set(copied.get("source_evidence_ids")) or set(fallback_evidence_ids))
    return copied


def _required_mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    nested = value.get(key)
    if not isinstance(nested, Mapping):
        raise GuardrailExportReadinessError([f"fixture is missing {key}"])
    return nested


def _mapping_items(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item.strip() for item in value if isinstance(item, str) and item.strip()}


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _dedupe_by_id(predicates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for predicate in predicates:
        predicate_id = str(predicate.get("predicate_id", ""))
        if predicate_id:
            deduped[predicate_id] = predicate
    return [deduped[key] for key in sorted(deduped)]


def _looks_consequential(value: Mapping[str, Any]) -> bool:
    text = " ".join(str(value.get(key, "")) for key in ("action_id", "action", "classification", "reason", "refusal_reason")).lower()
    consequential_terms = (
        "cancel",
        "certif",
        "checkout",
        "fee",
        "inspection",
        "pay",
        "payment",
        "schedule",
        "submit",
        "upload",
    )
    return any(term in text for term in consequential_terms)


def _confirmation_text_is_action_specific(predicate: Mapping[str, Any]) -> bool:
    confirmation_text = str(predicate.get("confirmation_text") or "").lower()
    action_text = f"{predicate.get('action_id', '')} {predicate.get('action', '')}".lower()
    tokens = [token for token in _TOKEN_PATTERN.findall(action_text) if token not in _ACTION_STOPWORDS and len(token) > 2]
    if not tokens:
        return False
    matching_tokens = {token for token in tokens if token in confirmation_text}
    required_matches = 1 if len(set(tokens)) == 1 else 2
    return len(matching_tokens) >= required_matches


def _stale_value_problems(value: Any, path: str = "packet") -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key).lower()
            nested_path = f"{path}.{key_text}"
            if key_text in {"stale_evidence", "stale_sources"} and isinstance(nested, list) and nested:
                problems.append(f"stale evidence is not allowed in export readiness packets: {nested_path}")
            if key_text in {"freshness_status", "refresh_status", "validation_status"} and str(nested).lower() in _STALE_VALUES:
                problems.append(f"stale bundle or evidence status is not allowed: {nested_path}")
            problems.extend(_stale_value_problems(nested, nested_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            problems.extend(_stale_value_problems(nested, f"{path}[{index}]"))
    return problems


def _unsafe_key_problems(value: Any, path: str = "packet") -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key).lower()
            nested_path = f"{path}.{key_text}"
            if key_text in _PRIVATE_KEYS:
                problems.append(f"private value field is not allowed: {nested_path}")
            if key_text in _RAW_OR_LIVE_KEYS:
                problems.append(f"raw or live artifact field is not allowed: {nested_path}")
            problems.extend(_unsafe_key_problems(nested, nested_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            problems.extend(_unsafe_key_problems(nested, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        if (
            "storage_state" in lowered
            or "set-cookie" in lowered
            or "file://" in lowered
            or ".auth/" in lowered
            or "trace.zip" in lowered
            or _LOCAL_PATH_PATTERN.search(value)
        ):
            problems.append(f"private or local artifact reference is not allowed: {path}")
    return problems
