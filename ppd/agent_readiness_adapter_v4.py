"""Offline PP&D agent readiness adapter v4.

The adapter is intentionally narrow: it reads the committed schema expectation
packet v4 fixtures and returns one of that packet's cited example responses. It
performs no live LLM calls, DevHub access, user-document reads, browser work, or
official PP&D actions.
"""

from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from ppd.agent_readiness_expectation_packet_v4 import (
    ALLOWED_NEXT_ACTION_CLASSES,
    EXAMPLE_KINDS,
    REQUIRED_ATTESTATIONS,
    _AUTHENTICATED_DEVHUB_KEYS,
    _FINAL_ACTION_LANGUAGE_RE,
    _LIVE_COMPLETION_CLAIM_RE,
    _LOCAL_PATH_RE,
    _MUTATION_FLAG_KEYS,
    _OUTCOME_GUARANTEE_RE,
    _PRIVATE_VALUE_KEYS,
    _RAW_ARTIFACT_KEYS,
    build_expectation_packet,
    validate_expectation_packet,
)


ADAPTER_VERSION = "offline-agent-readiness-adapter-v4"
DEFAULT_FIXTURE_ROOT = Path(__file__).parent / "tests" / "fixtures" / "agent_readiness_packet_v4"

OFFICIAL_ACTION_MARKERS = (
    "approve",
    "cancel",
    "certification",
    "certify",
    "finalize",
    "issue",
    "pay",
    "payment",
    "purchase",
    "schedule",
    "submit",
    "upload",
    "withdraw",
)
MISSING_INFORMATION_ACTIONS = {
    "ask_missing_information",
    "collect_missing_facts",
    "draft_readiness_response",
    "missing_information",
    "request_missing_fixture_fields",
}
STALE_OR_CONFLICTING_ACTIONS = {
    "conflicting_evidence",
    "refresh_evidence",
    "stale_evidence",
    "summarize_evidence_status",
    "surface_conflict",
}
REVERSIBLE_PREVIEW_ACTIONS = {
    "draft_local_preview",
    "preview_draft_only",
    "render_preview",
    "reversible_draft_preview",
}
NEXT_SAFE_ACTIONS = {
    "compare_fixtures",
    "continue_safely",
    "draft_local_readiness_note",
    "next_safe_read_only_action",
    "read_only_summary",
}
PROCESS_ID_FIELDS = {
    "permit_process_id",
    "process_id",
    "process_model_ref",
    "process_ref",
    "requested_process_id",
    "workflow_process_id",
}
PROCESS_ID_LIST_FIELDS = {"process_ids", "process_refs"}
REQUIRED_FACT_FIELDS = ("required_user_facts", "required_facts", "required_case_facts")
PROVIDED_FACT_FIELDS = ("user_facts", "provided_user_facts", "case_facts", "fixture_facts")
KNOWN_PROCESS_IDS = {"ppd-demo-permit-readiness"}
EXTRA_PRIVATE_VALUE_KEYS = {"authenticated_value", "document_path", "file_path"}
MUTATION_TEXT_RE = re.compile(
    r"\b(mutates?|mutation|rewrite|replace|update|edit|patch)\b.{0,60}"
    r"\b(prompt|guardrail|source registry|surface registry|release state|agent state)s?\b"
    r"|\b(prompt|guardrail|source registry|surface registry|release state|agent state)s?\b.{0,60}"
    r"\b(mutates?|mutation|rewrite|replace|update|edit|patch)\b",
    re.IGNORECASE,
)


def evaluate_offline_agent_readiness(
    request: Mapping[str, Any],
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
) -> dict[str, Any]:
    """Return a deterministic cited agent-facing readiness response.

    The request is used only for routing to a fixture-backed example kind. The
    returned output is copied from the validated expectation packet so arbitrary
    request values, user facts, document paths, and account-scoped data are never
    echoed into the agent-facing response.
    """

    if not isinstance(request, Mapping):
        raise TypeError("request must be a mapping")

    packet = build_expectation_packet(fixture_root)
    validate_expectation_packet(packet)
    examples = _examples_by_kind(packet)
    kind = _select_example_kind(request, packet)
    response = deepcopy(examples[kind]["response"])
    _validate_adapter_response(response, packet)
    response["adapter"] = {
        "adapter_version": ADAPTER_VERSION,
        "fixture_packet_id": packet["packet_id"],
        "selected_example_kind": kind,
        "attestations": {name: True for name in REQUIRED_ATTESTATIONS},
    }
    return response


def build_offline_agent_readiness_examples(
    fixture_root: Path = DEFAULT_FIXTURE_ROOT,
) -> dict[str, dict[str, Any]]:
    """Expose the validated fixture-backed examples indexed by example kind."""

    packet = build_expectation_packet(fixture_root)
    validate_expectation_packet(packet)
    examples = {kind: deepcopy(example["response"]) for kind, example in _examples_by_kind(packet).items()}
    for response in examples.values():
        _validate_adapter_response(response, packet)
    return examples


def _examples_by_kind(packet: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    examples: dict[str, Mapping[str, Any]] = {}
    for example in packet.get("examples", []):
        if isinstance(example, Mapping):
            kind = str(example.get("kind", ""))
            if kind:
                examples[kind] = example
    missing = sorted(set(EXAMPLE_KINDS) - set(examples))
    if missing:
        raise ValueError(f"expectation packet is missing examples: {missing}")
    return examples


def _select_example_kind(request: Mapping[str, Any], packet: Mapping[str, Any]) -> str:
    action = str(request.get("requested_action", "")).strip().lower()
    evidence_status = str(request.get("evidence_status", "")).strip().lower()
    evidence_refs = request.get("evidence_refs", [])

    if _has_unsafe_request_value(request) or _has_unsupported_process_id(request, packet):
        return "blocked_action_explanation"
    if _is_official_action(action):
        return "blocked_action_explanation"
    if _has_missing_citations(evidence_refs):
        return "missing_information_prompt"
    if _has_unknown_evidence_ref(evidence_refs, packet):
        return "stale_or_conflicting_evidence_notice"
    if action in STALE_OR_CONFLICTING_ACTIONS or evidence_status in {"stale", "conflicting", "stale_or_conflicting"}:
        return "stale_or_conflicting_evidence_notice"
    if _has_nonempty_list(request.get("stale_evidence")) or _has_nonempty_list(request.get("conflicting_evidence")):
        return "stale_or_conflicting_evidence_notice"
    if _is_missing_required_user_fact(request):
        return "missing_information_prompt"
    if action in REVERSIBLE_PREVIEW_ACTIONS:
        return "reversible_draft_preview"
    if action in NEXT_SAFE_ACTIONS:
        return "next_safe_read_only_action"
    if action in MISSING_INFORMATION_ACTIONS:
        return "missing_information_prompt"
    if _has_nonempty_list(request.get("missing_facts")) or _has_nonempty_list(request.get("missing_documents")):
        return "missing_information_prompt"
    return "next_safe_read_only_action"


def _validate_adapter_response(response: Mapping[str, Any], packet: Mapping[str, Any]) -> None:
    consumed_refs = _consumed_refs(packet)
    for field in ("citations", "process_refs", "gap_refs", "guardrail_refs"):
        refs = _string_list(response.get(field))
        if not refs:
            raise ValueError(f"adapter fixture response is missing {field}")
        unknown = sorted(set(refs) - consumed_refs)
        if unknown:
            raise ValueError(f"adapter fixture response has unsupported {field}: {unknown}")


def _is_official_action(action: str) -> bool:
    if not action:
        return False
    return any(marker in action for marker in OFFICIAL_ACTION_MARKERS)


def _has_missing_citations(value: Any) -> bool:
    return not _string_list(value)


def _has_unknown_evidence_ref(value: Any, packet: Mapping[str, Any]) -> bool:
    refs = _string_list(value)
    if not refs:
        return False
    allowed_refs = _consumed_refs(packet)
    return any(ref not in allowed_refs for ref in refs)


def _has_unsupported_process_id(request: Mapping[str, Any], packet: Mapping[str, Any]) -> bool:
    allowed = _consumed_refs(packet) | KNOWN_PROCESS_IDS | {str(request.get("workflow_id", "")).strip()}
    allowed = {item for item in allowed if item}
    for field in PROCESS_ID_FIELDS:
        value = request.get(field)
        if isinstance(value, str) and value.strip() and value.strip() not in allowed:
            return True
    for field in PROCESS_ID_LIST_FIELDS:
        value = request.get(field)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item.strip() and item.strip() not in allowed:
                    return True
    return False


def _is_missing_required_user_fact(request: Mapping[str, Any]) -> bool:
    required = _first_string_list(request, REQUIRED_FACT_FIELDS)
    if not required:
        return False
    supplied = _supplied_fact_names(request)
    return any(name not in supplied for name in required)


def _first_string_list(request: Mapping[str, Any], fields: tuple[str, ...]) -> list[str]:
    for field in fields:
        values = _string_list(request.get(field))
        if values:
            return values
    return []


def _supplied_fact_names(request: Mapping[str, Any]) -> set[str]:
    supplied: set[str] = set()
    for field in PROVIDED_FACT_FIELDS:
        value = request.get(field)
        if isinstance(value, Mapping):
            supplied.update(str(key) for key, child in value.items() if child not in (None, "", [], {}))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item:
                    supplied.add(item)
                elif isinstance(item, Mapping):
                    name = item.get("name") or item.get("id") or item.get("field")
                    fact_value = item.get("value", True)
                    if isinstance(name, str) and name and fact_value not in (None, "", [], {}):
                        supplied.add(name)
    return supplied


def _has_unsafe_request_value(value: Any, key_name: str = "") -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized_key = str(key).lower()
            if normalized_key in _PRIVATE_VALUE_KEYS | EXTRA_PRIVATE_VALUE_KEYS and child not in (None, "", [], {}):
                return True
            if normalized_key in _AUTHENTICATED_DEVHUB_KEYS and child not in (None, "", [], {}):
                return True
            if normalized_key in _RAW_ARTIFACT_KEYS and child not in (None, "", [], {}):
                return True
            if normalized_key in _MUTATION_FLAG_KEYS and child not in (False, None, "", [], {}):
                return True
            if normalized_key in {"next_action_class", "action_class"} and isinstance(child, str):
                if child not in ALLOWED_NEXT_ACTION_CLASSES:
                    return True
            if normalized_key in {"local_path", "path", "file_path", "document_path"} and _contains_local_path(child):
                return True
            if _has_unsafe_request_value(child, normalized_key):
                return True
    elif isinstance(value, list):
        return any(_has_unsafe_request_value(child, key_name) for child in value)
    elif isinstance(value, str):
        if _LOCAL_PATH_RE.search(value) and key_name in {"local_path", "path", "file_path", "document_path"}:
            return True
        if _LIVE_COMPLETION_CLAIM_RE.search(value):
            return True
        if _OUTCOME_GUARANTEE_RE.search(value):
            return True
        if _FINAL_ACTION_LANGUAGE_RE.search(value):
            return True
        if MUTATION_TEXT_RE.search(value):
            return True
    return False


def _has_nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and any(bool(item) for item in value)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _consumed_refs(packet: Mapping[str, Any]) -> set[str]:
    consumes = packet.get("consumes")
    if isinstance(consumes, Mapping):
        return {item for item in consumes.values() if isinstance(item, str) and item}
    return set()


def _contains_local_path(value: Any) -> bool:
    if isinstance(value, str):
        return bool(_LOCAL_PATH_RE.search(value))
    if isinstance(value, list):
        return any(_contains_local_path(item) for item in value)
    if isinstance(value, Mapping):
        return any(_contains_local_path(item) for item in value.values())
    return False
