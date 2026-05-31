"""Offline DevHub attended read-only preflight packet v2 builder.

This module is fixture-first by design. It does not open DevHub, launch a
browser, create authentication state, store traces, or perform live automation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PACKET_VERSION = "devhub_attended_readonly_preflight_packet_v2"
CONSUMES_PACKET_VERSION = "devhub_post_preview_human_review_handoff_packet_v2"

ALLOWED_READ_ONLY_DESTINATION_CATEGORIES = [
    {
        "category": "devhub_public_landing_and_help",
        "description": "Public DevHub landing, help, FAQ, and sign-in guidance pages used only for orientation.",
        "read_only_limit": "Observe text, headings, links, and navigation labels only.",
    },
    {
        "category": "authenticated_home_or_dashboard",
        "description": "User-visible DevHub home, dashboard, or equivalent account landing page after manual login.",
        "read_only_limit": "Observe account-scoped navigation labels, high-level status labels, and destination availability only.",
    },
    {
        "category": "existing_request_status_summary",
        "description": "Existing application, permit, inspection, or request summary pages selected by the attending user.",
        "read_only_limit": "Observe status labels and non-sensitive structural fields only after user directs the worker to the item.",
    },
    {
        "category": "message_or_notification_summary",
        "description": "Account notification or message list summaries visible after manual navigation by the attending user.",
        "read_only_limit": "Observe non-private labels, dates, and workflow states; do not capture message bodies unless separately reviewed and redacted.",
    },
    {
        "category": "payment_due_summary_without_payment_entry",
        "description": "Fee or balance summary screens where no payment method is entered and no payment action is taken.",
        "read_only_limit": "Observe amount labels and due-state labels only; never enter payment details or continue into checkout.",
    },
]

REQUIRED_USER_ATTENDANCE_STATEMENTS = [
    "The user remains present for the entire DevHub browser run.",
    "The user performs all credential, MFA, CAPTCHA, account recovery, and security-prompt steps manually.",
    "The user chooses each authenticated destination before the worker observes it.",
    "The user can stop the run at any time, and the worker must stop immediately.",
    "The worker does not treat read-only observation as permission to submit, upload, schedule, certify, cancel, pay, or modify records.",
]

REDACTION_REQUIREMENTS = [
    "Do not record credentials, passwords, one-time codes, recovery answers, cookies, tokens, browser profiles, auth state, screenshots, traces, HAR files, or downloaded private documents.",
    "Redact names, email addresses, phone numbers, mailing addresses, tax account details, permit applicant details, contractor license details, property-owner details, and private document names unless the user explicitly asks to discuss a value in chat.",
    "Record only structural UI facts needed for guardrails, such as page role, visible heading category, read-only destination category, and blocked action labels.",
    "Replace private identifiers with stable placeholders such as REDACTED_CASE_ID, REDACTED_ADDRESS, REDACTED_PERSON, and REDACTED_AMOUNT when an offline fixture needs shape-preserving examples.",
    "Do not persist local private file paths, raw authenticated page values, payment details, or uploaded-document metadata.",
]

ABORT_CONDITIONS = [
    {
        "condition": "mfa_or_security_prompt_presented",
        "required_response": "Pause automation-like observation. The attending user may complete the prompt manually, or the run is aborted.",
    },
    {
        "condition": "captcha_or_bot_challenge_presented",
        "required_response": "Abort worker interaction until the attending user resolves the challenge manually outside worker control.",
    },
    {
        "condition": "account_creation_or_registration_path_presented",
        "required_response": "Abort. The worker must not create accounts, accept terms, enroll MFA, or submit registration details.",
    },
    {
        "condition": "payment_entry_or_checkout_path_presented",
        "required_response": "Abort before entering payment details, selecting payment methods, or continuing to final payment submission.",
    },
    {
        "condition": "upload_submit_certify_schedule_cancel_or_final_action_presented",
        "required_response": "Abort before consequential action controls are activated or clicked.",
    },
    {
        "condition": "download_or_private_document_view_required",
        "required_response": "Abort unless a separate redacted offline review packet is prepared without storing private artifacts.",
    },
    {
        "condition": "user_absent_or_uncertain",
        "required_response": "Abort immediately because attendance is required for all authenticated DevHub observation.",
    },
]

NO_PRIVATE_ARTIFACT_COMMITMENTS = [
    "No DevHub browser is opened by this preflight packet.",
    "No credentials, cookies, tokens, local storage, browser profiles, auth state, traces, HAR files, screenshots, videos, raw crawl output, or downloaded private documents are created or stored.",
    "No live authenticated automation is performed during packet construction or validation.",
    "Only committed deterministic fixtures under ppd/tests/fixtures are used for offline validation.",
]

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/devhub/attended_readonly_preflight_packet_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_devhub_attended_readonly_preflight_packet_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]


def load_post_preview_handoff_packet_v2(path: str | Path) -> dict[str, Any]:
    """Load the committed post-preview handoff fixture from disk."""

    packet_path = Path(path)
    with packet_path.open("r", encoding="utf-8") as packet_file:
        packet = json.load(packet_file)
    if not isinstance(packet, dict):
        raise ValueError("post-preview handoff packet must be a JSON object")
    return packet


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _handoff_review_items(handoff_packet: dict[str, Any]) -> list[dict[str, Any]]:
    review_items = _as_list(handoff_packet.get("post_preview_human_review_items"))
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(review_items, start=1):
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "order": index,
                "review_item_id": str(item.get("review_item_id", f"review-item-{index}")),
                "source_packet_section": str(item.get("source_packet_section", "post_preview_human_review_items")),
                "manual_readiness_check": str(item.get("manual_readiness_check", "Confirm the item remains read-only and user-attended before any DevHub observation.")),
                "expected_evidence": _as_list(item.get("expected_evidence")),
                "blocks_if_missing": bool(item.get("blocks_if_missing", True)),
            }
        )
    return normalized


def build_attended_readonly_preflight_packet_v2(handoff_packet: dict[str, Any]) -> dict[str, Any]:
    """Build an offline-only preflight packet from a post-preview handoff packet."""

    handoff_version = handoff_packet.get("packet_version")
    if handoff_version != CONSUMES_PACKET_VERSION:
        raise ValueError(
            "expected packet_version "
            f"{CONSUMES_PACKET_VERSION!r}, got {handoff_version!r}"
        )

    handoff_items = _handoff_review_items(handoff_packet)
    ordered_manual_login_readiness_checks = [
        {
            "order": 1,
            "check_id": "offline_fixture_source_confirmed",
            "check": "Confirm the preflight is built only from a committed post-preview handoff fixture.",
            "required_result": "The packet input is local JSON under ppd/tests/fixtures and contains no private DevHub values.",
        },
        {
            "order": 2,
            "check_id": "user_attendance_confirmed_before_opening_browser",
            "check": "Confirm the user will be present before any later DevHub browser run starts.",
            "required_result": "The user is available to control login, MFA, CAPTCHA, destination selection, and stop decisions.",
        },
        {
            "order": 3,
            "check_id": "manual_login_only",
            "check": "Confirm all login and security prompts remain manual user actions.",
            "required_result": "The worker will not request, enter, store, replay, or derive credentials or auth state.",
        },
        {
            "order": 4,
            "check_id": "read_only_destination_scope_selected",
            "check": "Confirm the later destination is one of the allowed read-only destination categories.",
            "required_result": "Any destination outside the allowed categories blocks the run before navigation.",
        },
        {
            "order": 5,
            "check_id": "consequential_action_abort_rules_loaded",
            "check": "Confirm abort rules cover MFA, CAPTCHA, account creation, payment, upload, submission, certification, scheduling, cancellation, and private downloads.",
            "required_result": "The worker stops before any consequential path or private artifact creation.",
        },
        {
            "order": 6,
            "check_id": "handoff_review_items_resolved",
            "check": "Confirm all blocking post-preview human review handoff items have a manual readiness answer.",
            "required_result": "Blocking handoff items must be resolved before any later attended DevHub observation.",
            "handoff_review_item_count": len(handoff_items),
        },
    ]

    return {
        "packet_version": PACKET_VERSION,
        "consumes_packet_version": CONSUMES_PACKET_VERSION,
        "source_handoff_packet_id": str(handoff_packet.get("packet_id", "post-preview-handoff-fixture")),
        "mode": "offline_fixture_first_preflight_only",
        "live_devhub_opened": False,
        "auth_state_created": False,
        "browser_or_session_artifacts_created": False,
        "live_automation_performed": False,
        "ordered_manual_login_readiness_checks": ordered_manual_login_readiness_checks,
        "post_preview_handoff_review_items": handoff_items,
        "allowed_read_only_destination_categories": ALLOWED_READ_ONLY_DESTINATION_CATEGORIES,
        "required_user_attendance_statements": REQUIRED_USER_ATTENDANCE_STATEMENTS,
        "redaction_requirements": REDACTION_REQUIREMENTS,
        "abort_conditions": ABORT_CONDITIONS,
        "no_private_artifact_commitments": NO_PRIVATE_ARTIFACT_COMMITMENTS,
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
    }


def build_from_fixture(path: str | Path) -> dict[str, Any]:
    """Load a post-preview handoff fixture and build the v2 preflight packet."""

    return build_attended_readonly_preflight_packet_v2(load_post_preview_handoff_packet_v2(path))
