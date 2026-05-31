"""Validation for guardrail bundle stale-source impact matrix v2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

REQUIRED_IMPACT_ROW_IDS = frozenset(
    {
        "source_freshness_status",
        "affected_source_evidence",
        "affected_requirements",
        "affected_guardrails",
        "affected_prompts",
        "affected_contracts",
        "affected_devhub_surfaces",
        "blocked_agent_actions",
        "user_facing_cautions",
        "re_extraction_placeholders",
        "reviewer_dispositions",
        "validation_commands",
    }
)

REQUIRED_HOLD_REASONS = frozenset(
    {
        "stale_source_detected",
        "source_revalidation_required",
        "human_review_required",
    }
)

REQUIRED_MUTATION_FLAGS = frozenset(
    {
        "source_registry",
        "requirements",
        "guardrails",
        "prompts",
        "contracts",
        "devhub_surfaces",
        "release_state",
    }
)

FORBIDDEN_ARTIFACT_TERMS = (
    "auth_state",
    "browser_state",
    "cookie",
    "cookies",
    "downloaded_document",
    "downloaded_pdf",
    "har",
    "local_private_path",
    "private_upload",
    "raw_crawl_output",
    "raw_download",
    "session_storage",
    "screenshot",
    "trace.zip",
)

FORBIDDEN_CLAIM_TERMS = (
    "live crawl completed",
    "live devhub verified",
    "devhub production confirmed",
    "authenticated devhub observed",
    "real user account",
)

FORBIDDEN_GUARANTEE_TERMS = (
    "approval guaranteed",
    "permit guaranteed",
    "legally sufficient",
    "legal advice",
    "will be approved",
    "will pass inspection",
)


@dataclass(frozen=True)
class MatrixFinding:
    """A deterministic validation finding for a stale-source matrix."""

    code: str
    message: str
    location: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "location": self.location}


def validate_guardrail_stale_source_impact_matrix_v2(matrix: Mapping[str, Any]) -> list[MatrixFinding]:
    """Return findings that make a stale-source impact matrix v2 unacceptable."""

    findings: list[MatrixFinding] = []
    if matrix.get("version") != "guardrail_bundle_stale_source_impact_matrix_v2":
        findings.append(
            MatrixFinding(
                "invalid_version",
                "matrix version must be guardrail_bundle_stale_source_impact_matrix_v2",
                "version",
            )
        )

    rows = matrix.get("impact_rows")
    if not isinstance(rows, list) or not rows:
        findings.append(MatrixFinding("missing_impact_rows", "impact_rows must be a non-empty list", "impact_rows"))
        rows = []

    row_ids = {row.get("row_id") for row in rows if isinstance(row, Mapping)}
    for row_id in sorted(REQUIRED_IMPACT_ROW_IDS - row_ids):
        findings.append(
            MatrixFinding("missing_impact_row", f"required impact row is missing: {row_id}", "impact_rows")
        )

    for index, row in enumerate(rows):
        location = f"impact_rows[{index}]"
        if not isinstance(row, Mapping):
            findings.append(MatrixFinding("invalid_impact_row", "impact row must be an object", location))
            continue
        if not row.get("row_id"):
            findings.append(MatrixFinding("missing_impact_row_id", "impact row requires row_id", location))
        if not row.get("impact_summary"):
            findings.append(MatrixFinding("missing_impact_summary", "impact row requires impact_summary", location))
        if not row.get("source_evidence_ids"):
            findings.append(
                MatrixFinding("missing_row_source_evidence", "impact row requires source_evidence_ids", location)
            )

    stale_source_holds = matrix.get("stale_source_hold_reasons")
    if not isinstance(stale_source_holds, list) or not stale_source_holds:
        findings.append(
            MatrixFinding(
                "missing_stale_source_hold_reasons",
                "stale_source_hold_reasons must list fail-closed hold reasons",
                "stale_source_hold_reasons",
            )
        )
        stale_source_holds = []
    for reason in sorted(REQUIRED_HOLD_REASONS - set(_strings(stale_source_holds))):
        findings.append(
            MatrixFinding(
                "missing_stale_source_hold_reason",
                f"required stale-source hold reason is missing: {reason}",
                "stale_source_hold_reasons",
            )
        )

    if not _non_empty_list(matrix.get("re_extraction_placeholders")):
        findings.append(
            MatrixFinding(
                "missing_re_extraction_placeholders",
                "matrix must reserve re-extraction placeholders before promotion",
                "re_extraction_placeholders",
            )
        )

    if not _non_empty_list(matrix.get("user_facing_caution_templates")):
        findings.append(
            MatrixFinding(
                "missing_user_facing_caution_templates",
                "matrix must include user-facing stale-source caution templates",
                "user_facing_caution_templates",
            )
        )

    if not _non_empty_list(matrix.get("blocked_action_reminders")):
        findings.append(
            MatrixFinding(
                "missing_blocked_action_reminders",
                "matrix must remind agents which actions remain blocked while sources are stale",
                "blocked_action_reminders",
            )
        )

    reviewer_dispositions = matrix.get("reviewer_dispositions")
    if not _non_empty_list(reviewer_dispositions):
        findings.append(
            MatrixFinding(
                "missing_reviewer_dispositions",
                "matrix must include reviewer disposition slots",
                "reviewer_dispositions",
            )
        )
    else:
        for index, disposition in enumerate(reviewer_dispositions):
            location = f"reviewer_dispositions[{index}]"
            if not isinstance(disposition, Mapping):
                findings.append(MatrixFinding("invalid_reviewer_disposition", "disposition must be an object", location))
                continue
            if not disposition.get("reviewer_role"):
                findings.append(MatrixFinding("missing_reviewer_role", "disposition requires reviewer_role", location))
            if disposition.get("status") not in {"pending", "approved", "rejected", "needs_rework"}:
                findings.append(
                    MatrixFinding(
                        "invalid_reviewer_disposition_status",
                        "disposition status must be pending, approved, rejected, or needs_rework",
                        location,
                    )
                )

    validation_commands = matrix.get("validation_commands")
    if not _valid_commands(validation_commands):
        findings.append(
            MatrixFinding(
                "missing_validation_commands",
                "matrix must include deterministic validation commands as lists of strings",
                "validation_commands",
            )
        )

    mutation_flags = matrix.get("active_mutation_flags")
    if not isinstance(mutation_flags, Mapping):
        findings.append(
            MatrixFinding(
                "missing_active_mutation_flags",
                "active_mutation_flags must explicitly disable all mutation categories",
                "active_mutation_flags",
            )
        )
    else:
        for flag in sorted(REQUIRED_MUTATION_FLAGS):
            if mutation_flags.get(flag) is not False:
                findings.append(
                    MatrixFinding(
                        "active_mutation_flag_enabled",
                        f"mutation flag must be false while stale-source impact review is pending: {flag}",
                        f"active_mutation_flags.{flag}",
                    )
                )

    flattened = _flatten_text(matrix).lower()
    for term in FORBIDDEN_ARTIFACT_TERMS:
        if term in flattened:
            findings.append(
                MatrixFinding(
                    "forbidden_private_or_raw_artifact",
                    f"matrix references a private, browser/session, raw, or downloaded artifact: {term}",
                    "$",
                )
            )
    for term in FORBIDDEN_CLAIM_TERMS:
        if term in flattened:
            findings.append(
                MatrixFinding(
                    "forbidden_live_crawl_or_devhub_claim",
                    f"matrix makes an unsupported live crawl or DevHub claim: {term}",
                    "$",
                )
            )
    for term in FORBIDDEN_GUARANTEE_TERMS:
        if term in flattened:
            findings.append(
                MatrixFinding(
                    "forbidden_legal_or_permitting_guarantee",
                    f"matrix makes a legal or permitting guarantee: {term}",
                    "$",
                )
            )

    return findings


def assert_guardrail_stale_source_impact_matrix_v2(matrix: Mapping[str, Any]) -> None:
    """Raise ValueError when the stale-source matrix contains validation findings."""

    findings = validate_guardrail_stale_source_impact_matrix_v2(matrix)
    if findings:
        detail = "; ".join(f"{finding.code} at {finding.location}" for finding in findings)
        raise ValueError(f"invalid guardrail stale-source impact matrix v2: {detail}")


def _strings(values: Sequence[Any]) -> list[str]:
    return [value for value in values if isinstance(value, str) and value]


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _valid_commands(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    return all(isinstance(command, list) and command and all(isinstance(part, str) and part for part in command) for command in value)


def _flatten_text(value: Any) -> str:
    if isinstance(value, Mapping):
        return "\n".join(str(key) + "\n" + _flatten_text(item) for key, item in value.items())
    if isinstance(value, list):
        return "\n".join(_flatten_text(item) for item in value)
    if isinstance(value, str):
        return value
    return ""


__all__ = [
    "MatrixFinding",
    "assert_guardrail_stale_source_impact_matrix_v2",
    "validate_guardrail_stale_source_impact_matrix_v2",
]
