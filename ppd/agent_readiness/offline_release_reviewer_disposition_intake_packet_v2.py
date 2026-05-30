"""Validation for offline release reviewer disposition intake packet v2.

The intake packet is a fixture-only reviewer handoff. It must contain enough
reviewer disposition structure to support release-gate review, while rejecting
private artifacts, raw captures, live execution claims, consequential PP&D
action language, outcome guarantees, active promotion flags, and active mutation
flags.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PACKET_TYPE = "ppd.offline_release_reviewer_disposition_intake_packet.v2"

ALLOWED_DECISIONS = {"approved_for_offline_review", "blocked", "deferred", "no_go"}
BLOCKER_CARRY_FORWARD_STATUSES = {"blocked", "deferred", "escalated"}
RISK_STATUSES = {"open", "carried_forward", "deferred", "accepted_for_offline_review"}

_PRIVATE_FIELD_NAMES = {
    "auth",
    "auth_file",
    "auth_state",
    "authenticated_artifact",
    "browser_artifact",
    "browser_file",
    "browser_state",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "devhub_session",
    "har",
    "har_file",
    "password",
    "private_artifact",
    "private_artifacts",
    "private_file",
    "private_path",
    "private_value",
    "screenshot",
    "screenshot_file",
    "screenshots",
    "secret",
    "session",
    "session_artifact",
    "session_file",
    "session_state",
    "storage_state",
    "token",
    "trace",
    "trace_file",
    "traces",
}

_RAW_FIELD_NAMES = {
    "download",
    "downloaded_artifact",
    "downloaded_artifacts",
    "downloaded_data",
    "downloaded_document",
    "downloaded_pdf",
    "pdf_download",
    "raw_artifact",
    "raw_body",
    "raw_capture",
    "raw_crawl",
    "raw_crawl_output",
    "raw_data",
    "raw_download",
    "raw_html",
    "raw_pdf",
}

_MUTATION_FIELD_NAMES = {
    "active_agent_state_mutation",
    "active_artifact_mutation",
    "active_fixture_mutation",
    "active_prompt_mutation",
    "active_promotion",
    "active_release_promotion",
    "active_release_state_mutation",
    "agent_state_mutation",
    "artifact_mutation",
    "fixture_mutation",
    "mutates_agent_state",
    "mutates_artifacts",
    "mutates_fixtures",
    "mutates_prompt",
    "mutates_release_state",
    "prompt_mutation",
    "promotes_release",
    "promotion_enabled",
    "release_state_mutation",
}

_MUTATION_FLAG_NAMES = {
    "agent_state",
    "artifact",
    "artifacts",
    "fixture",
    "fixtures",
    "promotion",
    "prompt",
    "prompts",
    "release",
    "release_promotion",
    "release_state",
}

_UNSAFE_TEXT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/tmp/)|"
    r"(auth[_ -]?state|authenticated|browser[_ -]?state|cookie|credential|har\b|password|private[_ -]?(artifact|artifacts|file|path|value)|"
    r"raw[_ -]?(artifact|body|capture|crawl|data|download|html|pdf)|downloaded[_ -]?(artifact|artifacts|data|document|pdf)|"
    r"screenshot|session[_ -]?(artifact|state|storage)?|storage[_ -]?state|token|trace[_ -]?(file|zip)?)|"
    r"\b(live\s+(crawl|browser|devhub|execution|processor|promotion|run)|release\s+(complete|completed)|released\s+to\s+production|"
    r"executed\s+(the\s+)?(release|promotion)|promoted\s+(to\s+)?(production|release)|active\s+promotion|"
    r"official\s+action\s+(performed|completed|authorized|approved)|consequential\s+official\s+action|"
    r"permit\s+will\s+be\s+(approved|issued)|approval\s+is\s+guaranteed|guaranteed\s+(approval|issuance|permit\s+outcome)|"
    r"legal(ly)?\s+(sufficient|compliant|guaranteed)|city\s+will\s+(approve|issue)|"
    r"payment|pay\s+(the\s+)?fee|submit(ted|s|ting)?\b|submission|schedule\s+(the\s+)?inspection|"
    r"cancel\s+(the\s+)?inspection|certif(y|ication)|upload(s|ed|ing)?\b)\b",
    re.IGNORECASE,
)

_COMMAND_UNSAFE_RE = re.compile(
    r"\b(live|crawl|crawler|devhub|playwright|browser|network|auth|session|download|raw|trace|har)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class IntakeValidationIssue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class IntakeValidationResult:
    ok: bool
    issues: tuple[IntakeValidationIssue, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "issues": [issue.as_dict() for issue in self.issues]}


def load_offline_release_reviewer_disposition_intake_packet_v2(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def validate_offline_release_reviewer_disposition_intake_packet_v2(packet: Mapping[str, Any]) -> IntakeValidationResult:
    issues: list[IntakeValidationIssue] = []

    if packet.get("packet_type") != PACKET_TYPE:
        issues.append(IntakeValidationIssue("invalid_packet_type", "packet_type", f"packet_type must be {PACKET_TYPE}"))
    if packet.get("fixture_only") is not True:
        issues.append(IntakeValidationIssue("fixture_only_required", "fixture_only", "fixture_only must be true"))

    reviewer_decision_rows = _mapping_rows(packet.get("reviewer_decision_rows"))
    if not reviewer_decision_rows:
        issues.append(IntakeValidationIssue("missing_reviewer_decision_rows", "reviewer_decision_rows", "at least one reviewer decision row is required"))
    for index, row in enumerate(reviewer_decision_rows):
        _validate_reviewer_decision_row(row, f"reviewer_decision_rows[{index}]", issues)

    _validate_evidence_bundle_references(packet.get("evidence_bundle_references"), issues)
    _validate_validation_transcript_review_placeholders(packet.get("validation_transcript_review_placeholders"), issues)
    _validate_rollback_readiness_confirmations(packet.get("rollback_readiness_confirmations"), issues)
    _validate_unresolved_risk_notes(packet.get("unresolved_risk_notes"), issues)
    _validate_offline_validation_commands(packet.get("offline_validation_commands"), issues)

    _validate_acknowledgements(
        packet.get("evidence_summary_acknowledgements"),
        "evidence_summary_acknowledgements",
        "missing_evidence_summary_acknowledgements",
        "uncited_evidence_summary_acknowledgement",
        issues,
    )
    _validate_acknowledgements(
        packet.get("rollback_readiness_acknowledgements"),
        "rollback_readiness_acknowledgements",
        "missing_rollback_readiness_acknowledgements",
        "uncited_rollback_readiness_acknowledgement",
        issues,
    )
    _validate_acknowledgements(
        packet.get("validation_replay_acknowledgements"),
        "validation_replay_acknowledgements",
        "missing_validation_replay_acknowledgements",
        "uncited_validation_replay_acknowledgement",
        issues,
    )

    blocker_rows = _mapping_rows(packet.get("unresolved_blocker_carry_forward"))
    if not blocker_rows:
        issues.append(IntakeValidationIssue("missing_unresolved_blocker_carry_forward", "unresolved_blocker_carry_forward", "unresolved blocker carry-forward rows are required, even when the row records none open"))
    for index, row in enumerate(blocker_rows):
        _validate_blocker_carry_forward(row, f"unresolved_blocker_carry_forward[{index}]", issues)

    no_go_rows = _mapping_rows(packet.get("no_go_reason_placeholders"))
    if not no_go_rows:
        issues.append(IntakeValidationIssue("missing_no_go_reason_placeholders", "no_go_reason_placeholders", "no-go reason placeholders are required"))
    for index, row in enumerate(no_go_rows):
        _validate_no_go_placeholder(row, f"no_go_reason_placeholders[{index}]", issues)

    _scan_global_rejections(packet, "", issues)
    return IntakeValidationResult(not issues, tuple(issues))


def assert_valid_offline_release_reviewer_disposition_intake_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_offline_release_reviewer_disposition_intake_packet_v2(packet)
    if not result.ok:
        formatted = "; ".join(f"{issue.code} at {issue.path}" for issue in result.issues)
        raise ValueError(f"offline release reviewer disposition intake packet v2 validation failed: {formatted}")


def _validate_reviewer_decision_row(row: Mapping[str, Any], path: str, issues: list[IntakeValidationIssue]) -> None:
    if not _text(row.get("reviewer_id")):
        issues.append(IntakeValidationIssue("missing_reviewer_id", f"{path}.reviewer_id", "reviewer_id is required"))
    decision = _text(row.get("decision"))
    if decision not in ALLOWED_DECISIONS:
        issues.append(IntakeValidationIssue("invalid_reviewer_decision", f"{path}.decision", "reviewer decision must be an allowed offline review disposition"))
    if not _text(row.get("decided_at")):
        issues.append(IntakeValidationIssue("missing_decided_at", f"{path}.decided_at", "decided_at is required"))
    if not _text(row.get("rationale")):
        issues.append(IntakeValidationIssue("missing_reviewer_rationale", f"{path}.rationale", "reviewer rationale is required"))
    if not _has_citation(row.get("citations")):
        issues.append(IntakeValidationIssue("uncited_reviewer_decision", f"{path}.citations", "reviewer decision rows must cite fixture or public evidence"))


def _validate_evidence_bundle_references(value: Any, issues: list[IntakeValidationIssue]) -> None:
    rows = _mapping_rows(value)
    if not rows:
        issues.append(IntakeValidationIssue("missing_evidence_bundle_references", "evidence_bundle_references", "at least one evidence-bundle reference is required"))
        return
    for index, row in enumerate(rows):
        path = f"evidence_bundle_references[{index}]"
        for field in ("bundle_id", "reference", "reviewer_id"):
            if not _text(row.get(field)):
                issues.append(IntakeValidationIssue("missing_evidence_bundle_reference_field", f"{path}.{field}", f"{field} is required for evidence-bundle references"))
        if not _has_citation(row.get("citations")):
            issues.append(IntakeValidationIssue("uncited_evidence_bundle_reference", f"{path}.citations", "evidence-bundle references must cite fixture or public evidence"))


def _validate_validation_transcript_review_placeholders(value: Any, issues: list[IntakeValidationIssue]) -> None:
    rows = _mapping_rows(value)
    if not rows:
        issues.append(IntakeValidationIssue("missing_validation_transcript_review_placeholders", "validation_transcript_review_placeholders", "validation-transcript review placeholders are required"))
        return
    for index, row in enumerate(rows):
        path = f"validation_transcript_review_placeholders[{index}]"
        for field in ("transcript_id", "reviewer_id", "review_placeholder"):
            if not _text(row.get(field)):
                issues.append(IntakeValidationIssue("missing_validation_transcript_review_placeholder_field", f"{path}.{field}", f"{field} is required for validation-transcript review placeholders"))
        if not _has_citation(row.get("citations")):
            issues.append(IntakeValidationIssue("uncited_validation_transcript_review_placeholder", f"{path}.citations", "validation-transcript review placeholders must cite fixture or public evidence"))


def _validate_rollback_readiness_confirmations(value: Any, issues: list[IntakeValidationIssue]) -> None:
    rows = _mapping_rows(value)
    if not rows:
        issues.append(IntakeValidationIssue("missing_rollback_readiness_confirmations", "rollback_readiness_confirmations", "rollback-readiness confirmations are required"))
        return
    for index, row in enumerate(rows):
        path = f"rollback_readiness_confirmations[{index}]"
        if row.get("confirmed") is not True:
            issues.append(IntakeValidationIssue("rollback_readiness_confirmation_not_true", f"{path}.confirmed", "rollback-readiness confirmation must be explicitly true"))
        for field in ("confirmation_id", "reviewer_id"):
            if not _text(row.get(field)):
                issues.append(IntakeValidationIssue("missing_rollback_readiness_confirmation_field", f"{path}.{field}", f"{field} is required for rollback-readiness confirmations"))
        if not _has_citation(row.get("citations")):
            issues.append(IntakeValidationIssue("uncited_rollback_readiness_confirmation", f"{path}.citations", "rollback-readiness confirmations must cite fixture or public evidence"))


def _validate_unresolved_risk_notes(value: Any, issues: list[IntakeValidationIssue]) -> None:
    rows = _mapping_rows(value)
    if not rows:
        issues.append(IntakeValidationIssue("missing_unresolved_risk_notes", "unresolved_risk_notes", "unresolved-risk notes are required, even when the row records none open"))
        return
    for index, row in enumerate(rows):
        path = f"unresolved_risk_notes[{index}]"
        for field in ("risk_id", "note", "owner"):
            if not _text(row.get(field)):
                issues.append(IntakeValidationIssue("missing_unresolved_risk_note_field", f"{path}.{field}", f"{field} is required for unresolved-risk notes"))
        status = _text(row.get("status"))
        if status not in RISK_STATUSES:
            issues.append(IntakeValidationIssue("invalid_unresolved_risk_note_status", f"{path}.status", "unresolved-risk note status must be open, carried_forward, deferred, or accepted_for_offline_review"))
        if not _has_citation(row.get("citations")):
            issues.append(IntakeValidationIssue("uncited_unresolved_risk_note", f"{path}.citations", "unresolved-risk notes must cite fixture or public evidence"))


def _validate_offline_validation_commands(value: Any, issues: list[IntakeValidationIssue]) -> None:
    rows = _command_rows(value)
    if not rows:
        issues.append(IntakeValidationIssue("missing_offline_validation_commands", "offline_validation_commands", "at least one offline validation command is required"))
        return
    for index, command in enumerate(rows):
        path = f"offline_validation_commands[{index}]"
        if not command:
            issues.append(IntakeValidationIssue("empty_offline_validation_command", path, "offline validation commands must not be empty"))
            continue
        command_text = " ".join(command)
        if _COMMAND_UNSAFE_RE.search(command_text):
            issues.append(IntakeValidationIssue("unsafe_offline_validation_command", path, "offline validation commands must not invoke live crawl, DevHub, browser, network, session, raw, or download paths"))


def _validate_acknowledgements(value: Any, path: str, missing_code: str, uncited_code: str, issues: list[IntakeValidationIssue]) -> None:
    rows = _mapping_rows(value)
    if not rows:
        issues.append(IntakeValidationIssue(missing_code, path, f"{path} must contain at least one acknowledgement row"))
        return
    for index, row in enumerate(rows):
        row_path = f"{path}[{index}]"
        if row.get("acknowledged") is not True:
            issues.append(IntakeValidationIssue("acknowledgement_not_true", f"{row_path}.acknowledged", "acknowledgement must be explicitly true"))
        if not _text(row.get("reviewer_id")):
            issues.append(IntakeValidationIssue("missing_acknowledgement_reviewer", f"{row_path}.reviewer_id", "acknowledgement reviewer_id is required"))
        if not _has_citation(row.get("citations")):
            issues.append(IntakeValidationIssue(uncited_code, f"{row_path}.citations", "acknowledgements must cite fixture or public evidence"))


def _validate_blocker_carry_forward(row: Mapping[str, Any], path: str, issues: list[IntakeValidationIssue]) -> None:
    for field in ("blocker_id", "carry_forward_owner", "carry_forward_reason"):
        if not _text(row.get(field)):
            issues.append(IntakeValidationIssue("missing_unresolved_blocker_carry_forward_field", f"{path}.{field}", f"{field} is required for unresolved blocker carry-forward"))
    status = _text(row.get("carry_forward_status"))
    if status not in BLOCKER_CARRY_FORWARD_STATUSES:
        issues.append(IntakeValidationIssue("invalid_unresolved_blocker_carry_forward_status", f"{path}.carry_forward_status", "carry_forward_status must be blocked, deferred, or escalated"))
    if not _has_citation(row.get("citations")):
        issues.append(IntakeValidationIssue("uncited_unresolved_blocker_carry_forward", f"{path}.citations", "unresolved blocker carry-forward rows must cite fixture or public evidence"))


def _validate_no_go_placeholder(row: Mapping[str, Any], path: str, issues: list[IntakeValidationIssue]) -> None:
    for field in ("placeholder_id", "applies_to_decision", "reason_placeholder"):
        if not _text(row.get(field)):
            issues.append(IntakeValidationIssue("missing_no_go_reason_placeholder_field", f"{path}.{field}", f"{field} is required for no-go placeholders"))
    if not _has_citation(row.get("citations")):
        issues.append(IntakeValidationIssue("uncited_no_go_reason_placeholder", f"{path}.citations", "no-go placeholders must cite fixture or public evidence"))


def _scan_global_rejections(value: Any, path: str, issues: list[IntakeValidationIssue]) -> None:
    for child_path, child in _walk(value, path):
        name = _path_name(child_path).lower().replace("-", "_")
        if name in _PRIVATE_FIELD_NAMES and _present(child):
            issues.append(IntakeValidationIssue("private_authenticated_session_or_browser_artifact", child_path, "private, authenticated, session, browser, screenshot, trace, HAR, or auth artifacts are not allowed"))
        if name in _RAW_FIELD_NAMES and _present(child):
            issues.append(IntakeValidationIssue("raw_crawl_pdf_or_downloaded_data", child_path, "raw crawl, raw PDF, downloaded data, and raw artifacts are not allowed"))
        if name in _MUTATION_FIELD_NAMES and _active_flag(child):
            issues.append(IntakeValidationIssue("active_mutation_flag", child_path, "active promotion, artifact, prompt, release-state, fixture, or agent-state mutation flags are not allowed"))
        if name == "mutation_flags" and _has_active_named_mutation(child):
            issues.append(IntakeValidationIssue("active_mutation_flag", child_path, "active promotion, artifact, prompt, release-state, fixture, or agent-state mutation flags are not allowed"))
        if isinstance(child, str) and _UNSAFE_TEXT_RE.search(child):
            issues.append(IntakeValidationIssue("unsafe_release_intake_text", child_path, "packet text must not reference private artifacts, raw data, live execution, active promotion, release completion, guarantees, or consequential action language"))


def _mapping_rows(value: Any) -> tuple[Mapping[str, Any], ...]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(item for item in value if isinstance(item, Mapping))
    return ()


def _command_rows(value: Any) -> tuple[tuple[str, ...], ...]:
    rows: list[tuple[str, ...]] = []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    for item in value:
        if isinstance(item, str):
            rows.append((item,))
        elif isinstance(item, Sequence) and not isinstance(item, (str, bytes, bytearray)):
            rows.append(tuple(str(part) for part in item if str(part)))
    return tuple(rows)


def _has_citation(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return False
    for item in value:
        if isinstance(item, str) and item.strip():
            return True
        if isinstance(item, Mapping):
            for key in ("citation", "fixture_id", "source_evidence_id", "source_id", "path", "url", "canonical_url"):
                text = item.get(key)
                if isinstance(text, str) and text.strip():
                    return True
    return False


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


def _present(value: Any) -> bool:
    return value not in (None, "", [], {})


def _active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "active", "enabled", "true", "yes"}
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return False


def _has_active_named_mutation(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return _active_flag(value)
    for key, child in value.items():
        if str(key).lower().replace("-", "_") in _MUTATION_FLAG_NAMES and _active_flag(child):
            return True
    return False


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
