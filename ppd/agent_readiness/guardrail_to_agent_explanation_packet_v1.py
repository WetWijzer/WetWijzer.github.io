"""Fixture-first guardrail-to-agent explanation packet v1.

This module converts committed PP&D guardrail, gap-analysis, blocked-action,
and offline readiness-adapter fixture outputs into deterministic cited
explanation templates. It never calls an LLM, opens DevHub, reads private user
files, mutates live agent state, or performs an official PP&D action.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping


PACKET_TYPE = "ppd.guardrail_to_agent_explanation_packet.v1"
EXPLANATION_KINDS = (
    "missing_facts",
    "blocked_official_actions",
    "reversible_draft_limits",
    "stale_conflicting_evidence",
    "next_safe_read_only_actions",
)
REQUIRED_ATTESTATIONS = (
    "no_live_llm",
    "no_devhub",
    "no_private_data",
    "no_official_action",
)
SUPPORTED_PROCESS_IDS = frozenset({"ppd-single-pdf-plan-review-v1"})
SUPPORTED_GUARDRAIL_BUNDLE_IDS = frozenset({"guardrail-explanation-single-pdf-v1"})

_PRIVATE_KEYS = {
    "access_token",
    "account_number",
    "auth_state",
    "authenticated_fact",
    "authenticated_facts",
    "bank_account",
    "card_number",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "credit_card",
    "cvv",
    "email",
    "field_value",
    "file_path",
    "local_path",
    "password",
    "payment_details",
    "payment_method",
    "phone",
    "private_fact",
    "private_facts",
    "private_value",
    "private_values",
    "raw_value",
    "refresh_token",
    "routing_number",
    "secret",
    "session_state",
    "ssn",
    "token",
    "user_input",
    "value",
}
_RAW_KEYS = {
    "body",
    "browser_artifact",
    "browser_artifacts",
    "browser_trace",
    "document_artifact",
    "downloaded_document",
    "downloaded_documents",
    "dom_snapshot",
    "har",
    "html",
    "page_text",
    "raw_body",
    "raw_crawl_output",
    "raw_document",
    "raw_documents",
    "raw_dom",
    "raw_html",
    "raw_session",
    "raw_text",
    "screenshot",
    "session_artifact",
    "session_artifacts",
    "trace",
}
_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_source_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation_active",
    "guardrail_mutation_active",
    "prompt_mutation_active",
    "release_state_mutation_active",
    "source_mutation_active",
    "surface_registry_mutation_active",
}
_PRIVATE_CLASSIFICATIONS = {
    "account_private",
    "authenticated",
    "case_private",
    "devhub_authenticated",
    "devhub_authenticated_private",
    "private",
    "private_case",
    "private_case_fact",
    "private_fact",
    "user_private",
}
_PRIVATE_PATH_RE = re.compile(r"(file://|/home/|/users/|/var/folders/|/tmp/|\\users\\|[a-z]:\\)", re.IGNORECASE)
_AUTHENTICATED_URL_RE = re.compile(r"\b(devhub\.portlandoregon\.gov/.+/(account|dashboard|my|secure|session|signin|login)|auth|token|session)\b", re.IGNORECASE)
_PRIVATE_FACT_RE = re.compile(r"\b(private|authenticated|account-scoped|credential|cookie|session|payment detail|card number|applicant email|phone number)\b", re.IGNORECASE)
_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?\s+(approval|issuance|permit|legal|compliance|outcome)|"
    r"(approval|permit|issuance|legal outcome)\s+(is\s+)?(certain|guaranteed|assured)|"
    r"will\s+be\s+approved|permit\s+will\s+issue|cannot\s+be\s+denied|no\s+legal\s+risk|legally\s+sufficient)\b",
    re.IGNORECASE,
)
_FINAL_ACTION_RE = re.compile(
    r"\b(click|press|select|choose|complete|execute|perform|confirm|approve|authorize|go ahead and|proceed with)\s+"
    r"(the\s+)?(final\s+)?(submit|submission|payment|upload|schedule|scheduling|cancel|cancellation)\b|"
    r"\b(final\s+(submission|payment|upload|scheduling|cancellation)\s+(is|was|will be)\s+(done|complete|allowed|approved|scheduled|cancelled|canceled))\b",
    re.IGNORECASE,
)
_CONSEQUENTIAL_CLASSES = {
    "submission",
    "upload",
    "upload_to_official_record",
    "payment",
    "financial",
    "scheduling",
    "inspection_scheduling",
    "certification",
    "cancellation",
}


class GuardrailToAgentExplanationPacketError(ValueError):
    """Raised when fixtures cannot produce a safe explanation packet."""

    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid guardrail-to-agent explanation packet: " + "; ".join(self.problems))


def load_guardrail_to_agent_explanation_fixture(path: str | Path) -> dict[str, Any]:
    """Load a committed JSON fixture and build the v1 explanation packet."""

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise GuardrailToAgentExplanationPacketError(["fixture must be a JSON object"])
    return build_guardrail_to_agent_explanation_packet(
        guardrail_bundle=_required_mapping(raw, "guardrail_bundle"),
        user_gap_analysis=_required_mapping(raw, "user_gap_analysis"),
        blocked_action_fixtures=raw.get("blocked_action_fixtures"),
        agent_readiness_adapter_outputs=raw.get("agent_readiness_adapter_outputs"),
        source_evidence=raw.get("source_evidence"),
    )


def build_guardrail_to_agent_explanation_packet(
    *,
    guardrail_bundle: Mapping[str, Any],
    user_gap_analysis: Mapping[str, Any],
    blocked_action_fixtures: Any,
    agent_readiness_adapter_outputs: Any,
    source_evidence: Any,
) -> dict[str, Any]:
    """Build deterministic cited explanations from fixture-only inputs."""

    bundle = deepcopy(dict(guardrail_bundle))
    gap = deepcopy(dict(user_gap_analysis))
    blocked_actions = _sequence(blocked_action_fixtures, "blocked_action_fixtures")
    readiness_outputs = _sequence(agent_readiness_adapter_outputs, "agent_readiness_adapter_outputs")
    evidence = _evidence_by_id(source_evidence)

    problems = _input_problems(bundle, gap, blocked_actions, readiness_outputs, evidence)
    if problems:
        raise GuardrailToAgentExplanationPacketError(problems)

    cited_ids = sorted(_string_set(bundle.get("source_evidence_ids")))
    packet = {
        "packet_type": PACKET_TYPE,
        "fixture_first": True,
        "metadata_only": True,
        "case_id": gap["case_id"],
        "process_id": bundle["process_id"],
        "guardrail_bundle_id": bundle["guardrail_bundle_id"],
        "input_refs": {
            "guardrail_bundle_id": bundle["guardrail_bundle_id"],
            "user_gap_analysis_case_id": gap["case_id"],
            "blocked_action_fixture_ids": sorted(_text(item.get("fixture_id") or item.get("action_id")) for item in blocked_actions),
            "agent_readiness_output_ids": sorted(_text(item.get("response_id") or item.get("example_kind")) for item in readiness_outputs),
        },
        "attestations": {name: True for name in REQUIRED_ATTESTATIONS},
        "citation_index": [_citation(evidence[evidence_id]) for evidence_id in cited_ids],
        "explanation_order": list(EXPLANATION_KINDS),
        "explanation_templates": [
            _missing_facts_template(gap, cited_ids),
            _blocked_actions_template(bundle, gap, blocked_actions, cited_ids),
            _reversible_draft_template(bundle, gap, cited_ids),
            _stale_conflicting_template(gap, cited_ids),
            _next_safe_actions_template(gap, readiness_outputs, cited_ids),
        ],
    }

    errors = validate_guardrail_to_agent_explanation_packet(packet)
    if errors:
        raise GuardrailToAgentExplanationPacketError(errors)
    return packet


def validate_guardrail_to_agent_explanation_packet(packet: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a built explanation packet."""

    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be ppd.guardrail_to_agent_explanation_packet.v1")
    for key in ("fixture_first", "metadata_only"):
        if packet.get(key) is not True:
            errors.append(f"{key} must be true")
    errors.extend(_supported_id_problems(packet, "packet"))

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        errors.append("attestations must be an object")
    else:
        for name in REQUIRED_ATTESTATIONS:
            if attestations.get(name) is not True:
                errors.append(f"attestations.{name} must be true")

    citation_ids = set()
    citation_index = packet.get("citation_index")
    if not isinstance(citation_index, list) or not citation_index:
        errors.append("citation_index must be a non-empty list")
    else:
        for index, citation in enumerate(citation_index):
            if not isinstance(citation, Mapping):
                errors.append(f"citation_index[{index}] must be an object")
                continue
            evidence_id = _text(citation.get("evidence_id"))
            if not evidence_id:
                errors.append(f"citation_index[{index}].evidence_id is required")
            citation_ids.add(evidence_id)
            if not _text(citation.get("canonical_url")).startswith("https://www.portland.gov/ppd/"):
                errors.append(f"citation_index[{index}].canonical_url must be an official PP&D URL")
            if _text(citation.get("freshness_status")) != "current":
                errors.append(f"citation_index[{index}].freshness_status must be current")

    templates = packet.get("explanation_templates")
    if not isinstance(templates, list):
        errors.append("explanation_templates must be a list")
        templates = []
    if [item.get("kind") for item in templates if isinstance(item, Mapping)] != list(EXPLANATION_KINDS):
        errors.append("explanation_templates must appear in deterministic explanation_order")
    for index, template in enumerate(templates):
        if not isinstance(template, Mapping):
            errors.append(f"explanation_templates[{index}] must be an object")
            continue
        prefix = f"explanation_templates[{index}]"
        for key in ("template_id", "kind", "status", "agent_message"):
            if not _text(template.get(key)):
                errors.append(f"{prefix}.{key} is required")
        refs = _string_set(template.get("citation_ids"))
        if not refs:
            errors.append(f"{prefix}.citation_ids must be non-empty")
        elif citation_ids and not refs.issubset(citation_ids):
            errors.append(f"{prefix}.citation_ids must reference citation_index")
        if template.get("kind") == "blocked_official_actions":
            for action_index, action in enumerate(_mapping_items(template.get("actions"))):
                action_prefix = f"{prefix}.actions[{action_index}]"
                if action.get("status") != "blocked":
                    errors.append(f"{prefix}.actions must remain blocked")
                if action.get("requires_exact_confirmation") is not True:
                    errors.append(f"{prefix}.actions must require exact confirmation")
                if action.get("official_action_executed") is not False:
                    errors.append(f"{prefix}.actions must attest official_action_executed false")
                if not _text(action.get("reason")):
                    errors.append(f"{action_prefix}.reason is required for blocked-action rationale")
        if template.get("kind") == "reversible_draft_limits":
            for action in _mapping_items(template.get("actions")):
                if action.get("may_upload") is not False or action.get("may_submit") is not False:
                    errors.append(f"{prefix}.actions must forbid upload and submission")

    errors.extend(_unsafe_tree_problems(packet))
    return _dedupe(errors)


def _missing_facts_template(gap: Mapping[str, Any], citation_ids: list[str]) -> dict[str, Any]:
    missing_facts = sorted(_string_set(gap.get("missing_facts")))
    missing_documents = sorted(_string_set(gap.get("missing_documents")))
    return {
        "template_id": "explain:missing-facts:v1",
        "kind": "missing_facts",
        "status": "needs_user_input" if missing_facts or missing_documents else "no_missing_fixture_items",
        "agent_message": "Ask only for the listed missing facts and document metadata before drafting or previewing PP&D values.",
        "missing_facts": missing_facts,
        "missing_documents": missing_documents,
        "citation_ids": citation_ids,
    }


def _blocked_actions_template(bundle: Mapping[str, Any], gap: Mapping[str, Any], blocked_fixtures: list[Mapping[str, Any]], citation_ids: list[str]) -> dict[str, Any]:
    fixture_by_id = {_text(item.get("action_id")): item for item in blocked_fixtures}
    predicate_by_id = {_text(item.get("action_id")): item for item in _mapping_items(bundle.get("refused_action_predicates"))}
    actions = []
    for blocked in _mapping_items(gap.get("blocked_actions")):
        action_id = _text(blocked.get("action_id"))
        fixture = fixture_by_id.get(action_id, {})
        predicate = predicate_by_id.get(action_id, {})
        actions.append(
            {
                "action_id": action_id,
                "classification": _text(blocked.get("classification") or fixture.get("classification") or predicate.get("classification")),
                "status": "blocked",
                "reason": _text(blocked.get("reason") or fixture.get("reason") or predicate.get("refusal_reason")),
                "requires_exact_confirmation": True,
                "requires_user_attendance": True,
                "official_action_executed": False,
            }
        )
    return {
        "template_id": "explain:blocked-official-actions:v1",
        "kind": "blocked_official_actions",
        "status": "blocked",
        "agent_message": "Explain that consequential PP&D actions stay blocked unless the user is present and controls the exact confirmed action.",
        "actions": sorted(actions, key=lambda item: item["action_id"]),
        "citation_ids": citation_ids,
    }


def _reversible_draft_template(bundle: Mapping[str, Any], gap: Mapping[str, Any], citation_ids: list[str]) -> dict[str, Any]:
    safe_ids = {_text(item.get("action_id") or item.get("next_safe_action_id")) for item in _mapping_items(gap.get("next_safe_actions"))}
    actions = []
    for predicate in _mapping_items(bundle.get("reversible_action_predicates")):
        action_id = _text(predicate.get("action_id"))
        actions.append(
            {
                "action_id": action_id,
                "classification": "reversible_draft",
                "status": "next_safe_reversible_draft" if action_id in safe_ids else "not_currently_next_safe",
                "may_prepare_local_preview": action_id in safe_ids,
                "may_upload": False,
                "may_submit": False,
                "may_certify": False,
                "may_pay": False,
                "limits": "Local draft or checklist only; stop before consequential official actions.",
            }
        )
    return {
        "template_id": "explain:reversible-draft-limits:v1",
        "kind": "reversible_draft_limits",
        "status": "draft_limited",
        "agent_message": "Draft work is limited to reversible local previews and metadata checks.",
        "actions": sorted(actions, key=lambda item: item["action_id"]),
        "citation_ids": citation_ids,
    }


def _stale_conflicting_template(gap: Mapping[str, Any], citation_ids: list[str]) -> dict[str, Any]:
    stale = deepcopy(gap.get("stale_evidence") or [])
    conflicting = deepcopy(gap.get("conflicting_evidence") or [])
    return {
        "template_id": "explain:stale-conflicting-evidence:v1",
        "kind": "stale_conflicting_evidence",
        "status": "refresh_or_human_review_required" if stale or conflicting else "no_stale_or_conflicting_fixture_evidence",
        "agent_message": "If evidence is stale or conflicting, do not draft from it; surface the cited issue and recommend read-only review.",
        "stale_evidence": stale,
        "conflicting_evidence": conflicting,
        "citation_ids": citation_ids,
    }


def _next_safe_actions_template(gap: Mapping[str, Any], readiness_outputs: list[Mapping[str, Any]], citation_ids: list[str]) -> dict[str, Any]:
    safe_actions = []
    for action in _mapping_items(gap.get("next_safe_actions")):
        safe_actions.append(
            {
                "action_id": _text(action.get("action_id") or action.get("next_safe_action_id")),
                "classification": _text(action.get("classification") or "read_only"),
                "allowed_now": True,
                "official_action_executed": False,
            }
        )
    return {
        "template_id": "explain:next-safe-read-only-actions:v1",
        "kind": "next_safe_read_only_actions",
        "status": "read_only_or_reversible_only",
        "agent_message": "Recommend only cited read-only review or reversible local draft preparation as the next safe action.",
        "actions": sorted(safe_actions, key=lambda item: item["action_id"]),
        "readiness_adapter_refs": sorted(_text(item.get("response_id") or item.get("example_kind")) for item in readiness_outputs),
        "citation_ids": citation_ids,
    }


def _input_problems(bundle: Mapping[str, Any], gap: Mapping[str, Any], blocked_actions: list[Mapping[str, Any]], readiness_outputs: list[Mapping[str, Any]], evidence: Mapping[str, Mapping[str, Any]]) -> list[str]:
    problems: list[str] = []
    for key in ("guardrail_bundle_id", "process_id"):
        if not _text(bundle.get(key)):
            problems.append(f"guardrail_bundle.{key} is required")
    for key in ("case_id", "process_id", "guardrail_bundle_id"):
        if not _text(gap.get(key)):
            problems.append(f"user_gap_analysis.{key} is required")
    problems.extend(_supported_id_problems(bundle, "guardrail_bundle"))
    problems.extend(_supported_id_problems(gap, "user_gap_analysis"))
    if bundle.get("process_id") != gap.get("process_id"):
        problems.append("guardrail_bundle and user_gap_analysis process_id values must match")
    if bundle.get("guardrail_bundle_id") != gap.get("guardrail_bundle_id"):
        problems.append("guardrail_bundle and user_gap_analysis guardrail_bundle_id values must match")
    if _text(bundle.get("validation_status")) not in {"fixture_validated", "validated", "current"}:
        problems.append("guardrail_bundle.validation_status must be fixture_validated, validated, or current")

    source_ids = _string_set(bundle.get("source_evidence_ids"))
    if not source_ids:
        problems.append("guardrail_bundle.source_evidence_ids must be non-empty")
    missing_sources = sorted(source_ids.difference(evidence))
    if missing_sources:
        problems.append("source_evidence is missing cited ids: " + ", ".join(missing_sources))
    for evidence_id in source_ids.intersection(evidence):
        citation = _citation(evidence[evidence_id])
        if not citation["canonical_url"].startswith("https://www.portland.gov/ppd/"):
            problems.append(f"source_evidence[{evidence_id}] must use an official PP&D URL")
        if citation["freshness_status"] != "current":
            problems.append(f"source_evidence[{evidence_id}] must be current")

    if not isinstance(gap.get("missing_facts"), list):
        problems.append("user_gap_analysis.missing_facts must be a list")
    if not isinstance(gap.get("missing_documents"), list):
        problems.append("user_gap_analysis.missing_documents must be a list")
    if not _mapping_items(gap.get("blocked_actions")):
        problems.append("user_gap_analysis.blocked_actions must include blocked official actions")
    if not _mapping_items(gap.get("next_safe_actions")):
        problems.append("user_gap_analysis.next_safe_actions must include safe read-only or reversible actions")
    if not blocked_actions:
        problems.append("blocked_action_fixtures must be non-empty")
    if not readiness_outputs:
        problems.append("agent_readiness_adapter_outputs must be non-empty")

    blocked_ids = {_text(item.get("action_id")) for item in blocked_actions}
    for item in _mapping_items(gap.get("blocked_actions")):
        action_id = _text(item.get("action_id"))
        if action_id not in blocked_ids:
            problems.append(f"blocked_action_fixtures missing {action_id}")
        if _text(item.get("classification")) not in _CONSEQUENTIAL_CLASSES:
            problems.append(f"blocked action {action_id} must be consequential")
        if not _text(item.get("reason")):
            problems.append(f"blocked action {action_id} requires a rationale")
    for item in blocked_actions:
        if not _text(item.get("reason") or item.get("refusal_reason")):
            problems.append(f"blocked_action_fixtures[{_text(item.get('action_id'))}] requires a rationale")
    for item in _mapping_items(bundle.get("refused_action_predicates")):
        if not _text(item.get("refusal_reason") or item.get("reason")):
            problems.append(f"refused_action_predicates[{_text(item.get('action_id'))}] requires a rationale")
    for item in _mapping_items(gap.get("next_safe_actions")):
        classification = _text(item.get("classification"))
        if classification in _CONSEQUENTIAL_CLASSES:
            problems.append("next_safe_actions cannot include consequential official actions")

    problems.extend(_unsafe_tree_problems(bundle, "guardrail_bundle"))
    problems.extend(_unsafe_tree_problems(gap, "user_gap_analysis"))
    problems.extend(_unsafe_tree_problems(blocked_actions, "blocked_action_fixtures"))
    problems.extend(_unsafe_tree_problems(readiness_outputs, "agent_readiness_adapter_outputs"))
    return _dedupe(problems)


def _citation(record: Mapping[str, Any]) -> dict[str, str]:
    return {
        "evidence_id": _text(record.get("evidence_id")),
        "title": _text(record.get("title")),
        "canonical_url": _text(record.get("canonical_url")),
        "source_type": _text(record.get("source_type")),
        "last_verified_at": _text(record.get("last_verified_at")),
        "freshness_status": _text(record.get("freshness_status")),
    }


def _evidence_by_id(value: Any) -> dict[str, Mapping[str, Any]]:
    rows = _sequence(value, "source_evidence")
    indexed = {_text(row.get("evidence_id")): row for row in rows if _text(row.get("evidence_id"))}
    if not indexed:
        raise GuardrailToAgentExplanationPacketError(["source_evidence must include at least one evidence_id"])
    return indexed


def _required_mapping(raw: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = raw.get(key)
    if not isinstance(value, Mapping):
        raise GuardrailToAgentExplanationPacketError([f"{key} must be an object"])
    return value


def _sequence(value: Any, name: str) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        raise GuardrailToAgentExplanationPacketError([f"{name} must be a list"])
    result = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise GuardrailToAgentExplanationPacketError([f"{name}[{index}] must be an object"])
        result.append(item)
    return result


def _mapping_items(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {_text(item) for item in value if _text(item)}


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _supported_id_problems(value: Mapping[str, Any], path: str) -> list[str]:
    problems: list[str] = []
    process_id = _text(value.get("process_id"))
    guardrail_bundle_id = _text(value.get("guardrail_bundle_id"))
    if process_id and process_id not in SUPPORTED_PROCESS_IDS:
        problems.append(f"{path}.process_id is unsupported: {process_id}")
    if guardrail_bundle_id and guardrail_bundle_id not in SUPPORTED_GUARDRAIL_BUNDLE_IDS:
        problems.append(f"{path}.guardrail_bundle_id is unsupported: {guardrail_bundle_id}")
    return problems


def _unsafe_tree_problems(value: Any, path: str = "packet") -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = _normalize_key(key_text)
            child_path = f"{path}.{key_text}"
            if normalized_key in _PRIVATE_KEYS:
                problems.append(f"{child_path} is a private value field")
            if normalized_key in _RAW_KEYS:
                problems.append(f"{child_path} is a raw document, session, or browser artifact field")
            if normalized_key in _MUTATION_KEYS and _truthy(child):
                problems.append(f"{child_path} must not set active prompt, guardrail, source, surface-registry, release-state, or agent-state mutation flags")
            if normalized_key in {"privacy_classification", "data_classification", "source_type", "fact_scope", "evidence_scope"} and _text(child).lower() in _PRIVATE_CLASSIFICATIONS:
                problems.append(f"{child_path} must not include private or authenticated facts")
            problems.extend(_unsafe_tree_problems(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            problems.extend(_unsafe_tree_problems(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        if _PRIVATE_PATH_RE.search(value):
            problems.append(f"{path} contains a private local path")
        if _AUTHENTICATED_URL_RE.search(value):
            problems.append(f"{path} contains a private or authenticated artifact reference")
        if _GUARANTEE_RE.search(value):
            problems.append(f"{path} must not guarantee legal or permitting outcomes")
        if _FINAL_ACTION_RE.search(value):
            problems.append(f"{path} must not include final submission, payment, upload, scheduling, or cancellation instructions")
        if path.endswith(".known_facts") and _PRIVATE_FACT_RE.search(value):
            problems.append(f"{path} must not include private or authenticated facts")
    return problems


def _normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _truthy(value: Any) -> bool:
    return value not in (False, None, "", [], {})


def _dedupe(items: Iterable[str]) -> list[str]:
    return sorted(dict.fromkeys(item for item in items if item))
