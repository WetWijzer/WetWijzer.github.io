from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import re
from typing import Any

PACKET_TYPE = "ppd.process_guardrail_refresh_candidate_packet.v1"
CANDIDATE_STATUS = "candidate_deltas_not_applied"

_REQUIRED_TRUE_ATTESTATIONS = {
    "fixture_first",
    "candidate_packet_only",
    "no_active_process_mutation",
    "no_active_guardrail_mutation",
    "no_active_prompt_mutation",
    "no_active_surface_registry_mutation",
    "no_active_monitoring_mutation",
    "no_release_state_mutation",
}

_REQUIRED_FALSE_ATTESTATIONS = {
    "active_process_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_surface_registry_mutation",
    "active_monitoring_mutation",
    "release_state_mutation",
    "process_delta_applied",
    "guardrail_delta_applied",
    "prompt_updated",
    "surface_registry_updated",
    "monitoring_state_updated",
    "release_state_updated",
}

_MUTATION_FLAG_DOMAINS = {
    "process",
    "guardrail",
    "prompt",
    "surface_registry",
    "surface-registry",
    "monitoring",
    "release_state",
    "release-state",
}

_PRIVATE_CASE_FACT_KEYS = {
    "case_facts",
    "known_facts",
    "private_case_facts",
    "private_facts",
    "observed_private_values",
    "private_values",
    "authenticated_case_facts",
    "user_case_facts",
}

_PRIVATE_CLASSIFICATIONS = {
    "private",
    "confidential",
    "restricted",
    "user_private",
    "case_private",
    "authenticated",
    "devhub_authenticated_private",
}

_RAW_ARTIFACT_KEY_RE = re.compile(
    r"(^|_)(raw[_-]?body|body[_-]?path|download[_-]?(ref|url|path)?|archive[_-]?(ref|url|path)?|warc[_-]?(ref|path)?|raw[_-]?crawl|artifact[_-]?path|local[_-]?path)(_|$)",
    re.IGNORECASE,
)
_RAW_ARTIFACT_VALUE_RE = re.compile(
    r"(^(file|crawl|archive|warc)://|/(tmp|var/folders|private|home)/|\.warc(\.gz)?$|/raw/|/downloads?/|/archives?/|raw body|downloaded document|archive artifact)",
    re.IGNORECASE,
)
_LIVE_EXECUTION_RE = re.compile(
    r"\b(live extraction|live extractor|ran extraction|extraction executed|processor execution|processor executed|ran processor|live processor|invoked processor|crawler executed|live crawl)\b",
    re.IGNORECASE,
)
_OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?|will be approved|will approve|approval is assured|permit will issue|permit must issue|legally valid|legal outcome|no legal risk|cannot be denied|ensures issuance|ensures approval)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ProcessGuardrailRefreshCandidateValidationResult:
    valid: bool
    problems: tuple[str, ...]


def build_process_guardrail_refresh_candidate_packet(
    requirement_rerun_result_intake_packet: Mapping[str, Any],
    process_model_impact_review_packet: Mapping[str, Any],
    guardrail_bundle_update_candidate_packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic review-only process/guardrail refresh candidate packet."""

    result_id = _packet_id(requirement_rerun_result_intake_packet, "requirement-rerun-result-intake")
    impact_id = _packet_id(process_model_impact_review_packet, "process-model-impact-review")
    guardrail_id = _packet_id(guardrail_bundle_update_candidate_packet, "guardrail-bundle-update-candidate")
    evidence_ids = _packet_evidence_ids(
        requirement_rerun_result_intake_packet,
        process_model_impact_review_packet,
        guardrail_bundle_update_candidate_packet,
    )

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_id": "fixture-first-process-guardrail-refresh-candidate-packet",
        "fixture_only": True,
        "candidate_status": CANDIDATE_STATUS,
        "source_packet_ids": {
            "requirement_rerun_result_intake_packet": result_id,
            "process_model_impact_review_packet": impact_id,
            "guardrail_bundle_update_candidate_packet": guardrail_id,
        },
        "candidate_process_deltas": _candidate_process_deltas(
            requirement_rerun_result_intake_packet,
            process_model_impact_review_packet,
            evidence_ids,
        ),
        "candidate_guardrail_deltas": _candidate_guardrail_deltas(
            requirement_rerun_result_intake_packet,
            guardrail_bundle_update_candidate_packet,
            evidence_ids,
        ),
        "rollback_notes": _rollback_notes(process_model_impact_review_packet, guardrail_bundle_update_candidate_packet, evidence_ids),
        "reviewer_owner_fields": _reviewer_owner_fields(
            requirement_rerun_result_intake_packet,
            process_model_impact_review_packet,
            guardrail_bundle_update_candidate_packet,
            evidence_ids,
        ),
        "expected_offline_validation_commands": [
            ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
            ["python3", "-m", "unittest", "ppd.tests.test_process_guardrail_refresh_candidate_packet"],
        ],
        "attestations": _attestations(evidence_ids),
    }
    assert_valid_process_guardrail_refresh_candidate_packet(packet)
    return packet


def validate_process_guardrail_refresh_candidate_packet(packet: Mapping[str, Any]) -> ProcessGuardrailRefreshCandidateValidationResult:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return ProcessGuardrailRefreshCandidateValidationResult(False, ("packet must be an object",))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append("packet_type must be ppd.process_guardrail_refresh_candidate_packet.v1")
    if packet.get("fixture_only") is not True:
        problems.append("fixture_only must be true")
    if packet.get("candidate_status") != CANDIDATE_STATUS:
        problems.append("candidate_status must keep deltas unapplied")

    source_packet_ids = packet.get("source_packet_ids") if isinstance(packet.get("source_packet_ids"), Mapping) else {}
    for key in (
        "requirement_rerun_result_intake_packet",
        "process_model_impact_review_packet",
        "guardrail_bundle_update_candidate_packet",
    ):
        if not source_packet_ids.get(key):
            problems.append(f"source_packet_ids.{key} is required")

    _validate_delta_section(problems, packet, "candidate_process_deltas", "affected_process_ids")
    _validate_delta_section(problems, packet, "candidate_guardrail_deltas", "affected_guardrail_ids")
    _validate_rollback_notes(problems, packet)
    _validate_reviewer_owner_fields(problems, packet)
    _validate_expected_offline_commands(problems, packet)
    _validate_attestations(problems, packet)
    _validate_recursive_policy_rejections(problems, packet)

    return ProcessGuardrailRefreshCandidateValidationResult(not problems, tuple(problems))


def assert_valid_process_guardrail_refresh_candidate_packet(packet: Mapping[str, Any]) -> None:
    result = validate_process_guardrail_refresh_candidate_packet(packet)
    if not result.valid:
        raise ValueError("invalid process/guardrail refresh candidate packet: " + "; ".join(result.problems))


def _candidate_process_deltas(result_packet: Mapping[str, Any], impact_packet: Mapping[str, Any], evidence_ids: Sequence[str]) -> list[dict[str, Any]]:
    deltas: list[dict[str, Any]] = []
    for index, decision in enumerate(_mapping_sequence(result_packet.get("result_decisions"))):
        citations = _citation_ids(decision.get("citations")) or list(evidence_ids)
        process_id = _text(decision.get("process_id")) or "unknown-process"
        deltas.append(
            {
                "delta_id": f"process-delta.result-intake.{index + 1}",
                "delta_type": "requirement_result_alignment",
                "process_id": process_id,
                "affected_process_ids": [process_id],
                "requirement_id": _text(decision.get("requirement_id")),
                "decision": _text(decision.get("decision")),
                "summary": _text(decision.get("rationale")) or "Carry requirement rerun result into process-model refresh review.",
                "source_evidence_ids": citations,
                "activation_allowed": False,
            }
        )
    affected_process_ids = _string_list(impact_packet.get("affected_process_ids")) or ["unknown-process"]
    for index, claim in enumerate(_mapping_sequence(impact_packet.get("process_stage_impact_claims"))):
        citations = _string_list(claim.get("source_evidence_ids")) or list(evidence_ids)
        deltas.append(
            {
                "delta_id": f"process-delta.impact-review.{index + 1}",
                "delta_type": "process_stage_impact_review",
                "process_id": affected_process_ids[0],
                "affected_process_ids": affected_process_ids,
                "process_stage": _text(claim.get("process_stage")),
                "summary": _text(claim.get("impact")),
                "source_evidence_ids": citations,
                "activation_allowed": False,
            }
        )
    return deltas


def _candidate_guardrail_deltas(result_packet: Mapping[str, Any], guardrail_packet: Mapping[str, Any], evidence_ids: Sequence[str]) -> list[dict[str, Any]]:
    deltas: list[dict[str, Any]] = []
    for index, decision in enumerate(_mapping_sequence(result_packet.get("result_decisions"))):
        for guardrail_id in _string_list(decision.get("guardrail_ids")):
            deltas.append(
                {
                    "delta_id": f"guardrail-delta.result-intake.{index + 1}.{guardrail_id}",
                    "delta_type": "requirement_result_guardrail_alignment",
                    "guardrail_id": guardrail_id,
                    "affected_guardrail_ids": [guardrail_id],
                    "requirement_id": _text(decision.get("requirement_id")),
                    "decision": _text(decision.get("decision")),
                    "summary": "Review whether the rerun result changes guardrail predicate coverage.",
                    "source_evidence_ids": _citation_ids(decision.get("citations")) or list(evidence_ids),
                    "activation_allowed": False,
                }
            )
    bundle_id = _text(guardrail_packet.get("active_guardrail_bundle_id")) or "candidate-guardrail-bundle"
    for section_name in ("cited_predicate_additions", "cited_predicate_removals"):
        for index, predicate in enumerate(_mapping_sequence(guardrail_packet.get(section_name))):
            predicate_id = _text(predicate.get("predicate_id"))
            deltas.append(
                {
                    "delta_id": f"guardrail-delta.{section_name}.{index + 1}",
                    "delta_type": section_name,
                    "guardrail_bundle_id": bundle_id,
                    "affected_guardrail_ids": [predicate_id or bundle_id],
                    "predicate_id": predicate_id,
                    "operation": _text(predicate.get("operation")),
                    "summary": "Carry cited predicate candidate into refresh review without compiling or promoting a bundle.",
                    "source_evidence_ids": _string_list(predicate.get("source_evidence_ids")) or _citation_ids(predicate.get("citations")) or list(evidence_ids),
                    "activation_allowed": False,
                }
            )
    return deltas


def _rollback_notes(impact_packet: Mapping[str, Any], guardrail_packet: Mapping[str, Any], evidence_ids: Sequence[str]) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    for index, carryover in enumerate(_mapping_sequence(impact_packet.get("blocked_action_carryovers"))):
        notes.append(
            {
                "rollback_note_id": f"rollback.process-carryover.{index + 1}",
                "scope": "process_model_refresh_candidate",
                "summary": _text(carryover.get("reason")) or "Keep blocked-action carryover visible if candidate refresh is withdrawn.",
                "source_evidence_ids": list(evidence_ids),
            }
        )
    for index, note in enumerate(_mapping_sequence(guardrail_packet.get("rollback_notes"))):
        notes.append(
            {
                "rollback_note_id": f"rollback.guardrail-candidate.{index + 1}",
                "scope": "guardrail_refresh_candidate",
                "summary": _text(note.get("summary")) or _text(note.get("rollback_note")) or "Withdraw candidate guardrail deltas before any active bundle mutation.",
                "source_evidence_ids": _string_list(note.get("source_evidence_ids")) or list(evidence_ids),
            }
        )
    if notes:
        return notes
    return [
        {
            "rollback_note_id": "rollback.fixture-refresh-candidate.1",
            "scope": "process_guardrail_refresh_candidate",
            "summary": "Discard this candidate packet; no active process model, guardrail bundle, prompt, surface registry, monitoring state, or release state was mutated.",
            "source_evidence_ids": list(evidence_ids),
        }
    ]


def _reviewer_owner_fields(result_packet: Mapping[str, Any], impact_packet: Mapping[str, Any], guardrail_packet: Mapping[str, Any], evidence_ids: Sequence[str]) -> list[dict[str, Any]]:
    owners = set()
    owner = _text(result_packet.get("reviewer_owner"))
    if owner:
        owners.add(owner)
    owners.update(_string_list(impact_packet.get("reviewer_owners")))
    for predicate in _mapping_sequence(guardrail_packet.get("cited_predicate_removals")):
        owner = _text(predicate.get("reviewer_owner"))
        if owner:
            owners.add(owner)
    if not owners:
        owners.add("ppd-process-guardrail-refresh-reviewer")
    return [
        {
            "reviewer_owner_id": owner,
            "role": "process_guardrail_refresh_candidate_reviewer",
            "approval_status": "pending_human_review",
            "source_evidence_ids": list(evidence_ids),
        }
        for owner in sorted(owners)
    ]


def _attestations(evidence_ids: Sequence[str]) -> dict[str, Any]:
    attestations = {key: True for key in _REQUIRED_TRUE_ATTESTATIONS}
    attestations.update({key: False for key in _REQUIRED_FALSE_ATTESTATIONS})
    attestations["source_evidence_ids"] = list(evidence_ids)
    return attestations


def _validate_delta_section(problems: list[str], packet: Mapping[str, Any], section_name: str, affected_ids_field: str) -> None:
    section = packet.get(section_name)
    if not isinstance(section, list) or not section:
        problems.append(f"{section_name} must be a non-empty list")
        return
    for index, item in enumerate(_mapping_sequence(section)):
        if not item.get("delta_id"):
            problems.append(f"{section_name}[{index}] lacks delta_id")
        if not _string_list(item.get(affected_ids_field)):
            problems.append(f"{section_name}[{index}] lacks {affected_ids_field}")
        if not _string_list(item.get("source_evidence_ids")):
            problems.append(f"{section_name}[{index}] lacks source_evidence_ids")
        if item.get("activation_allowed") is not False:
            problems.append(f"{section_name}[{index}] must keep activation_allowed false")


def _validate_rollback_notes(problems: list[str], packet: Mapping[str, Any]) -> None:
    rollback_notes = packet.get("rollback_notes")
    if not isinstance(rollback_notes, list) or not rollback_notes:
        problems.append("rollback_notes must be a non-empty list")
    for index, note in enumerate(_mapping_sequence(rollback_notes)):
        if not note.get("rollback_note_id"):
            problems.append(f"rollback_notes[{index}] lacks rollback_note_id")
        if not _string_list(note.get("source_evidence_ids")):
            problems.append(f"rollback_notes[{index}] lacks source_evidence_ids")


def _validate_reviewer_owner_fields(problems: list[str], packet: Mapping[str, Any]) -> None:
    owners = packet.get("reviewer_owner_fields")
    if not isinstance(owners, list) or not owners:
        problems.append("reviewer_owner_fields must be a non-empty list")
    for index, owner in enumerate(_mapping_sequence(owners)):
        if not owner.get("reviewer_owner_id"):
            problems.append(f"reviewer_owner_fields[{index}] lacks reviewer_owner_id")
        if owner.get("approval_status") != "pending_human_review":
            problems.append(f"reviewer_owner_fields[{index}] must be pending_human_review")
        if not _string_list(owner.get("source_evidence_ids")):
            problems.append(f"reviewer_owner_fields[{index}] lacks source_evidence_ids")


def _validate_expected_offline_commands(problems: list[str], packet: Mapping[str, Any]) -> None:
    commands = packet.get("expected_offline_validation_commands")
    if not isinstance(commands, list) or not commands:
        problems.append("expected_offline_validation_commands must be a non-empty list")
    for index, command in enumerate(commands if isinstance(commands, list) else []):
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            problems.append(f"expected_offline_validation_commands[{index}] must be a non-empty argv list")


def _validate_attestations(problems: list[str], packet: Mapping[str, Any]) -> None:
    attestations = packet.get("attestations") if isinstance(packet.get("attestations"), Mapping) else {}
    for key in sorted(_REQUIRED_TRUE_ATTESTATIONS):
        if attestations.get(key) is not True:
            problems.append(f"attestations.{key} must be true")
    for key in sorted(_REQUIRED_FALSE_ATTESTATIONS):
        if attestations.get(key) is not False:
            problems.append(f"attestations.{key} must be false")
    if not _string_list(attestations.get("source_evidence_ids")):
        problems.append("attestations.source_evidence_ids must cite fixture evidence")


def _validate_recursive_policy_rejections(problems: list[str], packet: Mapping[str, Any]) -> None:
    for path, value in _walk(packet):
        key = path.rsplit(".", 1)[-1]
        normalized_key = key.lower().replace("-", "_")
        if normalized_key in _PRIVATE_CASE_FACT_KEYS and value:
            problems.append(f"{path} must not include private case facts")
        if isinstance(value, Mapping):
            classification = _text(value.get("privacy_classification") or value.get("privacy")).lower()
            if classification in _PRIVATE_CLASSIFICATIONS:
                problems.append(f"{path} must not include private case facts")
            mutation_flags = value.get("mutation_flags")
            if isinstance(mutation_flags, Mapping):
                for flag, flag_value in mutation_flags.items():
                    if str(flag).lower() in _MUTATION_FLAG_DOMAINS and flag_value is True:
                        problems.append(f"{path}.mutation_flags.{flag} must be false")
        if _RAW_ARTIFACT_KEY_RE.search(normalized_key):
            problems.append(f"{path} must not reference raw body, download, archive, WARC, or local artifacts")
        if isinstance(value, str):
            stripped = value.strip()
            if _RAW_ARTIFACT_VALUE_RE.search(stripped):
                problems.append(f"{path} must not reference raw body, download, archive, WARC, or local artifacts")
            if _LIVE_EXECUTION_RE.search(stripped):
                problems.append(f"{path} must not claim live extraction or processor execution")
            if _OUTCOME_GUARANTEE_RE.search(stripped):
                problems.append(f"{path} must not guarantee legal or permitting outcomes")
        if _is_active_mutation_flag(normalized_key, value):
            problems.append(f"{path} must not set active mutation flags")


def _is_active_mutation_flag(normalized_key: str, value: Any) -> bool:
    if value is not True:
        return False
    if normalized_key.startswith("no_active_"):
        return False
    if normalized_key in _REQUIRED_FALSE_ATTESTATIONS:
        return True
    if normalized_key.startswith("active_") and "mutation" in normalized_key:
        return True
    if normalized_key in {"process", "guardrail", "prompt", "surface_registry", "monitoring", "release_state"}:
        return True
    return False


def _packet_evidence_ids(*packets: Mapping[str, Any]) -> list[str]:
    ids: set[str] = set()
    for packet in packets:
        ids.update(_string_list(packet.get("source_evidence_ids")))
        ids.update(_string_list(packet.get("affected_requirement_ids")))
        ids.update(_string_list(packet.get("affected_process_ids")))
        ids.update(_string_list(packet.get("affected_guardrail_ids")))
        for path in ("result_decisions", "process_stage_impact_claims", "cited_predicate_additions", "cited_predicate_removals"):
            for item in _mapping_sequence(packet.get(path)):
                ids.update(_string_list(item.get("source_evidence_ids")))
                ids.update(_citation_ids(item.get("citations")))
    return sorted(ids or {"fixture-evidence-process-guardrail-refresh"})


def _citation_ids(value: Any) -> list[str]:
    ids: list[str] = []
    if not isinstance(value, list):
        return ids
    for item in value:
        if isinstance(item, str) and item.strip():
            ids.append(item.strip())
        elif isinstance(item, Mapping):
            selector = _text(item.get("selector"))
            fixture_id = _text(item.get("fixture_id")) or _text(item.get("source_id")) or _text(item.get("source_fixture"))
            if fixture_id and selector:
                ids.append(f"{fixture_id}:{selector}")
            elif fixture_id:
                ids.append(fixture_id)
    return sorted(set(ids))


def _packet_id(packet: Mapping[str, Any], fallback: str) -> str:
    if not isinstance(packet, Mapping):
        raise ValueError(f"{fallback} packet must be an object")
    return _text(packet.get("packet_id")) or fallback


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _walk(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            items.append((path, child))
            items.extend(_walk(child, path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            items.append((path, child))
            items.extend(_walk(child, path))
    return items


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
