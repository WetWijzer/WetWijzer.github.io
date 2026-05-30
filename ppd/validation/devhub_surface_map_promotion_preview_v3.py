"""Validate DevHub surface-map promotion preview v3 packets.

This validator is fixture-only and fail-closed. It validates proposed inactive
promotion preview rows before any surface/action patch candidate can be treated
as reviewable. It does not open DevHub, authenticate, run browser automation,
write registries, or create screenshots, traces, HAR files, session files, or
other private artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

PREVIEW_TYPE = "ppd.devhub_surface_map_promotion_preview.v3"
PREVIEW_VERSION = 3

_REQUIRED_ATTESTATIONS = {
    "fixture_first": True,
    "no_live_devhub": True,
    "no_browser_automation": True,
    "no_auth_state": True,
    "no_credentials": True,
    "no_private_values": True,
    "no_screenshots": True,
    "no_traces": True,
    "no_har": True,
    "no_active_surface_registry_mutation": True,
    "no_active_guardrail_mutation": True,
    "no_active_prompt_mutation": True,
    "no_active_monitoring_mutation": True,
    "no_active_release_state_mutation": True,
    "no_active_agent_state_mutation": True,
}

_PROHIBITED_KEY_TOKENS = (
    "access_token",
    "auth_state",
    "authorization",
    "bearer",
    "browser_context",
    "cookie",
    "credential",
    "devhub_session",
    "har",
    "local_storage",
    "login_secret",
    "password",
    "playwright_state",
    "private_value",
    "refresh_token",
    "screenshot",
    "secret",
    "session",
    "storage_state",
    "token",
    "trace",
)

_MUTATION_KEY_TOKENS = (
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_monitoring_mutation",
    "active_prompt_mutation",
    "active_registry_mutation",
    "active_release_state_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation",
    "apply_surface_registry_changes",
    "guardrail_mutation",
    "monitoring_mutation",
    "mutates_agent_state",
    "mutates_guardrails",
    "mutates_monitoring",
    "mutates_prompts",
    "mutates_release_state",
    "mutates_surface_registry",
    "prompt_mutation",
    "release_state_mutation",
    "surface_registry_mutation",
    "surface_registry_write",
    "update_surface_registry",
)

_PRIVATE_TEXT = (
    "access token",
    "authenticated value",
    "authorization header",
    "bearer token",
    "cookie value",
    "credential",
    "password",
    "private devhub value",
    "private value",
    "session cookie",
)

_SESSION_ARTIFACT_TEXT = (
    "auth state",
    "browser context state",
    "devhub session file",
    "local storage",
    "playwright state",
    "session artifact",
    "session storage",
    "storage-state.json",
    "storage state",
)

_BROWSER_ARTIFACT_TEXT = (
    ".har",
    ".webm",
    ".zip trace",
    "har file",
    "har path",
    "playwright trace",
    "screenshot file",
    "screenshot path",
    "trace.zip",
)

_LIVE_COMPLETION_TEXT = (
    "browser automation completed",
    "clicked in devhub",
    "devhub completed",
    "devhub live run completed",
    "live devhub completion",
    "opened devhub",
    "playwright clicked",
    "ran playwright",
)

_OUTCOME_GUARANTEE_TEXT = (
    "approval is guaranteed",
    "guaranteed approval",
    "guaranteed permit",
    "legal outcome guaranteed",
    "permit approved",
    "permit will be approved",
    "permitting outcome guaranteed",
    "will be approved",
    "will receive a permit",
)

_CONSEQUENTIAL_ACTION_TEXT = (
    "cancel request enabled",
    "certification enabled",
    "certify acknowledgement",
    "consequential action enabled",
    "enable payment",
    "enable scheduling",
    "enable submission",
    "final submit",
    "official upload enabled",
    "purchase permit",
    "schedule inspection",
    "submit application",
    "submit payment",
    "submit permit",
    "submission completed",
    "upload correction",
)


@dataclass(frozen=True)
class PromotionPreviewV3Violation:
    path: str
    code: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"path": self.path, "code": self.code, "message": self.message}


@dataclass(frozen=True)
class PromotionPreviewV3ValidationResult:
    ok: bool
    violations: tuple[PromotionPreviewV3Violation, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "violations": [violation.as_dict() for violation in self.violations]}


def validate_devhub_surface_map_promotion_preview_v3(packet: Mapping[str, Any]) -> PromotionPreviewV3ValidationResult:
    violations: list[PromotionPreviewV3Violation] = []

    if packet.get("preview_type") != PREVIEW_TYPE:
        violations.append(_violation("$", "invalid_preview_type", f"preview_type must be {PREVIEW_TYPE}"))
    if packet.get("preview_version") != PREVIEW_VERSION:
        violations.append(_violation("$", "invalid_preview_version", "preview_version must be 3"))
    if packet.get("mode") != "inactive_fixture_promotion_preview_only":
        violations.append(_violation("$.mode", "invalid_mode", "mode must be inactive_fixture_promotion_preview_only"))

    attestations = _mapping(packet.get("attestations"))
    for key, expected in _REQUIRED_ATTESTATIONS.items():
        if attestations.get(key) is not expected:
            violations.append(_violation(f"$.attestations.{key}", "missing_required_attestation", f"attestations.{key} must be {expected!r}"))

    candidates = _dicts(packet.get("surface_action_patch_candidates"))
    if not candidates:
        violations.append(_violation("$.surface_action_patch_candidates", "missing_patch_candidates", "surface_action_patch_candidates must be a non-empty list"))
    for index, candidate in enumerate(candidates):
        _validate_candidate(candidate, f"$.surface_action_patch_candidates[{index}]", violations)

    _reject_unsafe_content(packet, "$", violations)
    return PromotionPreviewV3ValidationResult(ok=not violations, violations=tuple(violations))


def require_devhub_surface_map_promotion_preview_v3(packet: Mapping[str, Any]) -> None:
    result = validate_devhub_surface_map_promotion_preview_v3(packet)
    if not result.ok:
        details = "; ".join(f"{violation.path}: {violation.code}" for violation in result.violations)
        raise ValueError("invalid DevHub surface-map promotion preview v3: " + details)


def _validate_candidate(candidate: Mapping[str, Any], path: str, violations: list[PromotionPreviewV3Violation]) -> None:
    for field in ("candidate_id", "surface_id", "patch_kind"):
        if not _text(candidate.get(field)):
            violations.append(_violation(f"{path}.{field}", "missing_candidate_field", f"{field} must be present"))

    if not _citations(candidate.get("citations")):
        violations.append(_violation(f"{path}.citations", "uncited_patch_candidate", "patch candidate must include at least one citation"))

    _validate_rows(path, "before_surface_rows", candidate.get("before_surface_rows"), violations)
    _validate_rows(path, "after_surface_rows", candidate.get("after_surface_rows"), violations)
    _validate_rows(path, "before_action_rows", candidate.get("before_action_rows"), violations)
    _validate_rows(path, "after_action_rows", candidate.get("after_action_rows"), violations)
    _validate_selector_deltas(path, candidate.get("selector_confidence_deltas"), violations)
    _validate_manual_handoff(path, candidate.get("manual_handoff_disposition"), violations)
    _validate_redaction(path, candidate.get("redaction_disposition"), violations)


def _validate_rows(path: str, field: str, value: Any, violations: list[PromotionPreviewV3Violation]) -> None:
    rows = _dicts(value)
    if not rows:
        violations.append(_violation(f"{path}.{field}", "missing_before_after_rows", f"{field} must contain at least one row"))
        return
    for index, row in enumerate(rows):
        row_path = f"{path}.{field}[{index}]"
        if not _text(row.get("row_id")):
            violations.append(_violation(f"{row_path}.row_id", "missing_row_id", "row_id must be present"))
        if not _text(row.get("surface_id")):
            violations.append(_violation(f"{row_path}.surface_id", "missing_row_surface_id", "surface_id must be present"))
        if not _citations(row.get("citations")):
            violations.append(_violation(f"{row_path}.citations", "uncited_patch_candidate", "row citations must be non-empty"))


def _validate_selector_deltas(path: str, value: Any, violations: list[PromotionPreviewV3Violation]) -> None:
    rows = _dicts(value)
    if not rows:
        violations.append(_violation(f"{path}.selector_confidence_deltas", "missing_selector_confidence_deltas", "selector_confidence_deltas must contain at least one row"))
        return
    for index, row in enumerate(rows):
        row_path = f"{path}.selector_confidence_deltas[{index}]"
        for field in ("surface_id", "selector", "before_confidence", "after_confidence", "delta_disposition"):
            if field not in row or not _present(row.get(field)):
                violations.append(_violation(f"{row_path}.{field}", "missing_selector_confidence_delta_field", f"{field} must be present"))
        if not _citations(row.get("citations")):
            violations.append(_violation(f"{row_path}.citations", "uncited_patch_candidate", "selector confidence delta citations must be non-empty"))


def _validate_manual_handoff(path: str, value: Any, violations: list[PromotionPreviewV3Violation]) -> None:
    row = _mapping(value)
    if not row:
        violations.append(_violation(f"{path}.manual_handoff_disposition", "missing_manual_handoff_disposition", "manual_handoff_disposition must be present"))
        return
    if row.get("required") is not True:
        violations.append(_violation(f"{path}.manual_handoff_disposition.required", "missing_manual_handoff_disposition", "manual handoff must be explicitly required"))
    if not _text(row.get("reason")):
        violations.append(_violation(f"{path}.manual_handoff_disposition.reason", "missing_manual_handoff_disposition", "manual handoff reason must be present"))
    if not _citations(row.get("citations")):
        violations.append(_violation(f"{path}.manual_handoff_disposition.citations", "uncited_patch_candidate", "manual handoff citations must be non-empty"))


def _validate_redaction(path: str, value: Any, violations: list[PromotionPreviewV3Violation]) -> None:
    row = _mapping(value)
    if not row:
        violations.append(_violation(f"{path}.redaction_disposition", "missing_redaction_disposition", "redaction_disposition must be present"))
        return
    if _text(row.get("disposition")) not in {"synthetic_only", "redacted", "public_metadata_only"}:
        violations.append(_violation(f"{path}.redaction_disposition.disposition", "missing_redaction_disposition", "redaction disposition must be synthetic_only, redacted, or public_metadata_only"))
    if not _text(row.get("reason")):
        violations.append(_violation(f"{path}.redaction_disposition.reason", "missing_redaction_disposition", "redaction reason must be present"))
    if not _citations(row.get("citations")):
        violations.append(_violation(f"{path}.redaction_disposition.citations", "uncited_patch_candidate", "redaction citations must be non-empty"))


def _reject_unsafe_content(value: Any, path: str, violations: list[PromotionPreviewV3Violation]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            normalized = _normalize_key(key)
            if any(token in normalized for token in _PROHIBITED_KEY_TOKENS) and _present(child):
                violations.append(_violation(child_path, "prohibited_private_or_auth_artifact", "private, credential, auth, session, screenshot, trace, or HAR fields are prohibited"))
            if any(token in normalized for token in _MUTATION_KEY_TOKENS) and _active_flag(child):
                violations.append(_violation(child_path, "active_mutation_flag", "active surface-registry, guardrail, prompt, monitoring, release-state, or agent-state mutation flags are prohibited"))
            _reject_unsafe_content(child, child_path, violations)
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _reject_unsafe_content(child, f"{path}[{index}]", violations)
        return
    if isinstance(value, str):
        lowered = " ".join(value.lower().split())
        if any(term in lowered for term in _PRIVATE_TEXT):
            violations.append(_violation(path, "prohibited_private_or_authenticated_value", "private/authenticated values or credentials are prohibited"))
        if any(term in lowered for term in _SESSION_ARTIFACT_TEXT):
            violations.append(_violation(path, "prohibited_session_or_auth_artifact", "session/auth artifacts are prohibited"))
        if any(term in lowered for term in _BROWSER_ARTIFACT_TEXT):
            violations.append(_violation(path, "prohibited_browser_artifact_reference", "screenshots, traces, HAR files, and browser artifacts are prohibited"))
        if any(term in lowered for term in _LIVE_COMPLETION_TEXT):
            violations.append(_violation(path, "prohibited_live_devhub_completion_claim", "browser automation and live DevHub completion claims are prohibited"))
        if any(term in lowered for term in _OUTCOME_GUARANTEE_TEXT):
            violations.append(_violation(path, "prohibited_outcome_guarantee", "legal or permitting outcome guarantees are prohibited"))
        if any(term in lowered for term in _CONSEQUENTIAL_ACTION_TEXT):
            violations.append(_violation(path, "prohibited_consequential_action_enablement", "consequential action enablement is prohibited"))


def _violation(path: str, code: str, message: str) -> PromotionPreviewV3Violation:
    return PromotionPreviewV3Violation(path=path, code=code, message=message)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _citations(value: Any) -> list[Mapping[str, Any]]:
    citations = []
    for item in _dicts(value):
        if _text(item.get("source_id")) and (_text(item.get("url")) or _text(item.get("citation"))):
            citations.append(item)
    return citations


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


def _active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"active", "enabled", "true", "yes", "write", "mutate"}
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return False


def _normalize_key(value: object) -> str:
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def validate_many_devhub_surface_map_promotion_preview_v3(packets: Sequence[Mapping[str, Any]]) -> tuple[PromotionPreviewV3ValidationResult, ...]:
    return tuple(validate_devhub_surface_map_promotion_preview_v3(packet) for packet in packets)
