"""Validation for attended DevHub reversible draft plans.

The validator is intentionally fixture-friendly and side-effect free. It accepts
plain dictionaries so draft-plan producers can run the same checks before any
Playwright session is opened.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import PureWindowsPath
from typing import Any
from urllib.parse import urlparse


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
    "field_value",
    "secret",
    "token",
}

PRIVATE_STEP_VALUE_KEYS = {
    "value",
    "raw_value",
    "field_value",
    "default_value",
    "input_value",
    "payment_details",
}

LOCAL_PATH_KEYS = {
    "path",
    "file_path",
    "local_path",
    "source_path",
    "attachment_path",
    "upload_path",
}

BROWSER_ARTIFACT_KEYS = {
    "browser_state": "browser_state",
    "storage_state": "browser_state",
    "session_state": "browser_state",
    "cookies": "cookies",
    "cookie": "cookies",
    "cookie_jar": "cookies",
    "screenshot": "screenshot",
    "screenshots": "screenshot",
    "screenshot_path": "screenshot",
    "trace": "trace",
    "traces": "trace",
    "trace_path": "trace",
    "har": "har_data",
    "har_data": "har_data",
    "har_path": "har_data",
    "network_har": "har_data",
}

CONSEQUENTIAL_ACTIONS = {
    "draft_persistence": {
        "save",
        "save_draft",
        "save_and_continue",
        "continue",
        "continue_application",
        "continue_draft",
        "next",
        "next_step",
    },
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
    "local_preview",
}

SIDE_EFFECT_WORDS = {
    "save": "draft_persistence",
    "continue": "draft_persistence",
    "submit": "submission",
    "certify": "certification",
    "upload": "official_upload",
    "payment": "payment_detail_entry",
    "pay": "final_payment_execution",
    "schedule": "scheduling",
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
        consequence = _consequential_category(action) or _step_side_effect_category(step)
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
            issues.append(DraftPlanIssue("ambiguous_selector", selector_issue, f"{location}.selector"))

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
        key = _normalized_text(location.rsplit(".", 1)[-1])
        if key in PRIVATE_VALUE_KEYS and _present(value):
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
        artifact_code = BROWSER_ARTIFACT_KEYS.get(key)
        if artifact_code is not None and _present(value):
            issues.append(
                DraftPlanIssue(
                    artifact_code,
                    "Browser state, cookies, screenshots, traces, and HAR data must not be embedded in draft packets.",
                    location,
                )
            )
        if isinstance(value, str) and _is_live_auth_url(location, value):
            issues.append(
                DraftPlanIssue(
                    "authenticated_live_url",
                    "Live DevHub URLs requiring authentication must not be embedded in reversible draft packets.",
                    location,
                )
            )

    issues.extend(_authenticated_url_issues(plan))
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


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _normalized_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _consequential_category(action: str) -> str | None:
    for category, actions in CONSEQUENTIAL_ACTIONS.items():
        if action in actions:
            return category
    return None


def _step_side_effect_category(step: Mapping[str, Any]) -> str | None:
    text_parts = []
    for key in ("action", "action_type", "kind", "label", "button_text", "aria_label", "description"):
        value = step.get(key)
        if isinstance(value, str):
            text_parts.append(_normalized_text(value))
    text = "_".join(text_parts)
    for word, category in SIDE_EFFECT_WORDS.items():
        if word in text:
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
    confidence = _normalized_text(step.get("selector_confidence"))

    if isinstance(selectors, Sequence) and not isinstance(selectors, str):
        concrete = [item for item in selectors if _non_empty_text(item)]
        if len(concrete) != 1:
            return "Each draft step must identify exactly one stable selector."
        selector = concrete[0]

    if not _non_empty_text(selector):
        return "Each draft step must identify one non-empty stable selector."

    if confidence != "high":
        return "Low-confidence, ambiguous, or unverified selectors are not allowed for reversible draft plans."

    if _normalized_text(selector) in {"button", "input", "select", "textarea", "a", "[role=button]"}:
        return "Generic selectors are ambiguous and must be replaced with stable accessible or test selectors."

    return None


def _step_uses_private_value(step: Mapping[str, Any]) -> bool:
    for key in PRIVATE_STEP_VALUE_KEYS:
        if key in step and _present(step.get(key)):
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


def _is_live_auth_url(location: str, value: str) -> bool:
    parsed = urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    normalized_location = _normalized_text(location)
    if any(marker in normalized_location for marker in ("auth", "login", "session", "live_url", "current_url")):
        return True
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    if "devhub.portlandoregon.gov" not in host:
        return False
    return any(marker in path for marker in ("/account", "/application", "/dashboard", "/login", "/permit", "/project"))


def _authenticated_url_issues(value: Any, location: str = "plan") -> list[DraftPlanIssue]:
    issues: list[DraftPlanIssue] = []
    if isinstance(value, Mapping):
        requires_auth = any(
            _normalized_text(key) in {"requires_auth", "auth_required", "authenticated", "login_required"} and child is True
            for key, child in value.items()
        )
        for key, child in value.items():
            child_location = f"{location}.{key}"
            if requires_auth and isinstance(child, str) and _looks_like_url(child):
                issues.append(
                    DraftPlanIssue(
                        "authenticated_live_url",
                        "Live URLs requiring authentication must not be embedded in reversible draft packets.",
                        child_location,
                    )
                )
            issues.extend(_authenticated_url_issues(child, child_location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            issues.extend(_authenticated_url_issues(child, f"{location}[{index}]"))
    return issues


def _looks_like_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


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
