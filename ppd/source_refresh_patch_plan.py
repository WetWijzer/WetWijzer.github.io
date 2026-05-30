"""Fixture-first public source refresh patch plan generation and validation.

This module intentionally produces proposed patch rows only. It does not crawl,
download, execute processors, persist raw bodies, or mutate registries.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping
from urllib.parse import parse_qsl, urlparse

PLAN_VERSION = "public-source-refresh-patch-plan-v1"
NON_EXECUTING_POLICY = {
    "recrawl": False,
    "download": False,
    "processor_execution": False,
    "raw_body_storage": False,
    "registry_mutation": False,
}

ALLOWLISTED_HOSTS = frozenset(
    {
        "www.portland.gov",
        "portland.gov",
        "devhub.portlandoregon.gov",
        "www.portlandoregon.gov",
        "portlandoregon.gov",
        "www.portlandmaps.com",
        "portlandmaps.com",
    }
)

AUTHENTICATED_PATH_MARKERS = (
    "/login",
    "/logout",
    "/signin",
    "/sign-in",
    "/sign_in",
    "/register",
    "/account",
    "/accounts",
    "/my-permits",
    "/mypermits",
    "/dashboard",
    "/user/",
    "/users/",
    "/profile",
    "/session",
    "/sessions",
    "/oauth",
    "/saml",
    "/auth",
)

AUTHENTICATED_QUERY_KEYS = frozenset(
    {
        "access_token",
        "auth",
        "code",
        "id_token",
        "key",
        "password",
        "refresh_token",
        "session",
        "sid",
        "signature",
        "sso",
        "state",
        "ticket",
        "token",
    }
)

RAW_BODY_KEYS = frozenset(
    {
        "body",
        "body_html",
        "body_text",
        "content",
        "content_html",
        "content_text",
        "dom",
        "html",
        "markdown",
        "page_body",
        "page_html",
        "page_text",
        "raw",
        "raw_body",
        "raw_content",
        "raw_html",
        "raw_markdown",
        "raw_page",
        "raw_text",
        "response_body",
        "text",
    }
)

DOWNLOADED_DOCUMENT_KEYS = frozenset(
    {
        "attachment_bytes",
        "attachment_path",
        "attachments",
        "base64_document",
        "blob",
        "document_bytes",
        "document_path",
        "download",
        "download_path",
        "downloaded_document",
        "downloaded_documents",
        "file_bytes",
        "file_path",
        "local_document",
        "local_path",
        "pdf_bytes",
        "pdf_path",
        "saved_file",
        "tmp_path",
        "warc_path",
    }
)

COMPLETION_CLAIM_KEYS = frozenset(
    {
        "archive_complete",
        "archive_completed",
        "archive_completion_claim",
        "archived",
        "completed",
        "completion_claim",
        "extraction_complete",
        "processor_complete",
        "processor_completed",
        "processor_completion_claim",
        "refresh_complete",
        "refresh_completed",
    }
)

MUTATION_FLAG_KEYS = frozenset(
    {
        "active_agent_state_mutation",
        "active_guardrail_mutation",
        "active_monitoring_mutation",
        "active_process_mutation",
        "active_release_state_mutation",
        "active_requirement_mutation",
        "active_source_mutation",
        "agent_state_mutation",
        "agent_state_mutation_enabled",
        "apply_agent_state_changes",
        "apply_guardrail_changes",
        "apply_monitoring_changes",
        "apply_process_changes",
        "apply_release_state_changes",
        "apply_requirement_changes",
        "apply_source_changes",
        "commit_agent_state",
        "commit_guardrails",
        "commit_monitoring",
        "commit_processes",
        "commit_release_state",
        "commit_requirements",
        "commit_sources",
        "guardrail_mutation",
        "guardrail_mutation_enabled",
        "monitoring_mutation",
        "monitoring_mutation_enabled",
        "mutate_agent_state",
        "mutate_guardrails",
        "mutate_monitoring",
        "mutate_processes",
        "mutate_release_state",
        "mutate_requirements",
        "mutate_sources",
        "process_mutation",
        "process_mutation_enabled",
        "release_state_mutation",
        "release_state_mutation_enabled",
        "requirement_mutation",
        "requirement_mutation_enabled",
        "source_mutation",
        "source_mutation_enabled",
        "update_agent_state",
        "update_guardrails",
        "update_monitoring",
        "update_processes",
        "update_release_state",
        "update_requirements",
        "update_sources",
    }
)

OUTCOME_GUARANTEE_PHRASES = (
    "guarantee approval",
    "guarantee permit",
    "guaranteed approval",
    "guaranteed issuance",
    "guarantees approval",
    "guarantees permit",
    "legal compliance guaranteed",
    "legally compliant",
    "permit approval guaranteed",
    "permit will be approved",
    "permit will be issued",
    "will be approved",
    "will be issued",
    "will pass inspection",
    "will satisfy code",
)

PROCESSOR_COMPLETION_PHRASES = (
    "archive completed",
    "archive is complete",
    "archived successfully",
    "processor completed",
    "processor execution completed",
    "processor finished",
    "refresh completed",
)


class SourceRefreshPatchPlanError(ValueError):
    """Raised when fixture inputs cannot produce a deterministic patch plan."""


@dataclass(frozen=True)
class PatchPlanValidationIssue:
    """A deterministic validation issue for a public source refresh patch plan."""

    code: str
    path: str
    message: str


class PatchPlanValidationError(ValueError):
    """Raised when callers request exception-based patch plan validation."""

    def __init__(self, issues: Iterable[PatchPlanValidationIssue]) -> None:
        self.issues = tuple(issues)
        joined = "; ".join(f"{issue.path}: {issue.code}" for issue in self.issues)
        super().__init__(joined)


@dataclass(frozen=True)
class ApprovedDisposition:
    disposition_id: str
    queue_item_id: str
    reviewer: str
    reviewed_at: str
    approved_action: str
    source_id: str
    requirement_ids: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class ReviewerQueueItem:
    queue_item_id: str
    source_id: str
    canonical_url: str
    visible_title: str
    visible_date_text: str
    visible_date_review_note: str
    previous_content_hash: str
    proposed_content_hash: str
    freshness_status: str
    observed_at: str
    affected_requirement_ids: tuple[str, ...]
    validation_checks: tuple[str, ...]


def build_public_source_refresh_patch_plan(
    disposition_ledger: Mapping[str, Any],
    reviewer_queue: Mapping[str, Any],
) -> dict[str, Any]:
    """Build non-executing proposed patch rows from approved fixture ledgers.

    The input shape is deliberately plain JSON-compatible data so committed
    fixtures can drive validation without live network access or processor runs.
    """

    dispositions = _approved_dispositions(disposition_ledger)
    queue_items = _queue_items_by_id(reviewer_queue)
    generated_at = _fixture_generated_at(disposition_ledger, reviewer_queue)

    rows: list[dict[str, Any]] = []
    for disposition in dispositions:
        queue_item = queue_items.get(disposition.queue_item_id)
        if queue_item is None:
            raise SourceRefreshPatchPlanError(
                f"approved disposition {disposition.disposition_id} references missing queue item "
                f"{disposition.queue_item_id}"
            )
        if disposition.source_id != queue_item.source_id:
            raise SourceRefreshPatchPlanError(
                f"approved disposition {disposition.disposition_id} source_id does not match queue item "
                f"{queue_item.queue_item_id}"
            )

        affected_requirement_ids = _unique_sorted(
            [*disposition.requirement_ids, *queue_item.affected_requirement_ids]
        )
        affected_source_ids = (queue_item.source_id,)
        rollback_checkpoint = {
            "checkpoint_id": f"rollback:{queue_item.source_id}:{queue_item.previous_content_hash}",
            "restore_source_id": queue_item.source_id,
            "restore_content_hash": queue_item.previous_content_hash,
            "restore_freshness_status": "unchanged_before_proposed_refresh_patch",
            "registry_mutation_required": False,
        }
        rows.append(
            {
                "patch_row_id": f"psrpp-v1:{queue_item.queue_item_id}:{disposition.disposition_id}",
                "row_type": "proposed_source_freshness_metadata_patch",
                "execution_mode": "proposal_only",
                "citations": [
                    {
                        "source_id": queue_item.source_id,
                        "url": queue_item.canonical_url,
                        "queue_item_id": queue_item.queue_item_id,
                        "disposition_id": disposition.disposition_id,
                    }
                ],
                "source_freshness_metadata": {
                    "source_id": queue_item.source_id,
                    "canonical_url": queue_item.canonical_url,
                    "freshness_status": queue_item.freshness_status,
                    "previous_content_hash": queue_item.previous_content_hash,
                    "proposed_content_hash": queue_item.proposed_content_hash,
                    "observed_at": queue_item.observed_at,
                    "reviewed_at": disposition.reviewed_at,
                    "reviewer": disposition.reviewer,
                    "approved_action": disposition.approved_action,
                },
                "requirement_impact_links": [
                    {
                        "source_id": queue_item.source_id,
                        "requirement_id": requirement_id,
                        "impact": "source_refresh_review_required",
                    }
                    for requirement_id in affected_requirement_ids
                ],
                "visible_page_review_notes": {
                    "title": queue_item.visible_title,
                    "visible_date_text": queue_item.visible_date_text,
                    "date_review_note": queue_item.visible_date_review_note,
                    "reviewer_disposition_note": disposition.notes,
                },
                "affected_source_ids": list(affected_source_ids),
                "affected_requirement_ids": affected_requirement_ids,
                "rollback_checkpoint": rollback_checkpoint,
                "rollback_checkpoints": [rollback_checkpoint],
                "validation_inventory": {
                    "fixture_queue_item_id": queue_item.queue_item_id,
                    "fixture_disposition_id": disposition.disposition_id,
                    "required_checks": list(queue_item.validation_checks),
                    "blocked_operations": dict(NON_EXECUTING_POLICY),
                    "requires_human_review_before_apply": True,
                },
            }
        )

    rows.sort(key=lambda row: row["patch_row_id"])
    plan = {
        "plan_version": PLAN_VERSION,
        "generated_at": generated_at,
        "execution_policy": dict(NON_EXECUTING_POLICY),
        "inputs": {
            "disposition_ledger_id": str(disposition_ledger.get("ledger_id", "")),
            "reviewer_queue_id": str(reviewer_queue.get("queue_id", "")),
        },
        "proposed_patch_rows": rows,
    }
    require_valid_public_source_refresh_patch_plan_v1(plan)
    return plan


def validate_public_source_refresh_patch_plan_v1(payload: Any) -> list[PatchPlanValidationIssue]:
    """Return validation issues for a public source refresh patch plan v1 payload."""

    issues: list[PatchPlanValidationIssue] = []
    if not isinstance(payload, dict):
        return [PatchPlanValidationIssue("payload_not_object", "$", "Patch plan must be an object.")]

    if payload.get("plan_version") != PLAN_VERSION:
        issues.append(
            PatchPlanValidationIssue(
                "invalid_plan_version",
                "plan_version",
                f"Patch plan must use {PLAN_VERSION}.",
            )
        )

    rows = payload.get("proposed_patch_rows")
    if not isinstance(rows, list) or not rows:
        issues.append(
            PatchPlanValidationIssue(
                "missing_patch_rows",
                "proposed_patch_rows",
                "Patch plan must include proposed_patch_rows.",
            )
        )
        rows = []

    _validate_non_executing_policy(payload.get("execution_policy"), "execution_policy", issues)
    _validate_common_safety(payload, "$", issues)

    for index, row in enumerate(rows):
        row_path = f"proposed_patch_rows[{index}]"
        if not isinstance(row, dict):
            issues.append(PatchPlanValidationIssue("patch_row_not_object", row_path, "Patch row must be an object."))
            continue
        _validate_patch_row(row, row_path, issues)
        _validate_common_safety(row, row_path, issues)

    return issues


def require_valid_public_source_refresh_patch_plan_v1(payload: Any) -> None:
    """Raise ``PatchPlanValidationError`` when the patch plan is invalid."""

    issues = validate_public_source_refresh_patch_plan_v1(payload)
    if issues:
        raise PatchPlanValidationError(issues)


def _validate_patch_row(row: dict[str, Any], path: str, issues: list[PatchPlanValidationIssue]) -> None:
    if not _has_citation(row):
        issues.append(PatchPlanValidationIssue("missing_citation", path, "Patch row must include at least one public source citation."))

    if not _is_nonempty_string_list(row.get("affected_source_ids")):
        issues.append(
            PatchPlanValidationIssue(
                "missing_affected_source_ids",
                f"{path}.affected_source_ids",
                "Patch row must name affected source IDs.",
            )
        )

    if not _is_nonempty_string_list(row.get("affected_requirement_ids")):
        issues.append(
            PatchPlanValidationIssue(
                "missing_affected_requirement_ids",
                f"{path}.affected_requirement_ids",
                "Patch row must name affected requirement IDs.",
            )
        )

    rollback_checkpoints = row.get("rollback_checkpoints")
    rollback_checkpoint = row.get("rollback_checkpoint")
    if not (_is_nonempty_list(rollback_checkpoints) or isinstance(rollback_checkpoint, dict)):
        issues.append(
            PatchPlanValidationIssue(
                "missing_rollback_checkpoints",
                path,
                "Patch row must include rollback checkpoints.",
            )
        )

    execution_mode = row.get("execution_mode")
    if execution_mode != "proposal_only":
        issues.append(
            PatchPlanValidationIssue(
                "invalid_execution_mode",
                f"{path}.execution_mode",
                "Patch rows must be proposal_only.",
            )
        )


def _validate_non_executing_policy(value: Any, path: str, issues: list[PatchPlanValidationIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(PatchPlanValidationIssue("missing_execution_policy", path, "Patch plan must include execution_policy."))
        return
    for key in NON_EXECUTING_POLICY:
        if value.get(key) is not False:
            issues.append(
                PatchPlanValidationIssue(
                    "unsafe_execution_policy",
                    f"{path}.{key}",
                    f"Execution policy {key} must be false.",
                )
            )


def _validate_common_safety(value: Any, path: str, issues: list[PatchPlanValidationIssue]) -> None:
    for key_path, key, child in _walk(value, path):
        normalized_key = key.lower() if key else ""
        if normalized_key in RAW_BODY_KEYS:
            issues.append(PatchPlanValidationIssue("raw_page_body_present", key_path, "Patch plan must not include raw page bodies."))
        if normalized_key in DOWNLOADED_DOCUMENT_KEYS:
            issues.append(PatchPlanValidationIssue("downloaded_document_present", key_path, "Patch plan must not include downloaded documents or local document paths."))
        if normalized_key in COMPLETION_CLAIM_KEYS and _truthy_claim(child):
            issues.append(PatchPlanValidationIssue("processor_or_archive_completion_claim", key_path, "Patch plan must not claim processor or archive completion."))
        if normalized_key in MUTATION_FLAG_KEYS and _truthy_claim(child):
            issues.append(PatchPlanValidationIssue("active_mutation_flag", key_path, "Patch plan must not enable source, requirement, process, guardrail, monitoring, release-state, or agent-state mutation."))
        if normalized_key in {"status", "state"} and isinstance(child, str) and child.strip().lower() in {"complete", "completed", "archived", "processed", "released"}:
            issues.append(PatchPlanValidationIssue("processor_or_archive_completion_claim", key_path, "Patch plan status must not claim completion."))
        if _looks_like_url_value(normalized_key, child):
            _validate_url(str(child), key_path, issues)
        if isinstance(child, str):
            if _contains_outcome_guarantee(child):
                issues.append(PatchPlanValidationIssue("outcome_guarantee", key_path, "Patch plan must not guarantee legal or permitting outcomes."))
            if _contains_processor_completion_claim(child):
                issues.append(PatchPlanValidationIssue("processor_or_archive_completion_claim", key_path, "Patch plan must not claim processor or archive completion."))


def _has_citation(row: dict[str, Any]) -> bool:
    citations = row.get("citations", row.get("source_citations", row.get("source_evidence")))
    if not isinstance(citations, list) or not citations:
        return False
    for citation in citations:
        if not isinstance(citation, dict):
            continue
        source_id = citation.get("source_id") or citation.get("id")
        url = citation.get("url") or citation.get("canonical_url")
        if _nonempty_string(source_id) and _nonempty_string(url):
            return True
    return False


def _validate_url(url: str, path: str, issues: list[PatchPlanValidationIssue]) -> None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or host not in ALLOWLISTED_HOSTS:
        issues.append(PatchPlanValidationIssue("url_not_allowlisted", path, "Patch plan URL must be HTTPS and on the PP&D public-source allowlist."))
        return
    lowered_path = parsed.path.lower()
    if any(marker in lowered_path for marker in AUTHENTICATED_PATH_MARKERS):
        issues.append(PatchPlanValidationIssue("authenticated_url", path, "Patch plan URL must not target authenticated or account-scoped surfaces."))
    query_keys = {key.lower() for key, _value in parse_qsl(parsed.query, keep_blank_values=True)}
    if query_keys & AUTHENTICATED_QUERY_KEYS:
        issues.append(PatchPlanValidationIssue("authenticated_url", path, "Patch plan URL must not include auth, token, session, or SSO query parameters."))


def _approved_dispositions(disposition_ledger: Mapping[str, Any]) -> list[ApprovedDisposition]:
    dispositions: list[ApprovedDisposition] = []
    for raw_item in disposition_ledger.get("items", []):
        if raw_item.get("disposition") != "approved":
            continue
        dispositions.append(
            ApprovedDisposition(
                disposition_id=_required_str(raw_item, "disposition_id"),
                queue_item_id=_required_str(raw_item, "queue_item_id"),
                reviewer=_required_str(raw_item, "reviewer"),
                reviewed_at=_required_str(raw_item, "reviewed_at"),
                approved_action=_required_str(raw_item, "approved_action"),
                source_id=_required_str(raw_item, "source_id"),
                requirement_ids=tuple(_required_str_list(raw_item, "requirement_ids")),
                notes=_required_str(raw_item, "notes"),
            )
        )
    dispositions.sort(key=lambda item: item.disposition_id)
    return dispositions


def _queue_items_by_id(reviewer_queue: Mapping[str, Any]) -> dict[str, ReviewerQueueItem]:
    queue_items: dict[str, ReviewerQueueItem] = {}
    for raw_item in reviewer_queue.get("items", []):
        queue_item = ReviewerQueueItem(
            queue_item_id=_required_str(raw_item, "queue_item_id"),
            source_id=_required_str(raw_item, "source_id"),
            canonical_url=_required_str(raw_item, "canonical_url"),
            visible_title=_required_str(raw_item, "visible_title"),
            visible_date_text=_required_str(raw_item, "visible_date_text"),
            visible_date_review_note=_required_str(raw_item, "visible_date_review_note"),
            previous_content_hash=_required_str(raw_item, "previous_content_hash"),
            proposed_content_hash=_required_str(raw_item, "proposed_content_hash"),
            freshness_status=_required_str(raw_item, "freshness_status"),
            observed_at=_required_str(raw_item, "observed_at"),
            affected_requirement_ids=tuple(_required_str_list(raw_item, "affected_requirement_ids")),
            validation_checks=tuple(_required_str_list(raw_item, "validation_checks")),
        )
        if queue_item.queue_item_id in queue_items:
            raise SourceRefreshPatchPlanError(f"duplicate queue item {queue_item.queue_item_id}")
        queue_items[queue_item.queue_item_id] = queue_item
    return queue_items


def _fixture_generated_at(
    disposition_ledger: Mapping[str, Any], reviewer_queue: Mapping[str, Any]
) -> str:
    generated_at = disposition_ledger.get("generated_at") or reviewer_queue.get("generated_at")
    if isinstance(generated_at, str) and generated_at:
        return generated_at
    return datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def _required_str(item: Mapping[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise SourceRefreshPatchPlanError(f"missing required string field {key}")
    return value


def _required_str_list(item: Mapping[str, Any], key: str) -> list[str]:
    value = item.get(key)
    if not isinstance(value, list) or not all(isinstance(entry, str) and entry for entry in value):
        raise SourceRefreshPatchPlanError(f"missing required string list field {key}")
    return value


def _unique_sorted(values: list[str] | tuple[str, ...]) -> list[str]:
    return sorted(set(values))


def _walk(value: Any, path: str) -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}" if path != "$" else key_text
            yield child_path, key_text, child
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, "", child
            yield from _walk(child, child_path)


def _looks_like_url_value(key: str, value: Any) -> bool:
    if not isinstance(value, str):
        return False
    stripped = value.strip().lower()
    if stripped.startswith("http://") or stripped.startswith("https://"):
        return True
    return key.endswith("url") or key in {"url", "canonical_url", "requested_url", "source_url"}


def _contains_outcome_guarantee(value: str) -> bool:
    lowered = " ".join(value.lower().split())
    return any(phrase in lowered for phrase in OUTCOME_GUARANTEE_PHRASES)


def _contains_processor_completion_claim(value: str) -> bool:
    lowered = " ".join(value.lower().split())
    return any(phrase in lowered for phrase in PROCESSOR_COMPLETION_PHRASES)


def _truthy_claim(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in {"", "false", "no", "none", "not_applicable", "n/a"}
    return value is not None


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_nonempty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(_nonempty_string(item) for item in value)


def _is_nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)
