"""Fixture-first requirement regeneration work-order v2 packets.

This module consumes already-materialized fixture dictionaries. It does not fetch
sources, invoke crawlers or processors, run requirement extraction, call LLMs, use
DevHub, guarantee legal or permitting outcomes, or mutate active PP&D state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


PACKET_TYPE = "ppd.requirement_regeneration_work_order_v2"
ALLOWED_DECISIONS = {"unchanged", "review", "regenerate"}
DEFAULT_VALIDATION_COMMANDS = [
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ["python3", "-m", "pytest", "ppd/tests/test_requirement_regeneration_work_order_v2.py"],
]
REQUIRED_ATTESTATIONS = {
    "no_live_extraction": True,
    "no_crawler_invocation": True,
    "no_processor_invocation": True,
    "no_devhub_invocation": True,
    "no_llm_invocation": True,
    "no_requirement_mutation": True,
    "no_process_mutation": True,
    "no_guardrail_mutation": True,
    "no_prompt_mutation": True,
    "no_source_mutation": True,
    "no_schedule_mutation": True,
    "no_monitoring_mutation": True,
    "no_release_state_mutation": True,
    "no_agent_state_mutation": True,
    "no_outcome_guarantees": True,
}
FORBIDDEN_TRUE_KEY_PARTS = (
    "live_extraction",
    "live_crawl",
    "live_crawler",
    "crawler_invocation",
    "crawler_invoked",
    "processor_invocation",
    "processor_invoked",
    "devhub_invocation",
    "devhub_invoked",
    "llm_invocation",
    "llm_invoked",
    "requirement_mutation",
    "process_mutation",
    "guardrail_mutation",
    "prompt_mutation",
    "source_mutation",
    "schedule_mutation",
    "monitoring_mutation",
    "release_state_mutation",
    "agent_state_mutation",
    "mutates_requirement",
    "mutates_process",
    "mutates_guardrail",
    "mutates_prompt",
    "mutates_source",
    "mutates_schedule",
    "mutates_monitoring",
    "mutates_release_state",
    "mutates_agent_state",
    "active_requirement",
    "active_process",
    "active_guardrail",
    "active_prompt",
    "active_source",
    "active_schedule",
    "active_monitoring",
    "active_release_state",
    "active_agent_state",
)
FORBIDDEN_PATH_PARTS = (
    "authenticated_fact",
    "auth_fact",
    "auth_state",
    "browser_state",
    "cookie",
    "credential",
    "password",
    "payment_detail",
    "private_case",
    "private_fact",
    "private_file",
    "private_path",
    "private_value",
    "raw_body",
    "raw_crawl",
    "raw_html",
    "raw_pdf",
    "session_state",
    "token",
)
FORBIDDEN_TEXT = (
    "live extraction",
    "live crawl",
    "live crawler",
    "crawler executed",
    "crawler invoked",
    "processor executed",
    "processor invoked",
    "processor ran",
    "ran processor",
    "devhub executed",
    "devhub invoked",
    "llm executed",
    "llm invoked",
    "llm ran",
    "raw crawl",
    "raw body",
    "raw html",
    "raw pdf",
    "pdf body",
    "downloaded document",
    "file://",
    ".warc",
    ".har",
    "trace.zip",
    "private fact",
    "authenticated fact",
    "credential",
    "cookie",
    "password",
    "payment detail",
    "guaranteed approval",
    "approval guaranteed",
    "will be approved",
    "permit will be issued",
    "permit will be approved",
    "legal outcome guaranteed",
    "permitting outcome guaranteed",
    "legally sufficient",
    "compliance guaranteed",
    "outcome guaranteed",
    "guarantees approval",
    "guarantee approval",
    "automatic approval",
)


@dataclass(frozen=True)
class RequirementRegenerationWorkOrderV2Issue:
    code: str
    path: str
    message: str


class RequirementRegenerationWorkOrderV2Error(ValueError):
    def __init__(self, issues: Sequence[RequirementRegenerationWorkOrderV2Issue]) -> None:
        self.issues = tuple(issues)
        detail = "; ".join(f"{issue.code} at {issue.path}: {issue.message}" for issue in self.issues)
        super().__init__(detail)


def build_requirement_regeneration_work_order_v2(packet_input: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic offline regeneration work-order v2 packet."""

    input_issues = _safety_issues(packet_input)
    if input_issues:
        raise RequirementRegenerationWorkOrderV2Error(input_issues)

    triage = _mapping(packet_input.get("source_freshness_drift_triage_v2"))
    rerun_queues = list(_mapping_sequence(packet_input.get("prior_requirement_rerun_work_queues")))
    extraction_fixtures = list(_mapping_sequence(packet_input.get("requirement_extraction_fixtures")))
    if not triage or not rerun_queues or not extraction_fixtures:
        raise RequirementRegenerationWorkOrderV2Error([
            RequirementRegenerationWorkOrderV2Issue(
                "missing_prerequisite_packets",
                "$",
                "source freshness drift triage v2, prior rerun queues, and extraction fixtures are required",
            )
        ])

    classifications = list(_mapping_sequence(triage.get("classifications")))
    classifications_by_requirement = _classifications_by_requirement(classifications)
    queued_requirement_decisions = _queued_decisions(
        extraction_fixtures,
        rerun_queues,
        classifications_by_requirement,
    )
    work_order = {
        "packet_type": PACKET_TYPE,
        "packet_id": str(packet_input.get("packet_id") or "fixture-requirement-regeneration-work-order-v2"),
        "fixture_only": True,
        "source_packets": {
            "source_freshness_drift_triage_v2": str(triage.get("packet_id") or "source-freshness-drift-triage-v2-fixture"),
            "prior_requirement_rerun_work_queues": [str(queue.get("packet_id") or queue.get("plan_id") or "requirement-rerun-work-queue-fixture") for queue in rerun_queues],
            "requirement_extraction_fixture_ids": [str(item.get("fixture_id") or item.get("extraction_fixture_id") or item.get("requirement_id")) for item in extraction_fixtures],
        },
        "queued_requirement_decisions": queued_requirement_decisions,
        "source_evidence_expectations": _source_evidence_expectations(queued_requirement_decisions),
        "reviewer_owner_fields": _reviewer_owner_fields(queued_requirement_decisions),
        "offline_validation_commands": [list(command) for command in DEFAULT_VALIDATION_COMMANDS],
        "attestations": dict(REQUIRED_ATTESTATIONS),
    }
    issues = validate_requirement_regeneration_work_order_v2(work_order)
    if issues:
        raise RequirementRegenerationWorkOrderV2Error(issues)
    return work_order


def validate_requirement_regeneration_work_order_v2(packet: Mapping[str, Any]) -> list[RequirementRegenerationWorkOrderV2Issue]:
    """Return deterministic validation issues for a work-order v2 packet."""

    issues: list[RequirementRegenerationWorkOrderV2Issue] = []
    if not isinstance(packet, Mapping):
        return [RequirementRegenerationWorkOrderV2Issue("invalid_packet", "$", "packet must be an object")]
    issues.extend(_safety_issues(packet))

    if packet.get("packet_type") != PACKET_TYPE:
        issues.append(RequirementRegenerationWorkOrderV2Issue("invalid_packet_type", "$.packet_type", "unexpected packet type"))
    if packet.get("fixture_only") is not True:
        issues.append(RequirementRegenerationWorkOrderV2Issue("not_fixture_only", "$.fixture_only", "work order must be fixture only"))

    source_packets = _mapping(packet.get("source_packets"))
    if not source_packets.get("source_freshness_drift_triage_v2"):
        issues.append(RequirementRegenerationWorkOrderV2Issue("missing_source_triage_ref", "$.source_packets.source_freshness_drift_triage_v2", "triage packet reference is required"))
    if not _strings(source_packets.get("prior_requirement_rerun_work_queues")):
        issues.append(RequirementRegenerationWorkOrderV2Issue("missing_rerun_queue_refs", "$.source_packets.prior_requirement_rerun_work_queues", "prior rerun queue references are required"))
    if not _strings(source_packets.get("requirement_extraction_fixture_ids")):
        issues.append(RequirementRegenerationWorkOrderV2Issue("missing_extraction_fixture_refs", "$.source_packets.requirement_extraction_fixture_ids", "extraction fixture references are required"))

    decisions = list(_mapping_sequence(packet.get("queued_requirement_decisions")))
    if not decisions:
        issues.append(RequirementRegenerationWorkOrderV2Issue("missing_queued_requirement_decisions", "$.queued_requirement_decisions", "queued decisions are required"))
    seen_decisions = set()
    for index, decision in enumerate(decisions):
        path = f"$.queued_requirement_decisions[{index}]"
        requirement_id = _text(decision.get("requirement_id"))
        decision_value = _text(decision.get("decision"))
        seen_decisions.add(decision_value)
        if not requirement_id:
            issues.append(RequirementRegenerationWorkOrderV2Issue("missing_requirement_id", path + ".requirement_id", "requirement ID is required"))
        if decision_value not in ALLOWED_DECISIONS:
            issues.append(RequirementRegenerationWorkOrderV2Issue("invalid_decision", path + ".decision", "decision must be unchanged, review, or regenerate"))
        if not _strings(decision.get("source_evidence_ids")):
            issues.append(RequirementRegenerationWorkOrderV2Issue("uncited_requirement_decision", path + ".source_evidence_ids", "decision must cite source evidence"))
        if not _strings(decision.get("source_evidence_expectations")):
            issues.append(RequirementRegenerationWorkOrderV2Issue("missing_source_evidence_expectations", path + ".source_evidence_expectations", "source evidence expectations are required"))
        if not _text(decision.get("reviewer_owner")):
            issues.append(RequirementRegenerationWorkOrderV2Issue("missing_reviewer_owner", path + ".reviewer_owner", "reviewer owner is required"))
        for key in (
            "live_extraction_allowed",
            "crawler_invocation_allowed",
            "processor_invocation_allowed",
            "devhub_invocation_allowed",
            "llm_invocation_allowed",
            "requirement_mutation_allowed",
            "process_mutation_allowed",
            "guardrail_mutation_allowed",
            "prompt_mutation_allowed",
            "source_mutation_allowed",
            "schedule_mutation_allowed",
            "monitoring_mutation_allowed",
            "release_state_mutation_allowed",
            "agent_state_mutation_allowed",
        ):
            if decision.get(key, False) is not False:
                issues.append(RequirementRegenerationWorkOrderV2Issue("forbidden_live_or_mutating_claim", path + "." + key, "live execution and active mutations must be blocked"))
    if decisions and not {"unchanged", "review", "regenerate"}.issubset(seen_decisions):
        issues.append(RequirementRegenerationWorkOrderV2Issue("missing_decision_coverage", "$.queued_requirement_decisions", "work order must cover unchanged, review, and regenerate decisions"))

    expectation_rows = list(_mapping_sequence(packet.get("source_evidence_expectations")))
    if not expectation_rows:
        issues.append(RequirementRegenerationWorkOrderV2Issue("missing_source_evidence_expectation_rows", "$.source_evidence_expectations", "source evidence expectation rows are required"))
    for index, row in enumerate(expectation_rows):
        path = f"$.source_evidence_expectations[{index}]"
        if not _text(row.get("requirement_id")):
            issues.append(RequirementRegenerationWorkOrderV2Issue("missing_requirement_id", path + ".requirement_id", "requirement ID is required"))
        if not _strings(row.get("expected_source_evidence_ids")):
            issues.append(RequirementRegenerationWorkOrderV2Issue("uncited_requirement_decision", path + ".expected_source_evidence_ids", "expectation row must cite source evidence"))
        if not _strings(row.get("expectations")):
            issues.append(RequirementRegenerationWorkOrderV2Issue("missing_source_evidence_expectations", path + ".expectations", "source evidence expectations are required"))
        if not _text(row.get("reviewer_owner")):
            issues.append(RequirementRegenerationWorkOrderV2Issue("missing_reviewer_owner", path + ".reviewer_owner", "reviewer owner is required"))

    owner_rows = list(_mapping_sequence(packet.get("reviewer_owner_fields")))
    if not owner_rows:
        issues.append(RequirementRegenerationWorkOrderV2Issue("missing_reviewer_owner_fields", "$.reviewer_owner_fields", "reviewer owner fields are required"))
    for index, row in enumerate(owner_rows):
        path = f"$.reviewer_owner_fields[{index}]"
        if not _text(row.get("requirement_id")):
            issues.append(RequirementRegenerationWorkOrderV2Issue("missing_requirement_id", path + ".requirement_id", "requirement ID is required"))
        if not _text(row.get("reviewer_owner")):
            issues.append(RequirementRegenerationWorkOrderV2Issue("missing_reviewer_owner", path + ".reviewer_owner", "reviewer owner is required"))
        if row.get("owner_must_confirm_citations_before_regeneration") is not True:
            issues.append(RequirementRegenerationWorkOrderV2Issue("missing_source_evidence_expectations", path + ".owner_must_confirm_citations_before_regeneration", "reviewer owner must confirm citations before regeneration"))

    commands = packet.get("offline_validation_commands")
    if not isinstance(commands, list) or not commands:
        issues.append(RequirementRegenerationWorkOrderV2Issue("missing_offline_validation_commands", "$.offline_validation_commands", "offline validation commands are required"))
    else:
        for index, command in enumerate(commands):
            if not _strings(command):
                issues.append(RequirementRegenerationWorkOrderV2Issue("invalid_validation_command", f"$.offline_validation_commands[{index}]", "validation command must be a list of strings"))

    attestations = _mapping(packet.get("attestations"))
    for key, expected in REQUIRED_ATTESTATIONS.items():
        if attestations.get(key) is not expected:
            issues.append(RequirementRegenerationWorkOrderV2Issue("missing_attestation", f"$.attestations.{key}", "required no-live/no-mutation/no-guarantee attestation is missing"))
    return issues


def assert_valid_requirement_regeneration_work_order_v2(packet: Mapping[str, Any]) -> None:
    issues = validate_requirement_regeneration_work_order_v2(packet)
    if issues:
        raise RequirementRegenerationWorkOrderV2Error(issues)


def _queued_decisions(
    extraction_fixtures: Sequence[Mapping[str, Any]],
    rerun_queues: Sequence[Mapping[str, Any]],
    classifications_by_requirement: Mapping[str, list[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    queued_ids = set(_queued_requirement_ids(rerun_queues))
    rows: list[dict[str, Any]] = []
    for fixture in extraction_fixtures:
        requirement_id = _text(fixture.get("requirement_id"))
        if not requirement_id:
            continue
        classifications = classifications_by_requirement.get(requirement_id, [])
        decision = _decision(requirement_id, queued_ids, classifications)
        source_evidence_ids = _ordered_unique(
            _strings(fixture.get("source_evidence_ids"))
            + _strings(fixture.get("citation_ids"))
            + _classification_citations(classifications)
        )
        rows.append(
            {
                "queue_item_id": "requirement-regeneration-v2." + _slug(requirement_id),
                "requirement_id": requirement_id,
                "decision": decision,
                "source_id": _text(fixture.get("source_id")),
                "source_evidence_ids": source_evidence_ids,
                "source_evidence_expectations": _strings(fixture.get("source_evidence_expectations")) or [
                    "confirm cited fixture evidence still supports the requirement decision"
                ],
                "reviewer_owner": _owner(fixture, classifications),
                "prior_rerun_queue_refs": _queue_refs_for_requirement(rerun_queues, requirement_id),
                "triage_classification_refs": [_text(item.get("classification_id")) or _text(item.get("classification")) for item in classifications],
                "live_extraction_allowed": False,
                "crawler_invocation_allowed": False,
                "processor_invocation_allowed": False,
                "devhub_invocation_allowed": False,
                "llm_invocation_allowed": False,
                "requirement_mutation_allowed": False,
                "process_mutation_allowed": False,
                "guardrail_mutation_allowed": False,
                "prompt_mutation_allowed": False,
                "source_mutation_allowed": False,
                "schedule_mutation_allowed": False,
                "monitoring_mutation_allowed": False,
                "release_state_mutation_allowed": False,
                "agent_state_mutation_allowed": False,
            }
        )
    return sorted(rows, key=lambda row: row["requirement_id"])


def _decision(requirement_id: str, queued_ids: set[str], classifications: Sequence[Mapping[str, Any]]) -> str:
    labels = {_text(item.get("classification")).lower() for item in classifications}
    recommended = {_text(item.get("recommended_disposition")).lower() for item in classifications}
    joined = " ".join(sorted(labels | recommended))
    if "changed" in joined or "regenerate" in joined:
        return "regenerate"
    if "stale" in joined or "review" in joined or requirement_id in queued_ids:
        return "review"
    return "unchanged"


def _source_evidence_expectations(decisions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for decision in decisions:
        rows.append(
            {
                "requirement_id": decision["requirement_id"],
                "decision": decision["decision"],
                "expected_source_evidence_ids": list(decision["source_evidence_ids"]),
                "expectations": list(decision["source_evidence_expectations"]),
                "reviewer_owner": decision["reviewer_owner"],
            }
        )
    return rows


def _reviewer_owner_fields(decisions: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for decision in decisions:
        rows.append(
            {
                "requirement_id": decision["requirement_id"],
                "reviewer_owner": decision["reviewer_owner"],
                "decision_owner_scope": decision["decision"],
                "owner_must_confirm_citations_before_regeneration": True,
            }
        )
    return rows


def _classifications_by_requirement(classifications: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    indexed: dict[str, list[Mapping[str, Any]]] = {}
    for item in classifications:
        requirement_ids = _strings(item.get("affected_requirement_ids"))
        for artifact_id in _strings(item.get("affected_artifact_ids")):
            if artifact_id.startswith("requirement:"):
                requirement_ids.append(artifact_id.split(":", 1)[1])
        for requirement_id in _ordered_unique(requirement_ids):
            indexed.setdefault(requirement_id, []).append(item)
    return indexed


def _queued_requirement_ids(rerun_queues: Sequence[Mapping[str, Any]]) -> list[str]:
    values: list[str] = []
    for queue in rerun_queues:
        values.extend(_strings(queue.get("cited_requirement_ids")))
        for item in _mapping_sequence(queue.get("work_items")):
            values.extend(_strings(item.get("requirement_ids")))
            requirement_id = _text(item.get("requirement_id"))
            if requirement_id:
                values.append(requirement_id)
    return _ordered_unique(values)


def _queue_refs_for_requirement(rerun_queues: Sequence[Mapping[str, Any]], requirement_id: str) -> list[str]:
    refs: list[str] = []
    for queue in rerun_queues:
        queue_id = _text(queue.get("packet_id")) or _text(queue.get("plan_id"))
        if requirement_id in _strings(queue.get("cited_requirement_ids")) and queue_id:
            refs.append(queue_id)
        for item in _mapping_sequence(queue.get("work_items")):
            if requirement_id == _text(item.get("requirement_id")) or requirement_id in _strings(item.get("requirement_ids")):
                refs.append(_text(item.get("work_item_id")) or queue_id)
    return _ordered_unique(refs)


def _classification_citations(classifications: Sequence[Mapping[str, Any]]) -> list[str]:
    values: list[str] = []
    for item in classifications:
        values.extend(_strings(item.get("source_evidence_ids")))
        for citation in _mapping_sequence(item.get("citations")):
            values.extend(_strings(citation.get("source_id")))
            values.extend(_strings(citation.get("evidence_id")))
            values.extend(_strings(citation.get("id")))
    return values


def _owner(fixture: Mapping[str, Any], classifications: Sequence[Mapping[str, Any]]) -> str:
    for key in ("reviewer_owner", "owner", "assigned_reviewer"):
        value = _text(fixture.get(key))
        if value:
            return value
    for item in classifications:
        value = _text(item.get("escalation_owner"))
        if value:
            return value
    return "ppd-requirement-reviewer"


def _safety_issues(value: Any) -> list[RequirementRegenerationWorkOrderV2Issue]:
    issues: list[RequirementRegenerationWorkOrderV2Issue] = []
    for path, item in _walk(value):
        normalized_path = path.lower().replace("-", "_")
        if any(part in normalized_path for part in FORBIDDEN_PATH_PARTS):
            issues.append(RequirementRegenerationWorkOrderV2Issue("forbidden_private_raw_or_live_reference", path, "private facts, raw artifacts, downloads, and live execution claims are forbidden"))
        if isinstance(item, bool) and item and any(part in normalized_path for part in FORBIDDEN_TRUE_KEY_PARTS):
            issues.append(RequirementRegenerationWorkOrderV2Issue("forbidden_live_or_mutating_claim", path, "live execution and active mutations must be blocked"))
        if isinstance(item, str):
            normalized_value = item.lower()
            if any(token in normalized_value for token in FORBIDDEN_TEXT):
                issues.append(RequirementRegenerationWorkOrderV2Issue("forbidden_private_raw_or_live_reference", path, "private facts, raw artifacts, downloads, live execution claims, and outcome guarantees are forbidden"))
    return issues


def _walk(value: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk(child, path + "." + str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, path + "[" + str(index) + "]")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        values: list[str] = []
        for item in value:
            values.extend(_strings(item))
        return values
    return []


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _ordered_unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = value.strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _slug(value: str) -> str:
    return "".join(character.lower() if character.isalnum() else "-" for character in value).strip("-")
