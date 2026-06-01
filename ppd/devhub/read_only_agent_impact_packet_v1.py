"""Fixture-first DevHub read-only agent impact packet v1.

This module maps synthetic DevHub read-only surface delta rows into an offline
agent-impact packet. It does not open DevHub, read private user facts, fill
forms, store auth state, crawl live sources, or mutate active prompt,
guardrail, source, document, release, crawler, surface, or daemon state.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

PACKET_VERSION = "devhub_read_only_agent_impact_packet_v1"
VALIDATION_COMMANDS: list[list[str]] = [
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ["python3", "-m", "unittest", "discover", "-s", "ppd/tests", "-p", "test_*.py"],
]


def build_devhub_read_only_agent_impact_packet_v1(
    surface_delta_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Return a deterministic offline impact packet for synthetic delta rows."""

    rows = [_normalize_delta_row(row, index) for index, row in enumerate(surface_delta_rows)]
    return {
        "packet_version": PACKET_VERSION,
        "packet_id": "devhub-read-only-agent-impact-v1-synthetic",
        "mode": "offline_fixture_read_only_agent_impact",
        "surface_delta_refs": [_surface_delta_ref(row) for row in rows],
        "affected_missing_information_prompts": [_missing_information_prompt(row) for row in rows],
        "blocked_action_predicates": [_blocked_action_predicate(row) for row in rows],
        "next_safe_action_rows": [_next_safe_action(row) for row in rows],
        "reversible_draft_eligibility_notes": [_reversible_draft_note(row) for row in rows],
        "exact_confirmation_warnings": [_exact_confirmation_warning(row) for row in rows],
        "citation_source_placeholders": [_citation_placeholder(row) for row in rows],
        "reviewer_holds": [_reviewer_hold(row) for row in rows],
        "artifact_policy": {
            "private_user_facts_included": False,
            "opens_devhub": False,
            "stores_auth_state": False,
            "stores_browser_artifacts": False,
            "stores_raw_crawl_output": False,
            "stores_downloaded_documents": False,
        },
        "mutation_flags": {
            "active_prompt_mutation": False,
            "active_guardrail_mutation": False,
            "active_process_model_mutation": False,
            "active_requirement_mutation": False,
            "active_contract_mutation": False,
            "active_source_mutation": False,
            "active_archive_mutation": False,
            "active_document_mutation": False,
            "active_devhub_surface_mutation": False,
            "active_release_mutation": False,
            "active_crawler_mutation": False,
            "active_daemon_state_mutation": False,
        },
        "validation_commands": [list(command) for command in VALIDATION_COMMANDS],
    }


def validate_devhub_read_only_agent_impact_packet_v1(packet: Mapping[str, Any]) -> list[str]:
    """Return compact deterministic validation codes for the synthetic packet."""

    errors: list[str] = []
    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("invalid_packet_version")
    for key in (
        "surface_delta_refs",
        "affected_missing_information_prompts",
        "blocked_action_predicates",
        "next_safe_action_rows",
        "reversible_draft_eligibility_notes",
        "exact_confirmation_warnings",
        "citation_source_placeholders",
        "reviewer_holds",
        "validation_commands",
    ):
        if not _non_empty_list(packet.get(key)):
            errors.append(f"missing_{key}")
    if packet.get("validation_commands") != VALIDATION_COMMANDS:
        errors.append("unexpected_validation_commands")
    for section in ("artifact_policy", "mutation_flags"):
        value = packet.get(section)
        if not isinstance(value, Mapping):
            errors.append(f"missing_{section}")
            continue
        for key, flag in value.items():
            if flag is not False:
                errors.append(f"{section}_{key}_must_be_false")
    return sorted(set(errors))


def assert_valid_devhub_read_only_agent_impact_packet_v1(packet: Mapping[str, Any]) -> None:
    errors = validate_devhub_read_only_agent_impact_packet_v1(packet)
    if errors:
        raise AssertionError("invalid DevHub read-only agent impact packet v1: " + ", ".join(errors))


def _normalize_delta_row(row: Mapping[str, Any], index: int) -> dict[str, str]:
    surface_id = _text(row.get("surface_id")) or f"synthetic-surface-{index + 1}"
    row_id = _text(row.get("candidate_row_id") or row.get("row_id")) or f"delta-row-{index + 1}"
    topic = _text(row.get("impact_topic")) or surface_id.replace("-", " ")
    return {
        "row_id": row_id,
        "surface_id": surface_id,
        "impact_topic": topic,
        "delta_ref_id": _text(row.get("delta_ref_id")) or f"surface-delta-ref-{index + 1}",
        "source_placeholder_id": _text(row.get("source_placeholder_id")) or f"source-placeholder-{index + 1}",
        "reviewer_owner": _text(row.get("reviewer_owner")) or "ppd-devhub-read-only-reviewer",
    }


def _surface_delta_ref(row: Mapping[str, str]) -> dict[str, str]:
    return {
        "delta_ref_id": row["delta_ref_id"],
        "surface_delta_row_id": row["row_id"],
        "surface_id": row["surface_id"],
        "source": "synthetic_fixture_only",
    }


def _missing_information_prompt(row: Mapping[str, str]) -> dict[str, str]:
    return {
        "prompt_id": f"missing-info-{row['row_id']}",
        "surface_delta_ref_id": row["delta_ref_id"],
        "prompt": f"Confirm the public-source evidence placeholder for {row['impact_topic']} before advising beyond read-only review.",
        "private_user_fact_status": "not_included",
    }


def _blocked_action_predicate(row: Mapping[str, str]) -> dict[str, Any]:
    return {
        "predicate_id": f"blocked-action-{row['row_id']}",
        "surface_delta_ref_id": row["delta_ref_id"],
        "predicate": "block_consequential_devhub_action_until_reviewed_source_and_exact_confirmation",
        "blocked": True,
    }


def _next_safe_action(row: Mapping[str, str]) -> dict[str, str]:
    return {
        "next_safe_action_id": f"next-safe-{row['row_id']}",
        "surface_delta_ref_id": row["delta_ref_id"],
        "action": "record reviewer note and cite synthetic placeholder only",
        "boundary": "offline_read_only_review",
    }


def _reversible_draft_note(row: Mapping[str, str]) -> dict[str, Any]:
    return {
        "eligibility_note_id": f"draft-eligibility-{row['row_id']}",
        "surface_delta_ref_id": row["delta_ref_id"],
        "eligible": False,
        "reason": "Synthetic surface delta needs reviewer acceptance before reversible draft guidance can be considered.",
    }


def _exact_confirmation_warning(row: Mapping[str, str]) -> dict[str, str]:
    return {
        "warning_id": f"exact-confirmation-{row['row_id']}",
        "surface_delta_ref_id": row["delta_ref_id"],
        "warning": "Any later consequential DevHub workflow requires user presence, reviewed source grounding, and exact confirmation.",
    }


def _citation_placeholder(row: Mapping[str, str]) -> dict[str, str]:
    return {
        "placeholder_id": row["source_placeholder_id"],
        "surface_delta_ref_id": row["delta_ref_id"],
        "citation_status": "placeholder_pending_review",
        "source_kind": "synthetic_offline_fixture",
    }


def _reviewer_hold(row: Mapping[str, str]) -> dict[str, Any]:
    return {
        "hold_id": f"reviewer-hold-{row['row_id']}",
        "surface_delta_ref_id": row["delta_ref_id"],
        "reviewer_owner": row["reviewer_owner"],
        "hold_active": True,
        "reason": "Agent impact remains reviewer-held until the synthetic delta mapping is accepted.",
    }


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
