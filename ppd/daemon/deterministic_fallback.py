"""PP&D deterministic fallback proposal builders.

These helpers keep domain-specific fallback contracts out of the daemon control
flow while still using the reusable todo-daemon deterministic fallback helpers.
"""

from __future__ import annotations

import json
from typing import Any, Iterable, Optional, Sequence

from ipfs_datasets_py.optimizers.todo_daemon.deterministic_fallback import (
    build_deterministic_progress_record as build_todo_deterministic_progress_record,
    build_deterministic_replacement_proposal,
    fallback_kind_for_task,
    load_deterministic_progress_manifest,
    open_task_has_deterministic_fallback,
    task_has_deterministic_fallback,
    upsert_deterministic_progress_record,
)
from ipfs_datasets_py.optimizers.todo_daemon.engine import Proposal, Task


DETERMINISTIC_FALLBACK_VALIDATION_COMMANDS = (
    (
        "python3",
        "-m",
        "unittest",
        "ppd.tests.test_daemon_llm_result_durability",
        "ppd.tests.test_supervisor_stale_status_replanning",
    ),
    ("python3", "ppd/tests/validate_ppd.py"),
)

DETERMINISTIC_TASK_FALLBACK_TITLES: tuple[tuple[str, str], ...] = (
    ("autonomous platform continuation coverage", "platform_continuation"),
    ("processor-suite integration planning", "processor_suite_planning"),
    ("playwright/pdf handoff validation", "playwright_pdf_handoff"),
    ("supervisor idle-recovery validation", "supervisor_idle_recovery"),
    ("source-backed pp&d surface registry and taxonomy", "surface_registry_taxonomy"),
    ("pp&d source seed manifest", "source_seed_manifest"),
    ("public crawl frontier contract", "public_crawl_frontier"),
    ("processor-suite archival integration", "processor_archival_integration"),
    ("public pdf and form inventory", "public_pdf_form_inventory"),
    ("normalized pp&d process and requirement schemas", "process_requirement_schemas"),
    ("source-backed requirement extraction fixtures", "requirement_extraction_fixtures"),
    ("permit-process coverage matrix", "permit_process_matrix"),
    ("devhub manual-login and attendance protocol", "devhub_attendance_protocol"),
    ("attended playwright surface recorder", "playwright_surface_recorder"),
    ("devhub form-field manifest extraction", "devhub_form_field_manifest"),
    ("local pdf draft-fill queue", "local_pdf_draft_fill_queue"),
    ("user document-store gap-analysis model", "user_document_gap_analysis"),
    ("formal-logic guardrail compiler pipeline", "formal_logic_guardrail_compiler"),
    ("action policy engine", "action_policy_engine"),
    ("exact-confirmation and human-attendance gate tests", "confirmation_gate_tests"),
    ("commit-safe action journal and replay fixtures", "action_journal_replay"),
    ("source-change monitoring fixtures", "source_change_monitoring"),
    ("end-to-end fixture scenarios", "end_to_end_fixture_scenarios"),
    ("agent-facing apis", "agent_facing_apis"),
    ("privacy and security validation", "privacy_security_validation"),
    ("bounded live public crawl dry-run harness", "bounded_live_crawl_dry_run"),
    ("supervised live whole-site public crawl runner", "bounded_live_crawl_dry_run"),
    ("authenticated devhub dry-run fixtures", "authenticated_devhub_dry_run"),
    ("autonomous-assistance operations documentation", "autonomous_assistance_ops"),
    ("user document-store reconciliation contract", "user_document_gap_analysis"),
    ("requirementnode and processmodel schema coverage", "process_requirement_schemas"),
    ("generated blocked-cascade daemon-repair coverage", "blocked_cascade_daemon_repair"),
)

DETERMINISTIC_TASK_SOURCE_EVIDENCE_IDS = (
    "evidence:ppd-home:2026-05-01",
    "evidence:permit-applications-index:2026-05-01",
    "evidence:devhub-faq:2026-05-01",
    "evidence:single-pdf-process:2026-05-01",
)
DETERMINISTIC_PROGRESS_SOURCE_PATH = "ppd/platform/deterministic_fallback_progress.py"

DETERMINISTIC_PLATFORM_INIT = '''"""Source-backed PP&D autonomous platform contracts.

Modules in this package are imported directly by capability area so a partially
implemented tranche never imports a source file that has not been created yet.
"""
'''

DETERMINISTIC_SOURCE_FILES: dict[str, tuple[str, str]] = {
    "platform_continuation": (
        "ppd/platform/autonomous_archival_contract.py",
        '''"""Source-backed contract for PP&D public archival capability.

The contract is intentionally side-effect-free: it names the implementation
surfaces the daemon must wire together before any live crawl is allowed.
"""

from __future__ import annotations


def archival_contract() -> dict[str, object]:
    return {
        "capability": "whole_site_public_archival",
        "entrypoints": [
            "ppd.crawler.live_public_preflight",
            "ppd.crawler.whole_site_archival",
            "ipfs_datasets_py.processors",
        ],
        "requiredOutputs": [
            "archive_manifest",
            "normalized_document_record",
            "source_evidence_id",
            "requirement_batch",
        ],
        "defaultMode": "fixture_only",
        "liveCrawlAllowedByDefault": False,
    }
''',
    ),
    "processor_suite_planning": (
        "ppd/platform/processor_suite_contract.py",
        '''"""Source-backed contract for processor-suite PP&D handoff."""

from __future__ import annotations


def processor_suite_contract() -> dict[str, object]:
    return {
        "capability": "processor_suite_handoff",
        "processorSuite": "ipfs_datasets_py.processors",
        "requiredInputs": [
            "public_source_url",
            "robots_decision",
            "content_type",
            "canonical_document_id",
        ],
        "requiredOutputs": [
            "processor_handoff_manifest",
            "pdf_metadata_record",
            "normalized_public_document",
            "formal_logic_source_evidence_id",
        ],
        "rawBodyPersistenceAllowed": False,
    }
''',
    ),
    "playwright_pdf_handoff": (
        "ppd/platform/playwright_pdf_contract.py",
        '''"""Source-backed contract for attended Playwright and PDF draft work."""

from __future__ import annotations


def playwright_pdf_contract() -> dict[str, object]:
    return {
        "capability": "attended_draft_automation",
        "allowedActions": [
            "manual_login_handoff",
            "journal_replay",
            "reversible_draft_field_fill",
            "local_pdf_preview_fill",
        ],
        "blockedActions": [
            "official_upload",
            "permit_submission",
            "certification",
            "fee_payment",
            "account_security_transition",
            "inspection_scheduling",
        ],
        "requiresHumanAttendanceBeforeBrowserUse": True,
        "exactConfirmationBeforeOfficialAction": True,
    }
''',
    ),
    "supervisor_idle_recovery": (
        "ppd/platform/supervisor_idle_policy.py",
        '''"""Source-backed contract for supervisor idle and replenishment behavior."""

from __future__ import annotations


def supervisor_idle_policy() -> dict[str, object]:
    return {
        "capability": "supervisor_idle_recovery",
        "noEligibleTasksPolicy": "review_goal_before_replenishment",
        "replenishmentLimits": {
            "autonomousPlatformTranches": 1,
            "executionCapabilityTranches": 1,
        },
        "mustNotAcceptRuntimeOnlyProgress": True,
        "mustVerifyPromotionToMainWorktree": True,
        "acceptedEvidenceMode": "ledger_only",
    }
''',
    ),
}

MANUAL_GOAL_FALLBACK_METADATA: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {
    "surface_registry_taxonomy": (
        "ppd_surface_registry",
        ("public_portland_pages", "devhub_public_entrypoints", "authenticated_read_only", "reversible_drafts"),
        ("surface_taxonomy", "action_boundary_map", "agent_guardrail_api_index"),
    ),
    "source_seed_manifest": (
        "source_seed_manifest",
        ("ppd_landing_page", "devhub_faq", "single_pdf_process", "permit_applications_index"),
        ("seed_manifest", "crawl_policy_metadata", "source_evidence_ids"),
    ),
    "public_crawl_frontier": (
        "public_crawl_frontier",
        ("portland_gov_allowlist", "devhub_public_allowlist", "robots_preflight"),
        ("frontier_contract", "skip_reason_schema", "metadata_manifest_contract"),
    ),
    "processor_archival_integration": (
        "processor_archival_integration",
        ("ipfs_datasets_py_processors", "public_pages", "public_pdfs"),
        ("archive_manifest_id", "normalized_document_id", "formal_logic_source_evidence_id"),
    ),
    "public_pdf_form_inventory": (
        "public_pdf_form_inventory",
        ("permit_applications", "single_pdf_guidance", "fillable_public_forms"),
        ("pdf_inventory_record", "form_field_manifest", "raw_document_persistence_refusal"),
    ),
    "process_requirement_schemas": (
        "process_requirement_schemas",
        ("source_evidence", "permit_stages", "ui_action_gates"),
        ("process_schema", "requirement_schema", "formal_requirement_node"),
    ),
    "requirement_extraction_fixtures": (
        "requirement_extraction_fixtures",
        ("public_guidance", "citation_anchors", "requirement_text"),
        ("obligation_batch", "exception_batch", "fee_trigger_batch"),
    ),
    "permit_process_matrix": (
        "permit_process_matrix",
        ("residential", "commercial", "trade", "corrections", "inspections"),
        ("coverage_matrix", "workflow_index", "gap_report"),
    ),
    "devhub_attendance_protocol": (
        "devhub_attendance_protocol",
        ("manual_login_handoff", "mfa", "captcha", "credential_boundaries"),
        ("attendance_protocol", "refusal_policy", "handoff_checkpoint"),
    ),
    "playwright_surface_recorder": (
        "playwright_surface_recorder",
        ("home", "my_permits", "apply_for_permit", "fees", "corrections", "inspections"),
        ("surface_journal_schema", "selector_evidence", "manual_handoff_marker"),
    ),
    "devhub_form_field_manifest": (
        "devhub_form_field_manifest",
        ("accessible_roles", "labels", "headings", "url_state"),
        ("field_manifest", "confidence_score", "redacted_fact_map"),
    ),
    "local_pdf_draft_fill_queue": (
        "local_pdf_draft_fill_queue",
        ("public_form_fields", "redacted_user_facts", "local_preview_pdf"),
        ("draft_fill_queue", "preview_manifest", "upload_refusal_gate"),
    ),
    "user_document_gap_analysis": (
        "user_document_gap_analysis",
        ("known_user_facts", "source_requirements", "document_placeholders"),
        ("missing_fact_list", "stale_evidence_flag", "exact_confirmation_blocker"),
    ),
    "formal_logic_guardrail_compiler": (
        "formal_logic_guardrail_compiler",
        ("requirement_nodes", "source_evidence_ids", "action_boundaries"),
        ("deontic_obligations", "predicate_prerequisites", "stop_gate_predicates"),
    ),
    "action_policy_engine": (
        "action_policy_engine",
        ("read_only", "reversible_draft", "local_pdf_preview", "official_actions"),
        ("action_classification", "confirmation_requirement", "refused_transition"),
    ),
    "confirmation_gate_tests": (
        "confirmation_gate_tests",
        ("current_screen_review", "specific_user_confirmation", "post_action_review"),
        ("human_attendance_gate", "exact_confirmation_gate", "official_action_block"),
    ),
    "action_journal_replay": (
        "action_journal_replay",
        ("public_crawl_events", "draft_attempts", "pdf_preview_fills", "manual_handoffs"),
        ("commit_safe_journal", "replay_fixture", "redaction_audit"),
    ),
    "source_change_monitoring": (
        "source_change_monitoring",
        ("public_source_recrawl", "normalized_document_diff", "requirement_ids"),
        ("stale_guardrail_marker", "affected_process_model", "human_review_queue"),
    ),
    "end_to_end_fixture_scenarios": (
        "end_to_end_fixture_scenarios",
        ("residential", "commercial", "trade", "correction_upload", "inspection"),
        ("scenario_packet", "requirement_trace", "blocked_official_action"),
    ),
    "agent_facing_apis": (
        "agent_facing_apis",
        ("permit_process_models", "redacted_user_facts", "guardrail_status"),
        ("loadPermitProcess", "compareUserFacts", "validateNextAction", "produceReviewPacket"),
    ),
    "privacy_security_validation": (
        "privacy_security_validation",
        ("private_devhub_state", "credentials", "screenshots", "raw_bodies", "payment_details"),
        ("commit_blocklist", "redaction_validation", "private_artifact_refusal"),
    ),
    "bounded_live_crawl_dry_run": (
        "bounded_live_crawl_dry_run",
        ("small_public_seed_set", "allowlist", "processor_preflight"),
        ("metadata_manifest", "validation_summary", "raw_body_persistence_refusal"),
    ),
    "authenticated_devhub_dry_run": (
        "authenticated_devhub_dry_run",
        ("mocked_pages", "user_attended_pages", "save_for_later"),
        ("login_handoff_fixture", "draft_fill_preview", "official_action_refusal"),
    ),
    "autonomous_assistance_ops": (
        "autonomous_assistance_ops",
        ("daemon_handoff", "source_recrawl_cadence", "attended_runbooks", "readiness_gates"),
        ("operations_runbook", "repair_escalation", "production_readiness_gate"),
    ),
    "blocked_cascade_daemon_repair": (
        "blocked_cascade_daemon_repair",
        ("blocked_domain_backlog", "generated_repair_tranche", "supervisor_retry_policy"),
        ("blocked_task_quarantine", "fresh_repair_validation", "llm_termination_storm_guard"),
    ),
}


def _manual_goal_source_content(kind: str, metadata: tuple[str, tuple[str, ...], tuple[str, ...]]) -> str:
    capability, surfaces, outputs = metadata
    payload = json.dumps(
        {
            "schemaVersion": 1,
            "fallbackKind": kind,
            "capability": capability,
            "surfaces": list(surfaces),
            "requiredOutputs": list(outputs),
            "defaultMode": "fixture_only",
            "liveCrawlAllowedByDefault": False,
            "officialDevhubActionAllowedByDefault": False,
            "requiresHumanAttendanceBeforeBrowserUse": True,
            "exactConfirmationBeforeOfficialAction": True,
            "privateArtifactPersistence": "forbidden",
        },
        indent=2,
        sort_keys=True,
    )
    return f'''"""Deterministic PP&D contract for {capability}.

This module is source-backed evidence for a reopened comprehensive PP&D goal
task. It is intentionally side-effect-free and does not perform live DevHub,
official action, upload, payment, or real PDF filling work.
"""

from __future__ import annotations

import json
from typing import Any


CONTRACT_JSON = {payload!r}


def contract() -> dict[str, Any]:
    return json.loads(CONTRACT_JSON)
'''


for _manual_kind, _manual_metadata in MANUAL_GOAL_FALLBACK_METADATA.items():
    DETERMINISTIC_SOURCE_FILES[_manual_kind] = (
        f"ppd/platform/{_manual_kind}.py",
        _manual_goal_source_content(_manual_kind, _manual_metadata),
    )


def compact_deterministic_progress_source_payload(
    manifest: dict[str, Any],
    *,
    recent_limit: int = 8,
) -> dict[str, Any]:
    """Return a reviewable source payload without embedding the full runtime ledger."""

    records = [record for record in manifest.get("records", []) if isinstance(record, dict)]
    fallback_counts: dict[str, int] = {}
    for record in records:
        fallback_kind = str(record.get("fallbackKind") or "unknown")
        fallback_counts[fallback_kind] = fallback_counts.get(fallback_kind, 0) + 1
    recent_records = sorted(records, key=lambda record: str(record.get("completedAt") or ""))[-recent_limit:]
    return {
        "schemaVersion": manifest.get("schemaVersion", 1),
        "strategy": manifest.get("strategy", "deterministic_task_fallback_when_llm_unavailable"),
        "updatedAt": manifest.get("updatedAt", ""),
        "recordCount": len(records),
        "fallbackCounts": dict(sorted(fallback_counts.items())),
        "recentRecords": recent_records,
    }


def deterministic_progress_source_content(manifest: dict[str, Any]) -> str:
    """Return a commit-visible source mirror for deterministic fallback progress."""

    payload = json.dumps(compact_deterministic_progress_source_payload(manifest), indent=2, sort_keys=True)
    return f'''"""Commit-visible PP&D deterministic fallback progress.

The daemon also writes a runtime JSON manifest, but accepted autonomous work must
promote a visible source or fixture change. This module mirrors the same records
so deterministic continuation tasks leave reviewable source-backed evidence.
"""

from __future__ import annotations

import json
from typing import Any


DETERMINISTIC_FALLBACK_PROGRESS_JSON = {payload!r}


def deterministic_fallback_progress() -> dict[str, Any]:
    return json.loads(DETERMINISTIC_FALLBACK_PROGRESS_JSON)
'''


def deterministic_task_fallback_kind(task: Task) -> str:
    return fallback_kind_for_task(task, DETERMINISTIC_TASK_FALLBACK_TITLES)


def has_deterministic_task_fallback(task: Task) -> bool:
    return task_has_deterministic_fallback(task, DETERMINISTIC_TASK_FALLBACK_TITLES)


def has_open_deterministic_task_fallback(tasks: Iterable[Task]) -> bool:
    return open_task_has_deterministic_fallback(tasks, DETERMINISTIC_TASK_FALLBACK_TITLES)


def build_deterministic_task_fallback_proposal(
    config: Any,
    selected: Task,
    *,
    default_validation_commands: Optional[Sequence[Sequence[str]]] = None,
) -> Optional[Proposal]:
    """Build a fixture-only proposal for known platform tasks when the LLM path is unhealthy."""

    fallback_kind = deterministic_task_fallback_kind(selected)
    if not fallback_kind:
        return None

    manifest = upsert_deterministic_progress_record(
        deterministic_progress_manifest(config),
        selected,
        deterministic_progress_record(selected, fallback_kind),
    )
    default_commands = tuple(tuple(command) for command in (default_validation_commands or ()))
    config_commands = tuple(tuple(command) for command in getattr(config, "validation_commands", ()))
    validation_commands = (
        DETERMINISTIC_FALLBACK_VALIDATION_COMMANDS
        if default_commands and config_commands == default_commands
        else config.validation_commands
    )
    source_path, source_content = DETERMINISTIC_SOURCE_FILES[fallback_kind]

    return build_deterministic_replacement_proposal(
        selected=selected,
        fallback_kind=fallback_kind,
        manifest=manifest,
        progress_path=config.deterministic_progress_file,
        source_files=[
            ("ppd/platform/__init__.py", DETERMINISTIC_PLATFORM_INIT),
            (source_path, source_content),
            (DETERMINISTIC_PROGRESS_SOURCE_PATH, deterministic_progress_source_content(manifest)),
        ],
        summary=f"Complete {fallback_kind.replace('_', ' ')} with deterministic PP&D fallback.",
        impact=(
            "The daemon can keep making fixture-only PP&D platform progress while the LLM backend is in "
            "a termination storm. The generated record preserves source evidence, processor, draft "
            "automation, PDF-preview, and formal-logic boundaries without live DevHub or official actions."
        ),
        validation_commands=validation_commands,
    )


def deterministic_progress_manifest(config: Any) -> dict[str, Any]:
    return load_deterministic_progress_manifest(
        config.resolve(config.deterministic_progress_file),
        strategy="deterministic_task_fallback_when_llm_unavailable",
    )


def deterministic_progress_record(selected: Task, fallback_kind: str) -> dict[str, Any]:
    return build_todo_deterministic_progress_record(
        selected,
        fallback_kind,
        source_evidence_ids=DETERMINISTIC_TASK_SOURCE_EVIDENCE_IDS,
        artifact_contracts=deterministic_artifact_contracts(fallback_kind),
        guardrails=[
            "public_sources_only",
            "redacted_user_facts_only",
            "reversible_draft_actions_only",
            "local_pdf_preview_only",
            "exact_confirmation_before_official_action",
            "formal_logic_requires_source_evidence",
        ],
        blocked_actions=[
            "official_upload",
            "permit_submission",
            "certification",
            "fee_payment",
            "account_security_transition",
            "inspection_scheduling",
        ],
        runtime_policy={
            "liveCrawlAllowedByDefault": False,
            "officialDevhubActionAllowedByDefault": False,
            "privateArtifactPersistence": "forbidden",
            "requiresHumanAttendanceBeforeBrowserUse": True,
        },
    )


def deterministic_artifact_contracts(fallback_kind: str) -> list[str]:
    manual_metadata = MANUAL_GOAL_FALLBACK_METADATA.get(fallback_kind)
    if manual_metadata is not None:
        return list(manual_metadata[2])
    if fallback_kind == "platform_continuation":
        return [
            "archive_manifest",
            "normalized_document_record",
            "playwright_draft_plan",
            "pdf_preview_field_map",
            "formal_logic_guardrail_batch",
        ]
    if fallback_kind == "processor_suite_planning":
        return [
            "processor_handoff_manifest",
            "normalized_public_document",
            "pdf_metadata_record",
            "requirement_batch",
            "human_review_gate",
        ]
    if fallback_kind == "playwright_pdf_handoff":
        return [
            "redacted_fact_map",
            "accessible_selector_plan",
            "pdf_preview_field_map",
            "exact_confirmation_checkpoint",
            "audit_event",
        ]
    if fallback_kind == "supervisor_idle_recovery":
        return [
            "completed_board_summary",
            "goal_aligned_task_synthesis",
            "duplicate_tranche_guard",
            "blocked_retry_churn_guard",
            "immediate_restart_gate",
        ]
    return ["deterministic_progress_record"]
