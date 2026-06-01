"""Validation for post-recompile agent readiness replay v4 packets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


REQUIRED_NON_EMPTY_FIELDS: Mapping[str, str] = {
    "reviewer_packet_refs": "missing reviewer packet references",
    "synthetic_agent_request_fixtures": "missing synthetic agent request fixtures",
    "affected_missing_information_prompts": "missing affected missing-information prompts",
    "blocked_stale_evidence_paths": "missing blocked stale-evidence paths",
    "blocked_consequential_or_financial_actions": "missing blocked consequential or financial actions",
    "reversible_draft_only_next_actions": "missing reversible draft-only next actions",
    "explanation_template_coverage": "missing explanation-template coverage",
    "manual_handoff_reminders": "missing manual handoff reminders",
    "rollback_notes": "missing rollback notes",
    "validation_commands": "missing validation commands",
}

PRIVATE_OR_AUTH_TOKENS: tuple[str, ...] = (
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "devhub_session",
    "har",
    "localstorage",
    "mfa",
    "password",
    "playwright_trace",
    "private_upload",
    "session_state",
    "storage_state",
    "token",
    "totp",
)

AUTONOMOUS_OFFICIAL_ACTION_PATTERNS: tuple[str, ...] = (
    "agent will submit",
    "agent can submit",
    "autonomously submit",
    "auto submit",
    "submitted without user",
    "schedule inspection automatically",
    "pay fees automatically",
    "upload corrections automatically",
    "certify acknowledgement automatically",
    "purchase permit automatically",
)

LEGAL_OR_PERMITTING_GUARANTEE_PATTERNS: tuple[str, ...] = (
    "approval guaranteed",
    "guaranteed approval",
    "permit guaranteed",
    "will be approved",
    "legally compliant",
    "legal advice",
    "no attorney needed",
    "certain to pass review",
)

ACTIVE_MUTATION_KEYS: tuple[str, ...] = (
    "active_mutation",
    "active_mutations",
    "allow_mutation",
    "allow_mutations",
    "auto_click",
    "auto_submit",
    "commit_live_changes",
    "execute_official_action",
    "live_mutation_enabled",
    "mutate_live_devhub",
    "mutation_enabled",
    "perform_payment",
    "submit_enabled",
    "upload_enabled",
)


@dataclass(frozen=True)
class ReplayV4ValidationResult:
    """Result returned by the replay v4 readiness validator."""

    ok: bool
    errors: tuple[str, ...]


def validate_post_recompile_agent_readiness_replay_v4(
    packet: Mapping[str, Any],
) -> ReplayV4ValidationResult:
    """Validate that a replay v4 readiness packet is complete and safe.

    The packet is intentionally treated as a plain mapping so fixtures can stay
    deterministic JSON and callers do not need to import shared PP&D contracts.
    """

    errors: list[str] = []

    for field_name, message in REQUIRED_NON_EMPTY_FIELDS.items():
        if _is_missing_or_empty(packet.get(field_name)):
            errors.append(message)

    for path, value in _walk(packet):
        lowered_path = path.lower()
        lowered_value = str(value).lower() if isinstance(value, str) else ""

        if any(token in lowered_path for token in PRIVATE_OR_AUTH_TOKENS):
            errors.append(f"private/session/auth artifact reference is not allowed at {path}")

        if isinstance(value, str) and any(
            token in lowered_value for token in PRIVATE_OR_AUTH_TOKENS
        ):
            errors.append(f"private/session/auth artifact reference is not allowed at {path}")

        if isinstance(value, str) and any(
            pattern in lowered_value for pattern in AUTONOMOUS_OFFICIAL_ACTION_PATTERNS
        ):
            errors.append(f"autonomous official-action claim is not allowed at {path}")

        if isinstance(value, str) and any(
            pattern in lowered_value for pattern in LEGAL_OR_PERMITTING_GUARANTEE_PATTERNS
        ):
            errors.append(f"legal or permitting guarantee is not allowed at {path}")

        if _is_active_mutation_flag(path, value):
            errors.append(f"active mutation flag is not allowed at {path}")

    return ReplayV4ValidationResult(ok=not errors, errors=tuple(dict.fromkeys(errors)))


def assert_post_recompile_agent_readiness_replay_v4(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when a replay v4 packet is incomplete or unsafe."""

    result = validate_post_recompile_agent_readiness_replay_v4(packet)
    if not result.ok:
        raise ValueError("post-recompile agent readiness replay v4 rejected: " + "; ".join(result.errors))


def _is_missing_or_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, Mapping):
        return not value
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return not value
    return False


def _walk(value: Any, path: str = "$.") -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}{key}"
            yield child_path, child
            yield from _walk(child, child_path + ".")
        return

    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, child
            yield from _walk(child, child_path + ".")


def _is_active_mutation_flag(path: str, value: Any) -> bool:
    key = path.rstrip(".").split(".")[-1].lower()
    if key.startswith("["):
        return False
    if key in ACTIVE_MUTATION_KEYS and value is True:
        return True
    if key in ACTIVE_MUTATION_KEYS and isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "enabled", "active"}
    return False
