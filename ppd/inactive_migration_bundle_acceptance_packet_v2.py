from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


PACKET_TYPE = "ppd.inactive_migration_bundle_acceptance_packet.v2"
PACKET_VERSION = 2

REQUIRED_ATTESTATIONS = {
    "fixture_first_offline_only": True,
    "no_private_or_authenticated_facts": True,
    "no_raw_crawl_pdf_session_or_browser_artifacts": True,
    "no_live_execution_or_active_promotion": True,
    "no_legal_or_permitting_outcome_guarantees": True,
    "no_consequential_action_language": True,
    "no_active_source_surface_guardrail_prompt_monitoring_release_or_agent_mutation": True,
}

DECISIONS = {"accept", "defer", "reject"}

MUTATION_FLAG_KEYS = {
    "active_source_mutation",
    "active_surface_registry_mutation",
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_monitoring_mutation",
    "active_release_state_mutation",
    "active_agent_state_mutation",
    "source_mutation_enabled",
    "surface_registry_mutation_enabled",
    "guardrail_mutation_enabled",
    "prompt_mutation_enabled",
    "monitoring_mutation_enabled",
    "release_state_mutation_enabled",
    "agent_state_mutation_enabled",
    "mutates_source_registry",
    "mutates_surface_registry",
    "mutates_guardrails",
    "mutates_prompts",
    "mutates_monitoring",
    "mutates_release_state",
    "mutates_agent_state",
    "apply_source_changes",
    "apply_surface_registry_changes",
    "apply_guardrail_changes",
    "apply_prompt_changes",
    "apply_monitoring_changes",
    "apply_release_state_changes",
    "apply_agent_state_changes",
}

PRIVATE_OR_AUTH_KEYS = {
    "access_token",
    "auth_state",
    "authorization",
    "browser_context_state",
    "cookie",
    "credentials",
    "devhub_session_file",
    "oauth_token",
    "password",
    "private_applicant_value",
    "private_authenticated_fact",
    "private_case_fact",
    "private_owner_value",
    "session_state",
    "storage_state",
    "token",
}

RAW_ARTIFACT_KEYS = {
    "browser_artifact",
    "browser_artifacts",
    "crawl_body",
    "downloaded_pdf",
    "har",
    "har_path",
    "pdf_base64",
    "pdf_bytes",
    "raw_browser_artifact",
    "raw_crawl_artifact",
    "raw_crawl_body",
    "raw_devhub_value",
    "raw_pdf",
    "raw_pdf_artifact",
    "raw_pdf_body",
    "raw_session_artifact",
    "screenshot",
    "screenshot_path",
    "session_artifact",
    "trace",
    "trace_path",
}

LIVE_OR_PROMOTION_KEYS = {
    "active_promotion",
    "browser_execution",
    "devhub_execution",
    "live_browser_execution",
    "live_crawl_execution",
    "live_devhub_execution",
    "live_execution",
    "live_pdf_execution",
    "live_promotion",
    "promote_to_active",
    "promotion_executed",
}

PRIVATE_OR_RAW_TEXT_MARKERS = (
    "access token",
    "authenticated fact",
    "authorization header",
    "browser cookie",
    "cookie value",
    "devhub session",
    "har file",
    "oauth token",
    "password",
    "playwright trace",
    "private applicant",
    "private case fact",
    "private devhub value",
    "raw crawl",
    "raw pdf",
    "screenshot file",
    "session storage",
    "storage-state.json",
    "trace.zip",
)

LIVE_OR_PROMOTION_TEXT_MARKERS = (
    "executed against devhub",
    "live browser run",
    "live crawl completed",
    "live devhub run",
    "live execution completed",
    "promote this bundle",
    "promoted to active",
    "promotion completed",
    "release is live",
)

OUTCOME_GUARANTEE_MARKERS = (
    "approval is guaranteed",
    "guaranteed approval",
    "guaranteed permit",
    "permit will be approved",
    "will be legally sufficient",
    "will satisfy code",
)

CONSEQUENTIAL_ACTION_MARKERS = (
    "cancel inspection",
    "certify application",
    "final payment",
    "pay fees",
    "schedule inspection",
    "submit application",
    "submit payment",
    "upload correction",
    "upload plans",
)


class InactiveMigrationBundleAcceptancePacketV2Error(ValueError):
    pass


def load_inactive_migration_bundle_acceptance_packet_v2(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object at {path}")
    return data


def validate_inactive_migration_bundle_acceptance_packet_v2(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []

    if packet.get("packet_type") != PACKET_TYPE:
        errors.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("packet_version") != PACKET_VERSION:
        errors.append("packet_version must be 2")
    if packet.get("mode") != "fixture_first_inactive_acceptance_only":
        errors.append("mode must be fixture_first_inactive_acceptance_only")

    _validate_attestations(packet.get("attestations"), errors)
    _validate_bundle_rows(packet.get("bundle_acceptance_rows"), errors)
    _validate_cross_artifact_checks(packet.get("cross_artifact_consistency_checks"), errors)
    _validate_forbidden_content(packet, errors)

    return errors


def assert_inactive_migration_bundle_acceptance_packet_v2(packet: Mapping[str, Any]) -> None:
    errors = validate_inactive_migration_bundle_acceptance_packet_v2(packet)
    if errors:
        raise InactiveMigrationBundleAcceptancePacketV2Error("; ".join(errors))


def _validate_attestations(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("attestations must be an object")
        return
    for key, expected in REQUIRED_ATTESTATIONS.items():
        if value.get(key) is not expected:
            errors.append(f"attestations.{key} must be true")


def _validate_bundle_rows(value: Any, errors: list[str]) -> None:
    rows = value if isinstance(value, list) else []
    if not rows:
        errors.append("bundle_acceptance_rows must not be empty")
        return

    seen_targets: set[tuple[str, str, str]] = set()
    for index, row in enumerate(rows):
        path = f"bundle_acceptance_rows[{index}]"
        if not isinstance(row, Mapping):
            errors.append(path + " must be an object")
            continue

        for key in ("row_id", "bundle_id", "reviewer_owner", "rollback_checkpoint"):
            if not _text(row.get(key)):
                errors.append(path + f".{key} is required")

        decision = _text(row.get("decision")).lower()
        if decision not in DECISIONS:
            errors.append(path + ".decision must be accept, defer, or reject")
        if not _text(row.get("rationale")):
            errors.append(path + ".rationale is required for accept/defer/reject")
        if not _citations(row):
            errors.append(path + ".citations must be non-empty")

        target_ids = row.get("target_ids")
        if not isinstance(target_ids, Mapping):
            errors.append(path + ".target_ids must be an object")
            continue
        source_ids = _strings(target_ids.get("source_ids"))
        surface_ids = _strings(target_ids.get("surface_ids"))
        guardrail_ids = _strings(target_ids.get("guardrail_ids"))
        if not source_ids:
            errors.append(path + ".target_ids.source_ids must be non-empty")
        if not surface_ids:
            errors.append(path + ".target_ids.surface_ids must be non-empty")
        if not guardrail_ids:
            errors.append(path + ".target_ids.guardrail_ids must be non-empty")
        for source_id in source_ids:
            for surface_id in surface_ids:
                for guardrail_id in guardrail_ids:
                    seen_targets.add((source_id, surface_id, guardrail_id))

    checks = value if isinstance(value, list) else []
    if rows and not seen_targets:
        errors.append("bundle_acceptance_rows must include source, surface, and guardrail target IDs")


def _validate_cross_artifact_checks(value: Any, errors: list[str]) -> None:
    checks = value if isinstance(value, list) else []
    if not checks:
        errors.append("cross_artifact_consistency_checks must not be empty")
        return

    for index, check in enumerate(checks):
        path = f"cross_artifact_consistency_checks[{index}]"
        if not isinstance(check, Mapping):
            errors.append(path + " must be an object")
            continue
        for key in ("check_id", "source_id", "surface_id", "guardrail_id", "status", "reviewer_owner"):
            if not _text(check.get(key)):
                errors.append(path + f".{key} is required")
        if _text(check.get("status")) not in {"consistent", "deferred_with_reason", "rejected_with_reason"}:
            errors.append(path + ".status must be consistent, deferred_with_reason, or rejected_with_reason")
        if not _text(check.get("rationale")):
            errors.append(path + ".rationale is required")
        if not _citations(check):
            errors.append(path + ".citations must be non-empty")


def _validate_forbidden_content(value: Any, errors: list[str], path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            normalized_key = _normalize_key(key)
            if normalized_key in MUTATION_FLAG_KEYS and _active(child):
                errors.append(child_path + " declares an active mutation flag")
            if normalized_key in PRIVATE_OR_AUTH_KEYS and _present(child):
                errors.append(child_path + " contains private or authenticated facts")
            if normalized_key in RAW_ARTIFACT_KEYS and _present(child):
                errors.append(child_path + " contains raw crawl/PDF/session/browser artifacts")
            if normalized_key in LIVE_OR_PROMOTION_KEYS and _active(child):
                errors.append(child_path + " contains live execution or promotion claims")
            _validate_forbidden_content(child, errors, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_forbidden_content(child, errors, f"{path}[{index}]")
    elif isinstance(value, str):
        normalized = _normalize_text(value)
        if any(marker in normalized for marker in PRIVATE_OR_RAW_TEXT_MARKERS):
            errors.append(path + " contains private/authenticated facts or raw artifacts")
        if any(marker in normalized for marker in LIVE_OR_PROMOTION_TEXT_MARKERS):
            errors.append(path + " contains live execution or promotion claims")
        if any(marker in normalized for marker in OUTCOME_GUARANTEE_MARKERS):
            errors.append(path + " contains legal or permitting outcome guarantees")
        if any(marker in normalized for marker in CONSEQUENTIAL_ACTION_MARKERS):
            errors.append(path + " contains consequential action language")


def _citations(row: Mapping[str, Any]) -> list[str]:
    value = row.get("citations")
    if isinstance(value, list):
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return []


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return True


def _active(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"active", "enabled", "true", "yes", "promoted", "executed"}
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return False


def _normalize_key(value: Any) -> str:
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def _normalize_text(value: str) -> str:
    return " ".join(value.lower().replace("-", " ").replace("_", " ").split())
