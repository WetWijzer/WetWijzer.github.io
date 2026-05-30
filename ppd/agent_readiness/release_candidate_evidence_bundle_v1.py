from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

PACKET_TYPE = "ppd.release_candidate_evidence_bundle.v1"

_PRIVATE_OR_AUTHENTICATED_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/root/)|(^/tmp/)|(^[A-Za-z]:\\Users\\[^\\]+\\)|"
    r"(https?://[^\s?#]+[^\s]*(?:[?&](?:access_token|auth|password|session|token)=))|"
    r"(authenticated[_-]?artifact|authenticated[_-]?url|auth[_-]?state|browser[_-]?state|cookie|credential|"
    r"devhub[_-]?session|private[_-]?(artifact|path|url|value)|secret|session[_-]?(state|storage)|storage[_-]?state|token)",
    re.IGNORECASE,
)

_RAW_CAPTURE_RE = re.compile(
    r"(raw[_-]?(body|crawl|download|html|pdf|capture|archive)|downloaded[_-]?pdf|original[_-]?pdf|pdf[_-]?bytes|"
    r"\.har\b|har[_-]?file|trace\.zip|playwright[_-]?trace|screenshot|browser[_-]?(snapshot|trace|recording|dump)|"
    r"\.warc(?:\.gz)?\b|archive/raw|crawl-output|/downloads?/|session[_-]?dump)",
    re.IGNORECASE,
)

_LIVE_PROMOTION_OR_EXECUTION_RE = re.compile(
    r"\b(live\s+(promotion|release|deployment|execution|crawl|crawler|processor|registry\s+refresh)|"
    r"promoted\s+(to\s+)?live|published\s+live|deployed\s+to\s+production|production\s+release\s+complete|"
    r"executed\s+(the\s+)?(promotion|release|crawl|mutation|registry\s+update)|"
    r"submitted\s+to\s+devhub|uploaded\s+to\s+devhub|paid\s+fees?|scheduled\s+inspection|certified\s+application)\b",
    re.IGNORECASE,
)

_OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?\s+(approval|issuance|permit|legal|compliance|outcome)|"
    r"(permit|application|inspection|appeal)\s+(will|shall)\s+be\s+(approved|issued|accepted|granted|upheld)|"
    r"approval\s+guaranteed|issuance\s+guaranteed|legally\s+binding\s+determination|guaranteed\s+code\s+compliance)\b",
    re.IGNORECASE,
)

_CONSEQUENTIAL_ACTION_RE = re.compile(
    r"\b((?:will|shall|may|can|ready\s+to|authorized\s+to|cleared\s+to)\s+"
    r"(?:submit|certify|upload|schedule|cancel|withdraw|pay|purchase|reactivate|execute)|"
    r"submit\s+(?:the\s+)?(?:permit|application|request)|certify\s+(?:the\s+)?(?:application|acknowledgement)|"
    r"upload\s+(?:corrections?|documents?)\s+to\s+(?:devhub|the\s+official\s+record)|"
    r"schedule\s+(?:an\s+)?inspection|cancel\s+(?:the\s+)?(?:permit|inspection|request)|"
    r"withdraw\s+(?:the\s+)?(?:permit|application|request)|pay\s+(?:the\s+)?fees?|purchase\s+(?:the\s+)?permit)\b",
    re.IGNORECASE,
)

_MUTATION_FLAG_KEYS = {
    "agent_state_mutation_active",
    "agent_state_mutation_enabled",
    "guardrail_mutation_active",
    "guardrail_mutation_enabled",
    "prompt_mutation_active",
    "prompt_mutation_enabled",
    "release_state_mutation_active",
    "release_state_mutation_enabled",
    "source_mutation_active",
    "source_mutation_enabled",
    "surface_registry_mutation_active",
    "surface_registry_mutation_enabled",
}

_MUTATION_KEY_RE = re.compile(
    r"(source|surface[_-]?registry|guardrail|prompt|release[_-]?state|agent[_-]?state).*"
    r"(mutation|mutate|write|publish|promote|refresh|activate|enabled|active)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ReleaseCandidateEvidenceBundleIssue:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ReleaseCandidateEvidenceBundleValidationResult:
    valid: bool
    issues: tuple[ReleaseCandidateEvidenceBundleIssue, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "issues": [
                {"code": issue.code, "path": issue.path, "message": issue.message}
                for issue in self.issues
            ],
        }


def validate_release_candidate_evidence_bundle_v1(
    bundle: Mapping[str, Any],
) -> ReleaseCandidateEvidenceBundleValidationResult:
    """Validate a side-effect-free PP&D release candidate evidence bundle."""

    issues: list[ReleaseCandidateEvidenceBundleIssue] = []
    if bundle.get("packet_type") != PACKET_TYPE:
        issues.append(
            ReleaseCandidateEvidenceBundleIssue(
                "invalid_packet_type",
                "$.packet_type",
                f"packet_type must be {PACKET_TYPE}",
            )
        )
    if bundle.get("fixture_only") is not True:
        issues.append(
            ReleaseCandidateEvidenceBundleIssue(
                "fixture_only_required",
                "$.fixture_only",
                "release candidate evidence bundles must be fixture-only and side-effect-free",
            )
        )

    _require_cited_evidence_rows(bundle, issues)
    _require_unresolved_blocker_summaries(bundle, issues)
    _require_rollback_checkpoints(bundle, issues)
    _require_validation_command_inventory(bundle, issues)
    _reject_recursive_unsafe_content(bundle, issues)
    _reject_active_mutation_flags(bundle, issues)
    return ReleaseCandidateEvidenceBundleValidationResult(valid=not issues, issues=tuple(issues))


def assert_valid_release_candidate_evidence_bundle_v1(bundle: Mapping[str, Any]) -> None:
    result = validate_release_candidate_evidence_bundle_v1(bundle)
    if not result.valid:
        details = "; ".join(f"{issue.path}: {issue.code}" for issue in result.issues)
        raise ValueError("invalid_release_candidate_evidence_bundle_v1: " + details)


def _require_cited_evidence_rows(
    bundle: Mapping[str, Any],
    issues: list[ReleaseCandidateEvidenceBundleIssue],
) -> None:
    rows = _sequence(bundle.get("evidence_rows") or bundle.get("evidence"))
    if not rows:
        issues.append(
            ReleaseCandidateEvidenceBundleIssue(
                "missing_evidence_rows",
                "$.evidence_rows",
                "bundle must include cited evidence rows",
            )
        )
        return
    for index, row in enumerate(rows):
        path = f"$.evidence_rows[{index}]"
        if not isinstance(row, Mapping):
            issues.append(
                ReleaseCandidateEvidenceBundleIssue(
                    "invalid_evidence_row",
                    path,
                    "evidence row must be an object",
                )
            )
            continue
        if not _has_citation(row):
            issues.append(
                ReleaseCandidateEvidenceBundleIssue(
                    "uncited_evidence_row",
                    path,
                    "evidence row must cite source or validation evidence",
                )
            )


def _require_unresolved_blocker_summaries(
    bundle: Mapping[str, Any],
    issues: list[ReleaseCandidateEvidenceBundleIssue],
) -> None:
    blockers = _sequence(bundle.get("unresolved_blocker_summaries"))
    if not blockers:
        issues.append(
            ReleaseCandidateEvidenceBundleIssue(
                "missing_unresolved_blocker_summaries",
                "$.unresolved_blocker_summaries",
                "bundle must explicitly summarize unresolved blockers, even when the summary is none",
            )
        )
        return
    for index, blocker in enumerate(blockers):
        path = f"$.unresolved_blocker_summaries[{index}]"
        if not isinstance(blocker, Mapping):
            issues.append(ReleaseCandidateEvidenceBundleIssue("invalid_unresolved_blocker_summary", path, "blocker summary must be an object"))
            continue
        if not _nonempty_text(blocker.get("summary")):
            issues.append(ReleaseCandidateEvidenceBundleIssue("missing_unresolved_blocker_summary", path, "blocker entry must include a summary"))
        if not _has_citation(blocker):
            issues.append(ReleaseCandidateEvidenceBundleIssue("uncited_unresolved_blocker_summary", path, "blocker summary must cite evidence"))


def _require_rollback_checkpoints(
    bundle: Mapping[str, Any],
    issues: list[ReleaseCandidateEvidenceBundleIssue],
) -> None:
    checkpoints = _sequence(bundle.get("rollback_checkpoints"))
    if not checkpoints:
        issues.append(ReleaseCandidateEvidenceBundleIssue("missing_rollback_checkpoints", "$.rollback_checkpoints", "bundle must include rollback checkpoints"))
        return
    for index, checkpoint in enumerate(checkpoints):
        path = f"$.rollback_checkpoints[{index}]"
        if not isinstance(checkpoint, Mapping):
            issues.append(ReleaseCandidateEvidenceBundleIssue("invalid_rollback_checkpoint", path, "rollback checkpoint must be an object"))
            continue
        if not _nonempty_text(checkpoint.get("checkpoint") or checkpoint.get("summary")):
            issues.append(ReleaseCandidateEvidenceBundleIssue("missing_rollback_checkpoint", path, "rollback checkpoint must include checkpoint text"))
        if not _has_citation(checkpoint):
            issues.append(ReleaseCandidateEvidenceBundleIssue("uncited_rollback_checkpoint", path, "rollback checkpoint must cite evidence"))


def _require_validation_command_inventory(
    bundle: Mapping[str, Any],
    issues: list[ReleaseCandidateEvidenceBundleIssue],
) -> None:
    commands = _sequence(bundle.get("validation_command_inventory") or bundle.get("validation_commands"))
    if not commands:
        issues.append(ReleaseCandidateEvidenceBundleIssue("missing_validation_command_inventory", "$.validation_command_inventory", "bundle must include validation command inventory"))
        return
    for index, command in enumerate(commands):
        path = f"$.validation_command_inventory[{index}]"
        if not isinstance(command, Mapping):
            issues.append(ReleaseCandidateEvidenceBundleIssue("invalid_validation_command_inventory_entry", path, "validation command entry must be an object"))
            continue
        if not command.get("command"):
            issues.append(ReleaseCandidateEvidenceBundleIssue("missing_validation_command", path, "validation command entry must include command"))
        if not _nonempty_text(command.get("expected_result") or command.get("summary")):
            issues.append(ReleaseCandidateEvidenceBundleIssue("missing_validation_command_summary", path, "validation command entry must include expected result or summary"))
        if not _has_citation(command):
            issues.append(ReleaseCandidateEvidenceBundleIssue("uncited_validation_command", path, "validation command entry must cite evidence"))


def _reject_recursive_unsafe_content(
    value: Any,
    issues: list[ReleaseCandidateEvidenceBundleIssue],
    path: str = "$",
) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            _reject_unsafe_key_value(key_text, child, child_path, issues)
            _reject_recursive_unsafe_content(child, issues, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _reject_recursive_unsafe_content(child, issues, f"{path}[{index}]")
    elif isinstance(value, str):
        _reject_unsafe_text(value, path, issues)


def _reject_unsafe_key_value(
    key: str,
    value: Any,
    path: str,
    issues: list[ReleaseCandidateEvidenceBundleIssue],
) -> None:
    normalized = key.lower().replace("-", "_")
    if normalized in {"private_artifact", "authenticated_artifact", "raw_artifact", "raw_pdf", "browser_trace", "session_state"} and value not in (None, "", [], {}):
        issues.append(ReleaseCandidateEvidenceBundleIssue("private_authenticated_or_raw_artifact", path, "bundle must not include private, authenticated, raw, browser, or session artifacts"))
    if normalized in _MUTATION_FLAG_KEYS and value is True:
        issues.append(ReleaseCandidateEvidenceBundleIssue("active_mutation_flag", path, "source, surface-registry, guardrail, prompt, release-state, and agent-state mutation flags must be false"))
    if _MUTATION_KEY_RE.search(normalized) and value is True:
        issues.append(ReleaseCandidateEvidenceBundleIssue("active_mutation_flag", path, "source, surface-registry, guardrail, prompt, release-state, and agent-state mutation flags must be false"))


def _reject_unsafe_text(
    text: str,
    path: str,
    issues: list[ReleaseCandidateEvidenceBundleIssue],
) -> None:
    if _PRIVATE_OR_AUTHENTICATED_RE.search(text):
        issues.append(ReleaseCandidateEvidenceBundleIssue("private_or_authenticated_artifact", path, "bundle must not reference private or authenticated artifacts"))
    if _RAW_CAPTURE_RE.search(text):
        issues.append(ReleaseCandidateEvidenceBundleIssue("raw_capture_or_browser_artifact", path, "bundle must not reference raw crawl, PDF, session, or browser data"))
    if _LIVE_PROMOTION_OR_EXECUTION_RE.search(text):
        issues.append(ReleaseCandidateEvidenceBundleIssue("live_promotion_or_execution_claim", path, "bundle must not claim live promotion or execution"))
    if _OUTCOME_GUARANTEE_RE.search(text):
        issues.append(ReleaseCandidateEvidenceBundleIssue("legal_or_permitting_outcome_guarantee", path, "bundle must not guarantee legal or permitting outcomes"))
    if _CONSEQUENTIAL_ACTION_RE.search(text):
        issues.append(ReleaseCandidateEvidenceBundleIssue("consequential_action_language", path, "bundle must not include consequential official-action language"))


def _reject_active_mutation_flags(
    bundle: Mapping[str, Any],
    issues: list[ReleaseCandidateEvidenceBundleIssue],
) -> None:
    flags = bundle.get("mutation_flags") or bundle.get("state_mutation_flags") or {}
    if isinstance(flags, Mapping):
        for key, value in flags.items():
            _reject_unsafe_key_value(str(key), value, f"$.mutation_flags.{key}", issues)
    for field in (
        "source_mutation_flags",
        "surface_registry_mutation_flags",
        "guardrail_mutation_flags",
        "prompt_mutation_flags",
        "release_state_mutation_flags",
        "agent_state_mutation_flags",
    ):
        nested = bundle.get(field)
        if isinstance(nested, Mapping):
            for key, value in nested.items():
                if value is True:
                    issues.append(ReleaseCandidateEvidenceBundleIssue("active_mutation_flag", f"$.{field}.{key}", "all release candidate mutation flags must be false"))


def _has_citation(row: Mapping[str, Any]) -> bool:
    for key in ("source_evidence_ids", "citation_ids", "citations", "evidence_ids", "validation_evidence_ids"):
        if _has_nonempty_ref(row.get(key)):
            return True
    return False


def _has_nonempty_ref(value: Any) -> bool:
    if _nonempty_text(value):
        return True
    if isinstance(value, Mapping):
        return any(_has_nonempty_ref(child) for child in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_has_nonempty_ref(child) for child in value)
    return False


def _sequence(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return list(value)
    return [value]


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
