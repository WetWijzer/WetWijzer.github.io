"""Validation for post-recompile agent readiness replay v2 manifests."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

REQUIRED_REPLAY_CASE_TYPES = frozenset(
    {
        "replay_case",
        "stale_source_hold_resolution_placeholder",
        "caution_template_check",
        "next_safe_action_summary",
        "refused_consequential_action_example",
        "reviewer_disposition",
    }
)

FORBIDDEN_PATH_MARKERS = (
    "/private/",
    "private/",
    "/session/",
    "session/",
    "/browser/",
    "browser/",
    "/raw/",
    "raw/",
    "/downloaded/",
    "downloaded/",
)

FORBIDDEN_CLAIM_MARKERS = (
    "live devhub execution",
    "executed in devhub",
    "completed official action",
    "official action completed",
    "permit guaranteed",
    "permitting guaranteed",
    "legal guarantee",
    "legally guaranteed",
)

MUTATION_FLAG_KEYS = frozenset(
    {
        "prompt_mutation",
        "guardrail_mutation",
        "devhub_surface_mutation",
        "source_mutation",
        "contract_mutation",
        "requirement_mutation",
        "process_model_mutation",
        "release_state_mutation",
    }
)

MUTATION_FLAG_PREFIXES = (
    "active_prompt_",
    "active_guardrail_",
    "active_devhub_surface_",
    "active_source_",
    "active_contract_",
    "active_requirement_",
    "active_process_model_",
    "active_release_state_",
)


def validate_manifest(manifest: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a readiness replay v2 manifest."""

    errors: list[str] = []
    if manifest.get("version") != "post-recompile-agent-readiness-replay-v2":
        errors.append("version must be post-recompile-agent-readiness-replay-v2")

    replay_cases = manifest.get("replay_cases")
    if not isinstance(replay_cases, list) or not replay_cases:
        errors.append("replay_cases must contain deterministic replay cases")
        replay_cases = []

    seen_case_types = {
        str(case.get("type"))
        for case in replay_cases
        if isinstance(case, Mapping) and case.get("type") is not None
    }
    for case_type in sorted(REQUIRED_REPLAY_CASE_TYPES - seen_case_types):
        errors.append(f"missing replay case type: {case_type}")

    validation_commands = manifest.get("validation_commands")
    if not _is_command_list(validation_commands):
        errors.append("validation_commands must contain at least one argv-style command")

    for path, value in _walk(manifest):
        if isinstance(value, str):
            lowered = value.lower()
            if any(marker in lowered for marker in FORBIDDEN_PATH_MARKERS):
                errors.append(f"forbidden private/session/browser/raw/downloaded artifact at {path}")
            for marker in FORBIDDEN_CLAIM_MARKERS:
                if marker in lowered:
                    errors.append(f"forbidden claim at {path}: {marker}")
        if _is_active_mutation_flag(path, value):
            errors.append(f"active mutation flag is forbidden at {path}")

    return sorted(set(errors))


def _is_command_list(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for command in value:
        if not isinstance(command, list) or not command:
            return False
        if not all(isinstance(part, str) and part for part in command):
            return False
    return True


def _walk(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = [(path, value)]
    if isinstance(value, Mapping):
        for key, child in value.items():
            items.extend(_walk(child, f"{path}.{key}"))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            items.extend(_walk(child, f"{path}[{index}]"))
    return items


def _is_active_mutation_flag(path: str, value: Any) -> bool:
    if value is not True:
        return False
    key = path.rsplit(".", 1)[-1]
    return key in MUTATION_FLAG_KEYS or any(key.startswith(prefix) for prefix in MUTATION_FLAG_PREFIXES)
