"""Fixture-first combined inactive fixture promotion rehearsal v2.

This module combines already-offline PP&D fixture review packets into an ordered
manual rehearsal packet. It does not promote fixtures, crawl public sources,
open DevHub, change prompts, mutate release state, or perform official actions.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping, Sequence


PACKET_TYPE = "ppd.combined_inactive_fixture_promotion_rehearsal.v2"
VALIDATION_COMMANDS = [["python3", "ppd/daemon/ppd_daemon.py", "--self-test"]]
MUTATION_FLAGS = (
    "active_source_mutation",
    "active_document_mutation",
    "active_requirement_mutation",
    "active_process_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_fixture_promotion",
    "active_agent_state_mutation",
    "official_action_performed",
)

REQUIRED_GATE_FIELDS = (
    "citations",
    "dependency_checks",
    "manual_only_signoff_placeholder",
    "blocked_promotion_explanation",
    "validation_replay_commands",
    "rollback_checkpoint",
)

PRIVATE_ARTIFACT_KEYS = (
    "auth_state",
    "browser_artifact",
    "browser_context",
    "cookie",
    "credential",
    "devhub_session",
    "har",
    "local_private_path",
    "mfa",
    "password",
    "payment_detail",
    "private_value",
    "session_storage",
    "screenshot",
    "storage_state",
    "trace",
)

RAW_DATA_KEYS = (
    "downloaded_data",
    "downloaded_document",
    "downloaded_pdf",
    "pdf_bytes",
    "raw_body",
    "raw_crawl_output",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "warc_payload",
)

LIVE_CLAIM_KEYS = (
    "executed_live",
    "fixture_promoted",
    "live_crawl_completed",
    "live_execution_completed",
    "promoted_to_active",
    "promotion_completed",
    "promotion_executed",
    "release_state_updated",
)

UNSAFE_VALUE_PHRASES = (
    "auth state",
    "browser trace",
    "cookie jar",
    "downloaded pdf",
    "fixture promoted",
    "guarantee approval",
    "guaranteed approval",
    "har file",
    "legal advice",
    "legally compliant",
    "live crawl completed",
    "live execution completed",
    "permit approved",
    "permit will be approved",
    "private devhub session",
    "raw crawl output",
    "raw pdf data",
    "session storage",
    "storage state",
)

CONSEQUENTIAL_ACTION_PHRASES = (
    "cancel the permit",
    "certify acknowledgement",
    "certify the application",
    "create an account",
    "enter payment details",
    "make official changes",
    "pay fees",
    "purchase trade permit",
    "schedule inspection",
    "submit payment",
    "submit permit",
    "submit the application",
    "upload corrections",
    "upload to devhub",
)

_ALLOWED_NEGATED_ACTION_PREFIXES = (
    "do not ",
    "does not ",
    "must not ",
    "no ",
    "not ",
    "refuse ",
    "refused ",
    "blocked ",
    "blocks ",
    "block ",
    "remain blocked",
    "remains blocked",
)


class CombinedInactiveFixturePromotionRehearsalV2Error(ValueError):
    """Raised when the combined rehearsal packet is incomplete or unsafe."""

    def __init__(self, errors: Iterable[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("invalid combined inactive fixture promotion rehearsal v2: " + "; ".join(self.errors))


def build_combined_inactive_fixture_promotion_rehearsal_v2(
    *,
    public_source_refresh_inactive_patch_preview_v3: Mapping[str, Any],
    devhub_observed_surface_inactive_patch_preview_v2: Mapping[str, Any],
    guarded_agent_release_reviewer_checklist_v1: Mapping[str, Any],
    agent_behavior_dry_run_scenario_matrix_v1: Mapping[str, Any],
) -> dict[str, Any]:
    """Build an ordered offline rehearsal from existing fixture packets."""

    public_preview = deepcopy(dict(public_source_refresh_inactive_patch_preview_v3))
    devhub_preview = deepcopy(dict(devhub_observed_surface_inactive_patch_preview_v2))
    reviewer_checklist = deepcopy(dict(guarded_agent_release_reviewer_checklist_v1))
    behavior_matrix = deepcopy(dict(agent_behavior_dry_run_scenario_matrix_v1))

    gates = _ordered_gates(public_preview, devhub_preview, reviewer_checklist, behavior_matrix)
    packet: dict[str, Any] = {
        "packet_type": PACKET_TYPE,
        "packet_version": "v2",
        "mode": "offline_fixture_rehearsal_only",
        "fixture_first": True,
        "metadata_only": True,
        "consumed_input_packet_refs": {
            "public_source_refresh_inactive_patch_preview_v3": _text(
                public_preview.get("preview_version"), "public_source_refresh_inactive_patch_preview_v3"
            ),
            "devhub_observed_surface_inactive_patch_preview_v2": _text(
                devhub_preview.get("preview_version"), "devhub-observed-surface-inactive-patch-preview-v2"
            ),
            "guarded_agent_release_reviewer_checklist_v1": _text(
                reviewer_checklist.get("packet_type"), "ppd.guarded_agent_release_reviewer_checklist.v1"
            ),
            "agent_behavior_dry_run_scenario_matrix_v1": _text(
                behavior_matrix.get("schema_version"), "agent_behavior_dry_run_matrix.v1"
            ),
        },
        "attestations": {
            "no_fixture_promotion": True,
            "no_public_source_network_run": True,
            "no_devhub_session_use": True,
            "no_prompt_changes": True,
            "no_release_state_mutation": True,
            "no_official_actions": True,
        },
        "ordered_offline_rehearsal_gates": gates,
        "dependency_checks": _dependency_checks(gates),
        "manual_only_signoff_placeholders": _manual_signoffs(gates),
        "blocked_promotion_explanations": _blocked_promotion_explanations(
            public_preview, devhub_preview, reviewer_checklist, behavior_matrix
        ),
        "validation_replay_commands": VALIDATION_COMMANDS,
        "rollback_checkpoints": _rollback_checkpoints(public_preview, devhub_preview, reviewer_checklist, behavior_matrix),
        "handoff_notes": _handoff_notes(gates),
        "active_source_mutation": False,
        "active_document_mutation": False,
        "active_requirement_mutation": False,
        "active_process_mutation": False,
        "active_guardrail_mutation": False,
        "active_prompt_mutation": False,
        "active_release_state_mutation": False,
        "active_fixture_promotion": False,
        "active_agent_state_mutation": False,
        "official_action_performed": False,
    }
    errors = validate_combined_inactive_fixture_promotion_rehearsal_v2(packet)
    if errors:
        raise CombinedInactiveFixturePromotionRehearsalV2Error(errors)
    return packet


def validate_combined_inactive_fixture_promotion_rehearsal_v2(packet: Mapping[str, Any]) -> list[str]:
    """Return deterministic validation errors for a combined rehearsal packet."""

    errors: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be ppd.combined_inactive_fixture_promotion_rehearsal.v2")
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if packet.get("metadata_only") is not True:
        errors.append("metadata_only must be true")
    for flag in MUTATION_FLAGS:
        if packet.get(flag) is not False:
            errors.append(f"{flag} must be false")
    for key in (
        "ordered_offline_rehearsal_gates",
        "dependency_checks",
        "manual_only_signoff_placeholders",
        "blocked_promotion_explanations",
        "rollback_checkpoints",
        "handoff_notes",
    ):
        _validate_rows(packet, key, errors)
    _validate_ordered_gates(packet, errors)
    if packet.get("validation_replay_commands") != VALIDATION_COMMANDS:
        errors.append("validation_replay_commands must contain the PP&D daemon self-test command")
    _validate_no_unsafe_payload(packet, errors)
    return errors


def _ordered_gates(
    public_preview: Mapping[str, Any],
    devhub_preview: Mapping[str, Any],
    reviewer_checklist: Mapping[str, Any],
    behavior_matrix: Mapping[str, Any],
) -> list[dict[str, Any]]:
    public_blocked = len(_sequence(public_preview.get("blocked_rows")))
    devhub_rows = _sequence(devhub_preview.get("rows"))
    devhub_blocked = sum(1 for row in devhub_rows if isinstance(row, Mapping) and row.get("status") == "blocked")
    checklist_blockers = len(_sequence(reviewer_checklist.get("unresolved_blocker_references")))
    behavior_blocks = sum(
        1
        for row in _sequence(behavior_matrix.get("scenarios"))
        if isinstance(row, Mapping) and row.get("expected_outcome") == "block"
    )
    return [
        _gate(
            1,
            "public-source-inactive-preview",
            "public_source_refresh_inactive_patch_preview_v3",
            "Confirm inactive public source preview rows preserve citations and remain review-only.",
            _first_citations(public_preview, "public-source-preview:v3"),
            ["public preview fixture present", "citation preservation checks reviewed"],
            public_blocked,
            "Blocked public-source preview rows require reviewer disposition before any later promotion request.",
            "public source reviewer",
        ),
        _gate(
            2,
            "devhub-observed-surface-inactive-preview",
            "devhub_observed_surface_inactive_patch_preview_v2",
            "Confirm observed DevHub surface rows are redacted, read-only, and inactive.",
            _first_citations(devhub_preview, "devhub-observed-surface-preview:v2"),
            ["DevHub surface preview fixture present", "attendance and redaction gates reviewed"],
            devhub_blocked,
            "Blocked DevHub surface rows require manual disposition before use as fixture evidence.",
            "DevHub surface reviewer",
        ),
        _gate(
            3,
            "guarded-agent-release-reviewer-checklist",
            "guarded_agent_release_reviewer_checklist_v1",
            "Confirm reviewer checklist rows, blockers, and signoff placeholders are complete.",
            _first_citations(reviewer_checklist, "guarded-agent-release-reviewer-checklist:v1"),
            ["reviewer checklist fixture present", "manual signoff placeholders reviewed"],
            checklist_blockers,
            "Checklist blockers remain unresolved until a reviewer records manual disposition outside this packet.",
            "release supervisor",
        ),
        _gate(
            4,
            "agent-behavior-dry-run-matrix",
            "agent_behavior_dry_run_scenario_matrix_v1",
            "Confirm behavior scenarios cover missing facts, stale evidence, refusals, blocked actions, and next safe actions.",
            _first_citations(behavior_matrix, "agent-behavior-dry-run-matrix:v1"),
            ["behavior matrix fixture present", "pass and block outcomes reviewed"],
            behavior_blocks,
            "Block-outcome scenarios are expected rehearsal coverage and are not release approval evidence.",
            "agent behavior reviewer",
        ),
        _gate(
            5,
            "combined-manual-handoff",
            "combined_rehearsal_v2",
            "Confirm all prior gates have manual-only placeholders, replay commands, rollback checkpoints, and handoff notes.",
            ["combined-rehearsal:v2:manual-handoff"],
            ["all gate outputs reviewed in order", "all mutation flags remain false"],
            public_blocked + devhub_blocked + checklist_blockers + behavior_blocks,
            "Promotion remains blocked unless a separate future workflow receives explicit manual approval.",
            "PP&D release coordinator",
        ),
    ]


def _gate(
    order: int,
    gate_id: str,
    source_packet: str,
    gate_goal: str,
    citations: list[str],
    dependency_checks: list[str],
    blocker_count: int,
    blocked_explanation: str,
    signoff_role: str,
) -> dict[str, Any]:
    return {
        "order": order,
        "gate_id": gate_id,
        "source_packet": source_packet,
        "gate_goal": gate_goal,
        "citations": citations,
        "dependency_checks": dependency_checks,
        "manual_only_signoff_placeholder": {
            "role": signoff_role,
            "status": "pending_manual_review",
            "placeholder": "name, timestamp, and disposition intentionally blank",
        },
        "blocked_promotion_explanation": blocked_explanation,
        "blocker_count": blocker_count,
        "validation_replay_commands": VALIDATION_COMMANDS,
        "rollback_checkpoint": f"discard {gate_id} rehearsal output and leave active PP&D artifacts unchanged",
        "handoff_note": f"handoff {gate_id} to {signoff_role} for offline review",
    }


def _dependency_checks(gates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "check_id": f"dependency-{gate['order']}",
            "gate_id": gate["gate_id"],
            "required_before_gate": list(gate.get("dependency_checks", [])),
            "citations": list(gate.get("citations", [])),
        }
        for gate in gates
    ]


def _manual_signoffs(gates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for gate in gates:
        placeholder = gate.get("manual_only_signoff_placeholder", {})
        rows.append(
            {
                "signoff_id": f"signoff-{gate['gate_id']}",
                "gate_id": gate["gate_id"],
                "role": _text(placeholder.get("role") if isinstance(placeholder, Mapping) else None, "reviewer"),
                "status": "pending_manual_review",
                "citations": list(gate.get("citations", [])),
            }
        )
    return rows


def _blocked_promotion_explanations(
    public_preview: Mapping[str, Any],
    devhub_preview: Mapping[str, Any],
    reviewer_checklist: Mapping[str, Any],
    behavior_matrix: Mapping[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(_sequence(public_preview.get("blocked_rows")), start=1):
        if isinstance(row, Mapping):
            rows.append(
                {
                    "blocker_id": f"public-preview-blocker-{index}",
                    "source_packet": "public_source_refresh_inactive_patch_preview_v3",
                    "explanation": _text(row.get("explanation"), "public preview row requires reviewer disposition"),
                    "citations": _first_citations(row, "public-source-preview:v3:blocker"),
                }
            )
    devhub_blocked = [
        row for row in _sequence(devhub_preview.get("rows")) if isinstance(row, Mapping) and row.get("status") == "blocked"
    ]
    if devhub_blocked:
        rows.append(
            {
                "blocker_id": "devhub-preview-blocked-rows",
                "source_packet": "devhub_observed_surface_inactive_patch_preview_v2",
                "explanation": f"{len(devhub_blocked)} DevHub observed surface preview rows require manual disposition.",
                "citations": _first_citations(devhub_preview, "devhub-observed-surface-preview:v2:blocker"),
            }
        )
    for index, row in enumerate(_sequence(reviewer_checklist.get("unresolved_blocker_references")), start=1):
        if isinstance(row, Mapping):
            rows.append(
                {
                    "blocker_id": _text(row.get("blocker_ref"), f"reviewer-checklist-blocker-{index}"),
                    "source_packet": "guarded_agent_release_reviewer_checklist_v1",
                    "explanation": "Reviewer checklist blocker remains pending manual signoff.",
                    "citations": _first_citations(row, "guarded-agent-release-reviewer-checklist:v1:blocker"),
                }
            )
    behavior_block_count = sum(
        1
        for row in _sequence(behavior_matrix.get("scenarios"))
        if isinstance(row, Mapping) and row.get("expected_outcome") == "block"
    )
    rows.append(
        {
            "blocker_id": "agent-behavior-block-outcome-scenarios",
            "source_packet": "agent_behavior_dry_run_scenario_matrix_v1",
            "explanation": f"{behavior_block_count} expected block scenarios must be reviewed as rehearsal coverage, not approval evidence.",
            "citations": _first_citations(behavior_matrix, "agent-behavior-dry-run-matrix:v1:blocker"),
        }
    )
    return rows


def _rollback_checkpoints(
    public_preview: Mapping[str, Any],
    devhub_preview: Mapping[str, Any],
    reviewer_checklist: Mapping[str, Any],
    behavior_matrix: Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "checkpoint_id": "rollback-public-source-preview",
            "checkpoint": "discard combined rehearsal output and retain inactive public source fixtures as review inputs only",
            "citations": _first_citations(public_preview, "public-source-preview:v3:rollback"),
            "validation_replay_commands": VALIDATION_COMMANDS,
        },
        {
            "checkpoint_id": "rollback-devhub-surface-preview",
            "checkpoint": "discard combined rehearsal output and retain inactive DevHub surface fixtures as review inputs only",
            "citations": _first_citations(devhub_preview, "devhub-observed-surface-preview:v2:rollback"),
            "validation_replay_commands": VALIDATION_COMMANDS,
        },
        {
            "checkpoint_id": "rollback-reviewer-checklist",
            "checkpoint": "discard combined rehearsal output and keep reviewer checklist signoffs pending",
            "citations": _first_citations(reviewer_checklist, "guarded-agent-release-reviewer-checklist:v1:rollback"),
            "validation_replay_commands": VALIDATION_COMMANDS,
        },
        {
            "checkpoint_id": "rollback-agent-behavior-matrix",
            "checkpoint": "discard combined rehearsal output and keep behavior scenarios as offline dry-run material",
            "citations": _first_citations(behavior_matrix, "agent-behavior-dry-run-matrix:v1:rollback"),
            "validation_replay_commands": VALIDATION_COMMANDS,
        },
    ]


def _handoff_notes(gates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "note_id": f"handoff-{gate['gate_id']}",
            "gate_id": gate["gate_id"],
            "handoff_to": _text(gate.get("manual_only_signoff_placeholder", {}).get("role"), "reviewer"),
            "note": _text(gate.get("handoff_note")),
            "citations": list(gate.get("citations", [])),
        }
        for gate in gates
    ]


def _validate_rows(packet: Mapping[str, Any], key: str, errors: list[str]) -> None:
    rows = packet.get(key)
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        errors.append(f"{key} must be a non-empty list")
        return
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            errors.append(f"{key}[{index}] must be an object")
            continue
        if not _string_list(row.get("citations")):
            errors.append(f"{key}[{index}].citations must be non-empty")


def _validate_ordered_gates(packet: Mapping[str, Any], errors: list[str]) -> None:
    gates = packet.get("ordered_offline_rehearsal_gates")
    if not isinstance(gates, Sequence) or isinstance(gates, (str, bytes)):
        return
    orders = [gate.get("order") for gate in gates if isinstance(gate, Mapping)]
    if orders != sorted(orders):
        errors.append("ordered_offline_rehearsal_gates must be sorted by order")
    for index, gate in enumerate(gates):
        if not isinstance(gate, Mapping):
            continue
        for field in REQUIRED_GATE_FIELDS:
            if field not in gate:
                errors.append(f"ordered_offline_rehearsal_gates[{index}].{field} is required")
        if not _string_list(gate.get("citations")):
            errors.append(f"ordered_offline_rehearsal_gates[{index}].citations must be non-empty")
        if not _string_list(gate.get("dependency_checks")):
            errors.append(f"ordered_offline_rehearsal_gates[{index}].dependency_checks must be non-empty")
        signoff = gate.get("manual_only_signoff_placeholder")
        if not isinstance(signoff, Mapping) or signoff.get("status") != "pending_manual_review":
            errors.append(
                f"ordered_offline_rehearsal_gates[{index}].manual_only_signoff_placeholder must be pending manual review"
            )
        if not _text(gate.get("blocked_promotion_explanation")):
            errors.append(f"ordered_offline_rehearsal_gates[{index}].blocked_promotion_explanation is required")
        if gate.get("validation_replay_commands") != VALIDATION_COMMANDS:
            errors.append(f"ordered_offline_rehearsal_gates[{index}].validation_replay_commands must replay self-test")
        if not _text(gate.get("rollback_checkpoint")):
            errors.append(f"ordered_offline_rehearsal_gates[{index}].rollback_checkpoint is required")


def _validate_no_unsafe_payload(packet: Mapping[str, Any], errors: list[str]) -> None:
    for path, key, value in _walk(packet):
        key_name = key.lower()
        if _matches_any(key_name, PRIVATE_ARTIFACT_KEYS) and not _is_safe_negated_key(key_name) and _truthy_payload(value):
            errors.append(f"{path} must not include private, authenticated, session, or browser artifacts")
        if _matches_any(key_name, RAW_DATA_KEYS) and _truthy_payload(value):
            errors.append(f"{path} must not include raw crawl, PDF, downloaded, or WARC payload data")
        if _matches_any(key_name, LIVE_CLAIM_KEYS) and _truthy_payload(value):
            errors.append(f"{path} must not claim live execution, promotion, or release-state update")
        if isinstance(value, str):
            lowered = " ".join(value.lower().split())
            if _matches_any(lowered, UNSAFE_VALUE_PHRASES):
                errors.append(f"{path} must not contain private artifacts, raw data, live claims, or outcome guarantees")
            if _matches_any(lowered, CONSEQUENTIAL_ACTION_PHRASES) and not _contains_negated_action_context(lowered):
                errors.append(f"{path} must not contain consequential action language")


def _walk(value: Any, path: str = "packet", key: str = "") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{path}.{child_key_text}"
            yield child_path, child_key_text, child_value
            yield from _walk(child_value, child_path, child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child_value in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, key, child_value
            yield from _walk(child_value, child_path, key)


def _matches_any(text: str, needles: Sequence[str]) -> bool:
    return any(needle in text for needle in needles)


def _is_safe_negated_key(key_name: str) -> bool:
    return key_name.startswith("no_") or key_name.startswith("without_")


def _truthy_payload(value: Any) -> bool:
    if value is None or value is False:
        return False
    if value == "":
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and not value:
        return False
    if isinstance(value, Mapping) and not value:
        return False
    return True


def _contains_negated_action_context(text: str) -> bool:
    return any(prefix in text for prefix in _ALLOWED_NEGATED_ACTION_PREFIXES)


def _first_citations(packet: Mapping[str, Any], fallback: str) -> list[str]:
    direct = _citations(packet)
    if direct:
        return direct
    for value in packet.values():
        if isinstance(value, Mapping):
            nested = _citations(value)
            if nested:
                return nested
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            for item in value:
                if isinstance(item, Mapping):
                    nested = _citations(item)
                    if nested:
                        return nested
    return [fallback]


def _citations(row: Mapping[str, Any]) -> list[str]:
    value = row.get("citations") or row.get("offline_citations") or row.get("source_evidence_ids")
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return value
    return ()


def _string_list(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and any(
        isinstance(item, str) and item.strip() for item in value
    )


def _text(value: Any, fallback: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback
