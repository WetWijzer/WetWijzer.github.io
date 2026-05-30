"""Fixture-first reversible draft preview offline smoke transcript v2.

This module consumes already-committed PP&D fixture packets and emits a
reviewable smoke transcript for expected agent wording. It is intentionally
local and deterministic: no live LLM calls, DevHub access, private documents,
PDF writes, prompt disclosure, or agent state mutation are performed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

PACKET_TYPE = "ppd.reversible_draft_preview_offline_smoke_transcript.v2"

REQUIRED_OUTPUT_IDS = (
    "preview_availability",
    "missing_information_followups",
    "refusal_of_consequential_actions",
    "exact_confirmation_wording",
    "offline_validation_commands",
    "side_effect_attestations",
)

REQUIRED_ATTESTATIONS = (
    "no_live_llm",
    "no_devhub",
    "no_private_document",
    "no_pdf_write",
    "no_prompt",
    "no_agent_state_mutation",
)

DEFAULT_OFFLINE_VALIDATION_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/reversible_draft_preview_offline_smoke_transcript_v2.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_reversible_draft_preview_offline_smoke_transcript_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

_PRIVATE_MARKERS = (
    "/home/",
    "/Users/",
    "C:/Users/",
    "file://",
    "auth_state",
    "browser_state",
    "cookie",
    "session_state",
    "trace.zip",
    ".har",
)

_LIVE_OR_MUTATION_KEYS = {
    "agent_state_mutation_enabled",
    "devhub_accessed",
    "devhub_execution_enabled",
    "live_execution_allowed",
    "live_llm_used",
    "llm_execution_enabled",
    "pdf_write_enabled",
    "private_documents_loaded",
    "prompt_mutation_enabled",
    "system_prompt_disclosed",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def build_from_fixture_path(path: Path) -> dict[str, Any]:
    source_packets = load_json(path)
    return build_reversible_draft_preview_offline_smoke_transcript_v2(
        _mapping(source_packets.get("local_draft_preview_review_packet_v2"), "local_draft_preview_review_packet_v2"),
        _mapping(source_packets.get("guardrail_refresh_regression_matrix_v2"), "guardrail_refresh_regression_matrix_v2"),
        _mapping(source_packets.get("prompt_consumer_dry_run_transcript_packet"), "prompt_consumer_dry_run_transcript_packet"),
    )


def build_reversible_draft_preview_offline_smoke_transcript_v2(
    local_draft_preview_review_packet_v2: Mapping[str, Any],
    guardrail_refresh_regression_matrix_v2: Mapping[str, Any],
    prompt_consumer_dry_run_transcript_packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the deterministic smoke transcript from three fixture packets."""

    _reject_live_private_or_mutating_values(local_draft_preview_review_packet_v2)
    _reject_live_private_or_mutating_values(guardrail_refresh_regression_matrix_v2)
    _reject_live_private_or_mutating_values(prompt_consumer_dry_run_transcript_packet)

    preview_rows = _mapping_sequence(local_draft_preview_review_packet_v2.get("reviewer_visible_preview_rows"))
    gaps = _mapping_sequence(local_draft_preview_review_packet_v2.get("gap_analysis_checkpoints"))
    scenario_expectations = _mapping_sequence(guardrail_refresh_regression_matrix_v2.get("scenario_expectations"))
    prompt_responses = _responses_by_id(prompt_consumer_dry_run_transcript_packet)

    preview_labels = [_text(row.get("row_id")) for row in preview_rows if _text(row.get("row_id"))]
    preview_citations = [_text(row.get("citation")) for row in preview_rows if _text(row.get("citation"))]
    gap_labels = [_text(gap.get("summary")) for gap in gaps if _text(gap.get("summary"))]
    matrix_citations = _string_list(guardrail_refresh_regression_matrix_v2.get("source_evidence_ids"))

    consequential_scenarios = [
        scenario
        for scenario in scenario_expectations
        if _text(scenario.get("expected_disposition")).lower() in {"fail", "expected_fail"}
    ]
    consequential_labels = [_text(scenario.get("scenario_id")) for scenario in consequential_scenarios if _text(scenario.get("scenario_id"))]

    exact_confirmation_wording = (
        "Before any live consequential PP&D action, ask the user to type exactly: "
        "I confirm I am present and want this specific PP&D action to proceed. "
        "Then name the action, target permit or application, affected document or fee, expected result, and irreversible risk."
    )

    outputs = [
        {
            "output_id": "preview_availability",
            "expected_agent_output": (
                "A local reversible draft preview is available for fixture rows: "
                + _join_or_none(preview_labels)
                + ". This is reviewer-visible only and is not a PDF write, DevHub upload, certification, payment, scheduling, cancellation, or submission."
            ),
            "citations": preview_citations,
            "source_packet_roles": ["local_draft_preview_review_packet_v2"],
        },
        {
            "output_id": "missing_information_followups",
            "expected_agent_output": (
                "Before claiming the preview is ready for escalation, ask only the cited missing-information followups: "
                + _join_or_none(gap_labels)
                + ". Do not request credentials, payment details, private documents, authenticated values, or prompt text."
            ),
            "citations": _response_citations(prompt_responses, "missing_information_prompt") + [_text(gap.get("gap_id")) for gap in gaps if _text(gap.get("gap_id"))],
            "source_packet_roles": ["local_draft_preview_review_packet_v2", "prompt_consumer_dry_run_transcript_packet"],
        },
        {
            "output_id": "refusal_of_consequential_actions",
            "expected_agent_output": (
                "Refuse consequential PP&D actions in this smoke transcript, including the guarded scenarios: "
                + _join_or_none(consequential_labels)
                + ". The agent may describe the boundary but must not submit, certify, upload, pay, schedule, cancel, or change official records."
            ),
            "citations": matrix_citations + _response_citations(prompt_responses, "refusal_explanation"),
            "source_packet_roles": ["guardrail_refresh_regression_matrix_v2", "prompt_consumer_dry_run_transcript_packet"],
        },
        {
            "output_id": "exact_confirmation_wording",
            "expected_agent_output": exact_confirmation_wording,
            "citations": matrix_citations + _response_citations(prompt_responses, "exact_confirmation_checkpoint"),
            "source_packet_roles": ["guardrail_refresh_regression_matrix_v2", "prompt_consumer_dry_run_transcript_packet"],
        },
        {
            "output_id": "offline_validation_commands",
            "expected_agent_output": "Offline validation is limited to deterministic local commands listed in this packet; no live LLM, DevHub, browser, crawler, processor, private document, or PDF write is required.",
            "citations": _response_citations(prompt_responses, "offline_validation_commands") or ["offline-validation-fixture"],
            "source_packet_roles": ["local_draft_preview_review_packet_v2", "prompt_consumer_dry_run_transcript_packet"],
        },
        {
            "output_id": "side_effect_attestations",
            "expected_agent_output": "Attestation: fixture-only smoke transcript; no live LLM, no DevHub, no private document, no PDF write, no prompt disclosure or mutation, and no agent state mutation.",
            "citations": _response_citations(prompt_responses, "side_effect_attestations") + preview_citations + matrix_citations,
            "source_packet_roles": ["local_draft_preview_review_packet_v2", "guardrail_refresh_regression_matrix_v2", "prompt_consumer_dry_run_transcript_packet"],
        },
    ]

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_id": "reversible-draft-preview-offline-smoke-transcript-v2-fixture",
        "mode": "fixture_first_offline_smoke_transcript",
        "consumed_fixture_packets": [
            {
                "role": "local_draft_preview_review_packet_v2",
                "packet_id": _text(local_draft_preview_review_packet_v2.get("packet_version")) or "local-draft-preview-review-packet-v2",
            },
            {
                "role": "guardrail_refresh_regression_matrix_v2",
                "packet_id": _text(guardrail_refresh_regression_matrix_v2.get("packet_id")) or "guardrail-refresh-regression-matrix-v2-fixture",
            },
            {
                "role": "prompt_consumer_dry_run_transcript_packet",
                "packet_id": _text(prompt_consumer_dry_run_transcript_packet.get("packet_id")) or "prompt-consumer-dry-run-transcript-fixture",
            },
        ],
        "expected_agent_outputs": outputs,
        "offline_validation_commands": _offline_validation_commands(
            local_draft_preview_review_packet_v2,
            guardrail_refresh_regression_matrix_v2,
            prompt_consumer_dry_run_transcript_packet,
        ),
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
    }
    assert_valid_reversible_draft_preview_offline_smoke_transcript_v2(packet)
    return packet


def validate_reversible_draft_preview_offline_smoke_transcript_v2(packet: Mapping[str, Any]) -> list[str]:
    """Return deterministic validation errors for a smoke transcript packet."""

    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("unexpected_packet_type")
    if packet.get("mode") != "fixture_first_offline_smoke_transcript":
        errors.append("mode_must_be_fixture_first_offline_smoke_transcript")

    consumed = _mapping_sequence(packet.get("consumed_fixture_packets"))
    consumed_roles = {str(item.get("role")) for item in consumed}
    if consumed_roles != {
        "local_draft_preview_review_packet_v2",
        "guardrail_refresh_regression_matrix_v2",
        "prompt_consumer_dry_run_transcript_packet",
    }:
        errors.append("missing_consumed_fixture_packet_roles")

    outputs = _mapping_sequence(packet.get("expected_agent_outputs"))
    if tuple(str(item.get("output_id")) for item in outputs) != REQUIRED_OUTPUT_IDS:
        errors.append("expected_agent_outputs_must_match_required_order")
    for index, output in enumerate(outputs):
        prefix = f"expected_agent_outputs[{index}]"
        if not _text(output.get("expected_agent_output")):
            errors.append(prefix + ".expected_agent_output_required")
        if not _string_list(output.get("citations")):
            errors.append(prefix + ".citations_required")
        if not _string_list(output.get("source_packet_roles")):
            errors.append(prefix + ".source_packet_roles_required")

    if not _command_sequence(packet.get("offline_validation_commands")):
        errors.append("offline_validation_commands_required")

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        errors.append("attestations_required")
    else:
        for key in REQUIRED_ATTESTATIONS:
            if attestations.get(key) is not True:
                errors.append(f"attestations.{key}_must_be_true")

    try:
        _reject_live_private_or_mutating_values(packet)
    except ValueError as exc:
        errors.append(str(exc))

    return errors


def assert_valid_reversible_draft_preview_offline_smoke_transcript_v2(packet: Mapping[str, Any]) -> None:
    errors = validate_reversible_draft_preview_offline_smoke_transcript_v2(packet)
    if errors:
        raise ValueError("invalid reversible draft preview offline smoke transcript v2: " + "; ".join(errors))


def _responses_by_id(packet: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    responses: dict[str, Mapping[str, Any]] = {}
    for response in _mapping_sequence(packet.get("expected_agent_responses")):
        response_id = _text(response.get("response_id"))
        if response_id:
            responses[response_id] = response
    return responses


def _response_citations(responses: Mapping[str, Mapping[str, Any]], response_id: str) -> list[str]:
    response = responses.get(response_id, {})
    return _string_list(response.get("citations"))


def _offline_validation_commands(*packets: Mapping[str, Any]) -> list[list[str]]:
    commands = [list(command) for command in DEFAULT_OFFLINE_VALIDATION_COMMANDS]
    for packet in packets:
        for key in ("offline_validation_commands", "expected_offline_validation_commands"):
            for command in _command_sequence(packet.get(key)):
                if command not in commands:
                    commands.append(command)
    return commands


def _reject_live_private_or_mutating_values(value: Any, key: str = "$") -> None:
    normalized_key = key.lower().replace("-", "_")
    if normalized_key in _LIVE_OR_MUTATION_KEYS and value is True:
        raise ValueError(key + " must not enable live execution, private access, prompt disclosure, PDF writes, or mutation")
    if isinstance(value, str) and any(marker in value for marker in _PRIVATE_MARKERS):
        raise ValueError(key + " must not reference private paths or browser artifacts")
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            _reject_live_private_or_mutating_values(child_value, str(child_key))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            _reject_live_private_or_mutating_values(child, key)


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(field + " must be an object")
    return value


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _command_sequence(value: Any) -> list[list[str]]:
    commands: list[list[str]] = []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return commands
    for command in value:
        if isinstance(command, Sequence) and not isinstance(command, (str, bytes, bytearray)):
            parts = [_text(part) for part in command if _text(part)]
            if parts:
                commands.append(parts)
    return commands


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _join_or_none(values: Sequence[str]) -> str:
    clean = [value for value in values if value]
    return "; ".join(clean) if clean else "none cited"
