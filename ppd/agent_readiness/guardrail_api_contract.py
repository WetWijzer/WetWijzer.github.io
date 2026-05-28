"""Fixture-first PP&D guardrail API contract packets.

This module exposes one compiled GuardrailBundle and one UserGapAnalysis as a
small deterministic response packet for agents. It is intentionally side-effect
free: callers pass committed fixture data, and the module never calls DevHub,
browsers, crawlers, or network services.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping


RESPONSE_TYPES = (
    "missing_information",
    "reversible_draft",
    "refused_action",
    "exact_confirmation",
    "citation_explanation",
)

_ALLOWED_BUNDLE_VALIDATION_STATUSES = {"fixture_validated", "validated", "current"}
_STALE_STATUSES = {"expired", "invalidated", "needs_refresh", "outdated", "stale"}
_UNSUPPORTED_READY_STATUSES = {
    "ready",
    "ready_for_certification",
    "ready_for_payment",
    "ready_for_scheduling",
    "ready_for_submission",
    "ready_for_upload",
    "ready_to_certify",
    "ready_to_pay",
    "ready_to_schedule",
    "ready_to_submit",
    "ready_to_upload",
    "ready-to-submit",
}

_PRIVATE_KEYS = {
    "access_token",
    "account_number",
    "auth_state",
    "bank_account",
    "card_number",
    "cardholder",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "credit_card",
    "cvv",
    "email",
    "field_value",
    "local_path",
    "password",
    "payment_details",
    "payment_method",
    "payment_token",
    "phone",
    "private_value",
    "raw_value",
    "refresh_token",
    "routing_number",
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
    "financial",
    "inspection_scheduling",
    "payment",
    "scheduling",
    "submission",
    "upload",
    "upload_to_official_record",
}

_CONSEQUENTIAL_TERMS = (
    "certif",
    "payment",
    "pay",
    "schedule",
    "scheduling",
    "submit",
    "submission",
    "upload",
)

_PRIVATE_PATH_PATTERN = re.compile(
    r"(file://|/home/|/users/|/var/folders/|/tmp/[^\s]+|\\users\\|[a-z]:\\)",
    re.IGNORECASE,
)


class GuardrailApiContractError(ValueError):
    """Raised when a fixture cannot be exposed as an agent API packet."""

    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid guardrail API contract packet: " + "; ".join(self.problems))


def load_guardrail_api_contract_fixture(path: str | Path) -> dict[str, Any]:
    """Load a committed fixture and build the deterministic API packet."""

    fixture_path = Path(path)
    raw = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise GuardrailApiContractError(["fixture must be a JSON object"])
    return build_guardrail_api_contract_packet(
        compiled_guardrail_bundle=_required_mapping(raw, "compiled_guardrail_bundle"),
        user_gap_analysis=_required_mapping(raw, "user_gap_analysis"),
        source_evidence=raw.get("source_evidence", []),
    )


def build_guardrail_api_contract_packet(
    *,
    compiled_guardrail_bundle: Mapping[str, Any],
    user_gap_analysis: Mapping[str, Any],
    source_evidence: Any,
) -> dict[str, Any]:
    """Expose fixture GuardrailBundle and UserGapAnalysis as agent responses."""

    bundle = deepcopy(dict(compiled_guardrail_bundle))
    gap = deepcopy(dict(user_gap_analysis))
    evidence = _evidence_by_id(source_evidence)

    problems = _input_problems(bundle, gap, evidence)
    if problems:
        raise GuardrailApiContractError(problems)

    responses = [
        _missing_information_response(bundle, gap, evidence),
        _reversible_draft_response(bundle, gap, evidence),
        _refused_action_response(bundle, gap, evidence),
        _exact_confirmation_response(bundle, gap, evidence),
        _citation_explanation_response(bundle, gap, evidence),
    ]

    packet = {
        "packet_type": "ppd.guardrail_api_contract.v1",
        "fixture_first": True,
        "live_services_called": False,
        "metadata_only": True,
        "case_id": gap["case_id"],
        "process_id": bundle["process_id"],
        "guardrail_bundle_id": bundle["guardrail_bundle_id"],
        "response_order": list(RESPONSE_TYPES),
        "compiled_guardrail_bundle": _metadata_bundle(bundle),
        "user_gap_analysis": _metadata_gap(gap),
        "responses": responses,
    }

    packet_problems = validate_guardrail_api_contract_packet(packet)
    if packet_problems:
        raise GuardrailApiContractError(packet_problems)
    return packet


def validate_guardrail_api_contract_packet(packet: Mapping[str, Any]) -> list[str]:
    """Validate the assembled agent-facing packet."""

    problems: list[str] = []
    if packet.get("packet_type") != "ppd.guardrail_api_contract.v1":
        problems.append("packet_type must be ppd.guardrail_api_contract.v1")
    if packet.get("fixture_first") is not True:
        problems.append("packet must be fixture_first")
    if packet.get("live_services_called") is not False:
        problems.append("packet must confirm live_services_called is false")
    if packet.get("metadata_only") is not True:
        problems.append("packet must be metadata_only")
    if packet.get("response_order") != list(RESPONSE_TYPES):
        problems.append("response_order must expose the five guardrail response types")

    bundle = packet.get("compiled_guardrail_bundle")
    if not isinstance(bundle, Mapping):
        problems.append("compiled_guardrail_bundle must be an object")
    else:
        validation_status = str(bundle.get("validation_status") or "").lower()
        if validation_status not in _ALLOWED_BUNDLE_VALIDATION_STATUSES:
            problems.append("compiled_guardrail_bundle.validation_status must be current and validated")

    responses = packet.get("responses")
    if not isinstance(responses, list):
        problems.append("responses must be a list")
        responses = []
    response_types = [item.get("response_type") for item in responses if isinstance(item, Mapping)]
    if response_types != list(RESPONSE_TYPES):
        problems.append("responses must appear in deterministic response_order")

    exact_confirmed_ids = _packet_exact_confirmed_action_ids(responses)
    for index, response in enumerate(responses):
        if not isinstance(response, Mapping):
            problems.append(f"responses[{index}] must be an object")
            continue
        response_type = str(response.get("response_type") or "")
        if not _non_empty_text(response.get("response_id")):
            problems.append(f"responses[{index}] is missing response_id")
        if not _non_empty_text(response.get("status")):
            problems.append(f"responses[{index}] is missing status")
        if _unsupported_ready_status(response.get("status")):
            problems.append(f"responses[{index}] has unsupported ready-to-submit status")
        if not _non_empty_text(response.get("agent_message")):
            problems.append(f"responses[{index}] is missing agent_message")
        citations = response.get("citations")
        if not isinstance(citations, list) or not citations:
            problems.append(f"responses[{index}] must include citations")
        else:
            problems.extend(_citation_problems(citations, f"responses[{index}].citations"))
        problems.extend(
            _response_action_gate_problems(response, response_type, exact_confirmed_ids, f"responses[{index}]")
        )

    problems.extend(_unsafe_key_problems(packet))
    problems.extend(_stale_status_problems(packet))
    problems.extend(_unsupported_ready_status_problems(packet))
    return _dedupe(problems)


def _input_problems(
    bundle: Mapping[str, Any], gap: Mapping[str, Any], evidence: Mapping[str, Mapping[str, Any]]
) -> list[str]:
    problems: list[str] = []
    for key in ("guardrail_bundle_id", "process_id"):
        if not _non_empty_text(bundle.get(key)):
            problems.append(f"compiled_guardrail_bundle is missing {key}")
    validation_status = str(bundle.get("validation_status") or "").lower()
    if validation_status not in _ALLOWED_BUNDLE_VALIDATION_STATUSES:
        problems.append("compiled_guardrail_bundle.validation_status must be current and validated")
    for key in ("case_id", "process_id", "guardrail_bundle_id"):
        if not _non_empty_text(gap.get(key)):
            problems.append(f"user_gap_analysis is missing {key}")
    if bundle.get("process_id") != gap.get("process_id"):
        problems.append("compiled_guardrail_bundle and user_gap_analysis process_id values must match")
    if bundle.get("guardrail_bundle_id") != gap.get("guardrail_bundle_id"):
        problems.append("compiled_guardrail_bundle and user_gap_analysis guardrail_bundle_id values must match")

    bundle_evidence_ids = _string_set(bundle.get("source_evidence_ids"))
    if not bundle_evidence_ids:
        problems.append("compiled_guardrail_bundle must include source_evidence_ids")
    missing_evidence = sorted(bundle_evidence_ids.difference(evidence))
    if missing_evidence:
        problems.append("source_evidence is missing bundle citations: " + ", ".join(missing_evidence))
    for evidence_id in bundle_evidence_ids.intersection(evidence):
        problems.extend(_source_evidence_problems(evidence[evidence_id], f"source_evidence[{evidence_id}]"))

    for key in (
        "deterministic_predicates",
        "reversible_action_predicates",
        "refused_action_predicates",
        "exact_confirmation_predicates",
    ):
        if not isinstance(bundle.get(key), list) or not bundle.get(key):
            problems.append(f"compiled_guardrail_bundle.{key} must be a non-empty list")
        for predicate in _mapping_items(bundle.get(key)):
            refs = _string_set(predicate.get("source_evidence_ids"))
            if not refs:
                problems.append(f"compiled_guardrail_bundle.{key} predicates must cite source_evidence_ids")
            elif not refs.issubset(bundle_evidence_ids):
                problems.append(f"compiled_guardrail_bundle.{key} predicates cite unknown source_evidence_ids")

    if not isinstance(gap.get("missing_facts"), list):
        problems.append("user_gap_analysis.missing_facts must be a list")
    if not isinstance(gap.get("missing_documents"), list):
        problems.append("user_gap_analysis.missing_documents must be a list")
    if not isinstance(gap.get("blocked_actions"), list) or not gap.get("blocked_actions"):
        problems.append("user_gap_analysis.blocked_actions must be a non-empty list")
    if not isinstance(gap.get("required_confirmations"), list) or not gap.get("required_confirmations"):
        problems.append("user_gap_analysis.required_confirmations must be a non-empty list")
    if not isinstance(gap.get("next_safe_actions"), list) or not gap.get("next_safe_actions"):
        problems.append("user_gap_analysis.next_safe_actions must be a non-empty list")

    refused_action_ids = {
        str(item.get("action_id") or "") for item in _mapping_items(bundle.get("refused_action_predicates"))
    }
    exact_action_ids = {
        str(item.get("action_id") or "") for item in _mapping_items(bundle.get("exact_confirmation_predicates"))
    }
    required_confirmation_ids = {
        str(item.get("action_id") or item.get("confirmation_id") or item)
        for item in gap.get("required_confirmations", [])
        if isinstance(item, (str, Mapping))
    }
    for blocked in _mapping_items(gap.get("blocked_actions")):
        action_id = str(blocked.get("action_id") or "")
        if _action_requires_confirmation(blocked):
            if action_id not in refused_action_ids:
                problems.append(f"blocked consequential action {action_id} must have a refused predicate")
            if action_id not in exact_action_ids:
                problems.append(f"blocked consequential action {action_id} must have an exact-confirmation predicate")
            if action_id not in required_confirmation_ids:
                problems.append(f"blocked consequential action {action_id} must be listed in required_confirmations")

    for safe_action in _mapping_items(gap.get("next_safe_actions")):
        if _action_requires_confirmation(safe_action):
            action_id = str(safe_action.get("action_id") or safe_action.get("next_safe_action_id") or "")
            problems.append(f"next_safe_actions cannot include consequential action {action_id}")

    problems.extend(_unsafe_key_problems(bundle, "compiled_guardrail_bundle"))
    problems.extend(_unsafe_key_problems(gap, "user_gap_analysis"))
    problems.extend(_stale_status_problems(bundle, "compiled_guardrail_bundle"))
    problems.extend(_stale_status_problems(gap, "user_gap_analysis"))
    problems.extend(_unsupported_ready_status_problems(bundle, "compiled_guardrail_bundle"))
    problems.extend(_unsupported_ready_status_problems(gap, "user_gap_analysis"))
    return _dedupe(problems)


def _missing_information_response(
    bundle: Mapping[str, Any], gap: Mapping[str, Any], evidence: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    missing_facts = sorted(_string_set(gap.get("missing_facts")))
    missing_documents = sorted(_string_set(gap.get("missing_documents")))
    citations = _citations(bundle.get("source_evidence_ids"), evidence)
    return {
        "response_id": "response:missing-information",
        "response_type": "missing_information",
        "status": "needs_user_input" if missing_facts or missing_documents else "complete",
        "agent_message": "Ask only for the missing synthetic case fact and document metadata before preparing any draft.",
        "missing_facts": missing_facts,
        "missing_documents": missing_documents,
        "citations": citations,
    }


def _reversible_draft_response(
    bundle: Mapping[str, Any], gap: Mapping[str, Any], evidence: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    actions = []
    next_safe_ids = {
        str(item.get("action_id") or item.get("next_safe_action_id") or "")
        for item in _mapping_items(gap.get("next_safe_actions"))
    }
    for predicate in _mapping_items(bundle.get("reversible_action_predicates")):
        action_id = str(predicate.get("action_id") or "")
        actions.append(
            {
                "action_id": action_id,
                "action": str(predicate.get("action") or action_id),
                "classification": str(predicate.get("classification") or "reversible_draft"),
                "status": "available_as_reversible_draft" if action_id in next_safe_ids else "not_next_safe_action",
                "blocked_by_missing_facts": sorted(
                    _string_set(predicate.get("depends_on_missing_facts")).intersection(_string_set(gap.get("missing_facts")))
                ),
                "blocked_by_missing_documents": sorted(
                    _string_set(predicate.get("depends_on_missing_documents")).intersection(
                        _string_set(gap.get("missing_documents"))
                    )
                ),
            }
        )
    return {
        "response_id": "response:reversible-draft",
        "response_type": "reversible_draft",
        "status": "draft_only",
        "agent_message": "Prepare local draft metadata only; do not upload, certify, submit, schedule, cancel, or pay.",
        "actions": sorted(actions, key=lambda item: item["action_id"]),
        "citations": _citations(bundle.get("source_evidence_ids"), evidence),
    }


def _refused_action_response(
    bundle: Mapping[str, Any], gap: Mapping[str, Any], evidence: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    blocked_by_id = {
        str(item.get("action_id") or ""): item for item in _mapping_items(gap.get("blocked_actions"))
    }
    actions = []
    for predicate in _mapping_items(bundle.get("refused_action_predicates")):
        action_id = str(predicate.get("action_id") or "")
        blocked = blocked_by_id.get(action_id, {})
        actions.append(
            {
                "action_id": action_id,
                "action": str(predicate.get("action") or action_id),
                "classification": str(predicate.get("classification") or blocked.get("classification") or "official"),
                "status": "refused",
                "requires_manual_handoff": True,
                "requires_exact_confirmation": True,
                "exact_confirmation_blocks_execution": True,
                "reason": str(
                    blocked.get("reason")
                    or predicate.get("refusal_reason")
                    or "Official PP&D action is refused by default."
                ),
            }
        )
    return {
        "response_id": "response:refused-action",
        "response_type": "refused_action",
        "status": "refused",
        "agent_message": "Refuse consequential official PP&D actions unless the user is present and controls the exact confirmed action.",
        "actions": sorted(actions, key=lambda item: item["action_id"]),
        "citations": _citations(bundle.get("source_evidence_ids"), evidence),
    }


def _exact_confirmation_response(
    bundle: Mapping[str, Any], gap: Mapping[str, Any], evidence: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    required_ids = {
        str(item.get("action_id") or item.get("confirmation_id") or item)
        for item in gap.get("required_confirmations", [])
        if isinstance(item, (str, Mapping))
    }
    confirmations = []
    for predicate in _mapping_items(bundle.get("exact_confirmation_predicates")):
        action_id = str(predicate.get("action_id") or "")
        confirmations.append(
            {
                "action_id": action_id,
                "confirmation_id": str(predicate.get("confirmation_id") or action_id),
                "required_by_gap_analysis": action_id in required_ids,
                "blocks_execution_until_confirmed": True,
                "confirmation_text": str(predicate.get("confirmation_text") or ""),
            }
        )
    return {
        "response_id": "response:exact-confirmation",
        "response_type": "exact_confirmation",
        "status": "required_for_official_actions",
        "agent_message": "Show exact action text for user confirmation before any attended official DevHub step.",
        "confirmations": sorted(confirmations, key=lambda item: item["action_id"]),
        "citations": _citations(bundle.get("source_evidence_ids"), evidence),
    }


def _citation_explanation_response(
    bundle: Mapping[str, Any], gap: Mapping[str, Any], evidence: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    citations = _citations(bundle.get("source_evidence_ids"), evidence)
    return {
        "response_id": "response:citation-explanation",
        "response_type": "citation_explanation",
        "status": "cited",
        "agent_message": "Explain every guardrail response using the committed source evidence identifiers in this packet.",
        "citation_count": len(citations),
        "covered_outputs": list(RESPONSE_TYPES[:-1]),
        "citations": citations,
    }


def _metadata_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "guardrail_bundle_id": bundle.get("guardrail_bundle_id"),
        "process_id": bundle.get("process_id"),
        "source_evidence_ids": sorted(_string_set(bundle.get("source_evidence_ids"))),
        "validation_status": bundle.get("validation_status"),
    }


def _metadata_gap(gap: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "case_id": gap.get("case_id"),
        "process_id": gap.get("process_id"),
        "guardrail_bundle_id": gap.get("guardrail_bundle_id"),
        "known_facts": gap.get("known_facts", []),
        "matched_documents": gap.get("matched_documents", []),
        "missing_facts": sorted(_string_set(gap.get("missing_facts"))),
        "missing_documents": sorted(_string_set(gap.get("missing_documents"))),
        "stale_evidence": gap.get("stale_evidence", []),
        "conflicting_evidence": gap.get("conflicting_evidence", []),
        "required_confirmations": gap.get("required_confirmations", []),
        "blocked_actions": gap.get("blocked_actions", []),
        "next_safe_actions": gap.get("next_safe_actions", []),
    }


def _evidence_by_id(source_evidence: Any) -> dict[str, Mapping[str, Any]]:
    if not isinstance(source_evidence, list):
        raise GuardrailApiContractError(["source_evidence must be a list"])
    indexed: dict[str, Mapping[str, Any]] = {}
    for item in source_evidence:
        if not isinstance(item, Mapping):
            continue
        evidence_id = str(item.get("evidence_id") or "")
        if evidence_id:
            indexed[evidence_id] = item
    if not indexed:
        raise GuardrailApiContractError(["source_evidence must include at least one cited record"])
    return indexed


def _citations(raw_ids: Any, evidence: Mapping[str, Mapping[str, Any]]) -> list[dict[str, str]]:
    citations = []
    for evidence_id in sorted(_string_set(raw_ids)):
        record = evidence[evidence_id]
        citations.append(
            {
                "evidence_id": evidence_id,
                "title": str(record.get("title") or ""),
                "canonical_url": str(record.get("canonical_url") or ""),
                "source_type": str(record.get("source_type") or ""),
                "last_verified_at": str(record.get("last_verified_at") or ""),
                "freshness_status": str(record.get("freshness_status") or ""),
            }
        )
    return citations


def _required_mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    nested = value.get(key)
    if not isinstance(nested, Mapping):
        raise GuardrailApiContractError([f"fixture is missing {key}"])
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


def _citation_problems(citations: list[Any], path: str) -> list[str]:
    problems: list[str] = []
    for index, citation in enumerate(citations):
        citation_path = f"{path}[{index}]"
        if not isinstance(citation, Mapping):
            problems.append(f"{citation_path} must be an object")
            continue
        problems.extend(_source_evidence_problems(citation, citation_path, citation_mode=True))
    return problems


def _source_evidence_problems(record: Mapping[str, Any], path: str, *, citation_mode: bool = False) -> list[str]:
    problems: list[str] = []
    for key in ("evidence_id", "canonical_url", "source_type", "last_verified_at"):
        if not _non_empty_text(record.get(key)):
            problems.append(f"{path}.{key} is required for cited guardrail output")
    canonical_url = str(record.get("canonical_url") or "")
    if canonical_url and not canonical_url.startswith("https://www.portland.gov/ppd/"):
        problems.append(f"{path}.canonical_url must be an official PP&D URL")
    last_verified_at = str(record.get("last_verified_at") or "")
    if last_verified_at and not last_verified_at.endswith("Z"):
        problems.append(f"{path}.last_verified_at must be an ISO UTC timestamp")
    freshness_status = str(record.get("freshness_status") or "").lower()
    if citation_mode and not freshness_status:
        problems.append(f"{path}.freshness_status is required")
    if freshness_status in _STALE_STATUSES:
        problems.append(f"{path}.freshness_status must not be stale")
    if not citation_mode and record.get("no_raw_body_persisted") is not True:
        problems.append(f"{path}.no_raw_body_persisted must be true")
    return problems


def _packet_exact_confirmed_action_ids(responses: Any) -> set[str]:
    if not isinstance(responses, list):
        return set()
    confirmed: set[str] = set()
    for response in responses:
        if not isinstance(response, Mapping) or response.get("response_type") != "exact_confirmation":
            continue
        for confirmation in _mapping_items(response.get("confirmations")):
            action_id = str(confirmation.get("action_id") or "")
            if (
                action_id
                and confirmation.get("blocks_execution_until_confirmed") is True
                and _non_empty_text(confirmation.get("confirmation_text"))
            ):
                confirmed.add(action_id)
    return confirmed


def _response_action_gate_problems(
    response: Mapping[str, Any], response_type: str, exact_confirmed_ids: set[str], path: str
) -> list[str]:
    problems: list[str] = []
    for field in ("actions", "confirmations"):
        nested = response.get(field)
        if nested is None:
            continue
        if not isinstance(nested, list):
            problems.append(f"{path}.{field} must be a list")
            continue
        for index, action in enumerate(nested):
            action_path = f"{path}.{field}[{index}]"
            if not isinstance(action, Mapping):
                problems.append(f"{action_path} must be an object")
                continue
            action_id = str(action.get("action_id") or action.get("confirmation_id") or "")
            if _unsupported_ready_status(action.get("status")):
                problems.append(f"{action_path} has unsupported ready-to-submit status")
            if not _action_requires_confirmation(action):
                continue
            if response_type == "exact_confirmation":
                if action.get("blocks_execution_until_confirmed") is not True:
                    problems.append(f"{action_path} must block execution until exact confirmation")
                if not _non_empty_text(action.get("confirmation_text")):
                    problems.append(f"{action_path} must include exact confirmation_text")
                continue
            if action.get("requires_exact_confirmation") is not True:
                problems.append(f"{action_path} must require exact confirmation")
            if action.get("exact_confirmation_blocks_execution") is not True:
                problems.append(f"{action_path} must block execution until exact confirmation")
            if action_id not in exact_confirmed_ids:
                problems.append(f"{action_path} must link to an exact-confirmation response")
            if response_type != "refused_action" and str(action.get("status") or "") not in {"blocked", "refused"}:
                problems.append(f"{action_path} consequential action must be refused or blocked")
    return problems


def _action_requires_confirmation(action: Mapping[str, Any]) -> bool:
    classification = str(action.get("classification") or action.get("action_classification") or "").lower()
    if classification in _CONSEQUENTIAL_CLASSES:
        return True
    searchable = " ".join(
        str(action.get(key) or "")
        for key in ("action_id", "action", "label", "button_label", "confirmation_id")
    ).lower()
    return any(term in searchable for term in _CONSEQUENTIAL_TERMS)


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
        if _PRIVATE_PATH_PATTERN.search(lowered) or "storage_state" in lowered or "trace.zip" in lowered:
            problems.append(f"private or live artifact reference is not allowed: {path}")
    return problems


def _stale_status_problems(value: Any, path: str = "packet") -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key).lower()
            nested_path = f"{path}.{key_text}"
            if key_text in {"stale_evidence", "conflicting_evidence"} and isinstance(nested, list) and nested:
                problems.append(f"stale or conflicting evidence is not allowed: {nested_path}")
            if key_text in {"freshness_status", "validation_status"} and str(nested).lower() in _STALE_STATUSES:
                problems.append(f"stale status is not allowed: {nested_path}")
            problems.extend(_stale_status_problems(nested, nested_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            problems.extend(_stale_status_problems(nested, f"{path}[{index}]"))
    return problems


def _unsupported_ready_status_problems(value: Any, path: str = "packet") -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            nested_path = f"{path}.{str(key).lower()}"
            if str(key).lower() == "status" and _unsupported_ready_status(nested):
                problems.append(f"unsupported ready-to-submit status is not allowed: {nested_path}")
            problems.extend(_unsupported_ready_status_problems(nested, nested_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            problems.extend(_unsupported_ready_status_problems(nested, f"{path}[{index}]"))
    return problems


def _unsupported_ready_status(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    return normalized in {status.replace("-", "_") for status in _UNSUPPORTED_READY_STATUSES}


def _dedupe(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
