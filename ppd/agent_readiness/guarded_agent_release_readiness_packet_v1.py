"""Fixture-first guarded agent release readiness packet v1.

This module consumes committed offline fixture packets and produces an
agent-facing release readiness packet. It does not update prompts, active
guardrails, agent state, release state, live sources, DevHub artifacts, or any
private browser/session material.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PACKET_TYPE = "ppd.guarded_agent_release_readiness_packet.v1"
VALIDATION_COMMAND = ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]
REQUIRED_INPUTS = (
    "release_promotion_decision_packet_v1",
    "public_source_refresh_plan_v2",
    "devhub_observed_surface_update_plan_v2",
    "user_gap_analysis_impact_proposal_v1",
    "agent_response_delta_proposal_v1",
)
MUTATION_FLAGS = (
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_user_gap_mutation",
    "active_release_state_mutation",
    "active_fixture_mutation",
    "active_agent_state_mutation",
    "active_source_mutation",
    "active_document_mutation",
    "active_requirement_mutation",
    "active_devhub_artifact_mutation",
)
REQUIRED_EXPECTATION_TYPES = {
    "missing-information expectation",
    "refusal expectation",
    "next-safe-action expectation",
}
PRIVATE_OR_AUTHENTICATED_TERMS = (
    "auth_state",
    "authenticated artifact",
    "authenticated browser",
    "authenticated session",
    "browser artifact",
    "browser_profile",
    "cookie",
    "credential",
    "devhub session",
    "har file",
    "local private file",
    "mfa token",
    "password",
    "payment detail",
    "private artifact",
    "private devhub",
    "session artifact",
    "storage_state",
    "trace.zip",
)
RAW_ARTIFACT_TERMS = (
    "downloaded data",
    "downloaded document",
    "downloaded file",
    "downloaded pdf",
    "raw crawl",
    "raw downloaded",
    "raw html",
    "raw pdf",
    "raw response body",
)
FORBIDDEN_TEXT_GROUPS = (
    ("private_or_authenticated_artifact", PRIVATE_OR_AUTHENTICATED_TERMS),
    ("raw_crawl_pdf_or_downloaded_data", RAW_ARTIFACT_TERMS),
)
LIVE_EXECUTION_PATTERNS = (
    re.compile(r"\b(live|production)\s+(crawl|execution|run|refresh|processor|devhub|browser|automation)\s+(completed|executed|ran|started|succeeded)\b"),
    re.compile(r"\b(executed|ran|started|completed)\s+(a\s+)?(live|production)\s+(crawl|run|refresh|processor|devhub|browser|automation)\b"),
)
PROMOTION_CLAIM_PATTERNS = (
    re.compile(r"\b(promoted|released|deployed)\s+(to\s+)?(live|production|active|consumer)\b"),
    re.compile(r"\b(active|production|consumer)\s+(release|promotion)\s+(is\s+)?(complete|done|approved|live)\b"),
)
LEGAL_GUARANTEE_PATTERNS = (
    re.compile(r"\b(permit|application|inspection|plan review|approval)\s+(will|shall|is guaranteed to)\s+(be\s+)?(approved|accepted|issued|pass)\b"),
    re.compile(r"\bguarantee(s|d)?\s+(approval|issuance|acceptance|compliance|permit outcome|legal outcome)\b"),
    re.compile(r"\blegally\s+(valid|sufficient|compliant|approved)\b"),
)
CONSEQUENTIAL_ACTION_PATTERNS = (
    re.compile(r"\b(i|we|agent|system)\s+(will|can|may|should|must)\s+(submit|upload|pay|certify|schedule|cancel|approve|issue|promote|release)\b"),
    re.compile(r"\b(submit|upload|pay|certify|schedule|cancel)\s+(the\s+)?(permit|application|plans|correction|inspection|payment|fee)\b"),
)
SAFE_REFUSAL_MARKERS = ("cannot", "do not", "must not", "stop before", "refuse", "blocked", "without touching")


class GuardedAgentReleaseReadinessPacketV1Error(ValueError):
    """Raised when fixture inputs cannot produce a safe readiness packet."""

    def __init__(self, errors: Iterable[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("invalid guarded agent release readiness packet v1: " + "; ".join(self.errors))


def load_guarded_agent_release_readiness_fixture(path: str | Path) -> dict[str, Any]:
    """Load a committed fixture bundle and build the readiness packet."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise GuardedAgentReleaseReadinessPacketV1Error(["fixture bundle must be a JSON object"])
    missing = [name for name in REQUIRED_INPUTS if name not in payload]
    if missing:
        raise GuardedAgentReleaseReadinessPacketV1Error([f"missing fixture input: {name}" for name in missing])
    return build_guarded_agent_release_readiness_packet_v1(
        release_promotion_decision_packet_v1=_mapping(payload, "release_promotion_decision_packet_v1"),
        public_source_refresh_plan_v2=_mapping(payload, "public_source_refresh_plan_v2"),
        devhub_observed_surface_update_plan_v2=_mapping(payload, "devhub_observed_surface_update_plan_v2"),
        user_gap_analysis_impact_proposal_v1=_mapping(payload, "user_gap_analysis_impact_proposal_v1"),
        agent_response_delta_proposal_v1=_mapping(payload, "agent_response_delta_proposal_v1"),
    )


def build_guarded_agent_release_readiness_packet_v1(
    *,
    release_promotion_decision_packet_v1: Mapping[str, Any],
    public_source_refresh_plan_v2: Mapping[str, Any],
    devhub_observed_surface_update_plan_v2: Mapping[str, Any],
    user_gap_analysis_impact_proposal_v1: Mapping[str, Any],
    agent_response_delta_proposal_v1: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a cited, metadata-only readiness packet from offline inputs."""

    release = deepcopy(dict(release_promotion_decision_packet_v1))
    source_refresh = deepcopy(dict(public_source_refresh_plan_v2))
    surface_update = deepcopy(dict(devhub_observed_surface_update_plan_v2))
    gap_impact = deepcopy(dict(user_gap_analysis_impact_proposal_v1))
    response_delta = deepcopy(dict(agent_response_delta_proposal_v1))

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_version": "v1",
        "fixture_first": True,
        "metadata_only": True,
        "consumed_input_packet_refs": _input_refs(release, source_refresh, surface_update, gap_impact, response_delta),
        "attestations": {
            "no_prompt_changes": True,
            "no_active_guardrail_changes": True,
            "no_process_changes": True,
            "no_user_gap_changes": True,
            "no_agent_state_changes": True,
            "no_release_state_changes": True,
            "no_fixture_changes": True,
            "no_live_source_refresh": True,
            "no_devhub_artifact_changes": True,
        },
        "agent_facing_readiness_rows": _agent_readiness_rows(release, source_refresh, surface_update, response_delta),
        "expectation_rows": _expectation_rows(gap_impact, response_delta),
        "release_blockers": _release_blockers(release, gap_impact, response_delta),
        "validation_replay_commands": [VALIDATION_COMMAND],
        "rollback_checkpoints": _rollback_checkpoints(release),
        "human_handoff_notes": _handoff_notes(release, source_refresh, surface_update, gap_impact),
        "active_prompt_mutation": False,
        "active_guardrail_mutation": False,
        "active_process_mutation": False,
        "active_user_gap_mutation": False,
        "active_release_state_mutation": False,
        "active_fixture_mutation": False,
        "active_agent_state_mutation": False,
        "active_source_mutation": False,
        "active_document_mutation": False,
        "active_requirement_mutation": False,
        "active_devhub_artifact_mutation": False,
    }

    errors = validate_guarded_agent_release_readiness_packet_v1(packet)
    if errors:
        raise GuardedAgentReleaseReadinessPacketV1Error(errors)
    return packet


def validate_guarded_agent_release_readiness_packet_v1(packet: Mapping[str, Any]) -> list[str]:
    """Return deterministic validation errors for a readiness packet."""

    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be ppd.guarded_agent_release_readiness_packet.v1")
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if packet.get("metadata_only") is not True:
        errors.append("metadata_only must be true")
    for flag in MUTATION_FLAGS:
        if packet.get(flag) is not False:
            errors.append(f"{flag} must be false")

    _validate_cited_rows(packet, errors)
    _validate_expectation_coverage(packet, errors)
    _validate_validation_replay_commands(packet, errors)
    _validate_text_boundaries(packet, errors)
    return errors


def _validate_cited_rows(packet: Mapping[str, Any], errors: list[str]) -> None:
    for row_key in (
        "agent_facing_readiness_rows",
        "expectation_rows",
        "release_blockers",
        "rollback_checkpoints",
        "human_handoff_notes",
    ):
        rows = packet.get(row_key)
        if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
            errors.append(f"{row_key} must be a non-empty list")
            continue
        for index, row in enumerate(rows):
            if not isinstance(row, Mapping):
                errors.append(f"{row_key}[{index}] must be an object")
                continue
            if not _string_list(row.get("citations")):
                errors.append(f"{row_key}[{index}].citations must be non-empty")


def _validate_expectation_coverage(packet: Mapping[str, Any], errors: list[str]) -> None:
    rows = packet.get("expectation_rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        return
    observed = {row.get("expectation_type") for row in rows if isinstance(row, Mapping)}
    for expectation_type in sorted(REQUIRED_EXPECTATION_TYPES - observed):
        errors.append(f"expectation_rows missing {expectation_type}")


def _validate_validation_replay_commands(packet: Mapping[str, Any], errors: list[str]) -> None:
    commands = packet.get("validation_replay_commands")
    if commands != [VALIDATION_COMMAND]:
        errors.append("validation_replay_commands must contain only the PP&D daemon self-test command")
    checkpoints = packet.get("rollback_checkpoints")
    if isinstance(checkpoints, Sequence) and not isinstance(checkpoints, (str, bytes)):
        for index, checkpoint in enumerate(checkpoints):
            if isinstance(checkpoint, Mapping) and checkpoint.get("verification_command") != VALIDATION_COMMAND:
                errors.append(f"rollback_checkpoints[{index}].verification_command must be the PP&D daemon self-test command")


def _validate_text_boundaries(packet: Mapping[str, Any], errors: list[str]) -> None:
    for path, value in _walk(packet):
        if not isinstance(value, str):
            continue
        text = value.lower()
        for code, terms in FORBIDDEN_TEXT_GROUPS:
            if any(term in text for term in terms):
                errors.append(f"forbidden {code} text at {path}")
        if _matches_any(text, LIVE_EXECUTION_PATTERNS):
            errors.append(f"forbidden live execution claim at {path}")
        if _matches_any(text, PROMOTION_CLAIM_PATTERNS):
            errors.append(f"forbidden live promotion claim at {path}")
        if _matches_any(text, LEGAL_GUARANTEE_PATTERNS):
            errors.append(f"forbidden legal or permitting outcome guarantee at {path}")
        if _matches_any(text, CONSEQUENТIAL_ACTION_PATTERNS) and not _is_safe_refusal_context(text):
            errors.append(f"forbidden consequential action language at {path}")


def _matches_any(text: str, patterns: Sequence[re.Pattern[str]]) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def _is_safe_refusal_context(text: str) -> bool:
    return any(marker in text for marker in SAFE_REFUSAL_MARKERS)


def _input_refs(
    release: Mapping[str, Any],
    source_refresh: Mapping[str, Any],
    surface_update: Mapping[str, Any],
    gap_impact: Mapping[str, Any],
    response_delta: Mapping[str, Any],
) -> dict[str, str]:
    return {
        "release_promotion_decision_packet_v1": _text(release.get("packet_id") or release.get("packet_version")),
        "public_source_refresh_plan_v2": _text(source_refresh.get("packet_id") or source_refresh.get("schema_version")),
        "devhub_observed_surface_update_plan_v2": _text(surface_update.get("packet_id") or "devhub_observed_surface_update_plan_v2"),
        "user_gap_analysis_impact_proposal_v1": _text(gap_impact.get("proposal_id")),
        "agent_response_delta_proposal_v1": _text(response_delta.get("packet_type") or response_delta.get("proposal_id")),
    }


def _agent_readiness_rows(
    release: Mapping[str, Any],
    source_refresh: Mapping[str, Any],
    surface_update: Mapping[str, Any],
    response_delta: Mapping[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, decision in enumerate(_sequence(release.get("decision_rows"))):
        if isinstance(decision, Mapping):
            rows.append(
                {
                    "row_id": f"release-decision-{index + 1}",
                    "readiness_signal": _text(decision.get("decision") or "release decision reviewed"),
                    "agent_facing_use": "Use this only as offline readiness evidence; do not treat it as release-state mutation.",
                    "citations": _citations(decision),
                }
            )
    for trace in _sequence(source_refresh.get("traceability_rows")):
        if isinstance(trace, Mapping):
            rows.append(
                {
                    "row_id": _text(trace.get("trace_id")),
                    "readiness_signal": "Public source refresh trace is linked to process and guardrail ids.",
                    "agent_facing_use": "Cite these ids when explaining public-source-backed requirements.",
                    "citations": _citations(trace),
                }
            )
    observed = _sequence(_nested(surface_update, "source_packets", "devhub_observation_evidence_intake_packet_v1", "observed_surfaces"))
    for surface in observed:
        if isinstance(surface, Mapping):
            rows.append(
                {
                    "row_id": _text(surface.get("surface_id")),
                    "readiness_signal": "Observed DevHub surface metadata is reviewer-owned and redacted.",
                    "agent_facing_use": "Use only for read-only orientation and stop before official controls.",
                    "citations": _citations(surface),
                }
            )
    for example in _sequence(response_delta.get("final_response_examples")):
        if isinstance(example, Mapping):
            rows.append(
                {
                    "row_id": _text(example.get("example_kind")),
                    "readiness_signal": "Agent response delta has a cited example for this response kind.",
                    "agent_facing_use": _text(example.get("final_response")),
                    "citations": _citations(example),
                }
            )
    return rows


def _expectation_rows(gap_impact: Mapping[str, Any], response_delta: Mapping[str, Any]) -> list[dict[str, Any]]:
    category_to_expectation = {
        "required_user_facts": "missing-information expectation",
        "missing_documents": "missing-information expectation",
        "stale_or_conflicting_evidence": "missing-information expectation",
        "required_confirmations": "next-safe-action expectation",
        "blocked_actions": "refusal expectation",
        "next_safe_actions": "next-safe-action expectation",
    }
    rows: list[dict[str, Any]] = []
    for impact in _sequence(gap_impact.get("proposed_impacts")):
        if not isinstance(impact, Mapping):
            continue
        category = _text(impact.get("category"))
        rows.append(
            {
                "row_id": _text(impact.get("impact_id")),
                "expectation_type": category_to_expectation.get(category, "agent expectation"),
                "expected_agent_behavior": _expectation_text(category),
                "citations": _citations(impact),
            }
        )
    for example in _sequence(response_delta.get("final_response_examples")):
        if isinstance(example, Mapping):
            rows.append(
                {
                    "row_id": f"response-delta-{_text(example.get('example_kind'))}",
                    "expectation_type": _response_expectation_type(_text(example.get("example_kind"))),
                    "expected_agent_behavior": _text(example.get("final_response")),
                    "citations": _citations(example),
                }
            )
    return rows


def _release_blockers(release: Mapping[str, Any], gap_impact: Mapping[str, Any], response_delta: Mapping[str, Any]) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    for blocker in _sequence(release.get("release_blockers")):
        if isinstance(blocker, Mapping):
            blockers.append(
                {
                    "blocker_id": _text(blocker.get("blocker_id") or blocker.get("id")),
                    "blocked_release_area": _text(blocker.get("blocked_release_area") or blocker.get("area") or "offline release readiness"),
                    "reason": _text(blocker.get("reason") or blocker.get("blocker") or "manual review required"),
                    "citations": _citations(blocker),
                }
            )
    for impact in _sequence(gap_impact.get("proposed_impacts")):
        if isinstance(impact, Mapping) and impact.get("category") == "blocked_actions":
            blockers.append(
                {
                    "blocker_id": _text(impact.get("impact_id")),
                    "blocked_release_area": "official agent actions",
                    "reason": "Agent must refuse official submission, certification, payment, scheduling, cancellation, and official attachment actions.",
                    "citations": _citations(impact),
                }
            )
    for example in _sequence(response_delta.get("final_response_examples")):
        if isinstance(example, Mapping) and example.get("example_kind") == "blocked_official_actions":
            blockers.append(
                {
                    "blocker_id": "agent-response-blocked-official-actions",
                    "blocked_release_area": "agent response behavior",
                    "reason": _text(example.get("final_response")),
                    "citations": _citations(example),
                }
            )
    return blockers


def _rollback_checkpoints(release: Mapping[str, Any]) -> list[dict[str, Any]]:
    checkpoints = []
    for checkpoint in _sequence(release.get("rollback_checkpoints")):
        if isinstance(checkpoint, Mapping):
            checkpoints.append(
                {
                    "checkpoint_id": _text(checkpoint.get("checkpoint_id")),
                    "rollback_action": "Keep current prompts, guardrails, fixtures, source indexes, and release state unchanged.",
                    "verification_command": VALIDATION_COMMAND,
                    "citations": _citations(checkpoint) or ["release:rollback-checkpoint"],
                }
            )
    if checkpoints:
        return checkpoints
    return [
        {
            "checkpoint_id": "fixture-first-readiness-no-mutation",
            "rollback_action": "Discard the generated readiness packet and leave all active PP&D state unchanged.",
            "verification_command": VALIDATION_COMMAND,
            "citations": ["release:fixture-first-readiness-boundary"],
        }
    ]


def _handoff_notes(
    release: Mapping[str, Any],
    source_refresh: Mapping[str, Any],
    surface_update: Mapping[str, Any],
    gap_impact: Mapping[str, Any],
) -> list[dict[str, Any]]:
    owner = _text(_nested(surface_update, "reviewer_owner_assignments", "trade-permit-dashboard") or "PP&D release reviewer")
    return [
        {
            "note_id": "human-review-release-scope",
            "handoff_to": "release supervisor",
            "note": _text(_nested(release, "release_scope", "boundary_statement") or "Confirm offline readiness only before any release promotion."),
            "citations": ["release:scope-boundary"],
        },
        {
            "note_id": "human-review-public-source-refresh",
            "handoff_to": "public source reviewer",
            "note": "Review cited public source traceability before enabling any later live refresh plan.",
            "citations": _first_row_citations(source_refresh.get("traceability_rows"), "public-source:traceability"),
        },
        {
            "note_id": "human-review-devhub-surface",
            "handoff_to": owner,
            "note": "Review redacted observed surface rows by citation and keep attended DevHub work separate.",
            "citations": ["devhub:observed-surface-update-plan-v2"],
        },
        {
            "note_id": "human-review-gap-impact",
            "handoff_to": "agent readiness reviewer",
            "note": "Confirm missing-information, refusal, and next-safe-action expectations before consumer release.",
            "citations": _first_row_citations(gap_impact.get("proposed_impacts"), "gap-analysis:impact-proposal"),
        },
    ]


def _expectation_text(category: str) -> str:
    if category in {"required_user_facts", "missing_documents", "stale_or_conflicting_evidence"}:
        return "Ask for missing, stale, ambiguous, or conflicting information before drafting or relying on the fact."
    if category == "blocked_actions":
        return "Refuse consequential official actions and explain the attended confirmation boundary."
    if category in {"required_confirmations", "next_safe_actions"}:
        return "Offer only read-only review or reversible local drafting as the next safe action."
    return "Keep the response cited, offline, and within fixture-first readiness scope."


def _response_expectation_type(example_kind: str) -> str:
    if example_kind in {"missing_facts", "stale_conflicting_evidence"}:
        return "missing-information expectation"
    if example_kind == "blocked_official_actions":
        return "refusal expectation"
    return "next-safe-action expectation"


def _mapping(source: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = source.get(key)
    if not isinstance(value, Mapping):
        raise GuardedAgentReleaseReadinessPacketV1Error([f"{key} must be an object"])
    return value


def _nested(source: Mapping[str, Any], *keys: str) -> Any:
    value: Any = source
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return value
    return ()


def _citations(row: Mapping[str, Any]) -> list[str]:
    value = row.get("citations", row.get("source_evidence_ids"))
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    citations: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            citations.append(item.strip())
        elif isinstance(item, Mapping):
            packet = _text(item.get("packet"))
            pointer = _text(item.get("pointer"))
            if packet and pointer:
                citations.append(f"{packet}:{pointer}")
    return citations


def _first_row_citations(rows: Any, fallback: str) -> list[str]:
    for row in _sequence(rows):
        if isinstance(row, Mapping):
            citations = _citations(row)
            if citations:
                return citations
    return [fallback]


def _string_list(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and bool(value) and all(isinstance(item, str) and bool(item.strip()) for item in value)


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _walk(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")
    else:
        yield path, value
