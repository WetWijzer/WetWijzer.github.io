"""Fixture-first offline release rehearsal gate v2.

Consumes inactive promotion candidate packet v2, guardrail impact replay plan v2,
and guarded agent readiness delta packet v2 fixtures. The builder emits ordered
release gate checks and placeholders only; it does not promote artifacts, contact
live services, open DevHub, store private artifacts, or perform official actions.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.offline_release_rehearsal_gate.v2"
PACKET_VERSION = "v2"
EXACT_OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/agent_readiness/offline_release_rehearsal_gate_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_offline_release_rehearsal_gate_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_REQUIRED_ATTESTATIONS = {
    "fixture_first": True,
    "offline_only": True,
    "consumes_inactive_promotion_candidate_packet_v2": True,
    "consumes_guardrail_impact_replay_plan_v2": True,
    "consumes_guarded_agent_readiness_delta_packet_v2": True,
    "active_promotion_applied": False,
    "live_network_access": False,
    "devhub_opened": False,
    "private_artifacts_stored": False,
    "official_action_performed": False,
    "release_state_changed": False,
}

_FORBIDDEN_KEY_TOKENS = (
    "auth",
    "browser_state",
    "captcha",
    "cookie",
    "credential",
    "downloaded",
    "har",
    "mfa",
    "password",
    "payment",
    "private",
    "raw",
    "screenshot",
    "secret",
    "session",
    "storage_state",
    "token",
    "trace",
    "warc",
)

_MUTATION_KEYS = {
    "active_promotion_applied",
    "active_artifact_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "fixture_mutation",
    "release_state_changed",
}

_FORBIDDEN_TEXT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/tmp/)|"
    r"(auth state|browser state|cookie|credential|downloaded document|har file|password|private artifact|raw crawl|raw html|screenshot|session state|storage state|token|trace.zip|warc)|"
    r"\b(live crawl|live network|live devhub|opened devhub|active promotion applied|release state changed|release complete)\b|"
    r"\b(approval guaranteed|guaranteed approval|legal advice|legal guarantee|permit will be approved|permit guaranteed)\b|"
    r"\b(pay fees|purchase permit|submit permit|submit payment|schedule inspection|cancel request|certify acknowledgement|upload corrections)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class OfflineReleaseRehearsalGateV2ValidationResult:
    valid: bool
    problems: tuple[str, ...]


class OfflineReleaseRehearsalGateV2Error(ValueError):
    def __init__(self, problems: Iterable[str]) -> None:
        self.problems = tuple(problems)
        super().__init__("invalid offline release rehearsal gate v2: " + "; ".join(self.problems))


def load_offline_release_rehearsal_gate_v2_fixture(path: str | Path) -> dict[str, Any]:
    source = _load_json(path)
    if {
        "inactive_promotion_candidate_packet_v2",
        "guardrail_impact_replay_plan_v2",
        "guarded_agent_readiness_delta_packet_v2",
    }.issubset(source):
        packet = build_offline_release_rehearsal_gate_v2(
            inactive_promotion_candidate_packet_v2=_mapping(source.get("inactive_promotion_candidate_packet_v2")),
            guardrail_impact_replay_plan_v2=_mapping(source.get("guardrail_impact_replay_plan_v2")),
            guarded_agent_readiness_delta_packet_v2=_mapping(source.get("guarded_agent_readiness_delta_packet_v2")),
        )
    else:
        packet = source
    assert_valid_offline_release_rehearsal_gate_v2(packet)
    return packet


def build_offline_release_rehearsal_gate_v2(
    *,
    inactive_promotion_candidate_packet_v2: Mapping[str, Any],
    guardrail_impact_replay_plan_v2: Mapping[str, Any],
    guarded_agent_readiness_delta_packet_v2: Mapping[str, Any],
) -> dict[str, Any]:
    """Return a deterministic offline gate packet from three inactive inputs."""

    for input_packet in (
        inactive_promotion_candidate_packet_v2,
        guardrail_impact_replay_plan_v2,
        guarded_agent_readiness_delta_packet_v2,
    ):
        _raise_if_unsafe(input_packet)

    candidates = _candidate_rows(inactive_promotion_candidate_packet_v2)
    replay_cases = _mapping_sequence(guardrail_impact_replay_plan_v2.get("ordered_replay_cases"))
    readiness_rows = _readiness_rows(guarded_agent_readiness_delta_packet_v2)
    if not candidates:
        raise OfflineReleaseRehearsalGateV2Error(("inactive promotion candidate input must include candidate rows",))
    if not replay_cases:
        raise OfflineReleaseRehearsalGateV2Error(("guardrail replay input must include ordered replay cases",))
    if not readiness_rows:
        raise OfflineReleaseRehearsalGateV2Error(("agent readiness input must include readiness placeholders",))

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "packet_id": "offline-release-rehearsal-gate-v2-fixture",
        "fixture_first": True,
        "offline_only": True,
        "consumed_inputs": [
            _packet_ref(inactive_promotion_candidate_packet_v2, "inactive_promotion_candidate_packet_v2"),
            _packet_ref(guardrail_impact_replay_plan_v2, "guardrail_impact_replay_plan_v2"),
            _packet_ref(guarded_agent_readiness_delta_packet_v2, "guarded_agent_readiness_delta_packet_v2"),
        ],
        "ordered_release_gate_checks": _ordered_gate_checks(candidates, replay_cases, readiness_rows),
        "evidence_bundle_references": _evidence_bundle_references(candidates, replay_cases, readiness_rows),
        "validation_transcript_placeholders": _validation_transcript_placeholders(),
        "rollback_readiness_placeholders": _rollback_readiness_placeholders(candidates),
        "human_reviewer_decision_placeholders": _human_reviewer_decision_placeholders(candidates),
        "exact_offline_validation_commands": [list(command) for command in EXACT_OFFLINE_VALIDATION_COMMANDS],
        "attestations": dict(_REQUIRED_ATTESTATIONS),
        "release_gate_status": "blocked_pending_human_review",
    }
    assert_valid_offline_release_rehearsal_gate_v2(packet)
    return packet


def validate_offline_release_rehearsal_gate_v2(packet: Mapping[str, Any]) -> OfflineReleaseRehearsalGateV2ValidationResult:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return OfflineReleaseRehearsalGateV2ValidationResult(False, ("packet must be an object",))

    _collect_unsafe(packet, "$", problems)
    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("packet_version must be v2")
    if packet.get("fixture_first") is not True:
        problems.append("fixture_first must be true")
    if packet.get("offline_only") is not True:
        problems.append("offline_only must be true")

    consumed = _mapping_sequence(packet.get("consumed_inputs"))
    roles = {_text(item.get("input_role")) for item in consumed}
    for role in (
        "inactive_promotion_candidate_packet_v2",
        "guardrail_impact_replay_plan_v2",
        "guarded_agent_readiness_delta_packet_v2",
    ):
        if role not in roles:
            problems.append(f"consumed_inputs must include {role}")

    sections = (
        "ordered_release_gate_checks",
        "evidence_bundle_references",
        "validation_transcript_placeholders",
        "rollback_readiness_placeholders",
        "human_reviewer_decision_placeholders",
    )
    for section in sections:
        if not _mapping_sequence(packet.get(section)):
            problems.append(f"{section} must be a non-empty list")

    evidence_ids = _id_set(packet.get("evidence_bundle_references"), "bundle_id")
    transcript_ids = _id_set(packet.get("validation_transcript_placeholders"), "transcript_id")
    rollback_ids = _id_set(packet.get("rollback_readiness_placeholders"), "rollback_placeholder_id")
    reviewer_ids = _id_set(packet.get("human_reviewer_decision_placeholders"), "decision_placeholder_id")

    checks = _mapping_sequence(packet.get("ordered_release_gate_checks"))
    if [check.get("order") for check in checks] != list(range(1, len(checks) + 1)):
        problems.append("ordered_release_gate_checks must be sequentially ordered from 1")
    for index, check in enumerate(checks):
        prefix = f"ordered_release_gate_checks[{index}]"
        if not _text(check.get("gate_check_id")):
            problems.append(f"{prefix}.gate_check_id is required")
        if check.get("gate_decision") != "blocked_pending_human_review":
            problems.append(f"{prefix}.gate_decision must be blocked_pending_human_review")
        if not _string_sequence(check.get("candidate_refs")):
            problems.append(f"{prefix}.candidate_refs must be non-empty")
        if not _string_sequence(check.get("guardrail_replay_refs")):
            problems.append(f"{prefix}.guardrail_replay_refs must be non-empty")
        if not _string_sequence(check.get("agent_readiness_refs")):
            problems.append(f"{prefix}.agent_readiness_refs must be non-empty")
        if _text(check.get("evidence_bundle_ref")) not in evidence_ids:
            problems.append(f"{prefix}.evidence_bundle_ref must reference evidence_bundle_references")
        if _text(check.get("validation_transcript_ref")) not in transcript_ids:
            problems.append(f"{prefix}.validation_transcript_ref must reference validation_transcript_placeholders")
        if _text(check.get("rollback_readiness_ref")) not in rollback_ids:
            problems.append(f"{prefix}.rollback_readiness_ref must reference rollback_readiness_placeholders")
        if _text(check.get("human_reviewer_decision_ref")) not in reviewer_ids:
            problems.append(f"{prefix}.human_reviewer_decision_ref must reference human_reviewer_decision_placeholders")
        if not _citation_sequence(check.get("citations")):
            problems.append(f"{prefix}.citations must be non-empty")

    _validate_evidence(packet, problems)
    _validate_transcripts(packet, problems)
    _validate_rollback(packet, problems)
    _validate_reviewers(packet, problems)
    if packet.get("exact_offline_validation_commands") != EXACT_OFFLINE_VALIDATION_COMMANDS:
        problems.append("exact_offline_validation_commands must match offline release rehearsal gate v2 commands")
    attestations = _mapping(packet.get("attestations"))
    for key, expected in sorted(_REQUIRED_ATTESTATIONS.items()):
        if attestations.get(key) is not expected:
            problems.append(f"attestations.{key} must be {expected}")
    if packet.get("release_gate_status") != "blocked_pending_human_review":
        problems.append("release_gate_status must be blocked_pending_human_review")

    return OfflineReleaseRehearsalGateV2ValidationResult(not problems, tuple(_dedupe(problems)))


def assert_valid_offline_release_rehearsal_gate_v2(packet: Mapping[str, Any]) -> None:
    result = validate_offline_release_rehearsal_gate_v2(packet)
    if not result.valid:
        raise OfflineReleaseRehearsalGateV2Error(result.problems)


def _ordered_gate_checks(
    candidates: Sequence[Mapping[str, Any]],
    replay_cases: Sequence[Mapping[str, Any]],
    readiness_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        replay = replay_cases[(index - 1) % len(replay_cases)]
        readiness = readiness_rows[(index - 1) % len(readiness_rows)]
        checks.append(
            {
                "order": index,
                "gate_check_id": f"release-gate-check-{index:02d}",
                "candidate_refs": [_candidate_id(candidate, index)],
                "guardrail_replay_refs": [_text(replay.get("case_id"), f"replay-case-{index:02d}")],
                "agent_readiness_refs": [_readiness_id(readiness, index)],
                "gate_decision": "blocked_pending_human_review",
                "gate_rationale": "Inactive fixture inputs require evidence, transcript, rollback, and reviewer placeholders before release review.",
                "evidence_bundle_ref": f"evidence-bundle-{index:02d}",
                "validation_transcript_ref": f"validation-transcript-{index:02d}",
                "rollback_readiness_ref": f"rollback-readiness-{index:02d}",
                "human_reviewer_decision_ref": f"human-reviewer-decision-{index:02d}",
                "citations": _citations(candidate) + _citations(replay) + _citations(readiness),
            }
        )
    return checks


def _evidence_bundle_references(
    candidates: Sequence[Mapping[str, Any]],
    replay_cases: Sequence[Mapping[str, Any]],
    readiness_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    bundles: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        replay = replay_cases[(index - 1) % len(replay_cases)]
        readiness = readiness_rows[(index - 1) % len(readiness_rows)]
        bundles.append(
            {
                "bundle_id": f"evidence-bundle-{index:02d}",
                "candidate_ref": _candidate_id(candidate, index),
                "guardrail_replay_ref": _text(replay.get("case_id"), f"replay-case-{index:02d}"),
                "agent_readiness_ref": _readiness_id(readiness, index),
                "bundle_status": "referenced_pending_human_review",
                "evidence_ids": _string_sequence(candidate.get("source_evidence_ids")) + _string_sequence(replay.get("source_evidence_ids")),
                "citations": _citations(candidate) + _citations(replay) + _citations(readiness),
            }
        )
    return bundles


def _validation_transcript_placeholders() -> list[dict[str, Any]]:
    return [
        {
            "transcript_id": f"validation-transcript-{index:02d}",
            "command": list(command),
            "placeholder_status": "pending_offline_replay",
            "expected_result": "passes in fixture-only validation before any manual release review",
            "captured_output_ref": "placeholder_only_no_private_output",
            "citations": [{"fixture": "offline_release_rehearsal_gate_v2", "command": " ".join(command)}],
        }
        for index, command in enumerate(EXACT_OFFLINE_VALIDATION_COMMANDS, start=1)
    ]


def _rollback_readiness_placeholders(candidates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "rollback_placeholder_id": f"rollback-readiness-{index:02d}",
            "candidate_ref": _candidate_id(candidate, index),
            "rollback_plan_ref": _text(candidate.get("rollback_plan_ref"), f"rollback-plan-{index:02d}"),
            "readiness_status": "ready_no_active_changes",
            "rollback_scope": "Discard inactive fixture packet and rerun offline validation; no active artifact restoration is required.",
            "citations": _citations(candidate),
        }
        for index, candidate in enumerate(candidates, start=1)
    ]


def _human_reviewer_decision_placeholders(candidates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "decision_placeholder_id": f"human-reviewer-decision-{index:02d}",
            "candidate_ref": _candidate_id(candidate, index),
            "decision": "pending_manual_review",
            "reviewer": "",
            "reviewed_at": "",
            "notes": "",
            "required_decision_options": ["approve_offline_rehearsal", "hold_for_rework", "reject_release_rehearsal"],
            "citations": _citations(candidate),
        }
        for index, candidate in enumerate(candidates, start=1)
    ]


def _validate_evidence(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, bundle in enumerate(_mapping_sequence(packet.get("evidence_bundle_references"))):
        prefix = f"evidence_bundle_references[{index}]"
        if not _text(bundle.get("bundle_id")):
            problems.append(f"{prefix}.bundle_id is required")
        if bundle.get("bundle_status") != "referenced_pending_human_review":
            problems.append(f"{prefix}.bundle_status must be referenced_pending_human_review")
        if not _citation_sequence(bundle.get("citations")):
            problems.append(f"{prefix}.citations must be non-empty")


def _validate_transcripts(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, transcript in enumerate(_mapping_sequence(packet.get("validation_transcript_placeholders"))):
        prefix = f"validation_transcript_placeholders[{index}]"
        if not _text(transcript.get("transcript_id")):
            problems.append(f"{prefix}.transcript_id is required")
        if transcript.get("placeholder_status") != "pending_offline_replay":
            problems.append(f"{prefix}.placeholder_status must be pending_offline_replay")
        if _string_sequence(transcript.get("command")) not in EXACT_OFFLINE_VALIDATION_COMMANDS:
            problems.append(f"{prefix}.command must be one of exact_offline_validation_commands")
        if transcript.get("captured_output_ref") != "placeholder_only_no_private_output":
            problems.append(f"{prefix}.captured_output_ref must remain placeholder_only_no_private_output")
        if not _citation_sequence(transcript.get("citations")):
            problems.append(f"{prefix}.citations must be non-empty")


def _validate_rollback(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, rollback in enumerate(_mapping_sequence(packet.get("rollback_readiness_placeholders"))):
        prefix = f"rollback_readiness_placeholders[{index}]"
        if not _text(rollback.get("rollback_placeholder_id")):
            problems.append(f"{prefix}.rollback_placeholder_id is required")
        if rollback.get("readiness_status") != "ready_no_active_changes":
            problems.append(f"{prefix}.readiness_status must be ready_no_active_changes")
        if not _text(rollback.get("rollback_plan_ref")):
            problems.append(f"{prefix}.rollback_plan_ref is required")
        if not _citation_sequence(rollback.get("citations")):
            problems.append(f"{prefix}.citations must be non-empty")


def _validate_reviewers(packet: Mapping[str, Any], problems: list[str]) -> None:
    for index, reviewer in enumerate(_mapping_sequence(packet.get("human_reviewer_decision_placeholders"))):
        prefix = f"human_reviewer_decision_placeholders[{index}]"
        if not _text(reviewer.get("decision_placeholder_id")):
            problems.append(f"{prefix}.decision_placeholder_id is required")
        if reviewer.get("decision") != "pending_manual_review":
            problems.append(f"{prefix}.decision must be pending_manual_review")
        if reviewer.get("reviewer") != "" or reviewer.get("reviewed_at") != "" or reviewer.get("notes") != "":
            problems.append(f"{prefix} must remain unsigned")
        if not _string_sequence(reviewer.get("required_decision_options")):
            problems.append(f"{prefix}.required_decision_options must be non-empty")
        if not _citation_sequence(reviewer.get("citations")):
            problems.append(f"{prefix}.citations must be non-empty")


def _candidate_rows(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = _mapping_sequence(packet.get("promotion_candidate_rows"))
    if rows:
        return rows
    return _mapping_sequence(packet.get("candidate_rows"))


def _readiness_rows(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    for key in (
        "agent_schema_delta_placeholders",
        "reviewer_acceptance_placeholders",
        "ordered_agent_facing_delta_scenarios",
    ):
        rows = _mapping_sequence(packet.get(key))
        if rows:
            return rows
    return []


def _packet_ref(packet: Mapping[str, Any], role: str) -> dict[str, str]:
    return {
        "input_role": role,
        "packet_id": _text(packet.get("packet_id"), role),
        "packet_type": _text(packet.get("packet_type"), _text(packet.get("plan_type"), role)),
        "packet_version": _text(packet.get("packet_version"), _text(packet.get("plan_version"), "v2")),
    }


def _candidate_id(candidate: Mapping[str, Any], index: int) -> str:
    return _text(candidate.get("candidate_id"), f"candidate-{index:02d}")


def _readiness_id(row: Mapping[str, Any], index: int) -> str:
    for key in ("delta_id", "acceptance_id", "expectation_id", "kind"):
        value = _text(row.get(key))
        if value:
            return value
    return f"agent-readiness-{index:02d}"


def _citations(value: Mapping[str, Any]) -> list[Any]:
    citations = _citation_sequence(value.get("citations"))
    citations.extend(_citation_sequence(value.get("citation_placeholders")))
    citations.extend(_citation_sequence(value.get("citation_traceability")))
    citations.extend(_string_sequence(value.get("source_evidence_ids")))
    if not citations:
        citations.append({"fixture": "offline_release_rehearsal_gate_v2", "ref": "metadata"})
    return citations


def _load_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object at {path}")
    return value


def _raise_if_unsafe(value: Any) -> None:
    problems: list[str] = []
    _collect_unsafe(value, "$", problems)
    if problems:
        raise OfflineReleaseRehearsalGateV2Error(problems)


def _collect_unsafe(value: Any, path: str, problems: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if any(token in normalized for token in _FORBIDDEN_KEY_TOKENS) and _truthy(child):
                problems.append(f"{child_path} must not contain private, raw, browser, session, payment, or downloaded artifacts")
            if normalized in _MUTATION_KEYS and child is True:
                problems.append(f"{child_path} must not enable active promotion, mutation, or release-state changes")
            _collect_unsafe(child, child_path, problems)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _collect_unsafe(child, f"{path}[{index}]", problems)
    elif isinstance(value, str) and _FORBIDDEN_TEXT_RE.search(value):
        problems.append(f"{path} contains forbidden live, private, official-action, guarantee, or mutation language")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [item for item in value if isinstance(item, Mapping)]
    return []


def _string_sequence(value: Any) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return [str(item) for item in value if str(item).strip()]
    return []


def _citation_sequence(value: Any) -> list[Any]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return [item for item in value if isinstance(item, Mapping) or (isinstance(item, str) and item.strip())]
    return []


def _id_set(value: Any, field: str) -> set[str]:
    return {_text(item.get(field)) for item in _mapping_sequence(value) if _text(item.get(field))}


def _truthy(value: Any) -> bool:
    if value in (None, False, "", [], {}):
        return False
    return True


def _text(value: Any, fallback: str = "") -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
