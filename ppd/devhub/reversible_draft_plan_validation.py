"""Validation for attended DevHub reversible draft plans.

The validator is intentionally fixture-friendly and side-effect free. It accepts
plain dictionaries so draft-plan producers can run the same checks before any
Playwright session is opened.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PureWindowsPath
from typing import Any, Iterable, Mapping, Sequence


PRIVATE_VALUE_KEYS = {
    "password",
    "ssn",
    "social_security_number",
    "date_of_birth",
    "dob",
    "card_number",
    "credit_card",
    "cvv",
    "cvc",
    "bank_account",
    "routing_number",
    "private_value",
    "raw_private_value",
    "secret",
    "token",
}

LOCAL_PATH_KEYS = {
    "path",
    "file_path",
    "local_path",
    "source_path",
    "attachment_path",
    "upload_path",
}

CONSEQUENTIAL_ACTIONS = {
    "official_upload": {
        "upload",
        "upload_correction",
        "attach_document",
        "official_attach",
        "official_upload",
    },
    "submission": {
        "submit",
        "submit_application",
        "submit_permit_request",
        "purchase_trade_permit",
    },
    "certification": {
        "certify",
        "acknowledge",
        "sign_certification",
        "accept_certification",
    },
    "scheduling": {
        "schedule",
        "schedule_inspection",
        "book_inspection",
    },
    "cancellation": {
        "cancel",
        "withdraw",
        "void",
        "cancel_inspection",
        "withdraw_application",
    },
    "payment_detail_entry": {
        "enter_payment_details",
        "enter_card",
        "save_payment_method",
        "payment_detail_entry",
    },
    "final_payment_execution": {
        "pay",
        "submit_payment",
        "execute_payment",
        "final_payment_execution",
        "confirm_payment",
    },
}

ALLOWED_REVERSIBLE_ACTIONS = {
    "address_search",
    "property_search",
    "select_permit_type",
    "fill_field",
    "set_checkbox",
    "set_radio",
    "select_option",
    "save_draft",
    "local_preview",
}


@dataclass(frozen=True)
class DraftPlanIssue:
    code: str
    message: str
    location: str


def validate_reversible_draft_plan(plan: Mapping[str, Any]) -> list[DraftPlanIssue]:
    """Return validation issues for a proposed attended DevHub draft plan."""

    issues: list[DraftPlanIssue] = []

    user_facts = _sequence(plan.get("required_user_facts"))
    if not user_facts:
        issues.append(
            DraftPlanIssue(
                "missing_user_facts",
                "Reversible draft plans must name the user facts used for every fillable value.",
                "required_user_facts",
            )
        )

    source_evidence_ids = _sequence(plan.get("source_evidence_ids"))
    if not source_evidence_ids or any(not _non_empty_text(item) for item in source_evidence_ids):
        issues.append(
            DraftPlanIssue(
                "missing_source_evidence_ids",
                "Reversible draft plans must cite public source evidence IDs.",
                "source_evidence_ids",
            )
        )

    preview = plan.get("preview")
    if not isinstance(preview, Mapping) or not preview.get("redacted") or not _sequence(preview.get("fields")):
        issues.append(
            DraftPlanIssue(
                "absent_preview",
                "A redacted user-visible preview with field mappings is required before attended draft work.",
                "preview",
            )
        )

    steps = _sequence(plan.get("steps"))
    if not steps:
        issues.append(
            DraftPlanIssue(
                "missing_steps",
                "A reversible draft plan must contain explicit draft steps.",
                "steps",
            )
        )

    for index, step in enumerate(steps):
        location = f"steps[{index}]"
        if not isinstance(step, Mapping):
            issues.append(DraftPlanIssue("invalid_step", "Each draft step must be an object.", location))
            continue

        action = _normalized_text(step.get("action") or step.get("action_type") or step.get("kind"))
        consequence = _consequential_category(action)
        if consequence is not None:
            issues.append(
                DraftPlanIssue(
                    consequence,
                    "Consequential DevHub actions are not reversible draft work and require manual attended handling.",
                    f"{location}.action",
                )
            )
        elif action and action not in ALLOWED_REVERSIBLE_ACTIONS:
            issues.append(
                DraftPlanIssue(
                    "unsupported_reversible_action",
                    "Only known read-only or reversible draft actions may appear in this plan.",
                    f"{location}.action",
                )
            )

        if _is_official_upload_step(step):
            issues.append(
                DraftPlanIssue(
                    "official_upload",
                    "Official upload or attachment staging is consequential and cannot be part of a reversible draft plan.",
                    location,
                )
            )

        selector_issue = _selector_issue(step)
        if selector_issue is not None:
            issues.append(
                DraftPlanIssue(
                    "ambiguous_selector",
                    selector_issue,
                    f"{location}.selector",
                )
            )

        if _step_uses_private_value(step):
            issues.append(
                DraftPlanIssue(
                    "private_value",
                    "Draft plans must reference redacted user fact IDs, not contain private values or payment details.",
                    location,
                )
            )

        private_path_location = _private_path_location(step, location)
        if private_path_location is not None:
            issues.append(
                DraftPlanIssue(
                    "local_private_path",
                    "Committed draft plans must not contain local private file paths.",
                    private_path_location,
                )
            )

    for location, value in _walk(plan):
        key = location.rsplit(".", 1)[-1].lower()
        if key in PRIVATE_VALUE_KEYS and _non_empty_text(value):
            issues.append(
                DraftPlanIssue(
                    "private_value",
                    "Private values and payment details must not be embedded in a draft plan.",
                    location,
                )
            )
        if key in LOCAL_PATH_KEYS and isinstance(value, str) and _looks_like_private_local_path(value):
            issues.append(
                DraftPlanIssue(
                    "local_private_path",
                    "Local private paths must stay out of committed plans and fixtures.",
                    location,
                )
            )

    return _dedupe_issues(issues)


def assert_reversible_draft_plan(plan: Mapping[str, Any]) -> None:
    """Raise ValueError when a draft plan is not safe reversible work."""

    issues = validate_reversible_draft_plan(plan)
    if issues:
        detail = "; ".join(f"{issue.code} at {issue.location}" for issue in issues)
        raise ValueError(f"Invalid DevHub reversible draft plan: {detail}")


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, list) or isinstance(value, tuple):
        return value
    return ()


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _normalized_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _consequential_category(action: str) -> str | None:
    for category, actions in CONSEQUENTIAL_ACTIONS.items():
        if action in actions:
            return category
    return None


def _is_official_upload_step(step: Mapping[str, Any]) -> bool:
    target = _normalized_text(step.get("target") or step.get("surface") or step.get("destination"))
    if target in {"official_record", "official_attachment", "official_upload"}:
        return True
    if step.get("official_record") is True or step.get("official") is True:
        return True
    return False


def _selector_issue(step: Mapping[str, Any]) -> str | None:
    selectors = step.get("selectors")
    selector = step.get("selector")
    confidence = step.get("selector_confidence")

    if isinstance(selectors, Sequence) and not isinstance(selectors, str):
        concrete = [item for item in selectors if _non_empty_text(item)]
        if len(concrete) != 1:
            return "Each draft step must identify exactly one stable selector."

    if not _non_empty_text(selector) and not (
        isinstance(selectors, Sequence)
        and not isinstance(selectors, str)
        and len([item for item in selectors if _non_empty_text(item)]) == 1
    ):
        return "Each draft step must identify one non-empty stable selector."

    if confidence in {"ambiguous", "low", "unknown"}:
        return "Low-confidence or ambiguous selectors are not allowed for reversible draft plans."

    if selector in {"button", "input", "select", "textarea", "a", "[role=button]"}:
        return "Generic selectors are ambiguous and must be replaced with stable accessible or test selectors."

    return None


def _step_uses_private_value(step: Mapping[str, Any]) -> bool:
    if "value" in step and _non_empty_text(step.get("value")):
        return True
    if "raw_value" in step and _non_empty_text(step.get("raw_value")):
        return True
    if "payment_details" in step or "card_number" in step or "cvv" in step:
        return True
    return False


def _private_path_location(step: Mapping[str, Any], base_location: str) -> str | None:
    for key in LOCAL_PATH_KEYS:
        value = step.get(key)
        if isinstance(value, str) and _looks_like_private_local_path(value):
            return f"{base_location}.{key}"
    return None


def _looks_like_private_local_path(value: str) -> bool:
    text = value.strip()
    lower = text.lower()
    if lower.startswith("file://"):
        return True
    if lower.startswith(("/home/", "/users/", "/private/", "/var/folders/")):
        return True
    if text.startswith("~/"):
        return True
    windows = PureWindowsPath(text)
    if windows.drive and "users" in [part.lower() for part in windows.parts]:
        return True
    return False


def _walk(value: Any, location: str = "plan") -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_location = f"{location}.{key}"
            yield child_location, child
            yield from _walk(child, child_location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_location = f"{location}[{index}]"
            yield child_location, child
            yield from _walk(child, child_location)


def _dedupe_issues(issues: Sequence[DraftPlanIssue]) -> list[DraftPlanIssue]:
    seen: set[tuple[str, str]] = set()
    deduped: list[DraftPlanIssue] = []
    for issue in issues:
        key = (issue.code, issue.location)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(issue)
    return deduped
