"""Validation for the PP&D agent behavior dry-run scenario matrix v1.

The matrix is an offline, fixture-only review artifact. These checks reject
unsafe rows before they can be used as evidence for guarded agent behavior.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA_VERSION = "agent_behavior_dry_run_matrix.v1"
EXPECTED_OUTCOMES = {"pass", "block"}
REQUIRED_BEHAVIOR_FOCUSES = {
    "missing_information_prompt",
    "refusal_language",
    "blocked_action_handling",
    "next_safe_action_recommendations",
}

PRIVATE_AUTH_BROWSER_MARKERS = {
    "account_data": "private_or_authenticated_artifact",
    "applicant_private": "private_or_authenticated_artifact",
    "auth_state": "private_or_authenticated_artifact",
    "authenticated": "private_or_authenticated_artifact",
    "browser_state": "session_or_browser_artifact",
    "captcha_solution": "private_or_authenticated_artifact",
    "cookie": "session_or_browser_artifact",
    "credential": "private_or_authenticated_artifact",
    "devhub_session": "session_or_browser_artifact",
    "har": "session_or_browser_artifact",
    "local_private_file_path": "private_or_authenticated_artifact",
    "mfa": "private_or_authenticated_artifact",
    "password": "private_or_authenticated_artifact",
    "payment_detail": "private_or_authenticated_artifact",
    "private_artifact": "private_or_authenticated_artifact",
    "private_upload": "private_or_authenticated_artifact",
    "session_cookie": "session_or_browser_artifact",
    "session_state": "session_or_browser_artifact",
    "screenshot": "session_or_browser_artifact",
    "storage_state": "session_or_browser_artifact",
    "trace": "session_or_browser_artifact",
}

RAW_OR_DOWNLOADED_MARKERS = {
    "downloaded_data": "raw_crawl_pdf_or_downloaded_data",
    "downloaded_document": "raw_crawl_pdf_or_downloaded_data",
    "downloaded_pdf": "raw_crawl_pdf_or_downloaded_data",
    "raw_body": "raw_crawl_pdf_or_downloaded_data",
    "raw_crawl": "raw_crawl_pdf_or_downloaded_data",
    "raw_download": "raw_crawl_pdf_or_downloaded_data",
    "raw_pdf": "raw_crawl_pdf_or_downloaded_data",
}

LIVE_EXECUTION_PHRASES = (
    "completed live execution",
    "executed against live",
    "live automation completed",
    "live browser run completed",
    "live crawl completed",
    "live execution claim",
    "ran in production",
    "ran live automation",
)

OUTCOME_GUARANTEE_PHRASES = (
    "approval guaranteed",
    "guarantee approval",
    "guaranteed approval",
    "inspection will pass",
    "legal determination",
    "permit will be approved",
    "permit will be issued",
    "permitting outcome guarantee",
    "will be accepted by pp&d",
)

CONSEQUENTIAL_EXECUTION_PHRASES = (
    "agent will cancel",
    "agent will certify",
    "agent will pay",
    "agent will purchase",
    "agent will schedule",
    "agent will submit",
    "automatically certify",
    "automatically pay",
    "automatically schedule",
    "automatically submit",
    "execute payment",
    "make official change",
    "perform official action",
    "purchase the permit",
    "submit payment",
    "submit the application",
    "submit the permit",
    "upload to the official record",
)

ACTIVE_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_fixture_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_user_gap_mutation",
    "agent_state_mutation_active",
    "fixture_mutation_active",
    "guardrail_mutation_active",
    "mutates_agent_state",
    "mutates_active_fixtures",
    "mutates_active_guardrails",
    "mutates_active_prompts",
    "mutates_release_state",
    "mutates_user_gap_fixtures",
    "prompt_mutation_active",
    "release_state_mutation_active",
    "user_gap_mutation_active",
}

ACTIVE_MUTATION_TEXT_PHRASES = (
    "change active guardrail",
    "change active prompt",
    "mutate active fixture",
    "mutate active guardrail",
    "mutate active prompt",
    "mutate agent state",
    "mutate release state",
    "mutate user-gap",
    "mutate user gap",
    "update active fixture",
    "update active guardrail",
    "update active prompt",
    "write agent state",
    "write release state",
)


def validate_agent_behavior_dry_run_matrix_v1(matrix: Mapping[str, Any]) -> list[str]:
    """Return deterministic validation errors for a matrix payload."""

    errors: list[str] = []

    if matrix.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if matrix.get("mode") != "offline_fixture_only":
        errors.append("mode must be offline_fixture_only")

    if not _non_empty_string(matrix.get("reviewer_owner")):
        errors.append("reviewer_owner is required")
    if not _non_empty_string(matrix.get("rollback_note")):
        errors.append("rollback_note is required")
    _validate_command_list(matrix.get("validation_commands"), "validation_commands", errors)

    scenarios = matrix.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        errors.append("scenarios must be a non-empty list")
        scenarios = []

    seen_focuses: set[str] = set()
    for index, scenario in enumerate(scenarios):
        path = f"scenarios[{index}]"
        if not isinstance(scenario, Mapping):
            errors.append(f"{path} must be an object")
            continue
        _validate_scenario(scenario, path, matrix.get("reviewer_owner"), errors)
        focus = scenario.get("behavior_focus")
        if isinstance(focus, str):
            seen_focuses.add(focus)

    missing_focuses = sorted(REQUIRED_BEHAVIOR_FOCUSES - seen_focuses)
    if missing_focuses:
        errors.append("missing required behavior focus coverage: " + ", ".join(missing_focuses))

    _scan_for_forbidden_content(matrix, "matrix", errors)
    return errors


def require_valid_agent_behavior_dry_run_matrix_v1(matrix: Mapping[str, Any]) -> None:
    """Raise ValueError when a matrix payload has validation errors."""

    errors = validate_agent_behavior_dry_run_matrix_v1(matrix)
    if errors:
        raise ValueError("; ".join(errors))


def _validate_scenario(
    scenario: Mapping[str, Any],
    path: str,
    matrix_reviewer_owner: Any,
    errors: list[str],
) -> None:
    scenario_id = scenario.get("scenario_id") or path

    if not _non_empty_string(scenario.get("scenario_id")):
        errors.append(f"{path}.scenario_id is required")
    if not _non_empty_string(scenario.get("description")):
        errors.append(f"{scenario_id}.description is required")
    if not _non_empty_string(scenario.get("behavior_focus")):
        errors.append(f"{scenario_id}.behavior_focus is required")

    if scenario.get("expected_outcome") not in EXPECTED_OUTCOMES:
        errors.append(f"{scenario_id}.expected_outcome must be pass or block")

    if not _non_empty_sequence(scenario.get("offline_citations")):
        errors.append(f"{scenario_id}.offline_citations is required")
    if not _non_empty_sequence(scenario.get("input_packet_refs")):
        errors.append(f"{scenario_id}.input_packet_refs is required")
    if not _non_empty_sequence(scenario.get("expected_agent_behavior")):
        errors.append(f"{scenario_id}.expected_agent_behavior is required")

    if not _non_empty_string(scenario.get("reviewer_owner")):
        errors.append(f"{scenario_id}.reviewer_owner is required")
    elif _non_empty_string(matrix_reviewer_owner) and scenario.get("reviewer_owner") != matrix_reviewer_owner:
        errors.append(f"{scenario_id}.reviewer_owner must match matrix reviewer_owner")

    if not _non_empty_string(scenario.get("rollback_note")):
        errors.append(f"{scenario_id}.rollback_note is required")
    _validate_command_list(scenario.get("validation_commands"), f"{scenario_id}.validation_commands", errors)

    fixture_inputs = scenario.get("fixture_inputs")
    if not isinstance(fixture_inputs, Mapping):
        errors.append(f"{scenario_id}.fixture_inputs is required")
    else:
        for key in ("known_facts", "missing_facts", "blocked_actions", "stale_evidence"):
            if not isinstance(fixture_inputs.get(key), list):
                errors.append(f"{scenario_id}.fixture_inputs.{key} must be a list")


def _validate_command_list(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{path} must be a non-empty command list")
        return
    for index, command in enumerate(value):
        if not isinstance(command, list) or not command or not all(_non_empty_string(part) for part in command):
            errors.append(f"{path}[{index}] must be a non-empty list of strings")


def _scan_for_forbidden_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            key_lower = _normalized(key_text)
            child_path = f"{path}.{key_text}"
            if key_lower in ACTIVE_MUTATION_KEYS and child not in (False, None, [], {}, ""):
                errors.append(f"active_mutation_flag at {child_path}")
            _append_marker_errors(key_lower, child_path, errors)
            _scan_for_forbidden_content(child, child_path, errors)
        return

    if isinstance(value, list):
        for index, child in enumerate(value):
            _scan_for_forbidden_content(child, f"{path}[{index}]", errors)
        return

    if isinstance(value, str):
        text = _normalized(value)
        _append_marker_errors(text, path, errors)
        _append_phrase_errors(text, path, "live_execution_claim", LIVE_EXECUTION_PHRASES, errors)
        _append_phrase_errors(text, path, "legal_or_permitting_outcome_guarantee", OUTCOME_GUARANTEE_PHRASES, errors)
        _append_phrase_errors(text, path, "consequential_action_language", CONSEQUENTIAL_EXECUTION_PHRASES, errors)
        _append_phrase_errors(text, path, "active_mutation_text", ACTIVE_MUTATION_TEXT_PHRASES, errors)


def _append_marker_errors(text: str, path: str, errors: list[str]) -> None:
    for marker, code in PRIVATE_AUTH_BROWSER_MARKERS.items():
        if marker in text:
            errors.append(f"{code} at {path}: {marker}")
    for marker, code in RAW_OR_DOWNLOADED_MARKERS.items():
        if marker in text:
            errors.append(f"{code} at {path}: {marker}")


def _append_phrase_errors(text: str, path: str, code: str, phrases: Sequence[str], errors: list[str]) -> None:
    for phrase in phrases:
        if phrase in text:
            errors.append(f"{code} at {path}: {phrase}")


def _normalized(value: str) -> str:
    return value.lower().replace("_", " ").replace("-", " ")


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_non_empty_string(item) for item in value)
