from __future__ import annotations

from dataclasses import dataclass
from typing import Any

CONSEQUENTIAL_ACTIONS = {
    "fill_live_form",
    "save_official_draft",
    "upload_file",
    "submit",
    "certify",
    "pay",
    "schedule",
    "cancel",
    "change_account",
    "activate_release_state",
}

REQUIRED_PREVIEW_FIELDS = (
    "synthetic_row_id",
    "request_kind",
    "preview_only",
    "source_action_id",
    "field_mapping",
    "user_fact_trace",
    "source_evidence_trace",
    "selector_confidence",
    "stop_gate",
    "refusal",
)

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/draft_executor_dry_run_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_draft_executor_dry_run_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]


@dataclass(frozen=True)
class DryRunValidationError(ValueError):
    message: str

    def __str__(self) -> str:
        return self.message


def build_draft_executor_dry_run_v2(preflight_table: dict[str, Any], review_packet: dict[str, Any]) -> dict[str, Any]:
    """Build an offline synthetic executor contract from fixture inputs.

    This function never executes browser automation and never mutates a live PP&D session.
    """

    actions = preflight_table.get("guarded_actions")
    if not isinstance(actions, list):
        raise DryRunValidationError("preflight_table.guarded_actions must be a list")

    facts = review_packet.get("user_facts")
    evidence = review_packet.get("source_evidence")
    if not isinstance(facts, dict) or not isinstance(evidence, dict):
        raise DryRunValidationError("review_packet must include user_facts and source_evidence objects")

    rows: list[dict[str, Any]] = []
    for index, action in enumerate(actions, start=1):
        if not isinstance(action, dict):
            raise DryRunValidationError("each guarded action must be an object")
        action_id = _required_string(action, "action_id")
        action_type = _required_string(action, "action_type")
        decision = _required_string(action, "decision")
        field_key = action.get("field_key")

        refusal = None
        if action_type in CONSEQUENTIAL_ACTIONS:
            refusal = {
                "refused": True,
                "reason": "consequential action is outside reversible preview-only dry-run scope",
                "example": action_type,
            }
        elif decision != "allow_preview":
            refusal = {
                "refused": True,
                "reason": "guarded preflight decision did not allow preview mapping",
                "example": decision,
            }

        row = {
            "synthetic_row_id": f"dryrun-v2-{index:03d}",
            "request_kind": "synthetic_executor_preview_request",
            "preview_only": True,
            "source_action_id": action_id,
            "field_mapping": _preview_field_mapping(field_key, facts, evidence),
            "user_fact_trace": _trace_for_key(field_key, facts, "user_fact"),
            "source_evidence_trace": _trace_for_key(field_key, evidence, "source_evidence"),
            "selector_confidence": {
                "placeholder": True,
                "value": None,
                "reason": "offline fixture contract does not evaluate live DOM selectors",
            },
            "stop_gate": {
                "requires_exact_confirmation": True,
                "confirmation_phrase": "I confirm this is a preview-only dry run and no official PP&D action will be taken.",
            },
            "refusal": refusal,
            "response": {
                "response_kind": "synthetic_executor_preview_response",
                "executed_playwright_actions": [],
                "saved_official_drafts": [],
                "uploaded_files": [],
                "submitted": False,
                "paid": False,
                "scheduled": False,
                "cancelled": False,
                "account_changed": False,
                "release_state_activated": False,
            },
        }
        _validate_row(row)
        rows.append(row)

    return {
        "contract_version": "draft_executor_dry_run_v2",
        "mode": "fixture_first_offline_preview_only",
        "source_contracts": [
            "guarded_action_preflight_decision_table_v2",
            "post_preview_human_review_handoff_packet_v2",
        ],
        "rows": rows,
        "refused_consequential_action_examples": sorted(CONSEQUENTIAL_ACTIONS),
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
    }


def _required_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise DryRunValidationError(f"missing required string: {key}")
    return value


def _preview_field_mapping(field_key: Any, facts: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(field_key, str) or not field_key:
        return {
            "mapped": False,
            "field_key": None,
            "preview_value": None,
            "requirement": "preview rows must identify a user fact key before mapping a value",
        }
    return {
        "mapped": field_key in facts,
        "field_key": field_key,
        "preview_value": facts.get(field_key),
        "requirement": "preview_value is synthetic review data only and must not be written to a live form",
        "source_evidence_available": field_key in evidence,
    }


def _trace_for_key(field_key: Any, values: dict[str, Any], trace_kind: str) -> list[dict[str, Any]]:
    if not isinstance(field_key, str) or field_key not in values:
        return []
    return [
        {
            "trace_kind": trace_kind,
            "key": field_key,
            "value_present": values.get(field_key) is not None,
        }
    ]


def _validate_row(row: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_PREVIEW_FIELDS if field not in row]
    if missing:
        raise DryRunValidationError(f"dry-run row missing fields: {', '.join(missing)}")
    if row["preview_only"] is not True:
        raise DryRunValidationError("dry-run row must be preview_only")
    if row["response"]["executed_playwright_actions"]:
        raise DryRunValidationError("dry-run row must not execute Playwright actions")
