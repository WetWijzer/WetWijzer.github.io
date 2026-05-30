"""Validation for post-promotion guarded agent replay plan v1.

The validator is intentionally fixture-first and side-effect free. It checks that
replay scenarios are cited, expectation-complete, and free of private artifacts,
live execution claims, consequential-action promises, and active mutation flags.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
import re


PASS = "pass"
BLOCK = "block"
VALID_OUTCOMES = {PASS, BLOCK}

SENSITIVE_KEY_RE = re.compile(
    r"(auth|credential|cookie|session|storage[_-]?state|browser[_-]?state|password|token|secret|mfa|captcha)",
    re.IGNORECASE,
)
SENSITIVE_VALUE_RE = re.compile(
    r"(\.har\b|trace\.zip\b|screenshot\b|\bauth\b|storage[_-]?state|cookies?\b|session\b|browser[_-]?state|credential|password|token|secret|mfa|captcha)",
    re.IGNORECASE,
)
RAW_ARTIFACT_RE = re.compile(
    r"(raw[_-]?crawl|download(?:ed)?[_-]?data|downloaded[_-]?document|source[_-]?pdf|raw[_-]?pdf|\.pdf\b|\.har\b|trace\.zip\b|screenshot\b)",
    re.IGNORECASE,
)
LIVE_OR_RELEASE_CLAIM_RE = re.compile(
    r"\b(live execution|live crawl|ran live|executed in devhub|submitted live|released to production|production release|activated guardrail|release is active|deployed)\b",
    re.IGNORECASE,
)
GUARANTEE_RE = re.compile(
    r"\b(guarantee(?:s|d)?|assure(?:s|d)?|will be approved|permit approval is certain|legal outcome|permitting outcome is guaranteed|compliance guaranteed)\b",
    re.IGNORECASE,
)
CONSEQUENTIAL_ACTION_RE = re.compile(
    r"\b(will|shall|must|should|can)\s+(submit|certify|upload|pay|schedule|cancel|issue|purchase|create an account|recover password|complete mfa|solve captcha)\b",
    re.IGNORECASE,
)
MUTATION_FLAG_RE = re.compile(
    r"(active[_-]?(guardrail|prompt|release[_-]?state|fixture|agent[_-]?state)[_-]?mutation|mutate[_-]?(guardrail|prompt|release[_-]?state|fixture|agent[_-]?state))",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ReplayPlanValidationResult:
    """Result returned by guarded replay plan validation."""

    valid: bool
    errors: tuple[str, ...]

    def require_valid(self) -> "ReplayPlanValidationResult":
        if not self.valid:
            raise ValueError("guarded replay plan rejected: " + "; ".join(self.errors))
        return self


def load_replay_plan(path: str | Path) -> dict[str, Any]:
    """Load a replay plan JSON fixture without executing any external action."""

    with Path(path).open("r", encoding="utf-8") as fixture:
        loaded = json.load(fixture)
    if not isinstance(loaded, dict):
        raise ValueError("guarded replay plan fixture must contain a JSON object")
    return loaded


def validate_replay_plan(plan: dict[str, Any]) -> ReplayPlanValidationResult:
    """Validate a guarded agent replay plan v1.

    The accepted shape is deliberately simple: a top-level object with
    replay_plan_version set to v1 and a non-empty scenarios list. Each scenario
    must include citations, expected_outcome, missing-information prompt
    expectations, reversible draft boundary checks, blocked-action expectations,
    DevHub attendance gates, journal safety checks, and rollback verification.
    """

    errors: list[str] = []

    if not isinstance(plan, dict):
        return ReplayPlanValidationResult(False, ("plan must be an object",))

    version = plan.get("replay_plan_version") or plan.get("version")
    if version != "v1":
        errors.append("replay_plan_version must be v1")

    _reject_prohibited_content(plan, "plan", errors)
    _reject_mutation_flags(plan, "plan", errors)

    scenarios = plan.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        errors.append("scenarios must be a non-empty list")
        return ReplayPlanValidationResult(False, tuple(errors))

    for index, scenario in enumerate(scenarios):
        path = f"scenarios[{index}]"
        if not isinstance(scenario, dict):
            errors.append(f"{path} must be an object")
            continue
        _validate_scenario(scenario, path, errors)

    return ReplayPlanValidationResult(not errors, tuple(errors))


def validate_replay_plan_file(path: str | Path) -> ReplayPlanValidationResult:
    """Load and validate a guarded replay plan fixture."""

    return validate_replay_plan(load_replay_plan(path))


def _validate_scenario(scenario: dict[str, Any], path: str, errors: list[str]) -> None:
    scenario_id = scenario.get("scenario_id")
    if not isinstance(scenario_id, str) or not scenario_id.strip():
        errors.append(f"{path}.scenario_id is required")

    citations = scenario.get("citations") or scenario.get("source_evidence_ids")
    if not _non_empty_string_list(citations):
        errors.append(f"{path} must include at least one citation/source_evidence_id")

    expected_outcome = scenario.get("expected_outcome")
    if expected_outcome not in VALID_OUTCOMES:
        errors.append(f"{path}.expected_outcome must be pass or block")

    missing_expectation = scenario.get("missing_information_prompt_expectation")
    if not isinstance(missing_expectation, dict) or not missing_expectation:
        errors.append(f"{path}.missing_information_prompt_expectation is required")
    else:
        prompts = missing_expectation.get("expected_prompts")
        if not _non_empty_string_list(prompts):
            errors.append(f"{path}.missing_information_prompt_expectation.expected_prompts must be non-empty")
        if missing_expectation.get("allows_guessing") is True:
            errors.append(f"{path}.missing_information_prompt_expectation must not allow guessing")

    reversible = scenario.get("reversible_draft_boundary_checks")
    if not isinstance(reversible, dict) or not reversible:
        errors.append(f"{path}.reversible_draft_boundary_checks is required")
    else:
        if reversible.get("draft_only") is not True:
            errors.append(f"{path}.reversible_draft_boundary_checks.draft_only must be true")
        if reversible.get("official_side_effects") is not False:
            errors.append(f"{path}.reversible_draft_boundary_checks.official_side_effects must be false")
        stop_actions = reversible.get("stops_before_actions")
        required_stops = {"submit", "certify", "upload", "pay", "schedule", "cancel"}
        if not isinstance(stop_actions, list) or not required_stops.issubset({str(item).lower() for item in stop_actions}):
            errors.append(f"{path}.reversible_draft_boundary_checks.stops_before_actions must cover submit/certify/upload/pay/schedule/cancel")

    blocked = scenario.get("blocked_action_expectations")
    if not isinstance(blocked, dict) or not blocked:
        errors.append(f"{path}.blocked_action_expectations is required")
    else:
        if expected_outcome == BLOCK and not _non_empty_string_list(blocked.get("expected_blocked_actions")):
            errors.append(f"{path}.blocked_action_expectations.expected_blocked_actions is required for blocked scenarios")
        if blocked.get("requires_exact_confirmation_before_consequential_action") is not True:
            errors.append(f"{path}.blocked_action_expectations must require exact confirmation before consequential action")

    attendance = scenario.get("devhub_attendance_gate_checks")
    if not isinstance(attendance, dict) or not attendance:
        errors.append(f"{path}.devhub_attendance_gate_checks is required")
    else:
        if attendance.get("attended_login_required") is not True:
            errors.append(f"{path}.devhub_attendance_gate_checks.attended_login_required must be true")
        if attendance.get("manual_mfa_captcha_only") is not True:
            errors.append(f"{path}.devhub_attendance_gate_checks.manual_mfa_captcha_only must be true")
        if attendance.get("blocks_unattended_official_actions") is not True:
            errors.append(f"{path}.devhub_attendance_gate_checks.blocks_unattended_official_actions must be true")

    journal = scenario.get("journal_safety_checks")
    if not isinstance(journal, dict) or not journal:
        errors.append(f"{path}.journal_safety_checks is required")
    else:
        if journal.get("commit_safe_only") is not True:
            errors.append(f"{path}.journal_safety_checks.commit_safe_only must be true")
        forbidden = journal.get("forbidden_artifacts")
        required_forbidden = {"credentials", "cookies", "session_state", "screenshots", "traces", "har", "private_values", "payment_details", "local_private_paths"}
        if not isinstance(forbidden, list) or not required_forbidden.issubset({str(item).lower() for item in forbidden}):
            errors.append(f"{path}.journal_safety_checks.forbidden_artifacts must cover private/session/browser artifacts and screenshots/traces/HAR")

    rollback = scenario.get("rollback_verification")
    if not isinstance(rollback, dict) or not rollback:
        errors.append(f"{path}.rollback_verification is required")
    else:
        if rollback.get("rollback_checked") is not True:
            errors.append(f"{path}.rollback_verification.rollback_checked must be true")
        if rollback.get("official_state_unchanged") is not True:
            errors.append(f"{path}.rollback_verification.official_state_unchanged must be true")

    _reject_prohibited_content(scenario, path, errors)
    _reject_mutation_flags(scenario, path, errors)


def _reject_prohibited_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            key_text = str(key)
            if SENSITIVE_KEY_RE.search(key_text):
                errors.append(f"{child_path} uses prohibited private/auth/session/browser artifact key")
            if RAW_ARTIFACT_RE.search(key_text):
                errors.append(f"{child_path} uses prohibited raw/download/PDF/screenshot/trace/HAR artifact key")
            _reject_prohibited_content(child, child_path, errors)
        return

    if isinstance(value, list):
        for index, child in enumerate(value):
            _reject_prohibited_content(child, f"{path}[{index}]", errors)
        return

    if isinstance(value, str):
        if SENSITIVE_VALUE_RE.search(value):
            errors.append(f"{path} references prohibited private/auth/session/browser artifact content")
        if RAW_ARTIFACT_RE.search(value):
            errors.append(f"{path} references prohibited raw/download/PDF/screenshot/trace/HAR artifact content")
        if LIVE_OR_RELEASE_CLAIM_RE.search(value):
            errors.append(f"{path} contains a live execution or release-state claim")
        if GUARANTEE_RE.search(value):
            errors.append(f"{path} contains a legal or permitting outcome guarantee")
        if CONSEQUENTIAL_ACTION_RE.search(value):
            errors.append(f"{path} contains consequential action language")


def _reject_mutation_flags(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if MUTATION_FLAG_RE.search(str(key)) and child is not False:
                errors.append(f"{child_path} is an active guardrail/prompt/release-state/fixture/agent-state mutation flag")
            _reject_mutation_flags(child, child_path, errors)
        return

    if isinstance(value, list):
        for index, child in enumerate(value):
            _reject_mutation_flags(child, f"{path}[{index}]", errors)


def _non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and any(isinstance(item, str) and item.strip() for item in value)


__all__ = [
    "ReplayPlanValidationResult",
    "load_replay_plan",
    "validate_replay_plan",
    "validate_replay_plan_file",
]
