"""Validation for PP&D public source freshness watch plan v3.

The validator is intentionally side-effect free. It checks proposed watch rows before
any crawler, processor, browser, archive, release, or agent-state mutation can be
represented as active work.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse


ALLOWED_PUBLIC_HOSTS = frozenset(
    {
        "www.portland.gov",
        "devhub.portlandoregon.gov",
        "www.portlandoregon.gov",
        "www.portlandmaps.com",
    }
)

AUTHENTICATED_URL_MARKERS = (
    "/account",
    "/accounts",
    "/auth",
    "/dashboard",
    "/login",
    "/logout",
    "/my-permits",
    "/oauth",
    "/permitcart",
    "/profile",
    "/register",
    "/session",
    "/signin",
    "/sign-in",
    "/user",
)

RAW_ARTIFACT_MARKERS = (
    "raw_body",
    "body_html",
    "body_text",
    "download_path",
    "download_url",
    "archive_path",
    "archive_url",
    "warc_path",
    "browser_artifact",
    "browser_trace",
    "trace_path",
    "har_path",
    "screenshot_path",
    "storage_state",
    "cookie_jar",
)

COMPLETION_CLAIM_MARKERS = (
    "crawler_completed",
    "crawl_completed",
    "processor_completed",
    "processing_completed",
    "extraction_completed",
    "archive_completed",
    "live_crawl_completed",
    "processor_run_completed",
)

OUTCOME_GUARANTEE_MARKERS = (
    "approval_guaranteed",
    "permit_guaranteed",
    "issuance_guaranteed",
    "inspection_pass_guaranteed",
    "legal_compliance_guaranteed",
    "guarantees_approval",
    "guarantees_permit",
    "guaranteed_outcome",
)

ACTIVE_MUTATION_MARKERS = (
    "active_source_mutation",
    "active_schedule_mutation",
    "active_requirement_mutation",
    "active_process_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_monitoring_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
    "mutates_sources",
    "mutates_schedule",
    "mutates_requirements",
    "mutates_processes",
    "mutates_guardrails",
    "mutates_prompts",
    "mutates_monitoring",
    "mutates_release_state",
    "mutates_agent_state",
)

PRIORITIES = frozenset({"critical", "high", "medium", "low"})


@dataclass(frozen=True)
class WatchPlanError:
    row: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"row": self.row, "code": self.code, "message": self.message}


class WatchPlanValidationError(ValueError):
    """Raised when a source freshness watch plan is not policy compliant."""

    def __init__(self, errors: Iterable[WatchPlanError]) -> None:
        self.errors = tuple(errors)
        detail = "; ".join(f"{error.row}:{error.code}" for error in self.errors)
        super().__init__(f"invalid public source freshness watch plan v3: {detail}")


def validate_public_source_freshness_watch_plan_v3(plan: Mapping[str, Any]) -> None:
    """Validate a public source freshness watch plan v3.

    Accepted inputs are dictionaries containing either ``watch_rows`` or ``rows``.
    The function raises ``WatchPlanValidationError`` with stable error codes when
    any row requests unsafe behavior or omits required traceability.
    """

    errors: list[WatchPlanError] = []

    version = str(plan.get("version", "")).strip()
    if version not in {"public_source_freshness_watch_plan_v3", "v3"}:
        errors.append(
            WatchPlanError(
                row="plan",
                code="unsupported_version",
                message="watch plan must declare public source freshness watch plan v3",
            )
        )

    rows = plan.get("watch_rows", plan.get("rows"))
    if not isinstance(rows, list) or not rows:
        errors.append(
            WatchPlanError(
                row="plan",
                code="missing_watch_rows",
                message="watch plan must include at least one watch row",
            )
        )
        raise WatchPlanValidationError(errors)

    for index, row in enumerate(rows):
        row_name = _row_name(row, index)
        if not isinstance(row, Mapping):
            errors.append(
                WatchPlanError(row=row_name, code="invalid_row", message="watch row must be an object")
            )
            continue

        _validate_citations(row, row_name, errors)
        _validate_url(row, row_name, errors)
        _validate_priority_and_rationale(row, row_name, errors)
        _validate_affected_refs(row, row_name, errors)
        _reject_markers(row, row_name, RAW_ARTIFACT_MARKERS, "raw_or_browser_artifact", errors)
        _reject_markers(row, row_name, COMPLETION_CLAIM_MARKERS, "live_completion_claim", errors)
        _reject_markers(row, row_name, OUTCOME_GUARANTEE_MARKERS, "outcome_guarantee", errors)
        _reject_markers(row, row_name, ACTIVE_MUTATION_MARKERS, "active_mutation_flag", errors)

    if errors:
        raise WatchPlanValidationError(errors)


def validate_public_source_freshness_watch_plan_v3_dict(plan: Mapping[str, Any]) -> dict[str, Any]:
    """Return a serializable validation result instead of raising."""

    try:
        validate_public_source_freshness_watch_plan_v3(plan)
    except WatchPlanValidationError as exc:
        return {"ok": False, "errors": [error.as_dict() for error in exc.errors]}
    return {"ok": True, "errors": []}


def _row_name(row: Any, index: int) -> str:
    if isinstance(row, Mapping):
        candidate = row.get("watch_id") or row.get("source_id") or row.get("id")
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return f"watch_rows[{index}]"


def _validate_citations(row: Mapping[str, Any], row_name: str, errors: list[WatchPlanError]) -> None:
    citations = row.get("citations", row.get("source_evidence_ids"))
    if not _non_empty_string_list(citations):
        errors.append(
            WatchPlanError(
                row=row_name,
                code="missing_citations",
                message="watch row must cite source evidence before freshness monitoring is proposed",
            )
        )


def _validate_url(row: Mapping[str, Any], row_name: str, errors: list[WatchPlanError]) -> None:
    url = row.get("canonical_url", row.get("url"))
    if not isinstance(url, str) or not url.strip():
        errors.append(WatchPlanError(row=row_name, code="missing_url", message="watch row must include a URL"))
        return

    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    path = parsed.path.lower()
    if parsed.scheme != "https" or host not in ALLOWED_PUBLIC_HOSTS:
        errors.append(
            WatchPlanError(
                row=row_name,
                code="non_allowlisted_url",
                message="watch row URL must be an HTTPS URL on the PP&D public allowlist",
            )
        )

    auth_scope = str(row.get("auth_scope", row.get("privacy_classification", ""))).lower()
    requires_auth = row.get("requires_auth") is True or row.get("authenticated") is True
    if requires_auth or "authenticated" in auth_scope or any(marker in path for marker in AUTHENTICATED_URL_MARKERS):
        errors.append(
            WatchPlanError(
                row=row_name,
                code="authenticated_url",
                message="watch row must not target authenticated or account-scoped URLs",
            )
        )


def _validate_priority_and_rationale(
    row: Mapping[str, Any], row_name: str, errors: list[WatchPlanError]
) -> None:
    priority = row.get("priority")
    if not isinstance(priority, str) or priority.strip().lower() not in PRIORITIES:
        errors.append(
            WatchPlanError(
                row=row_name,
                code="missing_priority",
                message="watch row must include priority critical, high, medium, or low",
            )
        )

    decision = str(row.get("decision", row.get("watch_decision", "watch"))).strip().lower()
    if decision in {"skip", "defer"}:
        rationale_key = "skip_rationale" if decision == "skip" else "defer_rationale"
        rationale = row.get(rationale_key) or row.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append(
                WatchPlanError(
                    row=row_name,
                    code=f"missing_{decision}_rationale",
                    message=f"{decision} watch rows must include a specific rationale",
                )
            )


def _validate_affected_refs(row: Mapping[str, Any], row_name: str, errors: list[WatchPlanError]) -> None:
    requirements = row.get("affected_requirements", row.get("affected_requirement_ids"))
    guardrails = row.get("affected_guardrails", row.get("affected_guardrail_bundle_ids"))
    if not _non_empty_string_list(requirements):
        errors.append(
            WatchPlanError(
                row=row_name,
                code="missing_affected_requirement",
                message="watch row must identify at least one affected requirement",
            )
        )
    if not _non_empty_string_list(guardrails):
        errors.append(
            WatchPlanError(
                row=row_name,
                code="missing_affected_guardrail",
                message="watch row must identify at least one affected guardrail bundle",
            )
        )


def _reject_markers(
    value: Any,
    row_name: str,
    markers: Iterable[str],
    code: str,
    errors: list[WatchPlanError],
) -> None:
    marker_set = set(markers)
    for path, found in _walk_marker_values(value):
        key = path.rsplit(".", 1)[-1].lower()
        if key in marker_set:
            errors.append(
                WatchPlanError(
                    row=row_name,
                    code=code,
                    message=f"watch row includes prohibited field {path}",
                )
            )
            continue
        if isinstance(found, str):
            normalized = found.strip().lower().replace("-", "_").replace(" ", "_")
            if normalized in marker_set:
                errors.append(
                    WatchPlanError(
                        row=row_name,
                        code=code,
                        message=f"watch row includes prohibited marker {found}",
                    )
                )
        elif found is True and key in marker_set:
            errors.append(
                WatchPlanError(
                    row=row_name,
                    code=code,
                    message=f"watch row enables prohibited flag {path}",
                )
            )


def _walk_marker_values(value: Any, prefix: str = "row") -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}"
            yield child_prefix, child
            yield from _walk_marker_values(child, child_prefix)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_prefix = f"{prefix}[{index}]"
            yield child_prefix, child
            yield from _walk_marker_values(child, child_prefix)


def _non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and any(isinstance(item, str) and item.strip() for item in value)
