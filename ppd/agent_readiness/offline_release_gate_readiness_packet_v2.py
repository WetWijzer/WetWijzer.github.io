from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.offline_release_gate_readiness_packet.v2"

REQUIRED_ATTESTATIONS = {
    "no_live": "No live crawl, live browser, live processor, or live DevHub action is used.",
    "no_auth": "No authenticated session, credential, cookie, token, browser state, MFA, CAPTCHA, or private account value is used.",
    "no_official_action": "No upload, submission, certification, payment, scheduling, cancellation, purchase, or other consequential PP&D action is performed.",
    "no_release_state_mutation": "No active source, surface-registry, guardrail, prompt, monitoring, release-state, or agent-state artifact is mutated.",
}

DEFAULT_REQUIRED_TEST_COMMANDS = (
    ("python3", "-m", "py_compile", "ppd/agent_readiness/offline_release_gate_readiness_packet_v2.py"),
    ("python3", "-m", "pytest", "ppd/tests/test_offline_release_gate_readiness_packet_v2.py"),
    ("python3", "ppd/daemon/ppd_daemon.py", "--self-test"),
)

_PRIVATE_KEYS = {
    "auth_state",
    "browser_state",
    "card_number",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "devhub_session",
    "downloaded_document",
    "email",
    "har",
    "local_path",
    "password",
    "payment_details",
    "phone",
    "private_fact",
    "private_facts",
    "private_path",
    "private_value",
    "raw_body",
    "raw_crawl",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "session",
    "session_state",
    "screenshot",
    "secret",
    "storage_state",
    "token",
    "trace",
    "user_input",
}

_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_monitoring_mutation",
    "active_prompt_mutation",
    "active_registry_mutation",
    "active_release_state_mutation",
    "active_source_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation_enabled",
    "apply_update",
    "commit_to_registry",
    "guardrail_mutation_enabled",
    "monitoring_mutation_enabled",
    "prompt_mutation_enabled",
    "registry_mutation_enabled",
    "release_state_mutation_enabled",
    "source_mutation_enabled",
    "surface_registry_mutation_enabled",
}

_MUTATION_FLAG_KEYS = {
    "agent_state",
    "guardrail",
    "guardrails",
    "monitor",
    "monitoring",
    "prompt",
    "prompts",
    "release",
    "release_state",
    "source",
    "sources",
    "surface",
    "surface_registry",
    "surfaces",
}

_UNSAFE_TEXT_RE = re.compile(
    r"(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/tmp/)|"
    r"(auth[_-]?state|authenticated\s+(fact|facts|value|values)|browser[_-]?state|cookie|credential|har|password|"
    r"private\s+(fact|facts|value|values)|raw[_-]?(body|crawl|html|pdf|download|artifact)|downloaded[_-]?document|"
    r"pdf[_-]?artifact|session[_-]?(state|storage)?|screenshot|secret|storage[_-]?state|token|trace\.zip)|"
    r"\b(live\s+(crawl|browser|devhub|execution|processor|promotion|run)|opened\s+devhub|logged\s+into\s+devhub|"
    r"executed\s+(the\s+)?(release|promotion)|promoted\s+(to\s+)?(production|release)|ran\s+processor|"
    r"registry\s+updated|source\s+updated|surface\s+registry\s+updated|guardrail\s+updated|prompt\s+updated|"
    r"monitoring\s+updated|agent\s+state\s+updated|release\s+state\s+updated|"
    r"click(ed)?\s+(submit|pay|certify|schedule|cancel)|submit(ted)?\s+(the\s+)?(permit|application|payment)|"
    r"pay\s+(the\s+)?fee|schedule\s+(the\s+)?inspection|certify\s+(the\s+)?application|"
    r"final\s+(submission|submit|payment|upload)|official\s+upload|consequential\s+action|"
    r"permit\s+will\s+be\s+(approved|issued)|approval\s+is\s+guaranteed|guaranteed\s+(approval|issuance|permit\s+outcome)|"
    r"legally\s+(sufficient|compliant)|city\s+will\s+(approve|issue))\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class OfflineReleaseGateReadinessV2ValidationResult:
    ok: bool
    errors: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "errors": list(self.errors)}


def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def build_offline_release_gate_readiness_packet_v2_from_fixture(path: str | Path) -> dict[str, Any]:
    return build_offline_release_gate_readiness_packet_v2(load_json(path))


def build_offline_release_gate_readiness_packet_v2(source: Mapping[str, Any]) -> dict[str, Any]:
    """Build a side-effect-free release gate readiness packet from fixtures only."""

    _reject_unsafe(source)
    staging_plan = _mapping(source.get("implementation_patch_staging_plan_v2"))
    if not staging_plan:
        raise ValueError("implementation_patch_staging_plan_v2 is required")
    validation_fixtures = _mapping_sequence(source.get("validation_fixtures"))
    if not validation_fixtures:
        raise ValueError("validation_fixtures must be non-empty")
    candidates = _mapping_sequence(staging_plan.get("patch_candidates"))
    if not candidates:
        raise ValueError("implementation patch staging plan must include patch_candidates")

    staging_issues = _staging_issues(candidates)
    command_rows = _required_test_commands(source, validation_fixtures)
    packet = {
        "packet_type": PACKET_TYPE,
        "packet_id": _text(source.get("packet_id")) or "offline-release-gate-readiness-v2",
        "fixture_only": True,
        "source_staging_plan_version": _text(staging_plan.get("version")),
        "gate_criteria": _gate_criteria(candidates, validation_fixtures, command_rows),
        "required_test_commands": command_rows,
        "blocker_dispositions": _blocker_dispositions(staging_issues, validation_fixtures),
        "rollback_verification": _rollback_verification(candidates),
        "reviewer_owner_fields": _reviewer_owner_fields(candidates, source),
        "attestations": _attestations(),
        "execution_boundaries": {
            "live_network": False,
            "authenticated_session": False,
            "official_action": False,
            "source_mutation": False,
            "surface_registry_mutation": False,
            "guardrail_mutation": False,
            "prompt_mutation": False,
            "monitoring_mutation": False,
            "release_state_mutation": False,
            "agent_state_mutation": False,
        },
        "release_gate_status": "blocked" if staging_issues else "ready_for_fixture_review_only",
    }
    require_offline_release_gate_readiness_packet_v2(packet)
    return packet


def validate_offline_release_gate_readiness_packet_v2(packet: Mapping[str, Any]) -> OfflineReleaseGateReadinessV2ValidationResult:
    errors: list[str] = []
    try:
        _reject_unsafe(packet)
    except ValueError as exc:
        errors.append(str(exc))

    if packet.get("packet_type") != PACKET_TYPE:
        errors.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("fixture_only") is not True:
        errors.append("fixture_only must be true")

    for field in ("gate_criteria", "required_test_commands", "blocker_dispositions", "rollback_verification", "reviewer_owner_fields", "attestations"):
        if not _mapping_sequence(packet.get(field)):
            errors.append(f"{field} must be a non-empty list of objects")

    criteria = _mapping_sequence(packet.get("gate_criteria"))
    blockers = _mapping_sequence(packet.get("blocker_dispositions"))
    rollbacks = _mapping_sequence(packet.get("rollback_verification"))
    owners = _mapping_sequence(packet.get("reviewer_owner_fields"))
    candidate_ids = {_text(row.get("candidate_id")) for row in criteria if _text(row.get("candidate_id"))}
    for candidate_id in sorted(candidate_ids):
        if not any(_text(row.get("candidate_id")) == candidate_id or _text(row.get("blocker_id")) == "no-open-staging-plan-blockers" for row in blockers):
            errors.append(f"candidate {candidate_id} is missing blocker disposition coverage")
        if not any(_text(row.get("candidate_id")) == candidate_id for row in rollbacks):
            errors.append(f"candidate {candidate_id} is missing rollback verification")
        if not any(_text(row.get("candidate_id")) == candidate_id for row in owners):
            errors.append(f"candidate {candidate_id} is missing reviewer owner")

    for index, criterion in enumerate(criteria):
        if not _text(criterion.get("criterion_id")):
            errors.append(f"gate_criteria[{index}].criterion_id must be present")
        if not _text(criterion.get("gate")):
            errors.append(f"gate_criteria[{index}].gate must be present")
        if not _citation_list(criterion.get("citations")):
            errors.append(f"gate_criteria[{index}].citations must be non-empty")
        if not _string_list(criterion.get("required_test_command_ids")):
            errors.append(f"gate_criteria[{index}].required_test_command_ids must be non-empty")

    for index, command in enumerate(_mapping_sequence(packet.get("required_test_commands"))):
        if not _text(command.get("command_id")):
            errors.append(f"required_test_commands[{index}].command_id must be present")
        if not _string_list(command.get("command")):
            errors.append(f"required_test_commands[{index}].command must be a command list")
        if not _citation_list(command.get("citations")):
            errors.append(f"required_test_commands[{index}].citations must be non-empty")

    for index, disposition in enumerate(blockers):
        if not _text(disposition.get("blocker_id")):
            errors.append(f"blocker_dispositions[{index}].blocker_id must be present")
        if _text(disposition.get("disposition")) not in {"blocked", "cleared_by_fixture_validation"}:
            errors.append(f"blocker_dispositions[{index}].disposition must be blocked or cleared_by_fixture_validation")
        if not _citation_list(disposition.get("citations")):
            errors.append(f"blocker_dispositions[{index}].citations must be non-empty")

    for index, rollback in enumerate(rollbacks):
        if not _text(rollback.get("checkpoint_id")):
            errors.append(f"rollback_verification[{index}].checkpoint_id must be present")
        if _text(rollback.get("verification_required_before")) != "release_gate_signoff":
            errors.append(f"rollback_verification[{index}].verification_required_before must be release_gate_signoff")
        if not _citation_list(rollback.get("citations")):
            errors.append(f"rollback_verification[{index}].citations must be non-empty")

    for index, owner in enumerate(owners):
        if not _text(owner.get("reviewer_owner")):
            errors.append(f"reviewer_owner_fields[{index}].reviewer_owner must be present")
        if _text(owner.get("reviewer_owner")) == "ppd-release-reviewer-unassigned":
            errors.append(f"reviewer_owner_fields[{index}].reviewer_owner must not be unassigned")
        if not _text(owner.get("candidate_id")):
            errors.append(f"reviewer_owner_fields[{index}].candidate_id must be present")
        if not _citation_list(owner.get("citations")):
            errors.append(f"reviewer_owner_fields[{index}].citations must be non-empty")

    attestations = {str(row.get("attestation_id")): row for row in _mapping_sequence(packet.get("attestations"))}
    for attestation_id in REQUIRED_ATTESTATIONS:
        row = attestations.get(attestation_id)
        if row is None:
            errors.append(f"missing attestation: {attestation_id}")
        elif row.get("value") is not True:
            errors.append(f"attestation must be true: {attestation_id}")

    boundaries = _mapping(packet.get("execution_boundaries"))
    for key in (
        "live_network",
        "authenticated_session",
        "official_action",
        "source_mutation",
        "surface_registry_mutation",
        "guardrail_mutation",
        "prompt_mutation",
        "monitoring_mutation",
        "release_state_mutation",
        "agent_state_mutation",
    ):
        if boundaries.get(key) is not False:
            errors.append(f"execution_boundaries.{key} must be explicitly false")

    if _text(packet.get("release_gate_status")) not in {"blocked", "ready_for_fixture_review_only"}:
        errors.append("release_gate_status must be blocked or ready_for_fixture_review_only")

    return OfflineReleaseGateReadinessV2ValidationResult(not errors, tuple(errors))


def require_offline_release_gate_readiness_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_offline_release_gate_readiness_packet_v2(packet)
    if not result.ok:
        raise ValueError("invalid offline release gate readiness packet v2: " + "; ".join(result.errors))


def _staging_issues(candidates: Sequence[Mapping[str, Any]]) -> list[str]:
    issues: list[str] = []
    for index, candidate in enumerate(candidates, start=1):
        target_id = _text(candidate.get("target_id")) or f"candidate-{index}"
        if not _citation_list(candidate.get("citations")):
            issues.append(f"{target_id}: candidate citations are required")
        if not _text(candidate.get("reviewer_owner")):
            issues.append(f"{target_id}: reviewer owner is required")
        if not _string_list(candidate.get("rollback_checkpoints")):
            issues.append(f"{target_id}: rollback checkpoints are required")
    return issues


def _gate_criteria(candidates: Sequence[Mapping[str, Any]], validation_fixtures: Sequence[Mapping[str, Any]], commands: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    command_ids = [_text(command.get("command_id")) for command in commands if _text(command.get("command_id"))]
    fixture_citations = _fixture_citations(validation_fixtures)
    rows = []
    for candidate in candidates:
        target_id = _text(candidate.get("target_id")) or "candidate"
        rows.append(
            {
                "criterion_id": f"gate-{_slug(target_id)}",
                "candidate_id": target_id,
                "gate": "Fixture-cited inactive patch candidate is reviewed, validated, rollback-covered, and owner-assigned before any release claim.",
                "required_test_command_ids": command_ids,
                "citations": _citation_list(candidate.get("citations")) + fixture_citations,
            }
        )
    return rows


def _required_test_commands(source: Mapping[str, Any], validation_fixtures: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    source_commands = source.get("required_test_commands")
    commands = source_commands if isinstance(source_commands, list) and source_commands else [list(command) for command in DEFAULT_REQUIRED_TEST_COMMANDS]
    fixture_citations = _fixture_citations(validation_fixtures)
    for index, command in enumerate(commands, start=1):
        command_parts = _string_list(command)
        if not command_parts:
            command_parts = [str(command)]
        rows.append(
            {
                "command_id": f"offline-gate-command-{index:02d}",
                "command": command_parts,
                "required_before": "release_gate_signoff",
                "citations": fixture_citations,
            }
        )
    return rows


def _blocker_dispositions(staging_issues: Sequence[str], validation_fixtures: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    citations = _fixture_citations(validation_fixtures)
    if not staging_issues:
        return [
            {
                "blocker_id": "no-open-staging-plan-blockers",
                "disposition": "cleared_by_fixture_validation",
                "summary": "Implementation patch staging plan v2 validator returned no issues for the consumed fixture.",
                "citations": citations,
            }
        ]
    rows = []
    for index, message in enumerate(staging_issues, start=1):
        rows.append(
            {
                "blocker_id": f"blocker-staging-issue-{index:02d}",
                "disposition": "blocked",
                "summary": message,
                "citations": citations,
            }
        )
    return rows


def _rollback_verification(candidates: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for candidate in candidates:
        target_id = _text(candidate.get("target_id")) or "candidate"
        checkpoints = _string_list(candidate.get("rollback_checkpoints")) or ["Remove the inactive patch candidate and rerun offline fixture validation."]
        for index, checkpoint in enumerate(checkpoints, start=1):
            rows.append(
                {
                    "checkpoint_id": f"rollback-{_slug(target_id)}-{index:02d}",
                    "candidate_id": target_id,
                    "verification": checkpoint,
                    "verification_required_before": "release_gate_signoff",
                    "citations": _citation_list(candidate.get("citations")),
                }
            )
    return rows


def _reviewer_owner_fields(candidates: Sequence[Mapping[str, Any]], source: Mapping[str, Any]) -> list[dict[str, Any]]:
    owners = _mapping(source.get("reviewer_owners"))
    rows = []
    for candidate in candidates:
        target_id = _text(candidate.get("target_id")) or "candidate"
        owner = _text(candidate.get("reviewer_owner")) or _text(owners.get(target_id)) or "ppd-release-reviewer-unassigned"
        rows.append(
            {
                "owner_field_id": f"owner-{_slug(target_id)}",
                "candidate_id": target_id,
                "reviewer_owner": owner,
                "required_before": "release_gate_signoff",
                "citations": _citation_list(candidate.get("citations")),
            }
        )
    return rows


def _attestations() -> list[dict[str, Any]]:
    return [
        {"attestation_id": attestation_id, "attests": text, "value": True}
        for attestation_id, text in REQUIRED_ATTESTATIONS.items()
    ]


def _fixture_citations(validation_fixtures: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for fixture in validation_fixtures:
        fixture_id = _text(fixture.get("fixture_id")) or _text(fixture.get("path")) or "validation-fixture"
        rows.append(
            {
                "fixture_id": fixture_id,
                "path": _text(fixture.get("path")) or "ppd/tests/fixtures",
                "purpose": _text(fixture.get("purpose")) or "offline validation fixture",
            }
        )
    return rows


def _reject_unsafe(value: Any, path: str = "$.") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.lower().replace("-", "_")
            child_path = f"{path}{key_text}"
            if normalized in _PRIVATE_KEYS and child not in (None, "", [], {}):
                raise ValueError(f"private, raw, session, browser, or payment field is not allowed at {child_path}")
            if normalized in _MUTATION_KEYS and _active(child):
                raise ValueError(f"active mutation flag is not allowed at {child_path}")
            if normalized == "mutation_flags" and _has_active_mutation_flag(child):
                raise ValueError(f"active mutation flag is not allowed at {child_path}")
            _reject_unsafe(child, f"{child_path}.")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _reject_unsafe(child, f"{path}[{index}].")
    elif isinstance(value, str) and _UNSAFE_TEXT_RE.search(value):
        raise ValueError(f"unsafe live/auth/raw/mutation/official-action text is not allowed at {path.rstrip('.')}")


def _active(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"active", "enabled", "true", "yes"}
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return False


def _has_active_mutation_flag(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return _active(value)
    for key, child in value.items():
        normalized = str(key).lower().replace("-", "_")
        if normalized in _MUTATION_FLAG_KEYS and _active(child):
            return True
    return False


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> tuple[Mapping[str, Any], ...]:
    if isinstance(value, Mapping):
        return (value,)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(item for item in value if isinstance(item, Mapping))
    return ()


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [str(item) for item in value if str(item).strip()]
    return []


def _citation_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        rows = [dict(item) for item in value if isinstance(item, Mapping)]
        if rows:
            return rows
        strings = [str(item) for item in value if str(item).strip()]
        if strings:
            return [{"citation": item} for item in strings]
    if isinstance(value, str) and value.strip():
        return [{"citation": value.strip()}]
    return []


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _slug(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value)
    return "-".join(part for part in cleaned.split("-") if part) or "item"
