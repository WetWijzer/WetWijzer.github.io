"""Combined offline patch rehearsal packet v2.

This module intentionally consumes committed fixtures and patch previews only. It does
not perform live crawling, authentication, browser automation, official submission,
or release-state mutation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

_REQUIRED_ATTESTATIONS = {
    "no_live_crawl": True,
    "no_auth": True,
    "no_official_action": True,
    "no_release_state_mutation": True,
}

_MUTATION_FLAG_KEYS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_monitoring_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_source_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation_enabled",
    "apply_to_active_agent_state",
    "apply_to_active_guardrails",
    "apply_to_active_monitoring",
    "apply_to_active_prompts",
    "apply_to_active_release_state",
    "apply_to_active_source_registry",
    "apply_to_active_sources",
    "apply_to_active_surface_registry",
    "guardrail_mutation_enabled",
    "monitoring_mutation_enabled",
    "prompt_mutation_enabled",
    "release_state_mutation_enabled",
    "source_mutation_enabled",
    "surface_registry_mutation_enabled",
}

_PRIVATE_OR_AUTH_KEYS = {
    "access_token",
    "auth_state",
    "authenticated_fact",
    "bank_account",
    "browser_context",
    "card_number",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "cvv",
    "devhub_private_fact",
    "email",
    "field_value",
    "mfa_code",
    "password",
    "payment_details",
    "phone",
    "private_fact",
    "private_value",
    "raw_value",
    "refresh_token",
    "secret",
    "session_cookie",
    "session_state",
    "ssn",
    "token",
    "user_input",
    "user_supplied_value",
}

_RAW_ARTIFACT_KEYS = {
    "browser_artifact",
    "browser_artifacts",
    "crawl_body",
    "downloaded_document",
    "har",
    "har_path",
    "pdf_binary",
    "playwright_trace",
    "raw_browser_artifact",
    "raw_crawl_artifact",
    "raw_crawl_output",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "raw_session_artifact",
    "screenshot",
    "screenshots",
    "session_artifact",
    "trace",
    "trace_path",
    "video",
}

_LIVE_OR_PROMOTION_KEYS = {
    "execute_live",
    "execution_claim",
    "live_execution",
    "live_execution_claim",
    "live_promotion",
    "promotion_claim",
    "promoted",
    "release_promoted",
    "run_live",
}

_CONSEQUENTIAL_ACTION_KEYS = {
    "action",
    "action_claim",
    "claim",
    "execution_claim",
    "next_action",
    "next_step",
    "promotion_claim",
    "recommended_action",
}

_LEGAL_GUARANTEE_MARKERS = (
    "approval guaranteed",
    "guarantee approval",
    "guarantee permit",
    "guaranteed approval",
    "guaranteed permit",
    "legal advice",
    "legally sufficient",
    "permit will be approved",
    "permitting outcome guaranteed",
    "will pass inspection",
)

_CONSEQUENTIAL_ACTION_MARKERS = (
    "cancel inspection",
    "certify acknowledgement",
    "make payment",
    "pay fee",
    "promote release",
    "schedule inspection",
    "submit application",
    "submit permit",
    "upload correction",
    "upload to official record",
)

_OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/agent_readiness/combined_offline_patch_rehearsal_packet_v2.py"],
    ["python3", "-m", "unittest", "ppd.tests.test_combined_offline_patch_rehearsal_packet_v2"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _require_mapping(data: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(data, Mapping):
        raise ValueError(f"{name} must be a mapping")
    return data


def _collect_citations(items: Iterable[Mapping[str, Any]]) -> List[str]:
    citations: List[str] = []
    for item in items:
        for citation in _as_list(item.get("citations")):
            if citation not in citations:
                citations.append(str(citation))
    return citations


def _index_by_id(items: Sequence[Mapping[str, Any]], id_key: str) -> Dict[str, Mapping[str, Any]]:
    indexed: Dict[str, Mapping[str, Any]] = {}
    for item in items:
        item_id = item.get(id_key)
        if not item_id:
            raise ValueError(f"preview item missing {id_key}")
        indexed[str(item_id)] = item
    return indexed


def _expected_fixture_diffs(previews: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    diffs: List[Dict[str, Any]] = []
    for preview in previews:
        fixture_path = str(preview.get("fixture_path", ""))
        if not fixture_path.startswith("ppd/tests/fixtures/"):
            raise ValueError("expected fixture diffs must reference ppd/tests/fixtures")
        diffs.append(
            {
                "artifact_id": str(preview["artifact_id"]),
                "fixture_path": fixture_path,
                "expected_change": str(preview.get("expected_change", "replace")),
                "before_hash": str(preview.get("before_hash", "fixture-before")),
                "after_hash": str(preview.get("after_hash", "fixture-after")),
                "reviewer_owner": str(preview.get("reviewer_owner", "ppd-reviewer")),
            }
        )
    return diffs


def _dependency_ordered_steps(
    source_previews: Sequence[Mapping[str, Any]],
    devhub_previews: Sequence[Mapping[str, Any]],
    guardrail_previews: Sequence[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    steps: List[Dict[str, Any]] = []

    for preview in source_previews:
        artifact_id = str(preview["artifact_id"])
        steps.append(
            {
                "step_id": f"step-source-{artifact_id}",
                "artifact_id": artifact_id,
                "artifact_type": "source_patch_preview",
                "depends_on": [],
                "reviewer_owner": str(preview.get("reviewer_owner", "source-reviewer")),
                "action": "Review the fixture-only source patch preview and verify cited public-source evidence before downstream surface or guardrail rehearsal.",
                "citations": _collect_citations([preview]),
                "offline_only": True,
            }
        )

    for preview in devhub_previews:
        artifact_id = str(preview["artifact_id"])
        depends_on = [f"step-source-{source_id}" for source_id in _as_list(preview.get("depends_on"))]
        steps.append(
            {
                "step_id": f"step-devhub-{artifact_id}",
                "artifact_id": artifact_id,
                "artifact_type": "devhub_surface_preview",
                "depends_on": depends_on,
                "reviewer_owner": str(preview.get("reviewer_owner", "devhub-reviewer")),
                "action": "Review the redacted DevHub surface preview against source evidence without opening DevHub or using authenticated browser state.",
                "citations": _collect_citations([preview]),
                "offline_only": True,
            }
        )

    source_ids = {str(preview["artifact_id"]) for preview in source_previews}
    devhub_ids = {str(preview["artifact_id"]) for preview in devhub_previews}
    for preview in guardrail_previews:
        artifact_id = str(preview["artifact_id"])
        explicit_dependencies = [str(value) for value in _as_list(preview.get("depends_on"))]
        depends_on = [f"step-source-{value}" for value in explicit_dependencies if value in source_ids]
        depends_on.extend(f"step-devhub-{value}" for value in explicit_dependencies if value in devhub_ids)
        steps.append(
            {
                "step_id": f"step-guardrail-{artifact_id}",
                "artifact_id": artifact_id,
                "artifact_type": "guardrail_patch_preview",
                "depends_on": depends_on,
                "reviewer_owner": str(preview.get("reviewer_owner", "guardrail-reviewer")),
                "action": "Review guardrail predicate and refusal changes after source and DevHub preview checks have passed.",
                "citations": _collect_citations([preview]),
                "offline_only": True,
            }
        )

    return steps


def _cross_artifact_checks(
    source_previews: Sequence[Mapping[str, Any]],
    devhub_previews: Sequence[Mapping[str, Any]],
    guardrail_previews: Sequence[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    source_by_id = _index_by_id(source_previews, "artifact_id")
    devhub_by_id = _index_by_id(devhub_previews, "artifact_id")
    guardrail_by_id = _index_by_id(guardrail_previews, "artifact_id")

    checks: List[Dict[str, Any]] = []
    for preview in devhub_previews:
        missing = [value for value in _as_list(preview.get("depends_on")) if str(value) not in source_by_id]
        checks.append(
            {
                "check_id": f"devhub-source-dependencies-{preview['artifact_id']}",
                "status": "pass" if not missing else "fail",
                "reviewer_owner": str(preview.get("reviewer_owner", "devhub-reviewer")),
                "description": "DevHub surface preview dependencies resolve to source patch previews.",
                "missing_dependencies": [str(value) for value in missing],
            }
        )

    known_dependency_ids = set(source_by_id) | set(devhub_by_id)
    for preview in guardrail_previews:
        missing = [value for value in _as_list(preview.get("depends_on")) if str(value) not in known_dependency_ids]
        checks.append(
            {
                "check_id": f"guardrail-preview-dependencies-{preview['artifact_id']}",
                "status": "pass" if not missing else "fail",
                "reviewer_owner": str(preview.get("reviewer_owner", "guardrail-reviewer")),
                "description": "Guardrail preview dependencies resolve to source or DevHub patch previews.",
                "missing_dependencies": [str(value) for value in missing],
            }
        )

    all_citations = _collect_citations(list(source_previews) + list(devhub_previews) + list(guardrail_previews))
    checks.append(
        {
            "check_id": "citation-coverage",
            "status": "pass" if all_citations else "fail",
            "reviewer_owner": "evidence-reviewer",
            "description": "Every rehearsal packet must carry source citations from the preview fixtures.",
            "citation_count": len(all_citations),
        }
    )
    checks.append(
        {
            "check_id": "combined-preview-presence",
            "status": "pass" if source_by_id and devhub_by_id and guardrail_by_id else "fail",
            "reviewer_owner": "release-reviewer",
            "description": "The packet combines source, DevHub surface, and guardrail patch application previews.",
            "artifact_counts": {
                "source": len(source_by_id),
                "devhub_surface": len(devhub_by_id),
                "guardrail": len(guardrail_by_id),
            },
        }
    )
    return checks


def _rollback_verification(previews: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    verification: List[Dict[str, Any]] = []
    for preview in previews:
        verification.append(
            {
                "artifact_id": str(preview["artifact_id"]),
                "reviewer_owner": str(preview.get("reviewer_owner", "rollback-reviewer")),
                "rollback_command": ["git", "diff", "--", str(preview.get("fixture_path", "ppd/tests/fixtures"))],
                "expected_result": "Only committed fixture preview diffs are present; no live, auth, official, or release-state artifacts are created.",
                "requires_manual_confirmation": True,
            }
        )
    return verification


def build_combined_offline_patch_rehearsal_packet(input_data: Mapping[str, Any]) -> Dict[str, Any]:
    """Build a deterministic fixture-first rehearsal packet from preview data."""
    data = _require_mapping(input_data, "input_data")
    _reject_forbidden_content(data)
    source_previews = [_require_mapping(item, "source_patch_preview") for item in _as_list(data.get("source_patch_previews"))]
    devhub_previews = [_require_mapping(item, "devhub_surface_preview") for item in _as_list(data.get("devhub_surface_previews"))]
    guardrail_previews = [_require_mapping(item, "guardrail_patch_preview") for item in _as_list(data.get("guardrail_patch_previews"))]
    all_previews = source_previews + devhub_previews + guardrail_previews

    if not source_previews or not devhub_previews or not guardrail_previews:
        raise ValueError("source, DevHub surface, and guardrail previews are all required")

    _require_preview_basics(all_previews)
    _require_explicit_dependency_ordering(source_previews, devhub_previews, guardrail_previews)

    attestations = dict(_REQUIRED_ATTESTATIONS)
    attestations.update({str(key): value for key, value in _require_mapping(data.get("attestations", {}), "attestations").items()})
    for key, expected in _REQUIRED_ATTESTATIONS.items():
        if attestations.get(key) is not expected:
            raise ValueError(f"attestation {key} must be {expected}")

    packet = {
        "packet_id": str(data.get("packet_id", "combined-offline-patch-rehearsal-v2")),
        "packet_version": "2",
        "mode": "fixture-first-offline",
        "summary": "Dependency-ordered offline rehearsal packet for source, DevHub surface, and guardrail patch previews.",
        "reviewer_owner_fields": {
            "source_owner": str(data.get("source_owner", "source-reviewer")),
            "devhub_surface_owner": str(data.get("devhub_surface_owner", "devhub-reviewer")),
            "guardrail_owner": str(data.get("guardrail_owner", "guardrail-reviewer")),
            "rollback_owner": str(data.get("rollback_owner", "release-reviewer")),
        },
        "dependency_ordered_rehearsal_steps": _dependency_ordered_steps(source_previews, devhub_previews, guardrail_previews),
        "cross_artifact_consistency_checks": _cross_artifact_checks(source_previews, devhub_previews, guardrail_previews),
        "expected_fixture_diffs": _expected_fixture_diffs(all_previews),
        "rollback_verification": _rollback_verification(all_previews),
        "offline_validation_commands": list(_OFFLINE_VALIDATION_COMMANDS),
        "attestations": attestations,
    }
    validate_combined_offline_patch_rehearsal_packet(packet)
    packet["validation_status"] = "pass"
    return packet


def validate_combined_offline_patch_rehearsal_packet(packet: Mapping[str, Any]) -> None:
    """Reject incomplete or unsafe combined offline rehearsal packets."""
    data = _require_mapping(packet, "packet")
    _reject_forbidden_content(data)

    steps = [_require_mapping(item, "dependency_ordered_rehearsal_step") for item in _as_list(data.get("dependency_ordered_rehearsal_steps"))]
    checks = [_require_mapping(item, "cross_artifact_consistency_check") for item in _as_list(data.get("cross_artifact_consistency_checks"))]
    diffs = [_require_mapping(item, "expected_fixture_diff") for item in _as_list(data.get("expected_fixture_diffs"))]
    rollbacks = [_require_mapping(item, "rollback_verification") for item in _as_list(data.get("rollback_verification"))]

    if not steps:
        raise ValueError("dependency_ordered_rehearsal_steps are required")
    if not checks:
        raise ValueError("cross_artifact_consistency_checks are required")
    if not diffs:
        raise ValueError("expected_fixture_diffs are required")
    if not rollbacks:
        raise ValueError("rollback_verification is required")

    seen_steps: set[str] = set()
    for step in steps:
        step_id = _require_non_empty_string(step, "step_id", "rehearsal step")
        citations = [str(value) for value in _as_list(step.get("citations")) if str(value)]
        if not citations:
            raise ValueError(f"rehearsal step lacks citations: {step_id}")
        if step.get("offline_only") is not True:
            raise ValueError(f"rehearsal step must be offline_only=true: {step_id}")
        for dependency in _as_list(step.get("depends_on")):
            dependency_id = str(dependency)
            if dependency_id not in seen_steps:
                raise ValueError(f"rehearsal step dependency is missing or out of order: {step_id} -> {dependency_id}")
        seen_steps.add(step_id)

    for check in checks:
        check_id = _require_non_empty_string(check, "check_id", "cross-artifact consistency check")
        if check.get("status") != "pass":
            raise ValueError(f"cross-artifact consistency check is not pass: {check_id}")

    diff_artifact_ids: set[str] = set()
    for diff in diffs:
        artifact_id = _require_non_empty_string(diff, "artifact_id", "expected fixture diff")
        fixture_path = _require_non_empty_string(diff, "fixture_path", "expected fixture diff")
        if not fixture_path.startswith("ppd/tests/fixtures/"):
            raise ValueError(f"expected fixture diff must stay under ppd/tests/fixtures: {artifact_id}")
        for key in ("expected_change", "before_hash", "after_hash"):
            _require_non_empty_string(diff, key, f"expected fixture diff {artifact_id}")
        diff_artifact_ids.add(artifact_id)

    for rollback in rollbacks:
        artifact_id = _require_non_empty_string(rollback, "artifact_id", "rollback verification")
        if artifact_id not in diff_artifact_ids:
            raise ValueError(f"rollback verification lacks matching expected fixture diff: {artifact_id}")
        if rollback.get("requires_manual_confirmation") is not True:
            raise ValueError(f"rollback verification must require manual confirmation: {artifact_id}")
        _require_non_empty_string(rollback, "expected_result", f"rollback verification {artifact_id}")


def _require_preview_basics(previews: Sequence[Mapping[str, Any]]) -> None:
    for preview in previews:
        artifact_id = _require_non_empty_string(preview, "artifact_id", "preview")
        fixture_path = _require_non_empty_string(preview, "fixture_path", f"preview {artifact_id}")
        if not fixture_path.startswith("ppd/tests/fixtures/"):
            raise ValueError(f"preview fixture_path must stay under ppd/tests/fixtures: {artifact_id}")
        citations = [str(value) for value in _as_list(preview.get("citations")) if str(value)]
        if not citations:
            raise ValueError(f"preview lacks citations: {artifact_id}")
        for key in ("expected_change", "before_hash", "after_hash"):
            _require_non_empty_string(preview, key, f"preview {artifact_id}")


def _require_explicit_dependency_ordering(
    source_previews: Sequence[Mapping[str, Any]],
    devhub_previews: Sequence[Mapping[str, Any]],
    guardrail_previews: Sequence[Mapping[str, Any]],
) -> None:
    source_ids = {str(preview["artifact_id"]) for preview in source_previews}
    devhub_ids = {str(preview["artifact_id"]) for preview in devhub_previews}
    known_ids = source_ids | devhub_ids

    for preview in devhub_previews:
        artifact_id = str(preview["artifact_id"])
        dependencies = {str(value) for value in _as_list(preview.get("depends_on")) if str(value)}
        if not dependencies:
            raise ValueError(f"DevHub surface preview lacks explicit source dependency ordering: {artifact_id}")
        missing = sorted(dependencies - source_ids)
        if missing:
            raise ValueError(f"DevHub surface preview has unresolved source dependencies: {artifact_id}: {missing}")

    for preview in guardrail_previews:
        artifact_id = str(preview["artifact_id"])
        dependencies = {str(value) for value in _as_list(preview.get("depends_on")) if str(value)}
        if not dependencies:
            raise ValueError(f"guardrail preview lacks explicit dependency ordering: {artifact_id}")
        if not dependencies.intersection(source_ids) or not dependencies.intersection(devhub_ids):
            raise ValueError(f"guardrail preview must depend on source and DevHub previews: {artifact_id}")
        missing = sorted(dependencies - known_ids)
        if missing:
            raise ValueError(f"guardrail preview has unresolved dependencies: {artifact_id}: {missing}")


def _reject_forbidden_content(value: Any, path: str = "$", key_name: str = "") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized_key = str(key).lower()
            child_path = f"{path}.{key}"
            if normalized_key in _PRIVATE_OR_AUTH_KEYS and child not in (None, "", [], {}, False):
                raise ValueError(f"private or authenticated facts are not allowed at {child_path}")
            if normalized_key in _RAW_ARTIFACT_KEYS and child not in (None, "", [], {}, False):
                raise ValueError(f"raw crawl/PDF/session/browser artifacts are not allowed at {child_path}")
            if normalized_key in _LIVE_OR_PROMOTION_KEYS and child not in (None, "", [], {}, False):
                raise ValueError(f"live execution or promotion claims are not allowed at {child_path}")
            if normalized_key in _MUTATION_FLAG_KEYS and child not in (None, "", [], {}, False):
                raise ValueError(f"active mutation flags are not allowed at {child_path}")
            _reject_forbidden_content(child, child_path, normalized_key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_content(child, f"{path}[{index}]", key_name)
    elif isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in _LEGAL_GUARANTEE_MARKERS):
            raise ValueError(f"legal or permitting outcome guarantees are not allowed at {path}")
        if key_name in _CONSEQUENTIAL_ACTION_KEYS and any(marker in lowered for marker in _CONSEQUENTIAL_ACTION_MARKERS):
            raise ValueError(f"consequential action language is not allowed at {path}")


def _require_non_empty_string(mapping: Mapping[str, Any], key: str, context: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{context} missing {key}")
    return value


def load_fixture_packet(path: Path) -> Dict[str, Any]:
    """Load fixture input JSON and return the generated rehearsal packet."""
    with path.open("r", encoding="utf-8") as handle:
        input_data = json.load(handle)
    return build_combined_offline_patch_rehearsal_packet(input_data)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build a combined offline patch rehearsal packet v2 from fixture previews.")
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    packet = load_fixture_packet(args.fixture)
    print(json.dumps(packet, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
