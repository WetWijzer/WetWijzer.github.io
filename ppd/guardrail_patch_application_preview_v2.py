"""Fixture-first guardrail patch application preview v2.

Consumes an implementation patch staging plan v2 and a post-dry-run guardrail
impact review v2 into inactive guardrail fixture preview rows. This module is
metadata-only: it does not call an LLM, open DevHub, crawl, run processors,
mutate guardrails, mutate prompts, or change release state.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from ppd.implementation_patch_staging_plan_v2 import (
    build_implementation_patch_staging_plan_v2_from_fixture,
    validate_implementation_patch_staging_plan_v2,
)
from ppd.logic.post_dry_run_guardrail_impact_review_v2 import (
    REVIEW_SCHEMA_VERSION,
    assert_valid_post_dry_run_guardrail_impact_review_v2,
)

PREVIEW_TYPE = "ppd.guardrail_patch_application_preview.v2"
PREVIEW_VERSION = 2

ATTESTATIONS = {
    "no_live_llm": True,
    "no_devhub": True,
    "no_crawler": True,
    "no_processor": True,
    "no_guardrail_mutation": True,
    "no_prompt_mutation": True,
    "no_release_state_mutation": True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/guardrail_patch_application_preview_v2.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_guardrail_patch_application_preview_v2.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_PROHIBITED_KEYS = {
    "auth_state",
    "browser_artifact",
    "browser_session",
    "crawl_output",
    "devhub_session",
    "downloaded_document",
    "har",
    "llm_response",
    "payment_details",
    "private_fact",
    "private_value",
    "raw_body",
    "raw_crawl",
    "raw_download",
    "raw_html",
    "raw_pdf",
    "screenshot",
    "session_artifact",
    "session_state",
    "storage_state",
    "trace",
}

_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_monitoring_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_source_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation",
    "apply_guardrail_changes",
    "guardrail_mutation",
    "guardrail_mutation_enabled",
    "monitoring_mutation",
    "mutates_agent_state",
    "mutates_guardrails",
    "mutates_monitoring",
    "mutates_prompts",
    "mutates_release_state",
    "prompt_mutation",
    "prompt_mutation_enabled",
    "release_state_mutation",
    "release_state_mutation_enabled",
    "update_guardrails",
    "update_prompts",
}

_PRIVATE_TEXT = (
    "authenticated value",
    "credential",
    "mfa",
    "password",
    "private devhub value",
    "private fact",
    "session token",
)

_LIVE_TEXT = (
    "called live llm",
    "crawler completed",
    "devhub live run completed",
    "live crawler completed",
    "live devhub",
    "live llm",
    "opened devhub",
    "processor completed",
    "ran crawler",
    "ran llm",
    "ran processor",
)

_OUTCOME_TEXT = (
    "approval is guaranteed",
    "guaranteed approval",
    "guaranteed permit",
    "legal outcome guaranteed",
    "permit will be approved",
    "will be approved",
)

_CONSEQUENTIAL_TEXT = (
    "cancel permit",
    "certify acknowledgement",
    "enable payment",
    "enable scheduling",
    "enable submission",
    "final submit",
    "official upload enabled",
    "schedule inspection",
    "submit application",
    "submit payment",
    "upload correction",
)


@dataclass(frozen=True)
class GuardrailPatchApplicationPreviewV2ValidationResult:
    ok: bool
    errors: tuple[str, ...]


def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def build_guardrail_patch_application_preview_v2_from_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    fixture = load_json(fixture_path)
    base = fixture_path.parent
    plan = build_implementation_patch_staging_plan_v2_from_fixture(base / _required_text(fixture, "implementation_patch_staging_plan_v2_fixture"))
    review = load_json(base / _required_text(fixture, "post_dry_run_guardrail_impact_review_v2_fixture"))
    return build_guardrail_patch_application_preview_v2(plan, review)


def build_guardrail_patch_application_preview_v2(
    implementation_patch_staging_plan_v2: Mapping[str, Any],
    post_dry_run_guardrail_impact_review_v2: Mapping[str, Any],
) -> dict[str, Any]:
    plan_result = validate_implementation_patch_staging_plan_v2(implementation_patch_staging_plan_v2)
    if not plan_result.ok:
        raise ValueError("invalid implementation patch staging plan v2: " + "; ".join(plan_result.errors))
    review = dict(post_dry_run_guardrail_impact_review_v2)
    assert_valid_post_dry_run_guardrail_impact_review_v2(review)

    decisions = _dicts(review.get("impact_decisions"))
    blocked_checks = _dicts(review.get("blocked_action_checks"))
    predicate_ids = _strings(review.get("predicate_ids"))
    bundle_id = _text(review.get("guardrail_bundle_id"))
    review_citations = _review_citations(review)

    previews: list[dict[str, Any]] = []
    for staged in _dicts(implementation_patch_staging_plan_v2.get("inactive_guardrail_patch_candidates")):
        target_id = _text(staged.get("target_id"))
        matched_decisions = [row for row in decisions if target_id in {_text(row.get("decision_id")), bundle_id}]
        matched_checks = [row for row in blocked_checks if target_id == _text(row.get("action_id"))]
        if not matched_decisions and not matched_checks and target_id != bundle_id:
            continue
        citations = _dicts(staged.get("citations")) + review_citations
        target_predicates = sorted({pid for row in matched_decisions for pid in _strings(row.get("predicate_ids"))}) or predicate_ids
        preview_bundle_id = bundle_id or target_id
        previews.append(
            {
                "preview_id": f"guardrail-preview-{_slug(target_id)}",
                "guardrail_patch_candidate_id": _text(staged.get("candidate_id")),
                "target_id": target_id,
                "guardrail_bundle_id": preview_bundle_id,
                "affected_guardrail_bundle_ids": [preview_bundle_id],
                "inactive": True,
                "guardrail_fixture_patch": True,
                "reviewer_owner": _text(staged.get("reviewer_owner")) or _reviewer_owner(review),
                "before_predicate_rows": _before_predicate_rows(preview_bundle_id, target_predicates, citations),
                "after_predicate_rows": _after_predicate_rows(preview_bundle_id, target_predicates, matched_decisions, citations),
                "blocked_consequential_action_checks": _blocked_action_rows(matched_checks or blocked_checks, citations),
                "explanation_template_deltas": _explanation_template_deltas(preview_bundle_id, target_predicates, citations),
                "rollback_checkpoint": _text(staged.get("rollback_checkpoint")) or _text(review.get("rollback_notes")),
                "citations": citations,
            }
        )

    packet = {
        "preview_type": PREVIEW_TYPE,
        "preview_version": PREVIEW_VERSION,
        "fixture_first": True,
        "mode": "inactive_guardrail_fixture_patch_preview_only",
        "consumes": {
            "implementation_patch_staging_plan_v2": _text(implementation_patch_staging_plan_v2.get("plan_type")),
            "post_dry_run_guardrail_impact_review_v2": _text(review.get("schema_version")),
        },
        "affected_guardrail_bundle_ids": sorted({bundle for preview in previews for bundle in _strings(preview.get("affected_guardrail_bundle_ids"))}),
        "guardrail_fixture_patch_previews": previews,
        "reviewer_owner_fields": _owner_rows(previews),
        "rollback_checkpoints": _rollback_rows(previews),
        "offline_validation_commands": list(OFFLINE_VALIDATION_COMMANDS),
        "attestations": dict(ATTESTATIONS),
    }
    require_guardrail_patch_application_preview_v2(packet)
    return packet


def validate_guardrail_patch_application_preview_v2(packet: Mapping[str, Any]) -> GuardrailPatchApplicationPreviewV2ValidationResult:
    errors: list[str] = []
    if packet.get("preview_type") != PREVIEW_TYPE:
        errors.append(f"preview_type must be {PREVIEW_TYPE}")
    if packet.get("preview_version") != PREVIEW_VERSION:
        errors.append("preview_version must be 2")
    if packet.get("fixture_first") is not True:
        errors.append("fixture_first must be true")
    if packet.get("mode") != "inactive_guardrail_fixture_patch_preview_only":
        errors.append("mode must be inactive_guardrail_fixture_patch_preview_only")
    consumes = _mapping(packet.get("consumes"))
    if consumes.get("implementation_patch_staging_plan_v2") != "ppd.implementation_patch_staging_plan.v2":
        errors.append("consumes.implementation_patch_staging_plan_v2 must reference implementation patch staging plan v2")
    if consumes.get("post_dry_run_guardrail_impact_review_v2") != REVIEW_SCHEMA_VERSION:
        errors.append("consumes.post_dry_run_guardrail_impact_review_v2 must reference post-dry-run guardrail impact review v2")
    affected = _strings(packet.get("affected_guardrail_bundle_ids"))
    if not affected:
        errors.append("affected_guardrail_bundle_ids must be non-empty")
    _validate_previews(packet.get("guardrail_fixture_patch_previews"), affected, errors)
    _validate_owner_rows(packet.get("reviewer_owner_fields"), errors)
    _validate_rollback_rows(packet.get("rollback_checkpoints"), errors)
    if packet.get("attestations") != ATTESTATIONS:
        errors.append("attestations must preserve no-live-LLM/no-DevHub/no-crawler/no-processor/no-guardrail/no-prompt/no-release-state-mutation guardrails")
    commands = packet.get("offline_validation_commands")
    if not isinstance(commands, list) or not commands:
        errors.append("offline_validation_commands must be non-empty")
    elif not all(isinstance(command, list) and _strings(command) for command in commands):
        errors.append("offline_validation_commands must contain command lists")
    _reject_unsafe_content(packet, "$", errors)
    return GuardrailPatchApplicationPreviewV2ValidationResult(not errors, tuple(errors))


def require_guardrail_patch_application_preview_v2(packet: Mapping[str, Any]) -> None:
    result = validate_guardrail_patch_application_preview_v2(packet)
    if not result.ok:
        raise ValueError("invalid guardrail patch application preview v2: " + "; ".join(result.errors))


def _before_predicate_rows(bundle_id: str, predicate_ids: list[str], citations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "row_id": f"before-predicate-{_slug(bundle_id)}-{_slug(predicate_id)}",
            "guardrail_bundle_id": bundle_id,
            "predicate_id": predicate_id,
            "predicate_state": "current_fixture_predicate_retained",
            "row_state": "before_inactive_preview",
            "citations": citations,
        }
        for predicate_id in predicate_ids
    ]


def _after_predicate_rows(bundle_id: str, predicate_ids: list[str], decisions: list[Mapping[str, Any]], citations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    outcome = "; ".join(_text(row.get("outcome")) for row in decisions if _text(row.get("outcome"))) or "Review candidate keeps consequential actions blocked."
    return [
        {
            "row_id": f"after-predicate-{_slug(bundle_id)}-{_slug(predicate_id)}",
            "guardrail_bundle_id": bundle_id,
            "predicate_id": predicate_id,
            "predicate_state": "after_inactive_fixture_preview",
            "delta_summary": outcome,
            "citations": citations,
        }
        for predicate_id in predicate_ids
    ]


def _blocked_action_rows(checks: list[Mapping[str, Any]], citations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "check_id": f"blocked-{_slug(_text(check.get('action_id')))}",
            "action_id": _text(check.get("action_id")),
            "blocked": check.get("blocked") is True,
            "reason": _text(check.get("rationale")) or "Consequential action remains blocked pending attended exact confirmation.",
            "citations": citations + _citation_id_rows(check),
        }
        for check in checks
        if _text(check.get("action_id"))
    ]


def _explanation_template_deltas(bundle_id: str, predicate_ids: list[str], citations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "template_delta_id": f"template-delta-{_slug(bundle_id)}-{_slug(predicate_id)}",
            "guardrail_bundle_id": bundle_id,
            "predicate_id": predicate_id,
            "before_template": "Use current fixture explanation template.",
            "after_template": "Explain that this inactive fixture preview preserves the consequential-action block until reviewer approval and exact user confirmation.",
            "delta_disposition": "review_required_before_any_active_guardrail_or_prompt_change",
            "citations": citations,
        }
        for predicate_id in predicate_ids
    ]


def _owner_rows(previews: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for preview in previews:
        owner = _text(preview.get("reviewer_owner"))
        bundle_id = _text(preview.get("guardrail_bundle_id"))
        key = (owner, bundle_id)
        if owner and bundle_id and key not in seen:
            seen.add(key)
            rows.append({"owner_field_id": f"owner-{_slug(owner)}-{_slug(bundle_id)}", "reviewer_owner": owner, "guardrail_bundle_id": bundle_id, "citations": _dicts(preview.get("citations"))})
    return rows


def _rollback_rows(previews: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        {
            "checkpoint_id": "discard-guardrail-patch-application-preview-v2",
            "summary": "Discard this inactive preview packet and rerun fixture validation; guardrail fixtures, prompts, and release state remain unchanged.",
            "affected_guardrail_bundle_ids": sorted({_text(preview.get("guardrail_bundle_id")) for preview in previews if _text(preview.get("guardrail_bundle_id"))}),
            "citations": [citation for preview in previews for citation in _dicts(preview.get("citations"))],
        }
    ]
    for preview in previews:
        rows.append(
            {
                "checkpoint_id": f"discard-{_slug(_text(preview.get('target_id')))}-guardrail-preview-row",
                "summary": _text(preview.get("rollback_checkpoint")) or "Discard this inactive guardrail preview row.",
                "affected_guardrail_bundle_ids": _strings(preview.get("affected_guardrail_bundle_ids")),
                "citations": _dicts(preview.get("citations")),
            }
        )
    return rows


def _validate_previews(value: Any, packet_affected: list[str], errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append("guardrail_fixture_patch_previews must be non-empty")
        return
    for index, row in enumerate(rows):
        path = f"guardrail_fixture_patch_previews[{index}]"
        for field in ("preview_id", "guardrail_patch_candidate_id", "target_id", "guardrail_bundle_id", "reviewer_owner", "rollback_checkpoint"):
            if not _text(row.get(field)):
                errors.append(f"{path}.{field} must be present")
        if row.get("inactive") is not True:
            errors.append(f"{path}.inactive must be true")
        if row.get("guardrail_fixture_patch") is not True:
            errors.append(f"{path}.guardrail_fixture_patch must be true")
        affected = _strings(row.get("affected_guardrail_bundle_ids"))
        if not affected:
            errors.append(f"{path}.affected_guardrail_bundle_ids must be non-empty")
        for bundle_id in affected:
            if bundle_id not in packet_affected:
                errors.append(f"{path}.affected_guardrail_bundle_ids must be included in packet affected_guardrail_bundle_ids")
        _validate_predicate_rows(path, "before_predicate_rows", row.get("before_predicate_rows"), errors)
        _validate_predicate_rows(path, "after_predicate_rows", row.get("after_predicate_rows"), errors)
        _validate_blocked_checks(path, row.get("blocked_consequential_action_checks"), errors)
        _validate_template_deltas(path, row.get("explanation_template_deltas"), errors)
        if not _dicts(row.get("citations")):
            errors.append(f"{path}.citations must be non-empty")


def _validate_predicate_rows(path: str, field: str, value: Any, errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append(f"{path}.{field} must be non-empty")
        return
    for index, row in enumerate(rows):
        row_path = f"{path}.{field}[{index}]"
        for required in ("row_id", "guardrail_bundle_id", "predicate_id", "predicate_state"):
            if not _text(row.get(required)):
                errors.append(f"{row_path}.{required} must be present")
        if not _dicts(row.get("citations")):
            errors.append(f"{row_path}.citations must be non-empty")


def _validate_blocked_checks(path: str, value: Any, errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append(f"{path}.blocked_consequential_action_checks must be non-empty")
        return
    for index, row in enumerate(rows):
        row_path = f"{path}.blocked_consequential_action_checks[{index}]"
        if not _text(row.get("check_id")) or not _text(row.get("action_id")):
            errors.append(f"{row_path} must include check_id and action_id")
        if row.get("blocked") is not True:
            errors.append(f"{row_path}.blocked must be true")
        if not _text(row.get("reason")):
            errors.append(f"{row_path}.reason must be present")
        if not _dicts(row.get("citations")):
            errors.append(f"{row_path}.citations must be non-empty")


def _validate_template_deltas(path: str, value: Any, errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append(f"{path}.explanation_template_deltas must be non-empty")
        return
    for index, row in enumerate(rows):
        row_path = f"{path}.explanation_template_deltas[{index}]"
        for required in ("template_delta_id", "guardrail_bundle_id", "predicate_id", "before_template", "after_template", "delta_disposition"):
            if not _text(row.get(required)):
                errors.append(f"{row_path}.{required} must be present")
        if not _dicts(row.get("citations")):
            errors.append(f"{row_path}.citations must be non-empty")


def _validate_owner_rows(value: Any, errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append("reviewer_owner_fields must be non-empty")
        return
    for index, row in enumerate(rows):
        if not _text(row.get("owner_field_id")) or not _text(row.get("reviewer_owner")) or not _text(row.get("guardrail_bundle_id")):
            errors.append(f"reviewer_owner_fields[{index}] must include owner_field_id, reviewer_owner, and guardrail_bundle_id")
        if not _dicts(row.get("citations")):
            errors.append(f"reviewer_owner_fields[{index}].citations must be non-empty")


def _validate_rollback_rows(value: Any, errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append("rollback_checkpoints must be non-empty")
        return
    for index, row in enumerate(rows):
        if not _text(row.get("checkpoint_id")) or not _text(row.get("summary")):
            errors.append(f"rollback_checkpoints[{index}] must include checkpoint_id and summary")
        if not _strings(row.get("affected_guardrail_bundle_ids")):
            errors.append(f"rollback_checkpoints[{index}].affected_guardrail_bundle_ids must be non-empty")
        if not _dicts(row.get("citations")):
            errors.append(f"rollback_checkpoints[{index}].citations must be non-empty")


def _reject_unsafe_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            normalized = str(key).lower().replace("-", "_")
            if normalized in _PROHIBITED_KEYS and _present(child):
                errors.append(f"{child_path} is prohibited in guardrail patch application previews")
            if normalized in _MUTATION_KEYS and _is_active_flag(child):
                errors.append(f"{child_path} active mutation flags are not allowed")
            _reject_unsafe_content(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_unsafe_content(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        lowered = " ".join(value.lower().split())
        if any(term in lowered for term in _PRIVATE_TEXT):
            errors.append(f"{path} contains prohibited private, credential, session, or authenticated value language")
        if any(term in lowered for term in _LIVE_TEXT):
            errors.append(f"{path} contains prohibited live LLM, DevHub, crawler, or processor execution claim")
        if any(term in lowered for term in _OUTCOME_TEXT):
            errors.append(f"{path} contains prohibited legal or permitting outcome guarantee")
        if any(term in lowered for term in _CONSEQUENTIAL_TEXT):
            errors.append(f"{path} contains prohibited consequential official-action language")


def _review_citations(review: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for decision in _dicts(review.get("impact_decisions")):
        rows.extend(_citation_id_rows(decision))
    for check in _dicts(review.get("blocked_action_checks")):
        rows.extend(_citation_id_rows(check))
    if not rows:
        rows.append({"packet_field": "post_dry_run_guardrail_impact_review_v2"})
    return rows


def _citation_id_rows(row: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [{"citation_id": citation_id} for citation_id in _strings(row.get("citation_ids"))]


def _reviewer_owner(review: Mapping[str, Any]) -> str:
    for owner in _dicts(review.get("reviewer_owners")):
        value = _text(owner.get("owner_id")) or _text(owner.get("team")) or _text(owner.get("name"))
        if value:
            return value
    return "ppd-guardrail-reviewer"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [item.strip() for item in value if isinstance(item, str) and item.strip()] if isinstance(value, list) else []


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = _text(mapping.get(key))
    if not value:
        raise ValueError(f"fixture must provide {key}")
    return value


def _is_active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"active", "enabled", "true", "yes"}
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return False


def _present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return True


def _slug(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value)
    return "-".join(part for part in cleaned.split("-") if part) or "item"
