"""Validation for PP&D agent readiness final smoke packets.

The validator is intentionally deterministic and fixture-friendly. It does not run
LLMs, DevHub, crawlers, processors, or browser automation; it only inspects a
packet that claims readiness evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping


_PATH_RE = re.compile(
    r"(?i)(/home/[^\s'\"]+|/users/[^\s'\"]+|c:\\\\users\\\\[^\s'\"]+|~/(?:[^\s'\"]+))"
)
_PRIVATE_FACT_KEY_RE = re.compile(
    r"(?i)(applicant|owner|tenant|contractor|email|phone|address|taxlot|permit_number|case_number|devhub_id|license|ssn|dob|payment|card|bank|routing)"
)
_RAW_AUTH_KEY_RE = re.compile(
    r"(?i)(cookie|session|token|authorization|auth_state|password|secret|credential|csrf|bearer|saml|oauth|mfa)"
)
_LIVE_EXECUTION_RE = re.compile(
    r"(?i)\b(live|actually|successfully|executed|ran|called|invoked|submitted|uploaded|paid|scheduled|crawled|processed|logged in|authenticated)\b.*\b(llm|devhub|crawler|processor|playwright|browser|portal|openai|api)\b|\b(llm|devhub|crawler|processor|playwright|browser|portal|openai|api)\b.*\b(live|actually|successfully|executed|ran|called|invoked|submitted|uploaded|paid|scheduled|crawled|processed|logged in|authenticated)\b"
)
_GUARANTEE_RE = re.compile(
    r"(?i)\b(guarantee[sd]?|certain|assured|will be approved|will be issued|permit will issue|approval is guaranteed|legally sufficient|compliant as a matter of law|no review issues|outcome is guaranteed)\b"
)
_MUTATION_FLAG_NAMES = {
    "prompt_mutation_enabled",
    "guardrail_mutation_enabled",
    "surface_registry_mutation_enabled",
    "surface_registry_write_enabled",
    "agent_state_mutation_enabled",
    "agent_state_write_enabled",
    "active_prompt_mutation",
    "active_guardrail_mutation",
    "active_surface_registry_mutation",
    "active_agent_state_mutation",
}
_CONSEQUENTIAL_ACTIONS = {
    "submit",
    "submission",
    "certify",
    "certification",
    "upload",
    "official_upload",
    "payment",
    "pay",
    "purchase",
    "schedule",
    "cancel",
    "withdraw",
    "extension",
    "reactivation",
    "account_creation",
    "password_recovery",
    "mfa",
    "captcha",
}


@dataclass(frozen=True)
class SmokePacketIssue:
    """A deterministic readiness packet validation issue."""

    code: str
    path: str
    message: str


class SmokePacketValidationError(ValueError):
    """Raised when a final smoke packet fails readiness validation."""

    def __init__(self, issues: Iterable[SmokePacketIssue]) -> None:
        self.issues = tuple(issues)
        detail = "; ".join(f"{issue.path}: {issue.code}" for issue in self.issues)
        super().__init__(detail)


def validate_final_smoke_packet(packet: Mapping[str, Any]) -> None:
    """Validate that a final smoke packet is safe to accept as readiness evidence.

    A valid packet must be cited, reviewer-owned, complete about prompts/refusals
    and previews, explicit about blocked-action explanations, privacy preserving,
    and free of live execution claims, outcome guarantees, enabled consequential
    controls, or active mutation flags.
    """

    issues = list(iter_final_smoke_packet_issues(packet))
    if issues:
        raise SmokePacketValidationError(issues)


def iter_final_smoke_packet_issues(packet: Mapping[str, Any]) -> tuple[SmokePacketIssue, ...]:
    issues: list[SmokePacketIssue] = []

    scenarios = packet.get("smoke_scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        issues.append(
            SmokePacketIssue(
                "missing_smoke_scenarios",
                "smoke_scenarios",
                "Final readiness packets must include at least one smoke scenario.",
            )
        )
        scenarios = []

    reviewer_owners = packet.get("reviewer_owners")
    if _empty_collection(reviewer_owners):
        issues.append(
            SmokePacketIssue(
                "missing_reviewer_owners",
                "reviewer_owners",
                "Final readiness packets must identify reviewer owners.",
            )
        )

    for index, scenario in enumerate(scenarios):
        path = f"smoke_scenarios[{index}]"
        if not isinstance(scenario, Mapping):
            issues.append(SmokePacketIssue("invalid_smoke_scenario", path, "Smoke scenario must be an object."))
            continue
        _validate_scenario(scenario, path, issues)

    _validate_blocked_actions(packet.get("blocked_actions"), "blocked_actions", issues)
    _validate_consequential_controls(packet.get("consequential_controls"), "consequential_controls", issues)
    _scan_value(packet, "$", issues)
    return tuple(issues)


def _validate_scenario(scenario: Mapping[str, Any], path: str, issues: list[SmokePacketIssue]) -> None:
    if _empty_collection(scenario.get("citations")) and _empty_collection(scenario.get("source_evidence_ids")):
        issues.append(
            SmokePacketIssue(
                "uncited_smoke_scenario",
                path,
                "Every smoke scenario must cite source evidence.",
            )
        )

    for field in ("expected_prompts", "expected_refusals", "expected_previews"):
        if _empty_collection(scenario.get(field)):
            issues.append(
                SmokePacketIssue(
                    f"missing_{field}",
                    f"{path}.{field}",
                    f"Smoke scenario must include {field}.",
                )
            )

    if not _nonempty_text(scenario.get("reviewer_owner")):
        issues.append(
            SmokePacketIssue(
                "missing_scenario_reviewer_owner",
                f"{path}.reviewer_owner",
                "Each smoke scenario must identify a reviewer owner.",
            )
        )

    _validate_blocked_actions(scenario.get("blocked_actions"), f"{path}.blocked_actions", issues)


def _validate_blocked_actions(value: Any, path: str, issues: list[SmokePacketIssue]) -> None:
    if value is None:
        return
    if not isinstance(value, list):
        issues.append(SmokePacketIssue("invalid_blocked_actions", path, "Blocked actions must be a list."))
        return
    for index, action in enumerate(value):
        action_path = f"{path}[{index}]"
        if not isinstance(action, Mapping):
            issues.append(SmokePacketIssue("invalid_blocked_action", action_path, "Blocked action must be an object."))
            continue
        if not _nonempty_text(action.get("explanation")) and not _nonempty_text(action.get("reason")):
            issues.append(
                SmokePacketIssue(
                    "missing_blocked_action_explanation",
                    action_path,
                    "Blocked actions must include a user-visible explanation or reason.",
                )
            )


def _validate_consequential_controls(value: Any, path: str, issues: list[SmokePacketIssue]) -> None:
    if value is None:
        return
    if not isinstance(value, list):
        issues.append(SmokePacketIssue("invalid_consequential_controls", path, "Consequential controls must be a list."))
        return
    for index, control in enumerate(value):
        control_path = f"{path}[{index}]"
        if not isinstance(control, Mapping):
            issues.append(SmokePacketIssue("invalid_consequential_control", control_path, "Control must be an object."))
            continue
        name = str(control.get("name") or control.get("action") or control.get("type") or "").lower()
        is_consequential = bool(_CONSEQUENTIAL_ACTIONS.intersection(re.split(r"[^a-z0-9_]+", name)))
        if is_consequential and control.get("enabled") is True:
            issues.append(
                SmokePacketIssue(
                    "enabled_consequential_control",
                    control_path,
                    "Consequential controls must not be enabled in readiness smoke packets.",
                )
            )


def _scan_value(value: Any, path: str, issues: list[SmokePacketIssue]) -> None:
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = str(raw_key)
            child_path = f"{path}.{key}" if path != "$" else key
            if key in _MUTATION_FLAG_NAMES and child is True:
                issues.append(
                    SmokePacketIssue(
                        "active_mutation_flag",
                        child_path,
                        "Prompt, guardrail, surface-registry, and agent-state mutation flags must be inactive.",
                    )
                )
            if _RAW_AUTH_KEY_RE.search(key) and _has_substantive_value(child):
                issues.append(
                    SmokePacketIssue(
                        "raw_authenticated_value",
                        child_path,
                        "Readiness packets must not contain raw authenticated values.",
                    )
                )
            if _PRIVATE_FACT_KEY_RE.search(key) and _has_substantive_value(child) and not _is_safe_expected_field(key):
                issues.append(
                    SmokePacketIssue(
                        "private_case_fact",
                        child_path,
                        "Readiness packets must not include private case facts.",
                    )
                )
            _scan_value(child, child_path, issues)
        return

    if isinstance(value, list):
        for index, child in enumerate(value):
            _scan_value(child, f"{path}[{index}]", issues)
        return

    if isinstance(value, str):
        if _PATH_RE.search(value):
            issues.append(
                SmokePacketIssue(
                    "local_private_path",
                    path,
                    "Readiness packets must not include local private file paths.",
                )
            )
        if _LIVE_EXECUTION_RE.search(value):
            issues.append(
                SmokePacketIssue(
                    "live_execution_claim",
                    path,
                    "Readiness packets must not claim live LLM, DevHub, crawler, or processor execution.",
                )
            )
        if _GUARANTEE_RE.search(value):
            issues.append(
                SmokePacketIssue(
                    "outcome_guarantee",
                    path,
                    "Readiness packets must not guarantee legal or permitting outcomes.",
                )
            )


def _empty_collection(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, (list, tuple, set, frozenset, dict)):
        return len(value) == 0
    if isinstance(value, str):
        return not value.strip()
    return False


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _has_substantive_value(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, frozenset, dict)):
        return bool(value)
    return True


def _is_safe_expected_field(key: str) -> bool:
    return key in {"expected_prompts", "expected_refusals", "expected_previews"}
