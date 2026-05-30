"""Fixture-first promotion acceptance packet v4.

This packet consumes already committed fixture producers only: public freshness
scheduler rehearsal v4, reversible draft preview handoff packet v4, guardrail
fixtures, and process model fixtures. It produces reviewer-ready acceptance
criteria without crawling, opening DevHub, reading private artifacts, executing
official actions, or mutating active state.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from ppd.draft_preview_agent_handoff_packet_v4 import build_packet_from_paths as build_draft_handoff_packet_from_paths
from ppd.public_freshness_scheduler_rehearsal_v4 import build_rehearsal, load_json as load_scheduler_json


PACKET_VERSION = "promotion-acceptance-packet-v4"
DEFAULT_MANIFEST_PATH = Path(__file__).parent / "tests" / "fixtures" / "promotion_acceptance_packet_v4" / "input_manifest.json"

REQUIRED_ATTESTATIONS = (
    "fixture_first",
    "no_live_crawl",
    "no_devhub",
    "no_private_artifact",
    "no_official_action",
    "no_active_state_mutation",
)

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/promotion_acceptance_packet_v4.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_promotion_acceptance_packet_v4.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_FORBIDDEN_KEYS = {
    "account_scoped_fact",
    "auth_fact",
    "auth_state",
    "auth_token",
    "authenticated_fact",
    "authenticated_page_value",
    "bearer_token",
    "browser_artifact",
    "browser_context",
    "browser_storage",
    "card_number",
    "cookie",
    "credentials",
    "downloaded_document",
    "har",
    "local_path",
    "mfa_code",
    "oauth_token",
    "password",
    "payment_details",
    "private_artifact",
    "private_fact",
    "private_file",
    "raw_body",
    "raw_crawl_output",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "screenshot",
    "session_artifact",
    "session_cookie",
    "session_state",
    "trace",
    "upload_payload",
}
_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_process_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_schedule_mutation",
    "active_source_mutation",
    "active_source_registry_mutation",
    "active_state_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation",
    "devhub_mutation",
    "guardrail_mutation",
    "prompt_mutation",
    "release_state_mutation",
    "source_registry_mutation",
    "surface_registry_mutation",
}
_FORBIDDEN_PHRASES = (
    "account scoped fact",
    "active state mutated",
    "authenticated fact",
    "cancel inspection",
    "cancel permit",
    "certify acknowledgement",
    "devhub completed",
    "entered payment details",
    "executed live",
    "file has been submitted",
    "guarantee approval",
    "guarantee issuance",
    "issued permit guaranteed",
    "live crawl completed",
    "live execution completed",
    "made official change",
    "opened devhub",
    "pay fees",
    "payment submitted",
    "permit approval guaranteed",
    "permit is guaranteed",
    "permit will be approved",
    "private artifact",
    "private fact",
    "promoted active",
    "promoted to active",
    "promoted to production",
    "promotion completed",
    "purchase permit",
    "raw crawl output",
    "raw pdf artifact",
    "release promoted",
    "schedule inspection",
    "session artifact",
    "submit application",
    "submit payment",
    "submit permit",
    "submitted to devhub",
    "upload correction",
    "upload corrections",
    "withdraw application",
)


class PromotionAcceptancePacketV4Error(ValueError):
    """Raised when the acceptance packet is not safe or complete."""


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise PromotionAcceptancePacketV4Error(f"fixture must be a JSON object: {path}")
    return loaded


def build_packet_from_manifest(manifest_path: Path = DEFAULT_MANIFEST_PATH) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    base = manifest_path.parent

    scheduler = build_rehearsal(
        load_scheduler_json(base / str(manifest["public_source_freshness_watch_plan_v3"])),
        load_scheduler_json(base / str(manifest["public_source_registry_promotion_preview_v3"])),
        load_scheduler_json(base / str(manifest["source_registry_fixtures"])),
    )
    draft_handoff = build_draft_handoff_packet_from_paths(
        base / str(manifest["pdf_field_mapping_fixtures"]),
        base / str(manifest["guardrail_bundle_fixtures"]),
        base / str(manifest["readiness_fixture_root"]),
    )
    guardrails = load_json(base / str(manifest["guardrail_bundle_fixtures"]))
    process_models = load_json(base / str(manifest["process_model_fixtures"]))

    return build_packet(
        scheduler,
        draft_handoff,
        guardrails,
        process_models,
        manifest_id=str(manifest.get("manifest_id", "promotion-acceptance-v4-input-manifest")),
    )


def build_packet(
    scheduler_rehearsal_v4: Mapping[str, Any],
    draft_preview_handoff_v4: Mapping[str, Any],
    guardrail_fixtures: Mapping[str, Any],
    process_model_fixtures: Mapping[str, Any],
    *,
    manifest_id: str = "inline-promotion-acceptance-v4",
) -> dict[str, Any]:
    _require_inputs(scheduler_rehearsal_v4, draft_preview_handoff_v4, guardrail_fixtures, process_model_fixtures)
    citation_ids = _citation_ids(scheduler_rehearsal_v4, draft_preview_handoff_v4, guardrail_fixtures, process_model_fixtures)

    packet = {
        "packet_version": PACKET_VERSION,
        "manifest_id": manifest_id,
        "mode": "fixture_first_promotion_acceptance_only",
        "consumes": {
            "public_freshness_scheduler_rehearsal_v4": str(scheduler_rehearsal_v4.get("schema")),
            "reversible_draft_preview_handoff_packet_v4": str(draft_preview_handoff_v4.get("packet_version")),
            "guardrail_fixtures": str(guardrail_fixtures.get("bundle_id")),
            "process_model_fixtures": str(process_model_fixtures.get("fixture_id")),
        },
        "reviewer_ready_acceptance_criteria": _acceptance_criteria(citation_ids, scheduler_rehearsal_v4, draft_preview_handoff_v4, guardrail_fixtures, process_model_fixtures),
        "dependency_order": _dependency_order(),
        "rollback_checkpoints": _rollback_checkpoints(citation_ids),
        "expected_fixture_diffs": _expected_fixture_diffs(citation_ids),
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
    }
    require_packet(packet)
    return packet


def validate_packet(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be promotion-acceptance-packet-v4")
    if packet.get("mode") != "fixture_first_promotion_acceptance_only":
        errors.append("mode must be fixture_first_promotion_acceptance_only")

    consumes = packet.get("consumes")
    if not isinstance(consumes, Mapping):
        errors.append("consumes must be an object")
    else:
        for key in ("public_freshness_scheduler_rehearsal_v4", "reversible_draft_preview_handoff_packet_v4", "guardrail_fixtures", "process_model_fixtures"):
            if not isinstance(consumes.get(key), str) or not consumes.get(key):
                errors.append(f"consumes.{key} must be present")

    criteria = _mapping_list(packet.get("reviewer_ready_acceptance_criteria"))
    if not criteria:
        errors.append("reviewer_ready_acceptance_criteria must be non-empty")
    for index, criterion in enumerate(criteria):
        for key in ("criterion_id", "reviewer_owner", "acceptance_text", "expected_result"):
            if not isinstance(criterion.get(key), str) or not criterion.get(key):
                errors.append(f"reviewer_ready_acceptance_criteria[{index}].{key} must be present")
        if criterion.get("ready_for_review") is not True:
            errors.append(f"reviewer_ready_acceptance_criteria[{index}].ready_for_review must be true")
        if not _string_list(criterion.get("citation_ids")):
            errors.append(f"reviewer_ready_acceptance_criteria[{index}].citation_ids must be non-empty")

    order = _mapping_list(packet.get("dependency_order"))
    if not order:
        errors.append("dependency_order must be non-empty")
    seen: set[str] = set()
    for index, step in enumerate(order):
        step_id = str(step.get("step_id", ""))
        dependencies = _string_list(step.get("depends_on"))
        if not step_id:
            errors.append(f"dependency_order[{index}].step_id must be present")
        if step_id in seen:
            errors.append(f"dependency_order[{index}].step_id must be unique")
        if index > 0 and not dependencies:
            errors.append(f"dependency_order[{index}].depends_on must include a prior step")
        for dependency in dependencies:
            if dependency not in seen:
                errors.append(f"dependency_order[{index}] dependency is missing or out of order: {dependency}")
        if step.get("offline_only") is not True:
            errors.append(f"dependency_order[{index}].offline_only must be true")
        seen.add(step_id)

    rollbacks = _mapping_list(packet.get("rollback_checkpoints"))
    if not rollbacks:
        errors.append("rollback_checkpoints must be non-empty")
    for index, checkpoint in enumerate(rollbacks):
        for key in ("checkpoint_id", "reviewer_owner", "rollback_scope", "expected_result"):
            if not isinstance(checkpoint.get(key), str) or not checkpoint.get(key):
                errors.append(f"rollback_checkpoints[{index}].{key} must be present")
        if checkpoint.get("requires_reviewer_confirmation") is not True:
            errors.append(f"rollback_checkpoints[{index}].requires_reviewer_confirmation must be true")
        if checkpoint.get("active_state_mutation_allowed") is not False:
            errors.append(f"rollback_checkpoints[{index}].active_state_mutation_allowed must be false")
        if not _string_list(checkpoint.get("citation_ids")):
            errors.append(f"rollback_checkpoints[{index}].citation_ids must be non-empty")

    diffs = _mapping_list(packet.get("expected_fixture_diffs"))
    if not diffs:
        errors.append("expected_fixture_diffs must be non-empty")
    for index, diff in enumerate(diffs):
        path = str(diff.get("fixture_path", ""))
        for key in ("artifact_id", "expected_change"):
            if not isinstance(diff.get(key), str) or not diff.get(key):
                errors.append(f"expected_fixture_diffs[{index}].{key} must be present")
        if not path.startswith("ppd/tests/fixtures/"):
            errors.append(f"expected_fixture_diffs[{index}].fixture_path must stay under ppd/tests/fixtures")
        if diff.get("live_artifact_expected") is not False:
            errors.append(f"expected_fixture_diffs[{index}].live_artifact_expected must be false")
        if not _string_list(diff.get("citation_ids")):
            errors.append(f"expected_fixture_diffs[{index}].citation_ids must be non-empty")

    commands = packet.get("offline_validation_commands")
    if not isinstance(commands, list) or not commands:
        errors.append("offline_validation_commands must be non-empty")
    else:
        for index, command in enumerate(commands):
            if not _string_list(command):
                errors.append(f"offline_validation_commands[{index}] must be a command list")

    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        errors.append("attestations must be an object")
    else:
        for key in REQUIRED_ATTESTATIONS:
            if attestations.get(key) is not True:
                errors.append(f"attestations.{key} must be true")

    errors.extend(_find_forbidden_content(packet))
    return sorted(dict.fromkeys(errors))


def require_packet(packet: Mapping[str, Any]) -> None:
    errors = validate_packet(packet)
    if errors:
        raise PromotionAcceptancePacketV4Error("invalid promotion acceptance packet v4: " + "; ".join(errors))


def _require_inputs(
    scheduler: Mapping[str, Any],
    draft_handoff: Mapping[str, Any],
    guardrails: Mapping[str, Any],
    process_models: Mapping[str, Any],
) -> None:
    if scheduler.get("schema") != "ppd.public_freshness_scheduler_rehearsal.v4":
        raise PromotionAcceptancePacketV4Error("scheduler rehearsal must be v4")
    if not _mapping_list(scheduler.get("cited_metadata_only_recrawl_schedule_candidates")):
        raise PromotionAcceptancePacketV4Error("scheduler rehearsal must include cited schedule candidates")
    if draft_handoff.get("packet_version") != "draft-preview-agent-handoff-packet-v4":
        raise PromotionAcceptancePacketV4Error("draft preview handoff must be v4")
    if not _mapping_list(draft_handoff.get("field_proposals")):
        raise PromotionAcceptancePacketV4Error("draft preview handoff must include field proposals")
    if not isinstance(guardrails.get("bundle_id"), str) or not guardrails.get("bundle_id"):
        raise PromotionAcceptancePacketV4Error("guardrail fixture bundle_id is required")
    if not isinstance(process_models.get("fixture_id"), str) or not process_models.get("fixture_id"):
        raise PromotionAcceptancePacketV4Error("process model fixture_id is required")


def _acceptance_criteria(
    citation_ids: Sequence[str],
    scheduler: Mapping[str, Any],
    draft_handoff: Mapping[str, Any],
    guardrails: Mapping[str, Any],
    process_models: Mapping[str, Any],
) -> list[dict[str, Any]]:
    scheduler_citations = _scheduler_citations(scheduler) or list(citation_ids)
    draft_citations = _draft_citations(draft_handoff) or list(citation_ids)
    guardrail_process_citations = _unique_non_empty([str(guardrails.get("bundle_id", "")), str(process_models.get("fixture_id", ""))])
    all_citations = _unique_non_empty(list(citation_ids))
    return [
        {
            "criterion_id": "freshness-scheduler-output-cited",
            "reviewer_owner": "public-freshness-reviewer",
            "acceptance_text": "Scheduler rehearsal contributes metadata-only public freshness candidates and defer rows with citations.",
            "expected_result": "Reviewer can confirm public freshness readiness from fixture evidence before any later crawl is considered.",
            "ready_for_review": True,
            "citation_ids": scheduler_citations,
        },
        {
            "criterion_id": "draft-preview-handoff-output-cited",
            "reviewer_owner": "draft-preview-reviewer",
            "acceptance_text": "Draft preview handoff contributes cited local preview proposals, blockers, user review checkpoints, and rollback notes.",
            "expected_result": "Reviewer can confirm reversible draft readiness from fixtures without DevHub or private artifacts.",
            "ready_for_review": True,
            "citation_ids": draft_citations,
        },
        {
            "criterion_id": "guardrail-process-boundary-aligned",
            "reviewer_owner": "guardrail-process-reviewer",
            "acceptance_text": "Guardrail and process model fixtures align on read-committed-fixtures, compare-fixture-evidence, and draft-reversible-preview boundaries.",
            "expected_result": "Reviewer can accept the packet only when process fixtures remain inside guardrail boundaries.",
            "ready_for_review": True,
            "citation_ids": guardrail_process_citations,
        },
        {
            "criterion_id": "rollback-and-diff-review-ready",
            "reviewer_owner": "promotion-reviewer",
            "acceptance_text": "Rollback checkpoints and expected fixture diffs are explicit, fixture-scoped, and citation-backed.",
            "expected_result": "Reviewer has a deterministic checklist for accepting or declining fixture-only promotion readiness.",
            "ready_for_review": True,
            "citation_ids": all_citations,
        },
    ]


def _dependency_order() -> list[dict[str, Any]]:
    return [
        {
            "step_id": "read-public-freshness-scheduler-rehearsal-v4",
            "depends_on": [],
            "reviewer_owner": "public-freshness-reviewer",
            "offline_only": True,
            "expected_evidence": "cited metadata-only schedule candidates and skip/defer rows",
        },
        {
            "step_id": "read-reversible-draft-preview-handoff-v4",
            "depends_on": ["read-public-freshness-scheduler-rehearsal-v4"],
            "reviewer_owner": "draft-preview-reviewer",
            "offline_only": True,
            "expected_evidence": "cited reversible draft proposals, blockers, checkpoints, and rollback notes",
        },
        {
            "step_id": "cross-check-guardrail-and-process-fixtures",
            "depends_on": ["read-reversible-draft-preview-handoff-v4"],
            "reviewer_owner": "guardrail-process-reviewer",
            "offline_only": True,
            "expected_evidence": "guardrail bundle fixture and process model fixture ids cited by acceptance criteria",
        },
        {
            "step_id": "review-acceptance-criteria-and-fixture-diffs",
            "depends_on": ["cross-check-guardrail-and-process-fixtures"],
            "reviewer_owner": "promotion-reviewer",
            "offline_only": True,
            "expected_evidence": "criteria, dependency order, rollback checkpoints, expected fixture diffs, and validation commands",
        },
    ]


def _rollback_checkpoints(citation_ids: Sequence[str]) -> list[dict[str, Any]]:
    citations = _unique_non_empty(list(citation_ids))
    return [
        {
            "checkpoint_id": "discard-generated-acceptance-packet",
            "reviewer_owner": "promotion-reviewer",
            "rollback_scope": "generated acceptance packet only",
            "requires_reviewer_confirmation": True,
            "active_state_mutation_allowed": False,
            "expected_result": "The reviewer can discard the packet and rerun from committed fixtures; no active PP&D state changes.",
            "citation_ids": citations,
        },
        {
            "checkpoint_id": "retain-consumed-fixtures-unchanged",
            "reviewer_owner": "fixture-owner",
            "rollback_scope": "consumed scheduler, draft, guardrail, and process fixtures",
            "requires_reviewer_confirmation": True,
            "active_state_mutation_allowed": False,
            "expected_result": "Consumed fixtures remain review inputs unless a later fixture-only change is separately proposed.",
            "citation_ids": citations,
        },
    ]


def _expected_fixture_diffs(citation_ids: Sequence[str]) -> list[dict[str, Any]]:
    citations = _unique_non_empty(list(citation_ids))
    return [
        {
            "artifact_id": "promotion-acceptance-input-manifest-v4",
            "fixture_path": "ppd/tests/fixtures/promotion_acceptance_packet_v4/input_manifest.json",
            "expected_change": "new fixture manifest that points only at committed PP&D fixtures",
            "live_artifact_expected": False,
            "citation_ids": citations,
        },
        {
            "artifact_id": "public-freshness-scheduler-rehearsal-v4-output",
            "fixture_path": "ppd/tests/fixtures/public_freshness_scheduler_rehearsal_v4/public_source_freshness_watch_plan_v3.json",
            "expected_change": "reviewed as consumed scheduler evidence; no live crawl output expected",
            "live_artifact_expected": False,
            "citation_ids": citations,
        },
        {
            "artifact_id": "draft-preview-handoff-v4-output",
            "fixture_path": "ppd/tests/fixtures/draft_preview_agent_handoff_packet_v4/pdf_field_mapping_fixtures.json",
            "expected_change": "reviewed as consumed reversible draft evidence; no DevHub or private artifact expected",
            "live_artifact_expected": False,
            "citation_ids": citations,
        },
    ]


def _citation_ids(
    scheduler: Mapping[str, Any],
    draft_handoff: Mapping[str, Any],
    guardrails: Mapping[str, Any],
    process_models: Mapping[str, Any],
) -> list[str]:
    ids: list[str] = []
    ids.extend(_scheduler_citations(scheduler))
    ids.extend(_draft_citations(draft_handoff))
    ids.append(str(guardrails.get("bundle_id", "")))
    ids.append(str(process_models.get("fixture_id", "")))
    return _unique_non_empty(ids)


def _scheduler_citations(scheduler: Mapping[str, Any]) -> list[str]:
    ids: list[str] = []
    for section in ("cited_metadata_only_recrawl_schedule_candidates", "skip_defer_reasons"):
        for row in _mapping_list(scheduler.get(section)):
            for citation in row.get("citations", []):
                if isinstance(citation, Mapping):
                    ids.append(str(citation.get("label", "")))
                elif isinstance(citation, str):
                    ids.append(citation)
    return _unique_non_empty(ids)


def _draft_citations(draft_handoff: Mapping[str, Any]) -> list[str]:
    ids: list[str] = []
    ids.extend(_string_list(draft_handoff.get("source_fixture_ids")))
    for section in ("readiness_adapter_outputs", "field_proposals", "missing_fact_blockers", "user_review_checkpoints", "rollback_notes"):
        for row in _mapping_list(draft_handoff.get(section)):
            ids.extend(_string_list(row.get("citation_ids")))
    return _unique_non_empty(ids)


def _find_forbidden_content(value: Any, path: str = "packet") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if normalized in _FORBIDDEN_KEYS and _present(child):
                errors.append(f"{child_path} must not contain private, authenticated, browser, session, raw crawl, or PDF artifacts")
            if normalized in _MUTATION_KEYS and _present(child):
                errors.append(f"{child_path} must not contain active mutation flags")
            errors.extend(_find_forbidden_content(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_find_forbidden_content(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = " ".join(value.lower().replace("_", " ").replace("-", " ").split())
        for phrase in _FORBIDDEN_PHRASES:
            normalized_phrase = " ".join(phrase.lower().replace("_", " ").replace("-", " ").split())
            if normalized_phrase in lowered:
                errors.append(f"{path} contains forbidden claim or consequential action language: {phrase}")
    return errors


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _unique_non_empty(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return True


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    args = parser.parse_args(argv)
    packet = build_packet_from_manifest(args.manifest)
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
