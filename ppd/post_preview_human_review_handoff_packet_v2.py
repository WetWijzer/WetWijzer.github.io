"""Fixture-first post-preview human review handoff packet v2.

The packet is intentionally side-effect free. It consumes an already-redacted
preflight decision table and produces a reviewer-facing checklist for attended
human review after a preview has been generated.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Sequence


PACKET_VERSION = "post-preview-human-review-handoff-packet-v2"
REQUIRED_TABLE_VERSION = "guarded-action-preflight-decision-table-v2"

PRIVATE_KEY_FRAGMENTS = (
    "auth",
    "card",
    "cookie",
    "credential",
    "document_path",
    "local_file",
    "password",
    "payment_detail",
    "private_value",
    "session",
    "ssn",
    "token",
    "trace",
    "upload_file",
)

FORBIDDEN_ACTION_TERMS = (
    "account change",
    "activate release",
    "cancel inspection",
    "certify",
    "official upload",
    "pay fee",
    "schedule inspection",
    "submit application",
)

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/post_preview_human_review_handoff_packet_v2.py"],
    ["python3", "-m", "py_compile", "ppd/tests/test_post_preview_human_review_handoff_packet_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_post_preview_human_review_handoff_packet_v2.py"],
]


def build_post_preview_handoff_packet_v2(decision_table: Mapping[str, Any]) -> Dict[str, Any]:
    """Build a deterministic reviewer handoff packet from preflight decisions."""

    table = deepcopy(dict(decision_table))
    _assert_no_private_keys(table)
    _validate_decision_table(table)

    actions = sorted(
        table["actions"],
        key=lambda action: (int(action.get("review_order", 9999)), str(action.get("action_id", ""))),
    )

    reviewer_prompts: List[Dict[str, Any]] = []
    evidence_summaries: List[Dict[str, Any]] = []
    missing_prompts: List[Dict[str, str]] = []
    stale_conflicting_prompts: List[Dict[str, str]] = []
    blocked_reminders: List[Dict[str, str]] = []
    attendance_reminders: List[Dict[str, str]] = []

    for action in actions:
        action_id = str(action["action_id"])
        label = str(action["label"])
        decision = str(action["allowed_decision"])
        prompt = _reviewer_prompt(action_id, label, decision, action)
        reviewer_prompts.append(prompt)
        evidence_summaries.append(_evidence_summary(action_id, label, action.get("evidence", [])))

        for fact in action.get("missing_facts", []):
            missing_prompts.append(
                {
                    "action_id": action_id,
                    "prompt": "Ask the user for the missing fact without collecting private values: " + str(fact),
                }
            )

        for stale in action.get("stale_evidence", []):
            stale_conflicting_prompts.append(
                {
                    "action_id": action_id,
                    "issue_type": "stale",
                    "prompt": "Confirm whether this evidence is still current before relying on it: " + str(stale),
                }
            )

        for conflict in action.get("conflicting_evidence", []):
            stale_conflicting_prompts.append(
                {
                    "action_id": action_id,
                    "issue_type": "conflicting",
                    "prompt": "Resolve this conflict with the user before proceeding: " + str(conflict),
                }
            )

        if action.get("prohibited_official_action") or decision == "blocked":
            blocked_reminders.append(
                {
                    "action_id": action_id,
                    "reminder": str(
                        action.get(
                            "blocked_reason",
                            "Do not perform official uploads, submissions, certifications, payments, scheduling, cancellations, account changes, or release activation.",
                        )
                    ),
                }
            )

        if action.get("requires_attendance") or action.get("requires_exact_confirmation"):
            attendance_reminders.append(
                {
                    "action_id": action_id,
                    "reminder": "User attendance and action-specific confirmation are required before any consequential DevHub step.",
                }
            )

    packet = {
        "packet_version": PACKET_VERSION,
        "source_decision_table_version": table["decision_table_version"],
        "case_reference": str(table.get("case_reference", "fixture-case")),
        "reviewer_prompts": reviewer_prompts,
        "evidence_summaries": evidence_summaries,
        "unresolved_missing_fact_prompts": missing_prompts,
        "stale_conflicting_evidence_prompts": stale_conflicting_prompts,
        "blocked_consequential_action_reminders": blocked_reminders,
        "user_attendance_reminders": attendance_reminders,
        "offline_validation_commands": deepcopy(OFFLINE_VALIDATION_COMMANDS),
        "privacy_boundaries": [
            "Do not collect private values in the packet.",
            "Do not store user documents, credentials, sessions, traces, screenshots, HAR files, payment details, or local private paths.",
            "Do not open DevHub or perform official uploads, submissions, certifications, payments, scheduling, cancellations, account changes, or release activation.",
        ],
    }
    validate_post_preview_handoff_packet_v2(packet)
    return packet


def validate_post_preview_handoff_packet_v2(packet: Mapping[str, Any]) -> None:
    """Validate the generated packet shape and safety boundaries."""

    _assert_no_private_keys(packet)
    if packet.get("packet_version") != PACKET_VERSION:
        raise ValueError("unexpected packet_version")
    if packet.get("source_decision_table_version") != REQUIRED_TABLE_VERSION:
        raise ValueError("unexpected source decision table version")

    required_lists = (
        "reviewer_prompts",
        "evidence_summaries",
        "unresolved_missing_fact_prompts",
        "stale_conflicting_evidence_prompts",
        "blocked_consequential_action_reminders",
        "user_attendance_reminders",
        "offline_validation_commands",
        "privacy_boundaries",
    )
    for key in required_lists:
        if not isinstance(packet.get(key), list):
            raise ValueError(key + " must be a list")

    commands = packet["offline_validation_commands"]
    if commands != OFFLINE_VALIDATION_COMMANDS:
        raise ValueError("offline validation commands must be exact and deterministic")

    prompt_ids = [str(item.get("action_id")) for item in packet["reviewer_prompts"]]
    if prompt_ids != sorted(prompt_ids, key=lambda value: prompt_ids.index(value)):
        raise ValueError("reviewer prompt action ids must preserve generated order")


def _validate_decision_table(table: Mapping[str, Any]) -> None:
    if table.get("decision_table_version") != REQUIRED_TABLE_VERSION:
        raise ValueError("decision table must be guarded-action-preflight-decision-table-v2")
    actions = table.get("actions")
    if not isinstance(actions, list) or not actions:
        raise ValueError("decision table must include actions")

    for action in actions:
        if not isinstance(action, dict):
            raise ValueError("each action must be an object")
        for key in ("action_id", "label", "allowed_decision"):
            if not action.get(key):
                raise ValueError("action is missing " + key)
        decision = str(action["allowed_decision"])
        if decision not in {"allowed", "needs_human_review", "blocked"}:
            raise ValueError("unsupported allowed_decision: " + decision)


def _reviewer_prompt(action_id: str, label: str, decision: str, action: Mapping[str, Any]) -> Dict[str, Any]:
    base_prompt = "Review preflight decision for " + label + "."
    if decision == "allowed":
        instruction = "Confirm evidence and preview text only; do not perform official actions."
    elif decision == "needs_human_review":
        instruction = "Resolve missing, stale, or conflicting facts before relying on the preview."
    else:
        instruction = "Keep this action blocked unless a future attended workflow creates a new preflight decision."

    return {
        "action_id": action_id,
        "label": label,
        "decision": decision,
        "prompt": base_prompt + " " + instruction,
        "safe_next_step": str(action.get("safe_next_step", "human review only")),
    }


def _evidence_summary(action_id: str, label: str, evidence: Sequence[Any]) -> Dict[str, Any]:
    summaries = []
    for item in evidence:
        if isinstance(item, Mapping):
            summaries.append(
                {
                    "source_id": str(item.get("source_id", "unknown-source")),
                    "summary": str(item.get("summary", "No summary supplied.")),
                    "freshness": str(item.get("freshness", "unknown")),
                }
            )
        else:
            summaries.append({"source_id": "inline", "summary": str(item), "freshness": "unknown"})
    return {"action_id": action_id, "label": label, "evidence": summaries}


def _assert_no_private_keys(value: Any, path: str = "root") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if any(fragment in key_text for fragment in PRIVATE_KEY_FRAGMENTS):
                raise ValueError("private or session-like key is not allowed at " + path + "." + str(key))
            _assert_no_private_keys(child, path + "." + str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_no_private_keys(child, path + "[" + str(index) + "]")
    elif isinstance(value, str):
        lowered = value.lower()
        if any(term in lowered for term in FORBIDDEN_ACTION_TERMS):
            return
        if "-----begin" in lowered or "portlandoregon.gov password" in lowered:
            raise ValueError("private value is not allowed at " + path)
