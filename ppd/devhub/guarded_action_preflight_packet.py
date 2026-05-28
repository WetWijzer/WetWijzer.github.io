"""Fixture-first guarded DevHub action preflight packet validation.

This module validates metadata-only packets for candidate DevHub draft actions.
It does not import Playwright, launch a browser, authenticate, save session state,
upload, submit, certify, schedule, cancel, pay, or persist private artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ppd.actions import ActionClass, ActionKind, classify_action
from ppd.surfaces.registry import AutomationMode, SurfaceKind, ppd_surface_registry


MINIMUM_SELECTOR_CONFIDENCE = 0.85
REQUIRED_STOP_BEFORE_ACTIONS = frozenset(
    {
        "official_upload",
        "submit_application",
        "certify_statement",
        "cancel_request",
        "schedule_inspection",
        "pay_fee",
        "enter_payment_details",
    }
)
FORBIDDEN_PACKET_KEYS = frozenset(
    {
        "auth_state",
        "browser_context",
        "card_number",
        "cookie",
        "cookies",
        "credential",
        "credentials",
        "cvv",
        "har",
        "password",
        "payment_details",
        "private_value",
        "raw_authenticated_html",
        "screenshot",
        "session_file",
        "session_state",
        "storage_state",
        "trace",
        "token",
    }
)


@dataclass(frozen=True)
class GuardedActionPreflightResult:
    """Validation result for one guarded action preflight packet."""

    valid: bool
    action_id: str
    surface_id: str
    action_kind: str
    action_class: str
    selector_confidence: float
    stop_before_actions: tuple[str, ...]
    issues: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "action_id": self.action_id,
            "surface_id": self.surface_id,
            "action_kind": self.action_kind,
            "action_class": self.action_class,
            "selector_confidence": self.selector_confidence,
            "stop_before_actions": list(self.stop_before_actions),
            "issues": list(self.issues),
        }


def validate_guarded_action_preflight_packet(
    packet: Mapping[str, Any],
    minimum_selector_confidence: float = MINIMUM_SELECTOR_CONFIDENCE,
) -> GuardedActionPreflightResult:
    """Validate a metadata-only preflight packet for a reversible draft action."""

    issues: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            issues.append(message)

    private_paths = _private_key_paths(packet)
    require(not private_paths, "packet contains private or authenticated artifact keys: " + ", ".join(private_paths))

    require(packet.get("fixture_only") is True, "packet must be explicitly fixture_only")
    require(packet.get("uses_live_devhub") is False, "packet must not use live DevHub")
    require(packet.get("playwright_executed") is False, "packet must not execute Playwright")
    require(packet.get("stores_authenticated_artifacts") is False, "packet must not store authenticated artifacts")

    action = _as_mapping(packet.get("action_classification"))
    action_id = _string(action.get("action_id"))
    description = _string(action.get("description"))
    policy = classify_action(description)
    require(bool(action_id), "action_classification.action_id is required")
    require(policy.kind is ActionKind.REVERSIBLE_DRAFT, "action description must classify as reversible_draft")
    require(policy.action_class is ActionClass.REVERSIBLE_DRAFT, "action class must be reversible_draft")
    require(action.get("kind") == policy.kind.value, "packet kind must match classifier output")
    require(action.get("action_class") == policy.action_class.value, "packet action_class must match classifier output")
    require(action.get("may_execute_after_preflight") is True, "reversible draft may execute only after preflight gates pass")
    require(action.get("executes_consequential_action") is False, "draft packet must not execute consequential action")

    surface_evidence = _as_mapping(packet.get("surface_registry_evidence"))
    surface_id = _string(surface_evidence.get("surface_id"))
    binding = _surface_binding(surface_id)
    require(binding is not None, f"surface {surface_id or ''!r} must exist in the PP&D surface registry")
    if binding is not None:
        require(binding.surface is SurfaceKind.DEVHUB_DRAFT, "packet must bind to the DevHub draft surface")
        require(binding.automation_mode is AutomationMode.ATTENDED_REVERSIBLE, "DevHub draft surface must be attended_reversible")
        required_guardrails = set(binding.required_guardrails)
        supplied_guardrails = set(_string_list(surface_evidence.get("required_guardrails")))
        missing_guardrails = sorted(required_guardrails - supplied_guardrails)
        require(not missing_guardrails, "surface evidence omits registry guardrails: " + ", ".join(missing_guardrails))

    evidence_ids = _string_list(packet.get("source_evidence_ids"))
    require(len(evidence_ids) >= 2, "at least two source evidence ids are required")
    require(all(value.startswith("ppd-src-") for value in evidence_ids), "source evidence ids must use committed PP&D source ids")

    selectors = _as_mapping(packet.get("selector_confidence"))
    overall_confidence = selectors.get("overall")
    require(_is_number(overall_confidence), "selector_confidence.overall must be numeric")
    selector_confidence = float(overall_confidence) if _is_number(overall_confidence) else 0.0
    require(selector_confidence >= minimum_selector_confidence, "selector confidence is below the guarded action threshold")
    require(bool(_as_list(selectors.get("evidence"))), "selector confidence evidence is required")

    required_facts = _as_list(packet.get("required_user_facts"))
    require(bool(required_facts), "required user facts must be listed")
    for index, fact in enumerate(required_facts):
        fact_map = _as_mapping(fact)
        require(_string(fact_map.get("fact_id")) != "", f"required_user_facts[{index}] must include fact_id")
        require(fact_map.get("status") in {"known", "confirmed", "not_required_for_fixture"}, f"required_user_facts[{index}] has unsupported status")
        require(bool(_string_list(fact_map.get("source_evidence_ids"))), f"required_user_facts[{index}] must cite source evidence")

    attendance = _as_mapping(packet.get("attendance_requirement"))
    require(attendance.get("requires_user_attendance") is True, "DevHub draft packet must require user attendance")
    require(attendance.get("manual_login_handoff") is True, "manual login handoff must be represented")
    require(attendance.get("credential_storage") == "forbidden", "credential storage must be forbidden")
    require(attendance.get("session_artifact_storage") == "forbidden", "session artifact storage must be forbidden")

    preview = _as_mapping(packet.get("preview_metadata"))
    require(preview.get("preview_only") is True, "preview metadata must be preview_only")
    require(preview.get("contains_private_values") is False, "preview metadata must not contain private values")
    require(preview.get("stores_file_paths") is False, "preview metadata must not store file paths")
    require(preview.get("browser_launch_allowed") is False, "preview metadata must not allow browser launch")
    require(_string(preview.get("redaction_policy")) != "", "preview metadata must include a redaction policy")

    checkpoints = _as_list(packet.get("stop_before_consequential_checkpoints"))
    represented = {_string(_as_mapping(checkpoint).get("action_kind")) for checkpoint in checkpoints}
    missing_checkpoints = sorted(REQUIRED_STOP_BEFORE_ACTIONS - represented)
    require(not missing_checkpoints, "missing stop-before checkpoints: " + ", ".join(missing_checkpoints))
    for checkpoint in checkpoints:
        checkpoint_map = _as_mapping(checkpoint)
        action_kind = _string(checkpoint_map.get("action_kind"))
        require(checkpoint_map.get("stop_before_selector_activation") is True, f"checkpoint {action_kind!r} must stop before selector activation")
        require(checkpoint_map.get("requires_exact_user_confirmation") is True, f"checkpoint {action_kind!r} must require exact user confirmation")
        require(checkpoint_map.get("automated_execution_allowed") is False, f"checkpoint {action_kind!r} must forbid automated execution")

    return GuardedActionPreflightResult(
        valid=not issues,
        action_id=action_id,
        surface_id=surface_id,
        action_kind=policy.kind.value,
        action_class=policy.action_class.value,
        selector_confidence=selector_confidence,
        stop_before_actions=tuple(sorted(represented)),
        issues=tuple(issues),
    )


def require_valid_guarded_action_preflight_packet(packet: Mapping[str, Any]) -> GuardedActionPreflightResult:
    """Return the validation result or raise ValueError with all packet issues."""

    result = validate_guarded_action_preflight_packet(packet)
    if not result.valid:
        raise ValueError("invalid guarded action preflight packet: " + "; ".join(result.issues))
    return result


def _surface_binding(surface_id: str):
    for binding in ppd_surface_registry():
        if binding.surface.value == surface_id:
            return binding
    return None


def _private_key_paths(value: Any, prefix: str = "") -> tuple[str, ...]:
    paths: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            if key_text.lower() in FORBIDDEN_PACKET_KEYS:
                paths.append(path)
            paths.extend(_private_key_paths(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            paths.extend(_private_key_paths(item, path))
    return tuple(paths)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def _string(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _string_list(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
