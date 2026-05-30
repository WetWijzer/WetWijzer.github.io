"""Fixture-first operator briefing packet v2 for PP&D live dry runs.

This module intentionally performs no network, browser, auth, release, or official-action
work. It only assembles and validates deterministic briefing data supplied by fixtures.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

REQUIRED_ATTESTATIONS = (
    "no_live_execution",
    "no_auth_state",
    "no_browser_artifact",
    "no_official_action",
    "no_release_state_mutation",
)

REQUIRED_SOURCE_KEYS = (
    "public_recrawl_live_dry_run_plan_v2",
    "attended_devhub_read_only_live_dry_run_plan_v2",
    "live_readiness_authorization_checklist_packet_v2",
)

ALLOWED_OFFLINE_VALIDATION_COMMANDS = (
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
    ("python3", "-m", "py_compile", "ppd/live_dry_run_operator_briefing_packet_v2.py"),
)


def build_operator_briefing_packet_v2(source_packets: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic operator briefing packet from fixture source packets."""
    missing = [key for key in REQUIRED_SOURCE_KEYS if key not in source_packets]
    if missing:
        raise ValueError(f"missing source packets: {', '.join(missing)}")

    sources = {key: deepcopy(source_packets[key]) for key in REQUIRED_SOURCE_KEYS}
    packet = {
        "packet_id": "fixture-first-live-dry-run-operator-briefing-packet-v2",
        "packet_version": 2,
        "mode": "fixture_first_live_dry_run_briefing_only",
        "source_packets": sources,
        "go_no_go_briefing_notes": [
            {
                "decision": "go_only_for_offline_fixture_validation",
                "note": "Proceed only with deterministic fixture validation and cited briefing review; do not begin live crawling or authenticated browser automation.",
                "citations": [
                    "public_recrawl_live_dry_run_plan_v2.scope",
                    "attended_devhub_read_only_live_dry_run_plan_v2.read_only_boundary",
                    "live_readiness_authorization_checklist_packet_v2.authorization_gate",
                ],
            },
            {
                "decision": "no_go_for_live_execution",
                "note": "Any step that would mutate release state, create auth artifacts, submit official actions, or persist browser traces is outside this packet.",
                "citations": [
                    "attended_devhub_read_only_live_dry_run_plan_v2.prohibited_actions",
                    "live_readiness_authorization_checklist_packet_v2.stop_conditions",
                ],
            },
        ],
        "required_human_attendance_checkpoints": [
            {
                "checkpoint": "pre_run_scope_review",
                "required_attendee": "task supervisor or delegated PP&D operator",
                "purpose": "Confirm fixture inputs, cited source packet versions, and no-live-execution boundaries before validation.",
                "citations": ["live_readiness_authorization_checklist_packet_v2.authorization_gate"],
            },
            {
                "checkpoint": "devhub_read_only_observation",
                "required_attendee": "human operator physically present at the browser session",
                "purpose": "Observe only; do not authenticate, submit, upload, certify, cancel, or persist browser artifacts.",
                "citations": ["attended_devhub_read_only_live_dry_run_plan_v2.human_attendance"],
            },
            {
                "checkpoint": "post_run_artifact_review",
                "required_attendee": "task supervisor or delegated PP&D reviewer",
                "purpose": "Review redacted briefing artifacts and confirm no private session state or raw crawl output was created.",
                "citations": ["public_recrawl_live_dry_run_plan_v2.artifact_policy"],
            },
        ],
        "independent_stop_conditions": [
            "Any prompt for CAPTCHA, MFA, payment, account creation, submission, certification, cancellation, or upload.",
            "Any request to store cookies, tokens, auth state, session files, traces, screenshots, downloads, or raw crawl output.",
            "Any mismatch between fixture packet versions and the cited briefing notes.",
            "Any command or operator instruction that would mutate release state or perform an official action.",
        ],
        "artifact_redaction_expectations": [
            "Briefing artifacts must contain citations and derived notes only, not raw DevHub pages or downloaded documents.",
            "Private identifiers, cookies, tokens, credentials, browser profiles, screenshots, traces, and session storage must be absent.",
            "Public recrawl examples must be fixture excerpts or stable public references, not newly captured live output.",
        ],
        "allowed_offline_validation_commands": [list(command) for command in ALLOWED_OFFLINE_VALIDATION_COMMANDS],
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
    }
    validate_operator_briefing_packet_v2(packet)
    return packet


def validate_operator_briefing_packet_v2(packet: dict[str, Any]) -> None:
    """Validate the briefing packet shape without touching external systems."""
    if packet.get("packet_version") != 2:
        raise ValueError("packet_version must be 2")
    sources = packet.get("source_packets")
    if not isinstance(sources, dict):
        raise ValueError("source_packets must be a mapping")
    missing_sources = [key for key in REQUIRED_SOURCE_KEYS if key not in sources]
    if missing_sources:
        raise ValueError(f"missing source packet citations: {', '.join(missing_sources)}")
    attestations = packet.get("attestations")
    if not isinstance(attestations, dict):
        raise ValueError("attestations must be a mapping")
    missing_attestations = [key for key in REQUIRED_ATTESTATIONS if attestations.get(key) is not True]
    if missing_attestations:
        raise ValueError(f"missing required attestations: {', '.join(missing_attestations)}")
    for section in (
        "go_no_go_briefing_notes",
        "required_human_attendance_checkpoints",
        "independent_stop_conditions",
        "artifact_redaction_expectations",
        "allowed_offline_validation_commands",
    ):
        value = packet.get(section)
        if not isinstance(value, list) or not value:
            raise ValueError(f"{section} must be a non-empty list")
    for command in packet["allowed_offline_validation_commands"]:
        if not isinstance(command, list) or not command:
            raise ValueError("validation commands must be argv lists")
        forbidden = {"curl", "wget", "playwright", "chromium", "chrome"}
        if command[0] in forbidden:
            raise ValueError(f"validation command is not offline-only: {command[0]}")
