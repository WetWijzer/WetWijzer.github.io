from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

PACKET_TYPE = "ppd.requirement_regeneration_promotion_approval_packet.v1"

_DECISIONS_REQUIRING_CITATIONS = {"approve", "defer"}
_ALLOWED_DECISIONS = _DECISIONS_REQUIRING_CITATIONS | {"reject"}
_REQUIRED_POLICY_FALSE_KEYS = {
    "uses_live_extraction",
    "invokes_live_crawlers",
    "invokes_processors",
    "invokes_devhub",
    "mutates_active_requirements",
    "mutates_active_processes",
    "mutates_active_process_models",
    "mutates_active_guardrails",
    "mutates_active_guardrail_bundles",
    "mutates_active_prompts",
    "mutates_active_surfaces",
    "mutates_surface_registry",
    "mutates_active_surface_registry",
    "mutates_release_state",
    "mutates_active_release_state",
    "writes_requirement_state",
    "writes_process_state",
    "writes_guardrail_state",
    "writes_prompt_state",
    "writes_surface_registry_state",
    "writes_release_state",
    "promotes_to_active",
    "publishes_release_state",
}
_PRIVATE_KEY_MARKERS = (
    "auth_state",
    "browser_state",
    "case_fact_value",
    "credential",
    "cookie",
    "password",
    "payment_detail",
    "private_case",
    "private_fact",
    "private_file",
    "private_path",
    "private_value",
    "secret",
    "session_state",
    "storage_state",
    "token",
)
_PRIVATE_VALUE_MARKERS = (
    "bearer ",
    "applicant private",
    "private parcel fact",
    "private case fact",
    "-----begin ",
    "sk-",
)
_RAW_KEY_MARKERS = (
    "archive_ref",
    "archive_path",
    "archive_url",
    "download_ref",
    "download_path",
    "download_url",
    "downloaded_document",
    "raw_archive",
    "raw_body",
    "raw_crawl",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "warc",
    "har",
    "screenshot",
    "trace_zip",
)
_RAW_VALUE_MARKERS = (
    "file://",
    "/tmp/",
    "/var/folders/",
    "/private/",
    "/home/",
    "/users/",
    "/raw/",
    "/download/",
    "/downloads/",
    "/archive/",
    "/archives/",
    ".warc",
    "raw_body",
    "raw body",
    "archive.warc",
    "trace.zip",
)
_LIVE_CLAIM_MARKERS = (
    "live extraction",
    "live crawler",
    "live crawl",
    "live processor",
    "processor executed",
    "processor ran",
    "devhub executed",
    "submitted to devhub",
    "uploaded to devhub",
    "paid fees",
    "scheduled inspection",
    "certified application",
)
_OUTCOME_GUARANTEE_MARKERS = (
    "guaranteed approval",
    "approval guaranteed",
    "will be approved",
    "permit will be issued",
    "permit will be approved",
    "legally sufficient",
    "compliance guaranteed",
    "outcome guaranteed",
    "guarantees approval",
    "guarantee approval",
    "automatic approval",
)
_MUTATION_SCOPE_MARKERS = (
    "active_requirement",
    "active_process",
    "active_guardrail",
    "active_prompt",
    "active_surface_registry",
    "surface_registry",
    "release_state",
)
_MUTATION_ACTION_MARKERS = (
    "mutate",
    "mutation",
    "write",
    "promote",
    "promotion",
    "publish",
    "replace",
)


@dataclass(frozen=True)
class RequirementRegenerationPromotionApprovalValidationResult:
    valid: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "problems": list(self.problems)}


def validate_requirement_regeneration_promotion_approval_packet(
    packet: Mapping[str, Any],
) -> RequirementRegenerationPromotionApprovalValidationResult:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return RequirementRegenerationPromotionApprovalValidationResult(False, ("packet must be an object",))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append("packet_type must be ppd.requirement_regeneration_promotion_approval_packet.v1")
    if packet.get("fixture_only") is not True:
        problems.append("fixture_only must be true")

    policy = packet.get("promotion_policy") if isinstance(packet.get("promotion_policy"), Mapping) else {}
    if policy.get("fixtures_only") is not True:
        problems.append("promotion_policy.fixtures_only must be true")
    for key in sorted(_REQUIRED_POLICY_FALSE_KEYS):
        if policy.get(key) is not False:
            problems.append(f"promotion_policy.{key} must be false")

    decisions = packet.get("promotion_decisions") or packet.get("approval_decisions")
    if not isinstance(decisions, list) or not decisions:
        problems.append("promotion_decisions must be a non-empty list")
    for index, decision in enumerate(_mapping_sequence(decisions)):
        decision_value = _normalized_text(decision.get("decision"))
        if decision_value not in _ALLOWED_DECISIONS:
            problems.append(f"promotion_decisions[{index}].decision must be approve, defer, or reject")
        if decision_value in _DECISIONS_REQUIRING_CITATIONS and not _string_list(decision.get("source_evidence_ids")):
            problems.append(f"promotion_decisions[{index}] {decision_value} decision must cite source_evidence_ids")
        if not _string_list(decision.get("affected_requirement_ids")):
            problems.append(f"promotion_decisions[{index}] lacks affected_requirement_ids")
        if not _string_list(decision.get("affected_process_ids")):
            problems.append(f"promotion_decisions[{index}] lacks affected_process_ids")
        if not _string_list(decision.get("affected_guardrail_ids")):
            problems.append(f"promotion_decisions[{index}] lacks affected_guardrail_ids")

    rollback_notes = packet.get("rollback_notes")
    if not isinstance(rollback_notes, list) or not rollback_notes:
        problems.append("rollback_notes must be a non-empty list")
    for index, note in enumerate(_mapping_sequence(rollback_notes)):
        if not note.get("rollback_note_id"):
            problems.append(f"rollback_notes[{index}] lacks rollback_note_id")
        if not note.get("summary"):
            problems.append(f"rollback_notes[{index}] lacks summary")
        if not _string_list(note.get("source_evidence_ids")):
            problems.append(f"rollback_notes[{index}] lacks source_evidence_ids")

    signoff = packet.get("reviewer_signoff")
    if not isinstance(signoff, Mapping):
        problems.append("reviewer_signoff is required")
    else:
        if signoff.get("signed_off") is not True:
            problems.append("reviewer_signoff.signed_off must be true")
        for key in ("reviewer_id", "reviewer_role", "signed_at", "source_evidence_ids"):
            value = signoff.get(key)
            if key == "source_evidence_ids":
                if not _string_list(value):
                    problems.append("reviewer_signoff.source_evidence_ids is required")
            elif not isinstance(value, str) or not value.strip():
                problems.append(f"reviewer_signoff.{key} is required")

    commands = packet.get("expected_offline_validation_commands")
    if not isinstance(commands, list) or not commands:
        problems.append("expected_offline_validation_commands must be a non-empty list")
    for index, command in enumerate(commands if isinstance(commands, list) else []):
        if not _string_list(command):
            problems.append(f"expected_offline_validation_commands[{index}] must be a list of strings")
        elif _command_mentions_live_or_processor(command):
            problems.append(
                f"expected_offline_validation_commands[{index}] must remain offline and must not invoke processors, downloads, archives, DevHub, or live extraction"
            )

    problems.extend(_recursive_safety_problems(packet))
    return RequirementRegenerationPromotionApprovalValidationResult(valid=not problems, problems=tuple(_dedupe(problems)))


def assert_valid_requirement_regeneration_promotion_approval_packet(packet: Mapping[str, Any]) -> None:
    result = validate_requirement_regeneration_promotion_approval_packet(packet)
    if not result.valid:
        raise ValueError("invalid_requirement_regeneration_promotion_approval_packet: " + "; ".join(result.problems))


def _mapping_sequence(value: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)


def _normalized_text(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_")


def _command_mentions_live_or_processor(command: Sequence[str]) -> bool:
    joined = " ".join(command).lower()
    forbidden = (
        " live_public_scrape",
        " live_public_preflight",
        "processor",
        "devhub",
        "crawl --live",
        "--live",
        "playwright",
        "download",
        "archive",
    )
    return any(marker in joined for marker in forbidden)


def _recursive_safety_problems(value: Any, path: str = "packet") -> list[str]:
    problems: list[str] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            normalized = _normalize(key_text)
            next_path = f"{path}.{key_text}"
            if key_text in _REQUIRED_POLICY_FALSE_KEYS and nested is not False:
                problems.append(f"{next_path} must be false")
            if _active_mutation_key(normalized) and nested not in (False, None, "", [], {}):
                problems.append(
                    f"{next_path} must not enable active requirement, process, guardrail, prompt, surface-registry, or release-state mutation"
                )
            if _contains_any(normalized, _PRIVATE_KEY_MARKERS) and nested not in (False, None, "", [], {}):
                problems.append(f"{next_path} references private case facts, credentials, sessions, or runtime-only material")
            if _contains_any(normalized, _RAW_KEY_MARKERS) and nested not in (False, None, "", [], {}):
                problems.append(f"{next_path} references raw body, download, archive, trace, screenshot, HAR, or WARC material")
            problems.extend(_recursive_safety_problems(nested, next_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, nested in enumerate(value):
            problems.extend(_recursive_safety_problems(nested, f"{path}[{index}]"))
    elif isinstance(value, str):
        lower_value = value.lower()
        normalized_value = _normalize(value)
        if _contains_any(normalized_value, _PRIVATE_KEY_MARKERS) or _contains_any(lower_value, _PRIVATE_VALUE_MARKERS):
            problems.append(f"{path} references private case facts, credentials, sessions, or runtime-only material")
        if _contains_any(lower_value, _RAW_VALUE_MARKERS):
            problems.append(f"{path} references raw body, download, archive, trace, screenshot, HAR, or WARC material")
        if _contains_any(lower_value, _LIVE_CLAIM_MARKERS):
            problems.append(f"{path} claims live extraction, processor execution, DevHub execution, or consequential live action")
        if _contains_any(lower_value, _OUTCOME_GUARANTEE_MARKERS):
            problems.append(f"{path} claims a legal or permitting outcome guarantee")
    return problems


def _active_mutation_key(normalized_key: str) -> bool:
    return _contains_any(normalized_key, _MUTATION_SCOPE_MARKERS) and _contains_any(normalized_key, _MUTATION_ACTION_MARKERS)


def _contains_any(value: str, markers: Sequence[str]) -> bool:
    return any(marker in value for marker in markers)


def _normalize(value: str) -> str:
    return value.lower().replace("-", "_").replace(" ", "_")


def _dedupe(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value not in seen:
            deduped.append(value)
            seen.add(value)
    return deduped
