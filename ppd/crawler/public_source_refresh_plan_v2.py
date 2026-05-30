from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

PACKET_TYPE = "ppd_public_source_refresh_plan_v2"
PACKET_VERSION = "2.0"
DEFAULT_REVIEWER_OWNER = "PP&D public source registry maintainer"
DEFAULT_VALIDATION_COMMANDS = [
    "python3 -m unittest ppd.tests.test_public_source_refresh_plan_v2",
    "python3 ppd/daemon/ppd_daemon.py --self-test",
]

_FORBIDDEN_TRUE_KEYS = {
    "livecrawlexecuted",
    "livecrawlperformed",
    "livefetchused",
    "livenetworkinvoked",
    "networkioallowed",
    "processorexecuted",
    "processorinvoked",
    "processorinvocationallowed",
    "rawbodypersisted",
    "rawbodiespersisted",
    "rawbodypersistenceallowed",
    "downloadeddocuments",
    "downloadsallowed",
    "sourceregistrymutated",
    "registrymutationallowed",
    "schedulemutationallowed",
    "requirementmutationallowed",
    "processmutationallowed",
    "guardrailmutationallowed",
}
_FORBIDDEN_VALUE_MARKERS = (
    "auth_state",
    "cookie",
    "credential",
    "password",
    "session_cookie",
    "storage_state",
    "trace.zip",
    "warc://",
    ".warc",
    "/raw/",
    "raw_crawl",
    "raw-crawl",
    "rawcrawl",
    "crawl_output",
    "crawl-output",
    "downloaded_documents",
    "downloaded-documents",
    "/downloads/",
    "processor_output",
    "processor-output",
    "processor_outputs",
)


@dataclass(frozen=True)
class PublicSourceRefreshPlanV2ValidationResult:
    valid: bool
    errors: tuple[str, ...]


class PublicSourceRefreshPlanV2Error(ValueError):
    pass


def build_public_source_refresh_plan_v2(
    official_source_anchor_audit_packet: Mapping[str, Any],
    public_source_refresh_intake_evidence_packet_v1: Mapping[str, Any],
    source_to_requirement_traceability_packet_v1: Mapping[str, Any],
    public_source_change_impact_rehearsal_v1: Mapping[str, Any],
    *,
    packet_id: str = "fixture-public-source-refresh-plan-v2-001",
    generated_at: str = "2026-05-30T00:00:00Z",
) -> dict[str, Any]:
    _require_mapping(official_source_anchor_audit_packet, "official_source_anchor_audit_packet")
    _require_mapping(public_source_refresh_intake_evidence_packet_v1, "public_source_refresh_intake_evidence_packet_v1")
    _require_mapping(source_to_requirement_traceability_packet_v1, "source_to_requirement_traceability_packet_v1")
    _require_mapping(public_source_change_impact_rehearsal_v1, "public_source_change_impact_rehearsal_v1")

    candidates_by_source: dict[str, dict[str, Any]] = {}
    citations_by_source: dict[str, list[dict[str, Any]]] = {}

    for row in _list(official_source_anchor_audit_packet.get("gap_rows")):
        if not isinstance(row, Mapping):
            continue
        source_ids = _text_list(row.get("affected_source_ids")) or [_source_id_from_url(_text(row.get("anchor_url")))]
        for source_id in source_ids:
            candidate = _candidate(candidates_by_source, source_id, _text(row.get("anchor_url")))
            candidate["candidate_sources"].append("official_source_anchor_audit_packet_v1")
            candidate["refresh_reasons"].extend("anchor_audit:" + issue for issue in _text_list(row.get("issue_types")))
            candidate["freshness_status"] = _text(row.get("freshness_status"), candidate["freshness_status"])
            candidate["policy_status"] = {
                "allowlist_status": _text(row.get("allowlist_status")),
                "robots_policy_status": _text(row.get("robots_policy_status")),
                "processor_policy_status": _text(row.get("processor_policy_status")),
            }
            candidate["reviewer_owner"] = _text(row.get("reviewer_owner"), candidate["reviewer_owner"])
            candidate["rollback_note_refs"].append(_text(row.get("rollback_note"), "discard_anchor_audit_refresh_candidate"))
            citations_by_source.setdefault(source_id, []).append(
                {
                    "citation_type": "official_anchor_audit_gap",
                    "source_id": source_id,
                    "public_url": _text(row.get("anchor_url")),
                    "citation_refs": _text_list(row.get("citations")) or ["official_source_anchor_audit_packet_v1"],
                    "basis": ", ".join(_text_list(row.get("issue_types"))) or "official anchor audit gap",
                }
            )

    for row in _list(public_source_refresh_intake_evidence_packet_v1.get("synthetic_reviewer_evidence")):
        if not isinstance(row, Mapping):
            continue
        source_id = _text(row.get("source_id"))
        candidate = _candidate(candidates_by_source, source_id, _text(row.get("canonical_url")))
        fields = row.get("synthetic_reviewer_evidence_fields") if isinstance(row.get("synthetic_reviewer_evidence_fields"), Mapping) else {}
        owners = fields.get("reviewer_owner_fields") if isinstance(fields.get("reviewer_owner_fields"), Mapping) else {}
        candidate["candidate_sources"].append("public_source_refresh_intake_evidence_packet_v1")
        candidate["refresh_reasons"].append(_text(fields.get("refresh_reason"), "intake_evidence_refresh_candidate"))
        candidate["reviewer_owner"] = _text(owners.get("reviewer_owner") or owners.get("owner"), candidate["reviewer_owner"])
        candidate["metadata_expectations"] = {
            "expected_metadata_fields": _text_list(fields.get("expected_metadata_fields")),
            "content_hash_expectation_fields": _text_list(fields.get("content_hash_expectation_fields")),
            "skipped_target_reason_slot": _text(fields.get("skipped_target_reason_slot")),
            "no_raw_body_attestation_id": _text(fields.get("no_raw_body_attestation_id")),
        }
        candidate["rollback_note_refs"].extend(_text_list(fields.get("rollback_note_ids")))
        citations_by_source.setdefault(source_id, []).append(
            {
                "citation_type": "refresh_intake_evidence",
                "source_id": source_id,
                "public_url": _text(row.get("canonical_url")),
                "citation_refs": [_text(row.get("evidence_id"), "public_source_refresh_intake_evidence_packet_v1")],
                "basis": "fixture metadata-only reviewer evidence intake",
            }
        )

    traceability_rows = _traceability_rows(source_to_requirement_traceability_packet_v1)
    for row in traceability_rows:
        source_id = _text(row.get("source_id"))
        candidate = _candidate(candidates_by_source, source_id, _text(row.get("canonical_url") or row.get("public_url")))
        candidate["candidate_sources"].append("source_to_requirement_traceability_packet_v1")
        candidate["affected_requirement_ids"].extend(_text_list(row.get("requirement_ids") or row.get("affected_requirement_ids")))
        candidate["affected_process_ids"].extend(_text_list(row.get("process_ids") or row.get("affected_process_ids")))
        candidate["affected_guardrail_bundle_ids"].extend(_text_list(row.get("guardrail_bundle_ids") or row.get("affected_guardrail_bundle_ids")))
        candidate["reviewer_owner"] = _text(row.get("reviewer_owner"), candidate["reviewer_owner"])
        citations_by_source.setdefault(source_id, []).append(
            {
                "citation_type": "source_to_requirement_traceability",
                "source_id": source_id,
                "public_url": _text(row.get("canonical_url") or row.get("public_url")),
                "citation_refs": _text_list(row.get("citations")) or [_text(row.get("trace_id"), "source_to_requirement_traceability_packet_v1")],
                "basis": _text(row.get("trace_basis"), "source-to-requirement traceability fixture row"),
            }
        )

    for row in _list(public_source_change_impact_rehearsal_v1.get("impact_rows")):
        if not isinstance(row, Mapping):
            continue
        source_id = _text(row.get("source_id"))
        candidate = _candidate(candidates_by_source, source_id, _first_public_url(row.get("citations")))
        candidate["candidate_sources"].append("public_source_change_impact_rehearsal_v1")
        candidate["refresh_reasons"].append(_text(row.get("impact_summary"), "change_impact_rehearsal_refresh_candidate"))
        candidate["affected_requirement_ids"].extend(_text_list(row.get("affected_requirement_ids")))
        candidate["affected_process_ids"].extend(_text_list(row.get("affected_process_ids")))
        candidate["affected_guardrail_bundle_ids"].extend(_text_list(row.get("affected_guardrail_bundle_ids")))
        for citation in _list(row.get("citations")):
            if not isinstance(citation, Mapping):
                continue
            citations_by_source.setdefault(source_id, []).append(
                {
                    "citation_type": "public_source_change_impact_rehearsal",
                    "source_id": source_id,
                    "public_url": _text(citation.get("public_url")),
                    "citation_refs": [_text(citation.get("span_ref"), "public_source_change_impact_rehearsal_v1")],
                    "requirement_id": _text(citation.get("requirement_id")),
                    "basis": _text(citation.get("quoted_or_paraphrased_basis"), "change impact rehearsal citation"),
                }
            )

    refresh_candidates = []
    freshness_priority_rows = []
    reviewer_owner_assignments = []
    affected = {
        "requirement_ids": set(),
        "process_ids": set(),
        "guardrail_bundle_ids": set(),
    }

    for source_id in sorted(candidates_by_source):
        candidate = candidates_by_source[source_id]
        candidate["candidate_sources"] = sorted(set(candidate["candidate_sources"]))
        candidate["refresh_reasons"] = sorted(set(filter(None, candidate["refresh_reasons"])))
        candidate["affected_requirement_ids"] = sorted(set(candidate["affected_requirement_ids"]))
        candidate["affected_process_ids"] = sorted(set(candidate["affected_process_ids"]))
        candidate["affected_guardrail_bundle_ids"] = sorted(set(candidate["affected_guardrail_bundle_ids"]))
        candidate["rollback_note_refs"] = sorted(set(filter(None, candidate["rollback_note_refs"])))
        candidate["citations"] = _dedupe_citations(citations_by_source.get(source_id, []))
        candidate["priority_band"] = _priority_band(candidate)
        refresh_candidates.append(candidate)
        affected["requirement_ids"].update(candidate["affected_requirement_ids"])
        affected["process_ids"].update(candidate["affected_process_ids"])
        affected["guardrail_bundle_ids"].update(candidate["affected_guardrail_bundle_ids"])
        freshness_priority_rows.append(
            {
                "source_id": source_id,
                "canonical_url": candidate["canonical_url"],
                "priority_band": candidate["priority_band"],
                "freshness_status": candidate["freshness_status"],
                "reason_count": len(candidate["refresh_reasons"]),
                "affected_requirement_count": len(candidate["affected_requirement_ids"]),
                "reviewer_owner": candidate["reviewer_owner"],
            }
        )
        reviewer_owner_assignments.append(
            {
                "source_id": source_id,
                "reviewer_owner": candidate["reviewer_owner"],
                "assignment_reason": "Review fixture refresh candidate before any live crawl or active artifact mutation.",
            }
        )

    rollback_notes = _rollback_notes(
        public_source_refresh_intake_evidence_packet_v1,
        official_source_anchor_audit_packet,
    )
    offline_validation_commands = _offline_validation_commands(
        official_source_anchor_audit_packet,
        source_to_requirement_traceability_packet_v1,
    )

    packet = {
        "packet_type": PACKET_TYPE,
        "packet_version": PACKET_VERSION,
        "packet_id": packet_id,
        "generated_at": generated_at,
        "fixture_first": True,
        "metadata_only": True,
        "live_network_invoked": False,
        "processor_invoked": False,
        "raw_bodies_persisted": False,
        "raw_downloaded_content_committed": False,
        "source_registry_mutated": False,
        "requirement_registry_mutated": False,
        "process_registry_mutated": False,
        "guardrail_registry_mutated": False,
        "input_packet_refs": {
            "official_source_anchor_audit_packet": _text(official_source_anchor_audit_packet.get("packet_id") or official_source_anchor_audit_packet.get("schema_version")),
            "public_source_refresh_intake_evidence_packet_v1": _text(public_source_refresh_intake_evidence_packet_v1.get("packet_id")),
            "source_to_requirement_traceability_packet_v1": _text(source_to_requirement_traceability_packet_v1.get("packet_id") or source_to_requirement_traceability_packet_v1.get("schema_version")),
            "public_source_change_impact_rehearsal_v1": _text(public_source_change_impact_rehearsal_v1.get("packet_id")),
        },
        "refresh_candidates": refresh_candidates,
        "freshness_priority_rows": freshness_priority_rows,
        "affected_ids": {
            "requirement_ids": sorted(affected["requirement_ids"]),
            "process_ids": sorted(affected["process_ids"]),
            "guardrail_bundle_ids": sorted(affected["guardrail_bundle_ids"]),
        },
        "offline_validation_commands": offline_validation_commands,
        "reviewer_owner_assignments": reviewer_owner_assignments,
        "rollback_notes": rollback_notes,
        "side_effect_boundary": {
            "network_io_allowed": False,
            "processor_invocation_allowed": False,
            "downloads_allowed": False,
            "raw_body_persistence_allowed": False,
            "source_registry_mutation_allowed": False,
            "requirement_mutation_allowed": False,
            "process_mutation_allowed": False,
            "guardrail_mutation_allowed": False,
        },
        "plan_summary": {
            "refresh_candidate_count": len(refresh_candidates),
            "freshness_priority_row_count": len(freshness_priority_rows),
            "reviewer_owner_assignment_count": len(reviewer_owner_assignments),
            "rollback_note_count": len(rollback_notes),
        },
    }
    require_valid_public_source_refresh_plan_v2(packet)
    return packet


def validate_public_source_refresh_plan_v2(packet: Mapping[str, Any]) -> PublicSourceRefreshPlanV2ValidationResult:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return PublicSourceRefreshPlanV2ValidationResult(False, ("packet must be an object",))
    _collect_forbidden_content(packet, "$", errors)
    if packet.get("packet_type") != PACKET_TYPE:
        errors.append("packet_type must be " + PACKET_TYPE)
    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be " + PACKET_VERSION)
    if not _text(packet.get("packet_id")):
        errors.append("packet_id is required")
    if not _text(packet.get("generated_at")).endswith("Z"):
        errors.append("generated_at must end in Z")
    for key in ("fixture_first", "metadata_only"):
        if packet.get(key) is not True:
            errors.append(key + " must be true")
    for key in (
        "live_network_invoked",
        "processor_invoked",
        "raw_bodies_persisted",
        "raw_downloaded_content_committed",
        "source_registry_mutated",
        "requirement_registry_mutated",
        "process_registry_mutated",
        "guardrail_registry_mutated",
    ):
        if packet.get(key) is not False:
            errors.append(key + " must be false")
    boundary = packet.get("side_effect_boundary")
    if not isinstance(boundary, Mapping):
        errors.append("side_effect_boundary must be an object")
    else:
        for key, value in boundary.items():
            if value is not False:
                errors.append("side_effect_boundary." + str(key) + " must be false")
    candidates = _require_list(packet.get("refresh_candidates"), "refresh_candidates", errors)
    priority_rows = _require_list(packet.get("freshness_priority_rows"), "freshness_priority_rows", errors)
    assignments = _require_list(packet.get("reviewer_owner_assignments"), "reviewer_owner_assignments", errors)
    rollback_notes = _require_list(packet.get("rollback_notes"), "rollback_notes", errors)
    commands = _require_list(packet.get("offline_validation_commands"), "offline_validation_commands", errors)
    if not candidates:
        errors.append("refresh_candidates must include at least one row")
    if len(priority_rows) != len(candidates):
        errors.append("freshness_priority_rows must match refresh_candidates count")
    if len(assignments) != len(candidates):
        errors.append("reviewer_owner_assignments must match refresh_candidates count")
    if not rollback_notes:
        errors.append("rollback_notes must not be empty")
    if not commands or not all(_text(command) for command in commands):
        errors.append("offline_validation_commands must include non-empty commands")
    affected_ids = packet.get("affected_ids")
    if not isinstance(affected_ids, Mapping):
        errors.append("affected_ids must be an object")
        affected_requirement_ids: set[str] = set()
        affected_process_ids: set[str] = set()
        affected_guardrail_ids: set[str] = set()
    else:
        affected_requirement_ids = set(_text_list(affected_ids.get("requirement_ids")))
        affected_process_ids = set(_text_list(affected_ids.get("process_ids")))
        affected_guardrail_ids = set(_text_list(affected_ids.get("guardrail_bundle_ids")))
    candidate_sources: set[str] = set()
    for index, row in enumerate(candidates):
        prefix = "refresh_candidates[" + str(index) + "]"
        if not isinstance(row, Mapping):
            errors.append(prefix + " must be an object")
            continue
        source_id = _text(row.get("source_id"))
        candidate_sources.add(source_id)
        for key in ("candidate_id", "source_id", "canonical_url", "priority_band", "reviewer_owner"):
            if not _text(row.get(key)):
                errors.append(prefix + "." + key + " is required")
        if not _text_list(row.get("candidate_sources")):
            errors.append(prefix + ".candidate_sources must not be empty")
        if not _text_list(row.get("refresh_reasons")):
            errors.append(prefix + ".refresh_reasons must not be empty")
        citations = _require_list(row.get("citations"), prefix + ".citations", errors)
        if not citations:
            errors.append(prefix + ".citations must include at least one cited source")
        for citation_index, citation in enumerate(citations):
            citation_prefix = prefix + ".citations[" + str(citation_index) + "]"
            if not isinstance(citation, Mapping):
                errors.append(citation_prefix + " must be an object")
                continue
            for key in ("citation_type", "source_id", "public_url", "basis"):
                if not _text(citation.get(key)):
                    errors.append(citation_prefix + "." + key + " is required")
            if _text(citation.get("source_id")) != source_id:
                errors.append(citation_prefix + ".source_id must match candidate source_id")
        for requirement_id in _text_list(row.get("affected_requirement_ids")):
            if requirement_id not in affected_requirement_ids:
                errors.append(prefix + ".affected_requirement_ids not represented in affected_ids: " + requirement_id)
        for process_id in _text_list(row.get("affected_process_ids")):
            if process_id not in affected_process_ids:
                errors.append(prefix + ".affected_process_ids not represented in affected_ids: " + process_id)
        for guardrail_id in _text_list(row.get("affected_guardrail_bundle_ids")):
            if guardrail_id not in affected_guardrail_ids:
                errors.append(prefix + ".affected_guardrail_bundle_ids not represented in affected_ids: " + guardrail_id)
    for index, row in enumerate(priority_rows):
        prefix = "freshness_priority_rows[" + str(index) + "]"
        if not isinstance(row, Mapping):
            errors.append(prefix + " must be an object")
            continue
        if _text(row.get("source_id")) not in candidate_sources:
            errors.append(prefix + ".source_id must reference a refresh candidate")
        if _text(row.get("priority_band")) not in {"high", "medium", "low"}:
            errors.append(prefix + ".priority_band must be high, medium, or low")
    for index, row in enumerate(assignments):
        prefix = "reviewer_owner_assignments[" + str(index) + "]"
        if not isinstance(row, Mapping):
            errors.append(prefix + " must be an object")
            continue
        if _text(row.get("source_id")) not in candidate_sources:
            errors.append(prefix + ".source_id must reference a refresh candidate")
        if not _text(row.get("reviewer_owner")):
            errors.append(prefix + ".reviewer_owner is required")
    summary = packet.get("plan_summary")
    if not isinstance(summary, Mapping):
        errors.append("plan_summary must be an object")
    else:
        expected = {
            "refresh_candidate_count": len(candidates),
            "freshness_priority_row_count": len(priority_rows),
            "reviewer_owner_assignment_count": len(assignments),
            "rollback_note_count": len(rollback_notes),
        }
        for key, value in expected.items():
            if summary.get(key) != value:
                errors.append("plan_summary." + key + " must be " + str(value))
    return PublicSourceRefreshPlanV2ValidationResult(not errors, tuple(dict.fromkeys(errors)))


def require_valid_public_source_refresh_plan_v2(packet: Mapping[str, Any]) -> None:
    result = validate_public_source_refresh_plan_v2(packet)
    if not result.valid:
        raise PublicSourceRefreshPlanV2Error("; ".join(result.errors))


def _candidate(candidates_by_source: dict[str, dict[str, Any]], source_id: str, canonical_url: str) -> dict[str, Any]:
    source = _text(source_id, _source_id_from_url(canonical_url))
    if source not in candidates_by_source:
        candidates_by_source[source] = {
            "candidate_id": "refresh-candidate-" + _stable_token(source),
            "source_id": source,
            "canonical_url": canonical_url,
            "candidate_sources": [],
            "refresh_reasons": [],
            "freshness_status": "unknown",
            "policy_status": {},
            "metadata_expectations": {},
            "affected_requirement_ids": [],
            "affected_process_ids": [],
            "affected_guardrail_bundle_ids": [],
            "citations": [],
            "reviewer_owner": DEFAULT_REVIEWER_OWNER,
            "rollback_note_refs": [],
        }
    elif canonical_url and not candidates_by_source[source].get("canonical_url"):
        candidates_by_source[source]["canonical_url"] = canonical_url
    return candidates_by_source[source]


def _traceability_rows(packet: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    for key in ("traceability_rows", "source_to_requirement_rows", "rows", "traces"):
        rows = packet.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, Mapping)]
    return []


def _priority_band(candidate: Mapping[str, Any]) -> str:
    status = _text(candidate.get("freshness_status")).lower()
    reasons = " ".join(_text_list(candidate.get("refresh_reasons"))).lower()
    if status in {"missing", "stale", "unknown", "synthetic_unverified", "fixture_seed_pending_first_crawl"}:
        return "high"
    if "policy" in reasons or "impact" in reasons or _text_list(candidate.get("affected_requirement_ids")):
        return "medium"
    return "low"


def _offline_validation_commands(*packets: Mapping[str, Any]) -> list[str]:
    commands: list[str] = []
    for packet in packets:
        commands.extend(_text_list(packet.get("offline_validation_commands")))
    commands.extend(DEFAULT_VALIDATION_COMMANDS)
    return sorted(set(commands))


def _rollback_notes(intake_packet: Mapping[str, Any], anchor_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    notes = []
    for row in _list(intake_packet.get("rollback_notes")):
        if isinstance(row, Mapping):
            notes.append(
                {
                    "rollback_note_id": _text(row.get("rollback_note_id"), "intake-rollback-note"),
                    "scope": _text(row.get("scope"), "refresh_plan"),
                    "rollback_required": False,
                    "reason": _text(row.get("reason"), "Fixture-only intake evidence can be discarded without active state changes."),
                }
            )
    anchor_note = _text(anchor_packet.get("rollback_note"))
    if anchor_note:
        notes.append(
            {
                "rollback_note_id": "official-anchor-audit-rollback-note",
                "scope": "official_source_anchor_audit",
                "rollback_required": False,
                "reason": anchor_note,
            }
        )
    notes.append(
        {
            "rollback_note_id": "refresh-plan-v2-discard-only",
            "scope": "public_source_refresh_plan_v2",
            "rollback_required": False,
            "reason": "Discard this fixture plan before any live crawl; no registry, requirement, process, guardrail, download, or processor artifact was changed.",
        }
    )
    seen: set[str] = set()
    unique = []
    for note in notes:
        note_id = note["rollback_note_id"]
        if note_id not in seen:
            unique.append(note)
            seen.add(note_id)
    return unique


def _dedupe_citations(citations: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    result: list[dict[str, Any]] = []
    for citation in citations:
        public_url = _text(citation.get("public_url"))
        source_id = _text(citation.get("source_id"))
        citation_type = _text(citation.get("citation_type"))
        key = (citation_type, source_id, public_url)
        if key in seen:
            continue
        seen.add(key)
        result.append(dict(citation))
    return result


def _first_public_url(citations: Any) -> str:
    for row in _list(citations):
        if isinstance(row, Mapping) and _text(row.get("public_url")):
            return _text(row.get("public_url"))
    return ""


def _collect_forbidden_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            if _normalized_key(key_text) in _FORBIDDEN_TRUE_KEYS and child not in (None, "", [], {}, False):
                errors.append(path + "." + key_text + " must be false or empty in refresh plan v2")
            _collect_forbidden_content(child, path + "." + key_text, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _collect_forbidden_content(child, path + "[" + str(index) + "]", errors)
    elif isinstance(value, str):
        lowered = value.lower()
        for marker in _FORBIDDEN_VALUE_MARKERS:
            if marker in lowered:
                errors.append(path + " contains forbidden private, raw, download, processor output, or authenticated marker " + marker)


def _require_mapping(value: Any, name: str) -> None:
    if not isinstance(value, Mapping):
        raise TypeError(name + " must be an object")


def _require_list(value: Any, field: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(field + " must be a list")
        return []
    return value


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_text(row) for row in value if _text(row)]
    return []


def _text(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else default
    return default


def _source_id_from_url(url: str) -> str:
    token = _stable_token(url.replace("https://", "").replace("http://", ""))
    return token or "unknown-source"


def _stable_token(value: str) -> str:
    chars = [character if character.isalnum() else "-" for character in value.lower()]
    return "-".join(part for part in "".join(chars).split("-") if part) or "unknown"


def _normalized_key(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


__all__ = [
    "PACKET_TYPE",
    "PACKET_VERSION",
    "PublicSourceRefreshPlanV2Error",
    "PublicSourceRefreshPlanV2ValidationResult",
    "build_public_source_refresh_plan_v2",
    "require_valid_public_source_refresh_plan_v2",
    "validate_public_source_refresh_plan_v2",
]
