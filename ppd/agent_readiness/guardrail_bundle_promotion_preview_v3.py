"""Fixture-first guardrail bundle promotion preview v3.

This module combines an attended review disposition summary v3 with the
fixture-only guardrail regression replay matrix v3. It emits reviewable guardrail
fixture patch candidates only; it does not call an LLM, open DevHub, crawl public
sources, run processors, or mutate active guardrails or prompts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from ppd.agent_readiness.guardrail_regression_replay_matrix_v3 import build_matrix, load_source_packets, validate_matrix
from ppd.validation.attended_review_disposition_summary_v3 import validate_attended_review_disposition_summary_v3

PREVIEW_TYPE = "ppd.guardrail_bundle_promotion_preview.v3"
PREVIEW_VERSION = 3

REQUIRED_ATTESTATIONS = {
    "no_live_llm": True,
    "no_devhub": True,
    "no_crawler": True,
    "no_processor": True,
    "no_active_guardrail_mutation": True,
    "no_active_prompt_mutation": True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/agent_readiness/guardrail_bundle_promotion_preview_v3.py"],
    ["python3", "-m", "unittest", "ppd.tests.test_guardrail_bundle_promotion_preview_v3"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_CONSEQUENTIAL_CLASSIFICATION = "refuse_consequential_action"


def load_manifest(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("guardrail bundle promotion preview manifest must be a JSON object")
    return data


def build_guardrail_bundle_promotion_preview_v3_from_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path)
    manifest = load_manifest(manifest_path)
    source_packets_ref = _text(manifest.get("guardrail_regression_replay_source_packets"))
    if not source_packets_ref:
        raise ValueError("manifest must include guardrail_regression_replay_source_packets")
    source_packets_path = manifest_path.parent / source_packets_ref
    matrix = build_matrix(load_source_packets(source_packets_path))
    summary = _mapping(manifest.get("attended_review_disposition_summary_v3"))
    return build_guardrail_bundle_promotion_preview_v3(
        attended_review_disposition_summary_v3=summary,
        guardrail_regression_replay_matrix_v3=matrix,
        source_manifest_id=_text(manifest.get("manifest_id"), "inline-guardrail-bundle-promotion-preview-v3"),
        disposition_summary_ref=_text(manifest.get("disposition_summary_ref"), "attended_review_disposition_summary_v3"),
        replay_matrix_ref=source_packets_ref,
    )


def build_guardrail_bundle_promotion_preview_v3(
    attended_review_disposition_summary_v3: Mapping[str, Any],
    guardrail_regression_replay_matrix_v3: Mapping[str, Any],
    source_manifest_id: str = "inline-fixtures",
    disposition_summary_ref: str = "attended_review_disposition_summary_v3",
    replay_matrix_ref: str = "guardrail_regression_replay_matrix_v3",
) -> dict[str, Any]:
    disposition_errors = validate_attended_review_disposition_summary_v3(attended_review_disposition_summary_v3)
    if disposition_errors:
        codes = ", ".join(_text(issue.get("code")) for issue in disposition_errors if isinstance(issue, Mapping))
        raise ValueError("attended review disposition summary v3 must validate before preview build: " + codes)

    matrix_errors = validate_matrix(guardrail_regression_replay_matrix_v3)
    if matrix_errors:
        raise ValueError("guardrail regression replay matrix v3 must validate before preview build: " + "; ".join(matrix_errors))

    disposition_rows = _mappings(attended_review_disposition_summary_v3.get("rows"))
    scenarios = _mappings(guardrail_regression_replay_matrix_v3.get("scenarios"))
    candidates = [_candidate_from_scenario(index, scenario, disposition_rows, disposition_summary_ref, replay_matrix_ref) for index, scenario in enumerate(scenarios)]
    dependency_order = [candidate["candidate_id"] for candidate in candidates]

    preview = {
        "preview_type": PREVIEW_TYPE,
        "preview_version": PREVIEW_VERSION,
        "mode": "fixture_first_guardrail_bundle_promotion_preview_only",
        "source_manifest_id": source_manifest_id,
        "consumes": {
            "attended_review_disposition_summary_v3": disposition_summary_ref,
            "guardrail_regression_replay_matrix_v3": replay_matrix_ref,
        },
        "guardrail_fixture_patch_candidates": candidates,
        "dependency_order": dependency_order,
        "rollback_checkpoints": [_rollback_checkpoint(candidate_id) for candidate_id in dependency_order],
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "attestations": dict(REQUIRED_ATTESTATIONS),
        "preview_status": "ready_for_guardrail_fixture_patch_review",
    }
    require_guardrail_bundle_promotion_preview_v3(preview)
    return preview


def validate_guardrail_bundle_promotion_preview_v3(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if packet.get("preview_type") != PREVIEW_TYPE:
        errors.append(f"preview_type must be {PREVIEW_TYPE}")
    if packet.get("preview_version") != PREVIEW_VERSION:
        errors.append("preview_version must be 3")
    if packet.get("mode") != "fixture_first_guardrail_bundle_promotion_preview_only":
        errors.append("mode must be fixture_first_guardrail_bundle_promotion_preview_only")

    consumes = _mapping(packet.get("consumes"))
    if not _text(consumes.get("attended_review_disposition_summary_v3")):
        errors.append("consumes.attended_review_disposition_summary_v3 must be present")
    if not _text(consumes.get("guardrail_regression_replay_matrix_v3")):
        errors.append("consumes.guardrail_regression_replay_matrix_v3 must be present")

    candidates = _mappings(packet.get("guardrail_fixture_patch_candidates"))
    if not candidates:
        errors.append("guardrail_fixture_patch_candidates must be non-empty")
    candidate_ids: list[str] = []
    for index, candidate in enumerate(candidates):
        prefix = f"guardrail_fixture_patch_candidates[{index}]"
        candidate_id = _text(candidate.get("candidate_id"))
        if not candidate_id:
            errors.append(f"{prefix}.candidate_id must be present")
        else:
            candidate_ids.append(candidate_id)
        for key in ("guardrail_bundle_id", "scenario_ref", "reviewer_owner", "patch_kind", "promotion_disposition", "rollback_checkpoint_id"):
            if not _text(candidate.get(key)):
                errors.append(f"{prefix}.{key} must be present")
        if not _mappings(candidate.get("citations")):
            errors.append(f"{prefix}.citations must be non-empty")
        if not _mappings(candidate.get("before_after_predicate_rows")):
            errors.append(f"{prefix}.before_after_predicate_rows must be non-empty")
        if not _mappings(candidate.get("explanation_template_deltas")):
            errors.append(f"{prefix}.explanation_template_deltas must be non-empty")
        checks = _mappings(candidate.get("blocked_consequential_action_regression_checks"))
        if candidate.get("next_action_classification") == _CONSEQUENTIAL_CLASSIFICATION and not checks:
            errors.append(f"{prefix}.blocked_consequential_action_regression_checks must be non-empty for consequential action replay rows")
        for row_index, row in enumerate(_mappings(candidate.get("before_after_predicate_rows"))):
            row_prefix = f"{prefix}.before_after_predicate_rows[{row_index}]"
            for key in ("predicate_id", "before", "after", "expected_regression_result"):
                if not _text(row.get(key)):
                    errors.append(f"{row_prefix}.{key} must be present")
            if not _mappings(row.get("citations")):
                errors.append(f"{row_prefix}.citations must be non-empty")

    dependency_order = _strings(packet.get("dependency_order"))
    if not dependency_order:
        errors.append("dependency_order must be non-empty")
    for candidate_id in candidate_ids:
        if candidate_id not in dependency_order:
            errors.append(f"dependency_order missing {candidate_id}")

    rollback_patch_ids = {_text(row.get("candidate_id")) for row in _mappings(packet.get("rollback_checkpoints"))}
    if not rollback_patch_ids:
        errors.append("rollback_checkpoints must be non-empty")
    for candidate_id in candidate_ids:
        if candidate_id not in rollback_patch_ids:
            errors.append(f"rollback_checkpoints missing {candidate_id}")

    commands = packet.get("offline_validation_commands")
    if not isinstance(commands, Sequence) or isinstance(commands, (str, bytes)) or not commands:
        errors.append("offline_validation_commands must be non-empty")
    else:
        for index, command in enumerate(commands):
            if not _strings(command):
                errors.append(f"offline_validation_commands[{index}] must be a command list")

    attestations = _mapping(packet.get("attestations"))
    for key, expected in REQUIRED_ATTESTATIONS.items():
        if attestations.get(key) is not expected:
            errors.append(f"attestations.{key} must be true")
    if _text(packet.get("preview_status")) != "ready_for_guardrail_fixture_patch_review":
        errors.append("preview_status must be ready_for_guardrail_fixture_patch_review")

    _reject_mutation_flags(packet, "$", errors)
    return errors


def require_guardrail_bundle_promotion_preview_v3(packet: Mapping[str, Any]) -> None:
    errors = validate_guardrail_bundle_promotion_preview_v3(packet)
    if errors:
        raise ValueError("invalid guardrail bundle promotion preview v3: " + "; ".join(errors))


def _candidate_from_scenario(
    index: int,
    scenario: Mapping[str, Any],
    disposition_rows: Sequence[Mapping[str, Any]],
    disposition_summary_ref: str,
    replay_matrix_ref: str,
) -> dict[str, Any]:
    scenario_id = _text(scenario.get("id"), f"scenario-{index + 1}")
    candidate_id = f"guardrail-fixture-patch-{index + 1:02d}-{_slug(scenario_id)}"
    citations = _candidate_citations(scenario, disposition_rows, disposition_summary_ref, replay_matrix_ref)
    after = _mapping(scenario.get("after_expected_outcome"))
    before = _mapping(scenario.get("before_expected_outcome"))
    classification = _text(scenario.get("next_action_classification"))
    candidate = {
        "candidate_id": candidate_id,
        "guardrail_bundle_id": "guardrail-bundle-fixture-preview-v3",
        "scenario_ref": scenario_id,
        "reviewer_owner": _text(scenario.get("reviewer_owner"), "guardrail-reviewer"),
        "patch_kind": "inactive_fixture_guardrail_patch_candidate",
        "promotion_disposition": _promotion_disposition(disposition_rows),
        "next_action_classification": classification,
        "citations": citations,
        "before_after_predicate_rows": [
            {
                "predicate_id": f"predicate-{_slug(scenario_id)}",
                "before": _text(before.get("text")),
                "after": _text(after.get("text")),
                "expected_regression_result": classification,
                "citations": citations,
            }
        ],
        "explanation_template_deltas": [
            {
                "template_id": f"template-{_slug(scenario_id)}",
                "before_template": "Fixture explanation did not require replay-row provenance for this guardrail family.",
                "after_template": "Fixture explanation must cite attended disposition and replay matrix provenance before any user-facing guardrail text is reviewable.",
                "citations": citations,
            }
        ],
        "blocked_consequential_action_regression_checks": _blocked_checks(candidate_id, scenario, citations),
        "dependency_refs": list(_strings(scenario.get("guardrail_refs"))) + list(_strings(scenario.get("gap_analysis_refs"))),
        "rollback_checkpoint_id": f"rollback-{candidate_id}",
    }
    return candidate


def _candidate_citations(
    scenario: Mapping[str, Any],
    disposition_rows: Sequence[Mapping[str, Any]],
    disposition_summary_ref: str,
    replay_matrix_ref: str,
) -> list[dict[str, str]]:
    citations: list[dict[str, str]] = []
    for row_index, row in enumerate(disposition_rows):
        citation = row.get("citation") or row.get("citations") or row.get("source_citation") or row.get("evidence")
        if citation:
            citations.append({"artifact": disposition_summary_ref, "row": str(row_index + 1), "citation": _text(citation)})
    for citation in _mappings(scenario.get("replay_row_citations")):
        citations.append(
            {
                "artifact": replay_matrix_ref,
                "packet_id": _text(citation.get("packet_id")),
                "section": _text(citation.get("section")),
            }
        )
    return citations


def _blocked_checks(candidate_id: str, scenario: Mapping[str, Any], citations: Sequence[Mapping[str, str]]) -> list[dict[str, Any]]:
    if _text(scenario.get("next_action_classification")) != _CONSEQUENTIAL_CLASSIFICATION:
        return []
    return [
        {
            "check_id": f"blocked-check-{candidate_id}",
            "expected_result": "blocked_until_user_attended_exact_confirmation",
            "regression_scope": "consequential_action_request",
            "citations": list(citations),
        }
    ]


def _rollback_checkpoint(candidate_id: str) -> dict[str, str]:
    return {
        "candidate_id": candidate_id,
        "checkpoint_id": f"rollback-{candidate_id}",
        "rollback_action": "discard_fixture_patch_candidate_only",
        "verification": "No active guardrail, prompt, DevHub, crawler, processor, or release-state artifact is changed by this preview.",
    }


def _promotion_disposition(rows: Sequence[Mapping[str, Any]]) -> str:
    dispositions = {_text(row.get("disposition") or row.get("decision")).lower() for row in rows}
    if "reject" in dispositions:
        return "review_required_rejections_present"
    if "defer" in dispositions:
        return "review_required_deferrals_present"
    return "reviewed_fixture_candidate"


def _reject_mutation_flags(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_").replace(" ", "_")
            if normalized in {"guardrail_mutation", "prompt_mutation", "active_guardrail_mutation", "active_prompt_mutation", "mutates_guardrails", "mutates_prompts"} and item:
                errors.append(f"{path}.{key} mutation flags must be absent or false")
            _reject_mutation_flags(item, f"{path}.{key}", errors)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, item in enumerate(value):
            _reject_mutation_flags(item, f"{path}[{index}]", errors)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mappings(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _strings(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [_text(item) for item in value if _text(item)]


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _slug(value: str) -> str:
    cleaned = []
    previous_dash = False
    for character in value.lower():
        if character.isalnum():
            cleaned.append(character)
            previous_dash = False
        elif not previous_dash:
            cleaned.append("-")
            previous_dash = True
    return "".join(cleaned).strip("-") or "item"
