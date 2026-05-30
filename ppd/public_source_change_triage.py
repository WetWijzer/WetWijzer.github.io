"""Validation for public source change triage packets.

The packet validator is intentionally schema-light: supervisors can add fields without
breaking old packets, but promotion-critical evidence and safety fields must be
present before a public source change packet can be accepted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


class PublicSourceChangeTriageError(ValueError):
    """Raised when a public source change triage packet fails validation."""


@dataclass(frozen=True)
class TriageValidationIssue:
    """A deterministic validation issue for a triage packet."""

    code: str
    path: str
    message: str


BLOCKED_SUBSTRINGS = (
    "cookie",
    "session",
    "auth state",
    "storage_state",
    "localstorage",
    "indexeddb",
    "trace.zip",
    "har",
    "screenshot",
    "browser artifact",
    "private devhub",
)

RAW_ARTIFACT_SUBSTRINGS = (
    "raw crawl",
    "raw html",
    "raw_body",
    "downloaded pdf",
    "downloaded document",
    "pdf bytes",
    "crawl output",
    "warc",
)

LIVE_CRAWL_SUBSTRINGS = (
    "live crawl",
    "crawled live",
    "freshly crawled",
    "real browser crawl",
)

GUARANTEE_SUBSTRINGS = (
    "will be approved",
    "guaranteed approval",
    "permit will issue",
    "legal advice",
    "legally sufficient",
    "compliance guaranteed",
)

CONSEQUENTIAL_ACTION_SUBSTRINGS = (
    "submit the permit",
    "click submit",
    "pay the fee",
    "schedule inspection",
    "upload correction",
    "certify acknowledgement",
    "purchase permit",
    "cancel permit",
    "withdraw application",
)

ACTIVE_MUTATION_KEYS = (
    "mutate_artifacts",
    "write_artifacts",
    "update_current_corpus",
    "promote_to_current",
    "apply_changes",
    "commit_outputs",
    "active_mutation",
)

ALLOWED_DISPOSITIONS = {"changed", "unchanged", "needs-review", "blocked"}


def validate_public_source_change_triage_packet_v1(packet: Mapping[str, Any]) -> list[TriageValidationIssue]:
    """Return validation issues for a public source change triage packet v1."""

    issues: list[TriageValidationIssue] = []
    if not isinstance(packet, Mapping):
        return [TriageValidationIssue("packet.not_mapping", "$", "packet must be a mapping")]

    version = packet.get("packet_version") or packet.get("version")
    if version != "public-source-change-triage-v1":
        issues.append(
            TriageValidationIssue(
                "packet.version",
                "$.packet_version",
                "packet_version must be public-source-change-triage-v1",
            )
        )

    rows = packet.get("rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        issues.append(TriageValidationIssue("rows.missing", "$.rows", "rows must be a non-empty list"))
    else:
        _validate_rows(rows, issues)

    _require_non_empty(packet, "impact_references", "packet.impact_references", issues)
    _require_non_empty(packet, "citation_preservation_checks", "packet.citation_preservation_checks", issues)
    _require_non_empty(packet, "rollback_notes", "packet.rollback_notes", issues)
    _require_non_empty(packet, "validation_replay_commands", "packet.validation_replay_commands", issues)

    blocked = packet.get("blocked_promotion_explanations")
    blocked_required = _has_blocked_row(rows) if isinstance(rows, Sequence) and not isinstance(rows, (str, bytes)) else False
    if blocked_required and not _non_empty(blocked):
        issues.append(
            TriageValidationIssue(
                "packet.blocked_promotion_explanations.missing",
                "$.blocked_promotion_explanations",
                "blocked rows require blocked promotion explanations",
            )
        )

    replay = packet.get("validation_replay_commands")
    if _non_empty(replay) and not _valid_replay_commands(replay):
        issues.append(
            TriageValidationIssue(
                "packet.validation_replay_commands.invalid",
                "$.validation_replay_commands",
                "validation replay commands must be non-empty argument lists",
            )
        )

    _scan_for_forbidden_text(packet, issues)
    _scan_for_active_mutation_flags(packet, issues)
    return issues


def assert_valid_public_source_change_triage_packet_v1(packet: Mapping[str, Any]) -> None:
    """Raise PublicSourceChangeTriageError if the packet is invalid."""

    issues = validate_public_source_change_triage_packet_v1(packet)
    if issues:
        rendered = "; ".join(f"{issue.code} at {issue.path}: {issue.message}" for issue in issues)
        raise PublicSourceChangeTriageError(rendered)


def _validate_rows(rows: Sequence[Any], issues: list[TriageValidationIssue]) -> None:
    dispositions_seen: set[str] = set()
    for index, row in enumerate(rows):
        path = f"$.rows[{index}]"
        if not isinstance(row, Mapping):
            issues.append(TriageValidationIssue("row.not_mapping", path, "row must be a mapping"))
            continue

        disposition = row.get("disposition")
        if disposition not in ALLOWED_DISPOSITIONS:
            issues.append(
                TriageValidationIssue(
                    "row.disposition.invalid",
                    f"{path}.disposition",
                    "disposition must be changed, unchanged, needs-review, or blocked",
                )
            )
        else:
            dispositions_seen.add(str(disposition))

        changed = disposition == "changed" or bool(row.get("changed"))
        if changed and not _non_empty(row.get("citations")) and not _non_empty(row.get("source_evidence_ids")):
            issues.append(
                TriageValidationIssue(
                    "row.changed.uncited",
                    path,
                    "changed rows require citations or source_evidence_ids",
                )
            )

        if changed and not _non_empty(row.get("impact_references")):
            issues.append(
                TriageValidationIssue(
                    "row.impact_references.missing",
                    f"{path}.impact_references",
                    "changed rows require impact references",
                )
            )

    if "unchanged" not in dispositions_seen:
        issues.append(
            TriageValidationIssue(
                "rows.unchanged_disposition.missing",
                "$.rows",
                "packet must include at least one unchanged disposition row",
            )
        )
    if "needs-review" not in dispositions_seen:
        issues.append(
            TriageValidationIssue(
                "rows.needs_review_disposition.missing",
                "$.rows",
                "packet must include at least one needs-review disposition row",
            )
        )


def _require_non_empty(
    packet: Mapping[str, Any], field: str, code_prefix: str, issues: list[TriageValidationIssue]
) -> None:
    if not _non_empty(packet.get(field)):
        issues.append(
            TriageValidationIssue(
                f"{code_prefix}.missing",
                f"$.{field}",
                f"{field} must be present and non-empty",
            )
        )


def _has_blocked_row(rows: Sequence[Any]) -> bool:
    return any(isinstance(row, Mapping) and row.get("disposition") == "blocked" for row in rows)


def _valid_replay_commands(value: Any) -> bool:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return False
    for command in value:
        if not isinstance(command, Sequence) or isinstance(command, (str, bytes)) or not command:
            return False
        if not all(isinstance(part, str) and part for part in command):
            return False
    return True


def _non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return bool(value)
    return bool(value)


def _scan_for_forbidden_text(packet: Mapping[str, Any], issues: list[TriageValidationIssue]) -> None:
    for path, text in _walk_text(packet):
        lowered = text.lower()
        for label, substrings in (
            ("private_artifact", BLOCKED_SUBSTRINGS),
            ("raw_artifact", RAW_ARTIFACT_SUBSTRINGS),
            ("live_crawl_claim", LIVE_CRAWL_SUBSTRINGS),
            ("outcome_guarantee", GUARANTEE_SUBSTRINGS),
            ("consequential_action", CONSEQUENTIAL_ACTION_SUBSTRINGS),
        ):
            if any(substring in lowered for substring in substrings):
                issues.append(
                    TriageValidationIssue(
                        f"packet.forbidden_text.{label}",
                        path,
                        f"packet text contains forbidden {label.replace('_', ' ')} language",
                    )
                )


def _scan_for_active_mutation_flags(packet: Mapping[str, Any], issues: list[TriageValidationIssue]) -> None:
    for path, key, value in _walk_items(packet):
        if key in ACTIVE_MUTATION_KEYS and value is True:
            issues.append(
                TriageValidationIssue(
                    "packet.active_mutation_flag",
                    path,
                    f"{key} must not be true in a triage packet",
                )
            )


def _walk_text(value: Any, path: str = "$ ") -> Iterable[tuple[str, str]]:
    normalized_path = path.strip()
    if isinstance(value, str):
        yield normalized_path, value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk_text(child, f"{normalized_path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            yield from _walk_text(child, f"{normalized_path}[{index}]")


def _walk_items(value: Any, path: str = "$ ") -> Iterable[tuple[str, str, Any]]:
    normalized_path = path.strip()
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{normalized_path}.{key_text}"
            yield child_path, key_text, child
            yield from _walk_items(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            yield from _walk_items(child, f"{normalized_path}[{index}]")


__all__ = [
    "PublicSourceChangeTriageError",
    "TriageValidationIssue",
    "assert_valid_public_source_change_triage_packet_v1",
    "validate_public_source_change_triage_packet_v1",
]
