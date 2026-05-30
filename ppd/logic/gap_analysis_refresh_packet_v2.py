"""Fixture-first refresh packet builder for PP&D gap-analysis expectations v2."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EXPECTATION_KINDS = (
    "missing_fact",
    "stale_evidence",
    "conflicting_evidence",
    "missing_document",
    "blocked_action",
    "next_safe_action",
)

ATTESTATIONS = {
    "no_live_devhub": True,
    "no_private_document": True,
    "no_gap_analysis_mutation": True,
    "no_process_mutation": True,
    "no_guardrail_mutation": True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/logic/gap_analysis_refresh_packet_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_gap_analysis_refresh_packet_v2.py"],
]


def load_json(path: str | Path) -> dict[str, Any]:
    """Load a JSON object fixture."""
    with Path(path).open("r", encoding="utf-8") as fixture_file:
        value = json.load(fixture_file)
    if not isinstance(value, dict):
        raise ValueError(f"fixture must contain a JSON object: {path}")
    return value


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _citation_set(*items: dict[str, Any]) -> list[str]:
    citations: set[str] = set()
    for item in items:
        for key in ("citation_ids", "source_evidence_ids", "evidence_ids"):
            for citation in _as_list(item.get(key)):
                if citation:
                    citations.add(str(citation))
    return sorted(citations)


def _reviewer_owner(item: dict[str, Any], defaults: dict[str, str]) -> dict[str, str]:
    return {
        "reviewer_role": str(item.get("reviewer_role") or defaults.get("reviewer_role") or "ppd_reviewer"),
        "owner_role": str(item.get("owner_role") or defaults.get("owner_role") or "user"),
    }


def _expectation(kind: str, item: dict[str, Any], defaults: dict[str, str], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    expectation_id = str(item.get("expectation_id") or item.get("fact_id") or item.get("document_id") or item.get("action_id"))
    if not expectation_id:
        raise ValueError(f"{kind} expectation is missing an id")

    result: dict[str, Any] = {
        "expectation_id": expectation_id,
        "kind": kind,
        "label": str(item.get("label") or item.get("name") or expectation_id),
        "reason": str(item.get("reason") or item.get("gap_reason") or item.get("impact_reason") or "fixture refresh expectation"),
        "citation_ids": _citation_set(item),
        "reviewer_owner": _reviewer_owner(item, defaults),
    }
    if extra:
        result.update(extra)
    return result


def _dedupe_expectations(expectations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for expectation in expectations:
        key = (str(expectation["kind"]), str(expectation["expectation_id"]))
        if key not in merged:
            merged[key] = dict(expectation)
            continue
        existing = merged[key]
        existing["citation_ids"] = sorted(set(existing.get("citation_ids", [])) | set(expectation.get("citation_ids", [])))
        if not existing.get("reason") and expectation.get("reason"):
            existing["reason"] = expectation["reason"]
    return sorted(merged.values(), key=lambda item: (item["kind"], item["expectation_id"]))


def build_refresh_packet_v2(
    process_model_refresh_impact: dict[str, Any],
    guardrail_bundle_refresh_candidate: dict[str, Any],
    existing_user_gap_analysis: dict[str, Any],
) -> dict[str, Any]:
    """Build a deterministic refresh packet from committed fixtures only."""
    defaults = {
        **guardrail_bundle_refresh_candidate.get("reviewer_owner_defaults", {}),
        **process_model_refresh_impact.get("reviewer_owner_defaults", {}),
    }

    expectations: list[dict[str, Any]] = []

    for item in _as_list(existing_user_gap_analysis.get("missing_facts")):
        expectations.append(_expectation("missing_fact", item, defaults, {"source": "existing_user_gap_analysis"}))
    for item in _as_list(process_model_refresh_impact.get("missing_fact_updates")):
        expectations.append(_expectation("missing_fact", item, defaults, {"source": "process_model_refresh_impact"}))

    for item in _as_list(existing_user_gap_analysis.get("stale_evidence")):
        expectations.append(_expectation("stale_evidence", item, defaults, {"source": "existing_user_gap_analysis"}))
    for item in _as_list(process_model_refresh_impact.get("stale_evidence_updates")):
        expectations.append(_expectation("stale_evidence", item, defaults, {"source": "process_model_refresh_impact"}))

    for item in _as_list(existing_user_gap_analysis.get("conflicting_evidence")):
        expectations.append(_expectation("conflicting_evidence", item, defaults, {"source": "existing_user_gap_analysis"}))
    for item in _as_list(process_model_refresh_impact.get("conflicting_evidence_updates")):
        expectations.append(_expectation("conflicting_evidence", item, defaults, {"source": "process_model_refresh_impact"}))

    for item in _as_list(existing_user_gap_analysis.get("missing_documents")):
        expectations.append(_expectation("missing_document", item, defaults, {"source": "existing_user_gap_analysis"}))
    for item in _as_list(process_model_refresh_impact.get("missing_document_updates")):
        expectations.append(_expectation("missing_document", item, defaults, {"source": "process_model_refresh_impact"}))

    for item in _as_list(existing_user_gap_analysis.get("blocked_actions")):
        expectations.append(_expectation("blocked_action", item, defaults, {"source": "existing_user_gap_analysis"}))
    for item in _as_list(guardrail_bundle_refresh_candidate.get("blocked_action_updates")):
        expectations.append(_expectation("blocked_action", item, defaults, {"source": "guardrail_bundle_refresh_candidate"}))

    for item in _as_list(existing_user_gap_analysis.get("next_safe_actions")):
        expectations.append(_expectation("next_safe_action", item, defaults, {"source": "existing_user_gap_analysis"}))
    for item in _as_list(guardrail_bundle_refresh_candidate.get("next_safe_action_updates")):
        expectations.append(_expectation("next_safe_action", item, defaults, {"source": "guardrail_bundle_refresh_candidate"}))

    grouped = {kind: [] for kind in EXPECTATION_KINDS}
    for expectation in _dedupe_expectations(expectations):
        grouped[expectation["kind"]].append(expectation)

    return {
        "packet_id": "gap-analysis-refresh-packet-v2",
        "packet_version": 2,
        "case_id": existing_user_gap_analysis.get("case_id"),
        "process_id": process_model_refresh_impact.get("process_id") or existing_user_gap_analysis.get("process_id"),
        "guardrail_bundle_id": guardrail_bundle_refresh_candidate.get("guardrail_bundle_id"),
        "input_fixture_ids": sorted(
            str(value)
            for value in (
                process_model_refresh_impact.get("fixture_id"),
                guardrail_bundle_refresh_candidate.get("fixture_id"),
                existing_user_gap_analysis.get("fixture_id"),
            )
            if value
        ),
        "expectation_updates": grouped,
        "reviewer_owner_fields": {
            "reviewer_role": defaults.get("reviewer_role", "ppd_reviewer"),
            "owner_role": defaults.get("owner_role", "user"),
            "required_for_each_expectation": True,
        },
        "offline_validation_commands": OFFLINE_VALIDATION_COMMANDS,
        "attestations": dict(ATTESTATIONS),
    }


def build_refresh_packet_from_files(
    process_model_refresh_impact_path: str | Path,
    guardrail_bundle_refresh_candidate_path: str | Path,
    existing_user_gap_analysis_path: str | Path,
) -> dict[str, Any]:
    return build_refresh_packet_v2(
        load_json(process_model_refresh_impact_path),
        load_json(guardrail_bundle_refresh_candidate_path),
        load_json(existing_user_gap_analysis_path),
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build a fixture-first PP&D gap-analysis refresh packet v2.")
    parser.add_argument("process_model_refresh_impact")
    parser.add_argument("guardrail_bundle_refresh_candidate")
    parser.add_argument("existing_user_gap_analysis")
    args = parser.parse_args()

    packet = build_refresh_packet_from_files(
        args.process_model_refresh_impact,
        args.guardrail_bundle_refresh_candidate,
        args.existing_user_gap_analysis,
    )
    print(json.dumps(packet, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
