"""Validation for reviewer disposition ledger v1 packets.

The ledger is intentionally conservative: reviewer dispositions are evidence
records, not execution records, release approvals, or mutation instructions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

LEDGER_VERSION = "reviewer_disposition_ledger_v1"

PRIVATE_ARTIFACT_MARKERS = (
    "authenticated",
    "auth_state",
    "browser_state",
    "cookie",
    "credential",
    "downloaded",
    "har",
    "local_private_path",
    "private",
    "raw_body",
    "raw_capture",
    "session",
    "screenshot",
    "storage_state",
    "trace",
)

LIVE_EXECUTION_CLAIM_MARKERS = (
    "executed live",
    "live crawl completed",
    "live execution completed",
    "live run completed",
    "promoted to production",
    "promotion completed",
    "released to production",
    "release completed",
)

OUTCOME_GUARANTEE_MARKERS = (
    "approval is guaranteed",
    "guarantee approval",
    "guaranteed approval",
    "guaranteed issuance",
    "permit will be approved",
    "permit will be issued",
    "will pass inspection",
    "will satisfy the city",
)

CONSEQUENTIAL_ACTION_MARKERS = (
    "cancel the inspection",
    "certify the application",
    "create the account",
    "enter payment details",
    "final payment",
    "pay the fee",
    "schedule the inspection",
    "submit the application",
    "submit payment",
    "upload corrections",
    "upload the plans",
)

MUTATION_FLAG_NAMES = (
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_source_mutation",
    "active_source_registry_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation",
    "guardrail_mutation",
    "mutates_agent_state",
    "mutates_guardrails",
    "mutates_prompt",
    "mutates_release_state",
    "mutates_source_registry",
    "mutates_sources",
    "mutates_surface_registry",
    "prompt_mutation",
    "release_state_mutation",
    "source_mutation",
    "source_registry_mutation",
    "surface_registry_mutation",
)

BLOCKER_OPEN_VALUES = {"blocked", "gap", "missing", "open", "unresolved"}
BLOCKER_SAFE_HANDLING_VALUES = {"blocked", "deferred", "escalated", "refused"}


@dataclass(frozen=True)
class LedgerValidationIssue:
    """A deterministic ledger validation issue."""

    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


def validate_reviewer_disposition_ledger_v1(packet: Mapping[str, Any]) -> list[LedgerValidationIssue]:
    """Return validation issues for a reviewer disposition ledger v1 packet."""

    issues: list[LedgerValidationIssue] = []
    if packet.get("ledger_version") != LEDGER_VERSION:
        issues.append(
            LedgerValidationIssue(
                "invalid_ledger_version",
                "ledger_version",
                f"ledger_version must be {LEDGER_VERSION}",
            )
        )

    dispositions = packet.get("dispositions")
    if not isinstance(dispositions, list):
        issues.append(
            LedgerValidationIssue(
                "missing_dispositions",
                "dispositions",
                "dispositions must be a list",
            )
        )
        dispositions = []

    _scan_mapping_for_global_rejections(packet, "", issues)

    for index, disposition in enumerate(dispositions):
        path = f"dispositions[{index}]"
        if not isinstance(disposition, Mapping):
            issues.append(
                LedgerValidationIssue(
                    "invalid_disposition",
                    path,
                    "each disposition must be an object",
                )
            )
            continue
        _validate_disposition(disposition, path, issues)

    return issues


def assert_valid_reviewer_disposition_ledger_v1(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when a ledger has validation issues."""

    issues = validate_reviewer_disposition_ledger_v1(packet)
    if issues:
        formatted = "; ".join(f"{issue.code} at {issue.path}" for issue in issues)
        raise ValueError(f"reviewer disposition ledger v1 validation failed: {formatted}")


def _validate_disposition(
    disposition: Mapping[str, Any],
    path: str,
    issues: list[LedgerValidationIssue],
) -> None:
    owner = disposition.get("reviewer_owner")
    if not isinstance(owner, str) or not owner.strip():
        issues.append(
            LedgerValidationIssue(
                "missing_reviewer_owner",
                f"{path}.reviewer_owner",
                "reviewer_owner is required for every disposition",
            )
        )

    rationale = disposition.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        issues.append(
            LedgerValidationIssue(
                "missing_rationale",
                f"{path}.rationale",
                "rationale is required for every disposition",
            )
        )

    citations = disposition.get("citations")
    if not _has_citation(citations):
        issues.append(
            LedgerValidationIssue(
                "uncited_disposition",
                f"{path}.citations",
                "each disposition must include at least one public citation or source evidence id",
            )
        )

    if _has_unresolved_blocker(disposition) and not _has_safe_blocker_handling(disposition):
        issues.append(
            LedgerValidationIssue(
                "unresolved_blocker_handling_gap",
                path,
                "unresolved blockers must be refused, escalated, deferred, or explicitly blocked with rationale and citation",
            )
        )

    _scan_mapping_for_global_rejections(disposition, path, issues)


def _has_citation(citations: Any) -> bool:
    if isinstance(citations, str):
        return bool(citations.strip())
    if not isinstance(citations, Sequence) or isinstance(citations, (bytes, bytearray)):
        return False
    for citation in citations:
        if isinstance(citation, str) and citation.strip():
            return True
        if isinstance(citation, Mapping):
            source_id = citation.get("source_id") or citation.get("source_evidence_id")
            url = citation.get("url") or citation.get("canonical_url")
            if isinstance(source_id, str) and source_id.strip():
                return True
            if isinstance(url, str) and url.startswith("https://www.portland.gov/"):
                return True
    return False


def _has_unresolved_blocker(disposition: Mapping[str, Any]) -> bool:
    blocker_status = _lower_text(disposition.get("blocker_status"))
    if blocker_status in BLOCKER_OPEN_VALUES:
        return True

    blockers = disposition.get("blockers")
    if isinstance(blockers, Sequence) and not isinstance(blockers, (str, bytes, bytearray)):
        for blocker in blockers:
            if not isinstance(blocker, Mapping):
                continue
            status = _lower_text(blocker.get("status"))
            resolved = blocker.get("resolved")
            if status in BLOCKER_OPEN_VALUES or resolved is False:
                return True
    return False


def _has_safe_blocker_handling(disposition: Mapping[str, Any]) -> bool:
    handling = disposition.get("blocker_handling")
    if not isinstance(handling, Mapping):
        return False

    status = _lower_text(handling.get("status"))
    rationale = handling.get("rationale")
    citations = handling.get("citations") or disposition.get("citations")
    return (
        status in BLOCKER_SAFE_HANDLING_VALUES
        and isinstance(rationale, str)
        and bool(rationale.strip())
        and _has_citation(citations)
    )


def _scan_mapping_for_global_rejections(
    value: Any,
    path: str,
    issues: list[LedgerValidationIssue],
) -> None:
    for child_path, child in _walk(value, path):
        if isinstance(child, str):
            lowered = child.lower().replace("-", "_")
            normalized_phrase = lowered.replace("_", " ")
            if any(marker in lowered for marker in PRIVATE_ARTIFACT_MARKERS):
                issues.append(
                    LedgerValidationIssue(
                        "private_or_raw_artifact_reference",
                        child_path,
                        "ledger must not reference private, authenticated, session, browser, raw, or downloaded artifacts",
                    )
                )
            if any(marker in normalized_phrase for marker in LIVE_EXECUTION_CLAIM_MARKERS):
                issues.append(
                    LedgerValidationIssue(
                        "live_execution_or_promotion_claim",
                        child_path,
                        "ledger must not claim live execution, promotion, or release completion",
                    )
                )
            if any(marker in normalized_phrase for marker in OUTCOME_GUARANTEE_MARKERS):
                issues.append(
                    LedgerValidationIssue(
                        "legal_or_permitting_outcome_guarantee",
                        child_path,
                        "ledger must not guarantee legal, permitting, approval, issuance, or inspection outcomes",
                    )
                )
            if any(marker in normalized_phrase for marker in CONSEQUENTIAL_ACTION_MARKERS):
                issues.append(
                    LedgerValidationIssue(
                        "consequential_action_language",
                        child_path,
                        "ledger must not direct consequential DevHub, payment, upload, certification, scheduling, cancellation, or submission actions",
                    )
                )
        if _path_name(child_path) in MUTATION_FLAG_NAMES and _is_active_flag(child):
            issues.append(
                LedgerValidationIssue(
                    "active_mutation_flag",
                    child_path,
                    "ledger must not carry active source, surface-registry, guardrail, release-state, prompt, or agent-state mutation flags",
                )
            )


def _walk(value: Any, path: str) -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = str(key) if not path else f"{path}.{key}"
            yield from _walk(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")


def _path_name(path: str) -> str:
    if not path:
        return ""
    return path.rsplit(".", 1)[-1].split("[", 1)[0]


def _is_active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "active", "true", "yes"}
    return False


def _lower_text(value: Any) -> str:
    return value.strip().lower() if isinstance(value, str) else ""
