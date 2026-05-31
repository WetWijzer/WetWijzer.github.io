"""Validation for DevHub authenticated workflow boundary packet v2.

The packet is a commit-safe description of an attended DevHub workflow boundary.
It must describe what can be observed or drafted without carrying private browser
state, authenticated evidence, or claims that an official action was completed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

PACKET_VERSION = "devhub-authenticated-workflow-boundary-packet-v2"

SURFACE_CATEGORIES = {
    "safe_read_only",
    "reversible_draft",
    "consequential_official",
    "unsupported",
}

ACTION_CLASSIFICATIONS = {
    "read_only",
    "reversible_draft",
    "exact_confirmation_required",
    "manual_handoff_required",
    "refused",
}

PROHIBITED_ARTIFACT_KINDS = {
    "auth_state",
    "browser_context",
    "browser_profile",
    "browser_storage",
    "captcha",
    "cookie",
    "credential",
    "downloaded_private_document",
    "har",
    "local_private_path",
    "mfa",
    "password",
    "payment_detail",
    "private_upload",
    "raw_authenticated_html",
    "raw_authenticated_response",
    "screenshot",
    "session",
    "session_storage",
    "trace",
    "video",
}

PROHIBITED_KEY_FRAGMENTS = (
    "auth_state",
    "browser_context",
    "browser_profile",
    "browser_storage",
    "captcha",
    "cookie",
    "credential",
    "har",
    "local_storage",
    "mfa",
    "password",
    "payment_detail",
    "private_upload",
    "screenshot",
    "session",
    "session_storage",
    "trace",
    "video",
)

PROHIBITED_CLAIM_FRAGMENTS = (
    "application submitted",
    "certification completed",
    "certified on behalf",
    "fee paid",
    "final approval",
    "guarantee",
    "guaranteed",
    "inspection scheduled",
    "legal advice",
    "legally sufficient",
    "permit approved",
    "permit guaranteed",
    "permit issued",
    "permit will be approved",
    "submitted to the city",
    "upload completed",
)

MUTATION_FLAG_NAMES = {
    "active_devhub_contract_mutation",
    "active_devhub_guardrail_mutation",
    "active_devhub_process_model_mutation",
    "active_devhub_prompt_mutation",
    "active_devhub_release_state_mutation",
    "active_devhub_source_mutation",
    "active_devhub_surface_mutation",
    "contract_mutation",
    "guardrail_mutation",
    "process_model_mutation",
    "prompt_mutation",
    "release_state_mutation",
    "source_mutation",
    "surface_mutation",
}


@dataclass(frozen=True)
class BoundaryPacketValidationResult:
    """Result returned by the v2 boundary packet validator."""

    ok: bool
    errors: tuple[str, ...]

    def raise_for_errors(self) -> None:
        if not self.ok:
            raise ValueError("DevHub boundary packet v2 validation failed: " + "; ".join(self.errors))


def validate_boundary_packet_v2(packet: Mapping[str, Any]) -> BoundaryPacketValidationResult:
    """Validate a commit-safe DevHub authenticated workflow boundary packet.

    The validator intentionally accepts plain dictionaries so fixtures, daemon
    checks, and future serializers can use it without sharing a heavyweight
    contract type. It rejects absent required boundary fields and commit-unsafe
    authenticated browser artifacts or claims.
    """

    errors: list[str] = []

    if not isinstance(packet, Mapping):
        return BoundaryPacketValidationResult(False, ("packet must be a mapping",))

    if packet.get("version") != PACKET_VERSION:
        errors.append(f"version must be {PACKET_VERSION!r}")

    surfaces = _required_sequence(packet, "surfaces", errors)
    actions = _required_sequence(packet, "actions", errors)
    validation_commands = _required_sequence(packet, "validation_commands", errors)

    _validate_surfaces(surfaces, errors)
    _validate_actions(actions, errors)
    _validate_validation_commands(validation_commands, errors)
    _validate_artifacts(packet.get("artifacts", ()), errors)
    _validate_claims(packet.get("claims", ()), errors)
    _validate_mutation_flags(packet, errors)
    _scan_for_prohibited_private_material(packet, errors)

    return BoundaryPacketValidationResult(not errors, tuple(dict.fromkeys(errors)))


def assert_valid_boundary_packet_v2(packet: Mapping[str, Any]) -> None:
    """Raise ValueError when a packet is not commit-safe."""

    validate_boundary_packet_v2(packet).raise_for_errors()


def _required_sequence(packet: Mapping[str, Any], key: str, errors: list[str]) -> Sequence[Any]:
    value = packet.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        errors.append(f"{key} must be a non-empty sequence")
        return ()
    return value


def _validate_surfaces(surfaces: Sequence[Any], errors: list[str]) -> None:
    for index, surface in enumerate(surfaces):
        location = f"surfaces[{index}]"
        if not isinstance(surface, Mapping):
            errors.append(f"{location} must be a mapping")
            continue
        _require_non_empty_string(surface, "surface_id", location, errors)
        _require_enum(surface, "category", SURFACE_CATEGORIES, location, errors)
        _require_boolean(surface, "requires_attendance", location, errors)
        _require_boolean(surface, "requires_exact_confirmation", location, errors)
        _require_non_empty_sequence(surface, "redaction_expectations", location, errors)
        _require_non_empty_sequence(surface, "abort_conditions", location, errors)
        _require_non_empty_string(surface, "reviewer_placeholder", location, errors)


def _validate_actions(actions: Sequence[Any], errors: list[str]) -> None:
    for index, action in enumerate(actions):
        location = f"actions[{index}]"
        if not isinstance(action, Mapping):
            errors.append(f"{location} must be a mapping")
            continue
        _require_non_empty_string(action, "action_id", location, errors)
        _require_enum(action, "classification", ACTION_CLASSIFICATIONS, location, errors)
        _require_boolean(action, "requires_attendance", location, errors)
        _require_boolean(action, "requires_exact_confirmation", location, errors)
        _require_non_empty_sequence(action, "redaction_expectations", location, errors)
        _require_non_empty_sequence(action, "abort_conditions", location, errors)
        _require_non_empty_string(action, "reviewer_placeholder", location, errors)


def _validate_validation_commands(commands: Sequence[Any], errors: list[str]) -> None:
    for index, command in enumerate(commands):
        if not isinstance(command, Sequence) or isinstance(command, (str, bytes)) or not command:
            errors.append(f"validation_commands[{index}] must be a non-empty argv sequence")
            continue
        for part_index, part in enumerate(command):
            if not isinstance(part, str) or not part.strip():
                errors.append(f"validation_commands[{index}][{part_index}] must be a non-empty string")


def _validate_artifacts(artifacts: Any, errors: list[str]) -> None:
    if artifacts in (None, ""):
        return
    if not isinstance(artifacts, Sequence) or isinstance(artifacts, (str, bytes)):
        errors.append("artifacts must be a sequence when present")
        return
    for index, artifact in enumerate(artifacts):
        location = f"artifacts[{index}]"
        if not isinstance(artifact, Mapping):
            errors.append(f"{location} must be a mapping")
            continue
        kind = str(artifact.get("kind", "")).strip().lower().replace("-", "_")
        if kind in PROHIBITED_ARTIFACT_KINDS:
            errors.append(f"{location}.kind is prohibited authenticated/private artifact: {kind}")


def _validate_claims(claims: Any, errors: list[str]) -> None:
    if claims in (None, ""):
        return
    if not isinstance(claims, Sequence) or isinstance(claims, (str, bytes)):
        errors.append("claims must be a sequence when present")
        return
    for index, claim in enumerate(claims):
        text = str(claim).casefold()
        for fragment in PROHIBITED_CLAIM_FRAGMENTS:
            if fragment in text:
                errors.append(f"claims[{index}] contains prohibited live, legal, permitting, or completion claim")
                break


def _validate_mutation_flags(packet: Mapping[str, Any], errors: list[str]) -> None:
    mutation_flags = packet.get("mutation_flags", ())
    if mutation_flags in (None, ""):
        mutation_flags = ()
    if not isinstance(mutation_flags, Sequence) or isinstance(mutation_flags, (str, bytes)):
        errors.append("mutation_flags must be a sequence when present")
        return
    for index, flag in enumerate(mutation_flags):
        if isinstance(flag, Mapping):
            name = str(flag.get("name", "")).strip().lower()
            active = bool(flag.get("active", False))
        else:
            name = str(flag).strip().lower()
            active = True
        normalized = name.replace("-", "_").replace(" ", "_")
        if active and normalized in MUTATION_FLAG_NAMES:
            errors.append(f"mutation_flags[{index}] prohibits active DevHub {normalized} flag")

    for key, value in packet.items():
        normalized = str(key).strip().lower().replace("-", "_").replace(" ", "_")
        if normalized in MUTATION_FLAG_NAMES and bool(value):
            errors.append(f"{key} prohibits active DevHub mutation flag")


def _scan_for_prohibited_private_material(value: Any, errors: list[str], path: str = "packet") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key).casefold().replace("-", "_")
            if any(fragment in key_text for fragment in PROHIBITED_KEY_FRAGMENTS):
                errors.append(f"{path}.{key} contains prohibited private/session/browser artifact field")
            _scan_for_prohibited_private_material(nested, errors, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, nested in enumerate(value):
            _scan_for_prohibited_private_material(nested, errors, f"{path}[{index}]")
    elif isinstance(value, str):
        lowered = value.casefold()
        if any(fragment in lowered for fragment in (".har", "trace.zip", "screenshot", "storage_state", "auth.json")):
            errors.append(f"{path} references prohibited private/session/browser artifact data")


def _require_non_empty_string(item: Mapping[str, Any], key: str, location: str, errors: list[str]) -> None:
    if not isinstance(item.get(key), str) or not item[key].strip():
        errors.append(f"{location}.{key} must be a non-empty string")


def _require_boolean(item: Mapping[str, Any], key: str, location: str, errors: list[str]) -> None:
    if not isinstance(item.get(key), bool):
        errors.append(f"{location}.{key} must be a boolean")


def _require_enum(item: Mapping[str, Any], key: str, allowed: Iterable[str], location: str, errors: list[str]) -> None:
    value = item.get(key)
    if value not in set(allowed):
        errors.append(f"{location}.{key} must be one of {sorted(allowed)!r}")


def _require_non_empty_sequence(item: Mapping[str, Any], key: str, location: str, errors: list[str]) -> None:
    value = item.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        errors.append(f"{location}.{key} must be a non-empty sequence")
