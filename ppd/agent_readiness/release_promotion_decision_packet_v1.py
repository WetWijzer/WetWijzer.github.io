"""Validation for PP&D release promotion decision packet v1.

The packet is intentionally an offline decision artifact. It may cite public,
normalized evidence and replay commands, but it must not carry private browser
state, raw crawl/PDF/download payloads, legal outcome guarantees, consequential
action wording, or mutation intent flags.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


MUTATION_FLAG_FIELDS = {
    "active_source_mutation",
    "active_document_mutation",
    "active_requirement_mutation",
    "active_process_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_fixture_mutation",
    "active_agent_state_mutation",
}

PRIVATE_ARTIFACT_TOKENS = (
    "auth_state",
    "storage_state",
    "storagestate",
    "cookie",
    "credential",
    "password",
    "session",
    "private",
    "browser_profile",
    "playwright_trace",
    "trace.zip",
    ".har",
    "screenshot",
)

RAW_DATA_TOKENS = (
    "raw_body",
    "raw_html",
    "raw_pdf",
    "pdf_bytes",
    "downloaded_file",
    "downloaded_document",
    "downloaded_pdf",
    "crawl_output",
    "crawl_dump",
    "warc",
    ".pdf",
)

GUARANTEE_TOKENS = (
    "guarantee approval",
    "approval guaranteed",
    "permit will be approved",
    "permit is guaranteed",
    "legally compliant",
    "legal determination",
    "legal advice",
    "entitled to approval",
    "will pass inspection",
)

CONSEQUENTIAL_ACTION_TOKENS = (
    "submit the permit",
    "submit permit",
    "certify acknowledgement",
    "certify the acknowledgement",
    "upload correction",
    "upload corrections",
    "pay fees",
    "make payment",
    "schedule inspection",
    "cancel permit",
    "withdraw application",
    "execute official action",
)


@dataclass(frozen=True)
class PacketValidationIssue:
    """A deterministic validation finding for release packet consumers."""

    code: str
    message: str
    path: str


@dataclass(frozen=True)
class PacketValidationResult:
    """Validation outcome for a release promotion decision packet."""

    valid: bool
    issues: tuple[PacketValidationIssue, ...]

    def raise_for_issues(self) -> None:
        if self.issues:
            details = "; ".join(f"{issue.code} at {issue.path}" for issue in self.issues)
            raise ValueError(f"release promotion decision packet v1 is invalid: {details}")


def validate_release_promotion_decision_packet_v1(packet: Mapping[str, Any]) -> PacketValidationResult:
    """Validate a release promotion decision packet v1.

    The validator only inspects supplied structured data. It performs no network,
    browser, filesystem, source, document, requirement, process, guardrail,
    prompt, release-state, fixture, or agent-state mutation.
    """

    issues: list[PacketValidationIssue] = []

    if packet.get("packet_version") != "release_promotion_decision_packet_v1":
        issues.append(
            PacketValidationIssue(
                "invalid_packet_version",
                "packet_version must be release_promotion_decision_packet_v1",
                "packet_version",
            )
        )

    _validate_decision_rows(packet, issues)
    _validate_release_scope(packet, issues)
    _validate_manual_signoffs(packet, issues)
    _validate_validation_replay(packet, issues)
    _validate_rollback_checkpoints(packet, issues)
    _validate_mutation_flags(packet, issues)
    _validate_recursive_content(packet, issues)

    return PacketValidationResult(valid=not issues, issues=tuple(issues))


def assert_release_promotion_decision_packet_v1(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when the packet fails validation."""

    validate_release_promotion_decision_packet_v1(packet).raise_for_issues()


def _validate_decision_rows(packet: Mapping[str, Any], issues: list[PacketValidationIssue]) -> None:
    rows = packet.get("decision_rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        issues.append(PacketValidationIssue("missing_decision_rows", "decision_rows must be a non-empty list", "decision_rows"))
        return

    for index, row in enumerate(rows):
        path = f"decision_rows[{index}]"
        if not isinstance(row, Mapping):
            issues.append(PacketValidationIssue("invalid_decision_row", "decision row must be an object", path))
            continue
        citations = row.get("citations", row.get("source_evidence_ids"))
        if not _non_empty_string_list(citations):
            issues.append(
                PacketValidationIssue(
                    "uncited_decision_row",
                    "each decision row must cite source evidence ids or citations",
                    f"{path}.citations",
                )
            )


def _validate_release_scope(packet: Mapping[str, Any], issues: list[PacketValidationIssue]) -> None:
    scope = packet.get("release_scope")
    if not isinstance(scope, Mapping):
        issues.append(PacketValidationIssue("missing_release_scope", "release_scope must describe promotion boundaries", "release_scope"))
        return

    in_scope = scope.get("in_scope")
    out_of_scope = scope.get("out_of_scope")
    boundary_statement = scope.get("boundary_statement")
    if not _non_empty_string_list(in_scope):
        issues.append(PacketValidationIssue("missing_release_scope_in_scope", "release_scope.in_scope must be non-empty", "release_scope.in_scope"))
    if not _non_empty_string_list(out_of_scope):
        issues.append(PacketValidationIssue("missing_release_scope_out_of_scope", "release_scope.out_of_scope must be non-empty", "release_scope.out_of_scope"))
    if not isinstance(boundary_statement, str) or not boundary_statement.strip():
        issues.append(
            PacketValidationIssue(
                "missing_release_scope_boundary_statement",
                "release_scope.boundary_statement must state release boundaries",
                "release_scope.boundary_statement",
            )
        )


def _validate_manual_signoffs(packet: Mapping[str, Any], issues: list[PacketValidationIssue]) -> None:
    signoffs = packet.get("manual_signoff_placeholders")
    if not isinstance(signoffs, Sequence) or isinstance(signoffs, (str, bytes)) or not signoffs:
        issues.append(
            PacketValidationIssue(
                "missing_manual_signoff_placeholders",
                "manual_signoff_placeholders must be a non-empty list",
                "manual_signoff_placeholders",
            )
        )
        return

    for index, signoff in enumerate(signoffs):
        path = f"manual_signoff_placeholders[{index}]"
        if not isinstance(signoff, Mapping):
            issues.append(PacketValidationIssue("invalid_manual_signoff_placeholder", "manual signoff placeholder must be an object", path))
            continue
        if not _non_empty_text(signoff.get("role")):
            issues.append(PacketValidationIssue("missing_manual_signoff_role", "manual signoff placeholder requires a role", f"{path}.role"))
        if not _non_empty_text(signoff.get("placeholder")):
            issues.append(
                PacketValidationIssue(
                    "missing_manual_signoff_placeholder_text",
                    "manual signoff placeholder requires placeholder text",
                    f"{path}.placeholder",
                )
            )


def _validate_validation_replay(packet: Mapping[str, Any], issues: list[PacketValidationIssue]) -> None:
    commands = packet.get("validation_replay_commands")
    if not isinstance(commands, Sequence) or isinstance(commands, (str, bytes)) or not commands:
        issues.append(
            PacketValidationIssue(
                "missing_validation_replay_commands",
                "validation_replay_commands must be a non-empty list of argv command lists",
                "validation_replay_commands",
            )
        )
        return

    for index, command in enumerate(commands):
        path = f"validation_replay_commands[{index}]"
        if not _non_empty_string_list(command):
            issues.append(PacketValidationIssue("invalid_validation_replay_command", "replay command must be a non-empty argv list", path))
            continue
        command_text = " ".join(command).lower()
        if "live" in command_text or "crawl" in command_text or "playwright" in command_text or "devhub" in command_text:
            issues.append(
                PacketValidationIssue(
                    "unsafe_validation_replay_command",
                    "replay commands must remain offline and unauthenticated",
                    path,
                )
            )


def _validate_rollback_checkpoints(packet: Mapping[str, Any], issues: list[PacketValidationIssue]) -> None:
    checkpoints = packet.get("rollback_checkpoints")
    if not isinstance(checkpoints, Sequence) or isinstance(checkpoints, (str, bytes)) or not checkpoints:
        issues.append(
            PacketValidationIssue(
                "missing_rollback_checkpoints",
                "rollback_checkpoints must be a non-empty list",
                "rollback_checkpoints",
            )
        )
        return

    for index, checkpoint in enumerate(checkpoints):
        path = f"rollback_checkpoints[{index}]"
        if not isinstance(checkpoint, Mapping):
            issues.append(PacketValidationIssue("invalid_rollback_checkpoint", "rollback checkpoint must be an object", path))
            continue
        if not _non_empty_text(checkpoint.get("checkpoint_id")):
            issues.append(PacketValidationIssue("missing_rollback_checkpoint_id", "rollback checkpoint requires checkpoint_id", f"{path}.checkpoint_id"))
        if not _non_empty_string_list(checkpoint.get("restore_command")):
            issues.append(PacketValidationIssue("missing_rollback_restore_command", "rollback checkpoint requires restore_command argv", f"{path}.restore_command"))
        if not _non_empty_string_list(checkpoint.get("verification_command")):
            issues.append(
                PacketValidationIssue(
                    "missing_rollback_verification_command",
                    "rollback checkpoint requires verification_command argv",
                    f"{path}.verification_command",
                )
            )


def _validate_mutation_flags(packet: Mapping[str, Any], issues: list[PacketValidationIssue]) -> None:
    for field in sorted(MUTATION_FLAG_FIELDS):
        if bool(packet.get(field)):
            issues.append(
                PacketValidationIssue(
                    "active_mutation_flag",
                    "release promotion decision packet must not carry active mutation flags",
                    field,
                )
            )


def _validate_recursive_content(packet: Mapping[str, Any], issues: list[PacketValidationIssue]) -> None:
    for path, value in _walk(packet):
        leaf = str(value).lower() if isinstance(value, str) else ""
        name = path.lower()
        combined = f"{name} {leaf}"

        if any(token in combined for token in PRIVATE_ARTIFACT_TOKENS):
            issues.append(
                PacketValidationIssue(
                    "private_or_authenticated_artifact",
                    "packet must not include private, authenticated, session, or browser artifacts",
                    path,
                )
            )
        if any(token in combined for token in RAW_DATA_TOKENS):
            issues.append(
                PacketValidationIssue(
                    "raw_or_downloaded_artifact",
                    "packet must not include raw crawl, PDF, or downloaded data artifacts",
                    path,
                )
            )
        if any(token in leaf for token in GUARANTEE_TOKENS):
            issues.append(
                PacketValidationIssue(
                    "legal_or_permitting_outcome_guarantee",
                    "packet must not include legal or permitting outcome guarantees",
                    path,
                )
            )
        if any(token in leaf for token in CONSEQUENTIAL_ACTION_TOKENS):
            issues.append(
                PacketValidationIssue(
                    "consequential_action_language",
                    "packet must not direct consequential official actions",
                    path,
                )
            )


def _walk(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            yield from _walk(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}[{index}]")
    else:
        yield path, value


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_string_list(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and bool(value) and all(_non_empty_text(item) for item in value)
