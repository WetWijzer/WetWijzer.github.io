from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.agent_readiness_replay_packet.v2"

_REQUIRED_ATTESTATIONS = {
    "fixture_first",
    "no_live_llm",
    "no_devhub",
    "no_user_data",
    "no_official_action",
    "no_prompt_mutation",
    "no_guardrail_mutation",
    "no_source_mutation",
    "no_surface_registry_mutation",
    "no_release_state_mutation",
    "no_agent_state_mutation",
}

_ALLOWED_NEXT_ACTION_CLASSES = {"read_only", "reversible_draft", "local_preview", "manual_handoff"}

_PRIVATE_VALUE_KEYS = {
    "known_facts",
    "user_input",
    "user_fact",
    "user_facts",
    "private_fact",
    "private_facts",
    "private_values",
    "authenticated_values",
    "devhub_values",
    "devhub_authenticated_values",
    "session_state",
    "auth_state",
    "cookies",
    "credential",
    "credentials",
    "password",
    "token",
    "payment_details",
    "browser_context",
    "raw_document",
    "raw_documents",
    "raw_pdf",
    "raw_html",
    "trace",
    "traces",
    "har",
    "screenshot",
    "screenshots",
}

_ACTIVE_MUTATION_KEYS = {
    "active_prompt_mutation",
    "prompt_mutation_active",
    "mutates_prompt",
    "active_guardrail_mutation",
    "guardrail_mutation_active",
    "mutates_guardrails",
    "active_source_mutation",
    "source_mutation_active",
    "mutates_sources",
    "active_surface_registry_mutation",
    "surface_registry_mutation_active",
    "mutates_surface_registry",
    "active_release_state_mutation",
    "release_state_mutation_active",
    "mutates_release_state",
    "active_agent_state_mutation",
    "agent_state_mutation_active",
    "mutates_agent_state",
}

_FORBIDDEN_TEXT_PATTERNS = (
    re.compile(r"\b(?:private user fact|known user fact|user supplied value|private address|private file path|authenticated value|authenticated devhub value)\b", re.IGNORECASE),
    re.compile(r"\b(?:cookie|session state|auth state|bearer token|password|credential|mfa|captcha)\b", re.IGNORECASE),
    re.compile(r"\b(?:raw document|raw pdf|raw html|raw crawl|downloaded document|browser artifact|screenshot|trace file|har file|playwright trace)\b", re.IGNORECASE),
    re.compile(r"\b(?:live llm|llm completed|live completion|called the model|opened devhub|clicked devhub|devhub completed|devhub session|browser completed)\b", re.IGNORECASE),
    re.compile(r"\b(?:permit will be approved|approval guaranteed|guarantees approval|legally sufficient|legal advice|compliance guaranteed|inspection will pass)\b", re.IGNORECASE),
    re.compile(r"\b(?:final submit|final submission|submitted the application|submit application|submit payment|paid the fee|upload to devhub|uploaded corrections|schedule inspection|scheduled inspection|cancel permit|cancelled permit|canceled permit)\b", re.IGNORECASE),
    re.compile(r"\b(?:active prompt|active guardrail|active source|active surface[-_ ]registry|active release[-_ ]state|active agent[-_ ]state)\b.{0,80}\b(?:mutat|write|patch|promot|replace|update)", re.IGNORECASE),
    re.compile(r"\b(?:mutat|write|patch|promot|replace|update)\b.{0,80}\b(?:active prompt|active guardrail|active source|active surface[-_ ]registry|active release[-_ ]state|active agent[-_ ]state)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class ReplayPacketV2ValidationResult:
    valid: bool
    problems: tuple[str, ...]


def load_json_fixture(path: str | Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("fixture must be a JSON object")
    return raw


def build_agent_readiness_replay_packet_v2(source_packets: Mapping[str, Any]) -> dict[str, Any]:
    proposal = _mapping(source_packets.get("refresh_implementation_proposal_v2"))
    gap = _mapping(source_packets.get("user_gap_analysis_fixture"))
    guardrail = _mapping(source_packets.get("guardrail_bundle_fixture"))

    proposal_evidence = _string_list(proposal.get("source_evidence_ids"))
    gap_evidence = _string_list(gap.get("source_evidence_ids"))
    guardrail_evidence = _string_list(guardrail.get("source_evidence_ids"))
    source_evidence_ids = sorted(set(proposal_evidence + gap_evidence + guardrail_evidence))

    missing_fact_prompts = [
        {
            "prompt_id": f"missing-fact-{index + 1}",
            "fact_id": _text(item.get("fact_id"), f"missing_fact_{index + 1}"),
            "prompt": _text(item.get("expected_prompt"), f"Ask for {_text(item.get('fact_id'), 'the missing fact')} before draft readiness."),
            "source_evidence_ids": _string_list(item.get("source_evidence_ids")) or gap_evidence,
        }
        for index, item in enumerate(_mapping_sequence(gap.get("missing_facts")))
    ]

    stale_notices = [
        {
            "notice_id": f"stale-evidence-{index + 1}",
            "evidence_id": _text(item.get("evidence_id"), f"stale_evidence_{index + 1}"),
            "notice": _text(item.get("notice"), "Evidence is stale and needs cited review before relying on it."),
            "source_evidence_ids": _string_list(item.get("source_evidence_ids")) or gap_evidence,
        }
        for index, item in enumerate(_mapping_sequence(gap.get("stale_evidence")))
    ]
    conflicting_notices = [
        {
            "notice_id": f"conflicting-evidence-{index + 1}",
            "conflict_id": _text(item.get("conflict_id"), f"conflict_{index + 1}"),
            "notice": _text(item.get("notice"), "Evidence conflicts and needs reviewer reconciliation before draft readiness."),
            "source_evidence_ids": _string_list(item.get("source_evidence_ids")) or gap_evidence,
        }
        for index, item in enumerate(_mapping_sequence(gap.get("conflicting_evidence")))
    ]

    blocked_action_explanations = [
        {
            "action_id": _text(item.get("action_id"), f"blocked_action_{index + 1}"),
            "action_class": _text(item.get("action_class"), "official_record_change"),
            "explanation": _text(item.get("explanation"), "Blocked: fixture replay can only prepare read-only review or reversible local drafts."),
            "source_evidence_ids": _string_list(item.get("source_evidence_ids")) or guardrail_evidence,
        }
        for index, item in enumerate(_mapping_sequence(guardrail.get("blocked_actions")))
    ]

    return {
        "packet_type": PACKET_TYPE,
        "packet_id": _text(proposal.get("packet_id"), "fixture-agent-readiness-replay-v2"),
        "fixture_only": True,
        "replay_mode": "offline_fixture_first_agent_readiness_replay_v2",
        "input_packet_ids": {
            "refresh_implementation_proposal_v2": _text(proposal.get("packet_id"), "missing-refresh-proposal"),
            "user_gap_analysis_fixture": _text(gap.get("fixture_id"), "missing-gap-fixture"),
            "guardrail_bundle_fixture": _text(guardrail.get("guardrail_bundle_id"), "missing-guardrail-fixture"),
        },
        "source_evidence_ids": source_evidence_ids,
        "expected_missing_fact_prompts": missing_fact_prompts,
        "stale_evidence_notices": stale_notices,
        "conflicting_evidence_notices": conflicting_notices,
        "blocked_action_explanations": blocked_action_explanations,
        "next_safe_actions": [
            {
                "action_id": _text(item.get("action_id"), f"safe_action_{index + 1}"),
                "action_class": _text(item.get("action_class"), "read_only"),
                "description": _text(item.get("description"), "Perform a cited read-only review or reversible local draft step."),
                "source_evidence_ids": _string_list(item.get("source_evidence_ids")) or source_evidence_ids,
            }
            for index, item in enumerate(_mapping_sequence(gap.get("next_safe_actions")))
        ],
        "reviewer_owner_fields": [
            {
                "field_id": "agent-readiness-reviewer",
                "owner": _text(proposal.get("owner"), "PP&D task supervisor"),
                "reviewer_owner": _text(proposal.get("reviewer_owner"), "PP&D agent readiness reviewer"),
                "review_status": "pending_human_review",
                "source_evidence_ids": source_evidence_ids,
            }
        ],
        "offline_validation_commands": [
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
            ["python3", "-m", "unittest", "ppd.tests.test_agent_readiness_replay_packet_v2"],
        ],
        "attestations": {
            "fixture_first": True,
            "no_live_llm": True,
            "no_devhub": True,
            "no_user_data": True,
            "no_official_action": True,
            "no_prompt_mutation": True,
            "no_guardrail_mutation": True,
            "no_source_mutation": True,
            "no_surface_registry_mutation": True,
            "no_release_state_mutation": True,
            "no_agent_state_mutation": True,
        },
    }


def build_agent_readiness_replay_packet_v2_from_fixture(path: str | Path) -> dict[str, Any]:
    return build_agent_readiness_replay_packet_v2(load_json_fixture(path))


def validate_agent_readiness_replay_packet_v2(packet: Mapping[str, Any]) -> ReplayPacketV2ValidationResult:
    problems: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("fixture_only") is not True:
        problems.append("fixture_only must be true")
    evidence_ids = set(_string_list(packet.get("source_evidence_ids")))
    if not evidence_ids:
        problems.append("source_evidence_ids must be non-empty")
    _validate_input_references(problems, packet, evidence_ids)
    for field in (
        "expected_missing_fact_prompts",
        "stale_evidence_notices",
        "conflicting_evidence_notices",
        "blocked_action_explanations",
        "next_safe_actions",
        "reviewer_owner_fields",
        "offline_validation_commands",
    ):
        if not _sequence(packet.get(field)):
            problems.append(f"{field} must be non-empty")
    attestations = _mapping(packet.get("attestations"))
    for key in sorted(_REQUIRED_ATTESTATIONS):
        if attestations.get(key) is not True:
            problems.append(f"attestations.{key} must be true")
    _validate_cited_items(problems, packet)
    _validate_next_action_classes(problems, packet)
    _validate_text_policy(problems, packet)
    return ReplayPacketV2ValidationResult(not problems, tuple(problems))


def assert_valid_agent_readiness_replay_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_agent_readiness_replay_packet_v2(packet)
    if not result.valid:
        raise ValueError("invalid agent readiness replay packet v2: " + "; ".join(result.problems))


def _validate_input_references(problems: list[str], packet: Mapping[str, Any], evidence_ids: set[str]) -> None:
    input_packet_ids = _mapping(packet.get("input_packet_ids"))
    if not _text(input_packet_ids.get("user_gap_analysis_fixture")) or _text(input_packet_ids.get("user_gap_analysis_fixture")).startswith("missing-"):
        problems.append("input_packet_ids.user_gap_analysis_fixture must reference a gap-analysis fixture")
    if not _text(input_packet_ids.get("guardrail_bundle_fixture")) or _text(input_packet_ids.get("guardrail_bundle_fixture")).startswith("missing-"):
        problems.append("input_packet_ids.guardrail_bundle_fixture must reference a guardrail bundle fixture")
    if not any(evidence_id.startswith("gap-analysis") or ":gap" in evidence_id for evidence_id in evidence_ids):
        problems.append("source_evidence_ids must include gap-analysis evidence")
    if not any(evidence_id.startswith("guardrail") or ":guardrail" in evidence_id for evidence_id in evidence_ids):
        problems.append("source_evidence_ids must include guardrail evidence")


def _validate_cited_items(problems: list[str], packet: Mapping[str, Any]) -> None:
    evidence_ids = set(_string_list(packet.get("source_evidence_ids")))
    for field in (
        "expected_missing_fact_prompts",
        "stale_evidence_notices",
        "conflicting_evidence_notices",
        "blocked_action_explanations",
        "next_safe_actions",
        "reviewer_owner_fields",
    ):
        for index, item in enumerate(_mapping_sequence(packet.get(field))):
            citations = _string_list(item.get("source_evidence_ids"))
            if not citations:
                problems.append(f"{field}[{index}].source_evidence_ids must cite fixture evidence")
            for citation in citations:
                if evidence_ids and citation not in evidence_ids:
                    problems.append(f"{field}[{index}].source_evidence_ids cites unknown evidence id {citation}")
            if field in {"expected_missing_fact_prompts", "stale_evidence_notices", "conflicting_evidence_notices"} and citations:
                if not any(citation.startswith("gap-analysis") or ":gap" in citation for citation in citations):
                    problems.append(f"{field}[{index}].source_evidence_ids must cite gap-analysis evidence")
            if field == "blocked_action_explanations" and citations:
                if not any(citation.startswith("guardrail") or ":guardrail" in citation for citation in citations):
                    problems.append(f"{field}[{index}].source_evidence_ids must cite guardrail evidence")


def _validate_next_action_classes(problems: list[str], packet: Mapping[str, Any]) -> None:
    for index, item in enumerate(_mapping_sequence(packet.get("next_safe_actions"))):
        action_class = _text(item.get("action_class"))
        if action_class not in _ALLOWED_NEXT_ACTION_CLASSES:
            problems.append(f"next_safe_actions[{index}].action_class must be one of {sorted(_ALLOWED_NEXT_ACTION_CLASSES)}")


def _validate_text_policy(problems: list[str], value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in _PRIVATE_VALUE_KEYS and child not in (None, "", [], {}):
                problems.append(f"{path}.{key} must not include private user facts, authenticated values, or raw session/browser artifacts")
            if normalized in _ACTIVE_MUTATION_KEYS and child not in (None, False, "", [], {}):
                problems.append(f"{path}.{key} must not declare active prompt, guardrail, source, surface-registry, release-state, or agent-state mutation")
            _validate_text_policy(problems, child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _validate_text_policy(problems, child, f"{path}[{index}]")
    elif isinstance(value, str):
        for pattern in _FORBIDDEN_TEXT_PATTERNS:
            if pattern.search(value):
                problems.append(f"{path} contains forbidden replay-packet safety language")
                break


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    return value if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) else ()


def _mapping_sequence(value: Any) -> tuple[Mapping[str, Any], ...]:
    return tuple(item for item in _sequence(value) if isinstance(item, Mapping))


def _string_list(value: Any) -> list[str]:
    return [item for item in _sequence(value) if isinstance(item, str) and item]


def _text(value: Any, fallback: str = "") -> str:
    return value if isinstance(value, str) and value else fallback
