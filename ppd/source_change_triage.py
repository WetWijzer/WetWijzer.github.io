"""Fixture-first public source change triage packet builder.

The packet produced here is intentionally offline-only. It consumes synthetic
freshness queue outcomes and emits deterministic review rows without fetching
live sources, persisting raw bodies, promoting public artifacts, or claiming any
official PP&D action occurred.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

PACKET_SCHEMA_VERSION = "public_source_change_triage_packet.v1"
OFFLINE_REPLAY_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("python3", "-m", "pytest", "ppd/tests/test_source_change_triage_packet.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)


@dataclass(frozen=True)
class CitationCheck:
    """Result of checking that cited evidence survived synthetic extraction."""

    status: str
    before_count: int
    after_count: int
    missing_evidence_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "before_count": self.before_count,
            "after_count": self.after_count,
            "missing_evidence_ids": list(self.missing_evidence_ids),
        }


def build_triage_packet(
    freshness_queue_outcomes: Mapping[str, Any],
    *,
    fixture_name: str = "synthetic freshness queue outcomes",
) -> dict[str, Any]:
    """Build an offline public source change triage packet.

    Args:
        freshness_queue_outcomes: Synthetic fixture data containing an
            ``outcomes`` list. The function treats the input as already-captured
            metadata and never dereferences source URLs.
        fixture_name: Human-readable fixture label for provenance.

    Returns:
        A deterministic packet suitable for committed validation fixtures.
    """

    outcomes = freshness_queue_outcomes.get("outcomes", [])
    if not isinstance(outcomes, Sequence) or isinstance(outcomes, (str, bytes)):
        raise ValueError("freshness queue fixture must contain an outcomes list")

    rows = [_build_row(outcome) for outcome in outcomes]
    rows.sort(key=lambda row: (row["source_id"], row["canonical_url"]))

    return {
        "schema_version": PACKET_SCHEMA_VERSION,
        "packet_id": _stable_packet_id(rows),
        "input_fixture": fixture_name,
        "source_queue_id": str(freshness_queue_outcomes.get("queue_id", "synthetic-freshness-queue")),
        "generated_from": "fixture-first synthetic freshness outcomes",
        "safety_invariants": {
            "live_source_access": False,
            "raw_body_persisted": False,
            "public_artifact_promotion": False,
            "official_action_claims": False,
        },
        "summary_counts": _summary_counts(rows),
        "rows": rows,
        "offline_validation_replay_commands": [list(command) for command in OFFLINE_REPLAY_COMMANDS],
    }


def _build_row(outcome: Any) -> dict[str, Any]:
    if not isinstance(outcome, Mapping):
        raise ValueError("each freshness outcome must be an object")

    source_id = _required_text(outcome, "source_id")
    canonical_url = _required_text(outcome, "canonical_url")
    previous_hash = _optional_text(outcome.get("previous_content_hash"))
    observed_hash = _optional_text(outcome.get("observed_content_hash"))
    fetch_status = str(outcome.get("fetch_status", "success"))
    extraction_status = str(outcome.get("extraction_status", "success"))
    raw_body_persisted = bool(outcome.get("raw_body_persisted", False))
    public_artifact_promotion_requested = bool(outcome.get("public_artifact_promotion_requested", False))
    live_source_access = bool(outcome.get("live_source_access", False))
    official_action_claimed = bool(outcome.get("official_action_claimed", False))

    citation_check = _citation_check(outcome)
    safety_violation = any(
        (
            raw_body_persisted,
            public_artifact_promotion_requested,
            live_source_access,
            official_action_claimed,
        )
    )
    needs_review_reason = _needs_review_reason(
        fetch_status=fetch_status,
        extraction_status=extraction_status,
        citation_check=citation_check,
        safety_violation=safety_violation,
    )

    if needs_review_reason:
        triage_status = "needs-review"
    elif previous_hash == observed_hash:
        triage_status = "unchanged"
    else:
        triage_status = "changed"

    impacted = {
        "requirement_ids": _sorted_texts(outcome.get("candidate_requirement_refs", [])),
        "process_ids": _sorted_texts(outcome.get("candidate_process_refs", [])),
        "guardrail_bundle_ids": _sorted_texts(outcome.get("candidate_guardrail_refs", [])),
    }

    return {
        "source_id": source_id,
        "canonical_url": canonical_url,
        "normalized_document_id": _optional_text(outcome.get("normalized_document_id")),
        "triage_status": triage_status,
        "previous_content_hash": previous_hash,
        "observed_content_hash": observed_hash,
        "fetch_status": fetch_status,
        "extraction_status": extraction_status,
        "impacted_references": impacted,
        "citation_preservation_check": citation_check.as_dict(),
        "blocked_promotion_explanation": _blocked_promotion_explanation(triage_status, needs_review_reason),
        "rollback_notes": _rollback_notes(triage_status, source_id),
        "safety_checks": {
            "live_source_access": live_source_access,
            "raw_body_persisted": raw_body_persisted,
            "public_artifact_promotion_requested": public_artifact_promotion_requested,
            "official_action_claimed": official_action_claimed,
        },
    }


def _citation_check(outcome: Mapping[str, Any]) -> CitationCheck:
    before = _sorted_texts(outcome.get("citation_evidence_ids_before", []))
    after = _sorted_texts(outcome.get("citation_evidence_ids_after", []))
    missing = tuple(item for item in before if item not in set(after))

    if not before:
        status = "not-applicable"
    elif missing:
        status = "failed"
    else:
        status = "passed"

    return CitationCheck(
        status=status,
        before_count=len(before),
        after_count=len(after),
        missing_evidence_ids=missing,
    )


def _needs_review_reason(
    *,
    fetch_status: str,
    extraction_status: str,
    citation_check: CitationCheck,
    safety_violation: bool,
) -> str | None:
    if safety_violation:
        return "fixture outcome reports a forbidden side effect"
    if fetch_status != "success":
        return f"synthetic fetch status is {fetch_status}"
    if extraction_status != "success":
        return f"synthetic extraction status is {extraction_status}"
    if citation_check.status == "failed":
        return "citation evidence was not preserved"
    return None


def _blocked_promotion_explanation(triage_status: str, needs_review_reason: str | None) -> str:
    base = (
        "Promotion blocked: this fixture-first triage packet is validation-only and "
        "does not include live source access, raw body persistence, public artifact "
        "promotion, or official PP&D action claims."
    )
    if triage_status == "needs-review" and needs_review_reason:
        return f"{base} Human review required because {needs_review_reason}."
    if triage_status == "changed":
        return f"{base} Changed rows require cited human review before any downstream promotion."
    return f"{base} Unchanged rows may only be used to replay offline validation."


def _rollback_notes(triage_status: str, source_id: str) -> str:
    if triage_status == "unchanged":
        return f"No rollback needed for {source_id}; keep prior requirement and guardrail references active."
    return (
        f"Rollback for {source_id}: retain the previously validated requirement, process, "
        "and guardrail bundle references until a cited human review approves a replacement packet."
    )


def _summary_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = {"changed": 0, "unchanged": 0, "needs-review": 0}
    for row in rows:
        status = str(row.get("triage_status", "needs-review"))
        counts[status] = counts.get(status, 0) + 1
    counts["total"] = len(rows)
    return counts


def _stable_packet_id(rows: Sequence[Mapping[str, Any]]) -> str:
    parts = [f"{row['source_id']}:{row['triage_status']}" for row in rows]
    return "triage-v1-" + str(abs(hash(tuple(parts))))


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    text = _optional_text(value)
    if not text:
        raise ValueError(f"freshness outcome missing required text field: {key}")
    return text


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _sorted_texts(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, (str, bytes)):
        raise ValueError("expected a list of text values, not a string")
    return sorted({str(value).strip() for value in values if str(value).strip()})
