"""Fixture-first agent readiness API schema expectation packet v4."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping


PACKET_VERSION = "agent-readiness-api-schema-expectation-packet-v4"
REQUIRED_ATTESTATIONS = (
    "no_live_llm",
    "no_devhub",
    "no_user_data",
    "no_official_action",
)
EXAMPLE_KINDS = (
    "missing_information_prompt",
    "stale_or_conflicting_evidence_notice",
    "reversible_draft_preview",
    "blocked_action_explanation",
    "next_safe_read_only_action",
)
REQUIRED_REFERENCE_FIELDS = ("process_refs", "gap_refs", "guardrail_refs")
ALLOWED_NEXT_ACTION_CLASSES = {
    "ask_missing_information",
    "compare_fixtures",
    "draft_local_preview",
    "explain_block",
    "read_only_summary",
    "remain_read_only",
    "surface_conflict",
}
_PRIVATE_VALUE_KEYS = {
    "access_token",
    "applicant_email",
    "applicant_name",
    "auth_state",
    "bank_account",
    "card_number",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "cvv",
    "devhub_session",
    "email",
    "entered_value",
    "field_value",
    "local_path",
    "password",
    "payment_details",
    "phone",
    "private_fact",
    "private_user_fact",
    "private_value",
    "raw_value",
    "refresh_token",
    "secret",
    "session_cookie",
    "session_state",
    "ssn",
    "token",
    "user_input",
    "user_supplied_value",
    "value",
}
_AUTHENTICATED_DEVHUB_KEYS = {
    "authenticated_devhub_value",
    "devhub_account_value",
    "devhub_authenticated_value",
    "devhub_field_value",
    "devhub_private_value",
    "devhub_profile_value",
    "devhub_session_value",
}
_RAW_ARTIFACT_KEYS = {
    "browser_snapshot",
    "browser_storage",
    "document_body",
    "downloaded_document",
    "har",
    "html",
    "page_content",
    "raw_browser_artifact",
    "raw_document",
    "raw_document_text",
    "raw_html",
    "raw_session",
    "screenshot",
    "session_artifact",
    "trace",
}
_MUTATION_FLAG_KEYS = {
    "agent_state_mutation",
    "agent_state_mutation_enabled",
    "allow_agent_state_mutation",
    "allow_guardrail_mutation",
    "allow_prompt_mutation",
    "allow_release_state_mutation",
    "allow_source_mutation",
    "allow_surface_registry_mutation",
    "guardrail_mutation",
    "guardrail_mutation_enabled",
    "mutate_agent_state",
    "mutate_guardrails",
    "mutate_prompt",
    "mutate_release_state",
    "mutate_source_registry",
    "mutate_sources",
    "mutate_surface_registry",
    "prompt_mutation",
    "prompt_mutation_enabled",
    "release_state_mutation",
    "release_state_mutation_enabled",
    "source_mutation",
    "source_mutation_enabled",
    "surface_registry_mutation",
    "surface_registry_mutation_enabled",
}
_LIVE_COMPLETION_CLAIM_RE = re.compile(
    r"\b(live llm|devhub)\b.{0,80}\b(completed|completion|executed|finished|ran|submitted|uploaded|paid|scheduled|cancelled|canceled)\b"
    r"|\b(completed|executed|finished|ran)\b.{0,80}\b(live llm|devhub)\b",
    re.IGNORECASE,
)
_OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee|guaranteed|will be approved|permit will issue|approval is certain|legally sufficient|complies with all laws|no legal risk)\b",
    re.IGNORECASE,
)
_FINAL_ACTION_LANGUAGE_RE = re.compile(
    r"\b(final submit|submit payment|submitted (the )?(application|permit|request)|paid (the )?fee|uploaded (the )?(file|document|correction|plans)|scheduled (the )?inspection|cancelled (the )?(inspection|permit|request)|canceled (the )?(inspection|permit|request))\b",
    re.IGNORECASE,
)
_LOCAL_PATH_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/private/)|(^~?/\.devhub/)|(^[A-Za-z]:\\Users\\[^\\]+\\)",
    re.IGNORECASE,
)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"fixture must be an object: {path}")
    return value


def build_expectation_packet(fixture_root: Path) -> dict[str, Any]:
    """Build the v4 expectation packet from committed offline fixtures."""
    coverage = _load_json(fixture_root / "coverage_v3.json")
    process_model = _load_json(fixture_root / "process_model_fixtures.json")
    gap_analysis = _load_json(fixture_root / "user_gap_analysis_fixtures.json")
    guardrails = _load_json(fixture_root / "guardrail_bundle_fixtures.json")

    citations = {
        "coverage": coverage["packet_id"],
        "process_model": process_model["fixture_id"],
        "gap_analysis": gap_analysis["fixture_id"],
        "guardrails": guardrails["bundle_id"],
    }

    return {
        "packet_id": PACKET_VERSION,
        "consumes": citations,
        "attestations": {name: True for name in REQUIRED_ATTESTATIONS},
        "api": {
            "method": "POST",
            "path": "/ppd/agent-readiness/v4/evaluate",
            "request_schema": {
                "type": "object",
                "required": ["workflow_id", "agent_goal", "evidence_refs", "requested_action"],
                "properties": {
                    "workflow_id": {"type": "string"},
                    "agent_goal": {"type": "string"},
                    "evidence_refs": {"type": "array", "items": {"type": "string"}},
                    "requested_action": {"type": "string"},
                },
            },
            "response_schema": {
                "type": "object",
                "required": [
                    "ready",
                    "example_kind",
                    "message",
                    "citations",
                    "process_refs",
                    "gap_refs",
                    "guardrail_refs",
                    "safe_next_actions",
                    "safe_next_action_classes",
                    "attestations",
                ],
            },
        },
        "examples": _examples(citations),
    }


def _safe_response(
    citations: dict[str, str],
    *,
    ready: bool,
    example_kind: str,
    message: str,
    citation_keys: list[str],
    safe_next_actions: list[str],
    safe_next_action_classes: list[str],
) -> dict[str, Any]:
    return {
        "ready": ready,
        "example_kind": example_kind,
        "message": message,
        "citations": [citations[key] for key in citation_keys],
        "process_refs": [citations["process_model"]],
        "gap_refs": [citations["gap_analysis"]],
        "guardrail_refs": [citations["guardrails"]],
        "safe_next_actions": safe_next_actions,
        "safe_next_action_classes": safe_next_action_classes,
        "attestations": {name: True for name in REQUIRED_ATTESTATIONS},
    }


def _examples(citations: dict[str, str]) -> list[dict[str, Any]]:
    base_request = {
        "workflow_id": "ppd-demo-permit-readiness",
        "agent_goal": "Prepare a read-only permit readiness draft from fixture evidence.",
        "evidence_refs": list(citations.values()),
        "requested_action": "draft_readiness_response",
    }
    return [
        {
            "kind": "missing_information_prompt",
            "request": base_request,
            "response": _safe_response(
                citations,
                ready=False,
                example_kind="missing_information_prompt",
                message="The fixtures do not identify the permit address or applicant role. Ask for those fields before drafting readiness language.",
                citation_keys=["gap_analysis", "coverage", "process_model", "guardrails"],
                safe_next_actions=["request_missing_fixture_fields", "remain_read_only"],
                safe_next_action_classes=["ask_missing_information", "remain_read_only"],
            ),
        },
        {
            "kind": "stale_or_conflicting_evidence_notice",
            "request": {**base_request, "requested_action": "summarize_evidence_status"},
            "response": _safe_response(
                citations,
                ready=False,
                example_kind="stale_or_conflicting_evidence_notice",
                message="The readiness contract marks one evidence item stale and the process model contains a conflicting checkpoint sequence.",
                citation_keys=["coverage", "process_model", "gap_analysis", "guardrails"],
                safe_next_actions=["surface_conflict", "ask_for_refreshed_fixture"],
                safe_next_action_classes=["surface_conflict", "ask_missing_information"],
            ),
        },
        {
            "kind": "reversible_draft_preview",
            "request": {**base_request, "requested_action": "preview_draft_only"},
            "response": _safe_response(
                citations,
                ready=True,
                example_kind="reversible_draft_preview",
                message="Produce a draft preview only; keep all official systems unchanged.",
                citation_keys=["guardrails", "process_model", "gap_analysis"],
                safe_next_actions=["render_preview", "allow_user_review"],
                safe_next_action_classes=["draft_local_preview", "remain_read_only"],
            ),
        },
        {
            "kind": "blocked_action_explanation",
            "request": {**base_request, "requested_action": "submit_application"},
            "response": _safe_response(
                citations,
                ready=False,
                example_kind="blocked_action_explanation",
                message="The requested official action is blocked because the offline fixture workflow permits only explanation and local review.",
                citation_keys=["guardrails", "process_model", "gap_analysis"],
                safe_next_actions=["explain_block", "offer_read_only_summary"],
                safe_next_action_classes=["explain_block", "read_only_summary"],
            ),
        },
        {
            "kind": "next_safe_read_only_action",
            "request": {**base_request, "requested_action": "continue_safely"},
            "response": _safe_response(
                citations,
                ready=True,
                example_kind="next_safe_read_only_action",
                message="The next safe action is to compare committed fixtures and prepare a cited local-only readiness note.",
                citation_keys=["coverage", "process_model", "gap_analysis", "guardrails"],
                safe_next_actions=["compare_fixtures", "draft_local_readiness_note"],
                safe_next_action_classes=["compare_fixtures", "read_only_summary"],
            ),
        },
    ]


def validate_expectation_packet(packet: dict[str, Any]) -> None:
    problems: list[str] = []
    if packet.get("packet_id") != PACKET_VERSION:
        problems.append("unexpected packet version")

    attestations = packet.get("attestations", {})
    missing = [name for name in REQUIRED_ATTESTATIONS if not isinstance(attestations, Mapping) or attestations.get(name) is not True]
    if missing:
        problems.append(f"missing attestations: {missing}")

    consumed_refs = _consumed_refs(packet)
    examples = packet.get("examples", [])
    if not isinstance(examples, list):
        problems.append("examples must be a list")
        examples = []
    kinds = {example.get("kind") for example in examples if isinstance(example, Mapping)}
    if kinds != set(EXAMPLE_KINDS):
        problems.append(f"unexpected example kinds: {sorted(kinds)}")

    for index, example in enumerate(examples):
        if not isinstance(example, Mapping):
            problems.append(f"example must be an object at examples[{index}]")
            continue
        example_path = f"examples[{index}]"
        response = example.get("response", {})
        if not isinstance(response, Mapping):
            problems.append(f"example response must be an object: {example.get('kind')}")
            continue
        problems.extend(_response_reference_problems(response, consumed_refs, example_path))
        problems.extend(_next_action_class_problems(response, example_path))
        response_attestations = response.get("attestations", {})
        if any(not isinstance(response_attestations, Mapping) or response_attestations.get(name) is not True for name in REQUIRED_ATTESTATIONS):
            problems.append(f"example lacks response attestations: {example.get('kind')}")

    problems.extend(_unsafe_value_problems(packet))
    if problems:
        raise ValueError("invalid agent readiness expectation packet v4: " + "; ".join(problems))


def _response_reference_problems(response: Mapping[str, Any], consumed_refs: set[str], path: str) -> list[str]:
    problems: list[str] = []
    citations = _string_list(response.get("citations"))
    if not citations:
        problems.append(f"example lacks citations at {path}.response")
    for citation in citations:
        if citation not in consumed_refs:
            problems.append(f"example cites unknown fixture reference {citation} at {path}.response.citations")

    for field in REQUIRED_REFERENCE_FIELDS:
        refs = _string_list(response.get(field))
        if not refs:
            problems.append(f"example response missing {field} at {path}.response")
        for ref in refs:
            if ref not in consumed_refs:
                problems.append(f"example response {field} cites unknown fixture reference {ref} at {path}.response")
    return problems


def _next_action_class_problems(response: Mapping[str, Any], path: str) -> list[str]:
    classes = _string_list(response.get("safe_next_action_classes"))
    if not classes:
        return [f"example response missing safe_next_action_classes at {path}.response"]
    unsupported = sorted(set(classes) - ALLOWED_NEXT_ACTION_CLASSES)
    if unsupported:
        return [f"unsupported next-action classes at {path}.response.safe_next_action_classes: {unsupported}"]
    return []


def _unsafe_value_problems(value: Any, path: str = "$", key_name: str = "") -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.lower()
            child_path = f"{path}.{key_text}"
            if normalized_key in _PRIVATE_VALUE_KEYS and child not in (None, "", [], {}):
                problems.append(f"private user fact or value is not allowed at {child_path}")
            if normalized_key in _AUTHENTICATED_DEVHUB_KEYS and child not in (None, "", [], {}):
                problems.append(f"authenticated DevHub value is not allowed at {child_path}")
            if normalized_key in _RAW_ARTIFACT_KEYS and child not in (None, "", [], {}):
                problems.append(f"raw document/session/browser artifact is not allowed at {child_path}")
            if normalized_key in _MUTATION_FLAG_KEYS and child not in (False, None, "", [], {}):
                problems.append(f"active mutation flag is not allowed at {child_path}")
            if normalized_key in {"next_action_class", "action_class"} and isinstance(child, str) and child not in ALLOWED_NEXT_ACTION_CLASSES:
                problems.append(f"unsupported next-action class is not allowed at {child_path}: {child}")
            if normalized_key in {"local_path", "path", "file_path"} and _contains_local_path(child):
                problems.append(f"private local path is not allowed at {child_path}")
            problems.extend(_unsafe_value_problems(child, child_path, normalized_key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            problems.extend(_unsafe_value_problems(child, f"{path}[{index}]", key_name))
    elif isinstance(value, str):
        if _LOCAL_PATH_RE.search(value) and key_name in {"local_path", "path", "file_path"}:
            problems.append(f"private local path is not allowed at {path}")
        if _LIVE_COMPLETION_CLAIM_RE.search(value):
            problems.append(f"live LLM or DevHub completion claim is not allowed at {path}")
        if _OUTCOME_GUARANTEE_RE.search(value):
            problems.append(f"legal or permitting outcome guarantee is not allowed at {path}")
        if _FINAL_ACTION_LANGUAGE_RE.search(value):
            problems.append(f"final submission/payment/upload/scheduling/cancellation language is not allowed at {path}")
    return problems


def _consumed_refs(packet: Mapping[str, Any]) -> set[str]:
    consumes = packet.get("consumes")
    if isinstance(consumes, Mapping):
        return {item for item in consumes.values() if isinstance(item, str) and item}
    return set()


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _contains_local_path(value: Any) -> bool:
    if isinstance(value, str):
        return bool(_LOCAL_PATH_RE.search(value))
    if isinstance(value, list):
        return any(_contains_local_path(item) for item in value)
    if isinstance(value, Mapping):
        return any(_contains_local_path(item) for item in value.values())
    return False
