"""Hardening checks for guardrail patch application preview v2 packets.

This module is side-effect free. It validates already-loaded preview packets and
never crawls, opens DevHub, calls an LLM, runs processors, downloads PDFs, or
mutates guardrails, prompts, source registries, monitoring, release state, or
agent state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


_PREVIEW_TYPE = "ppd.guardrail_patch_application_preview.v2"

_CITATION_KEYS = frozenset(
    {
        "citation_id",
        "document_id",
        "packet_field",
        "source_evidence_id",
        "source_id",
        "url",
    }
)

_PROHIBITED_KEYS = frozenset(
    {
        "archive_path",
        "auth_state",
        "authenticated_fact",
        "authenticated_value",
        "browser_artifact",
        "browser_session",
        "crawl_output",
        "devhub_session",
        "download_path",
        "downloaded_document",
        "har",
        "llm_response",
        "payment_details",
        "pdf_bytes",
        "pdf_path",
        "private_fact",
        "private_value",
        "raw_body",
        "raw_crawl",
        "raw_download",
        "raw_html",
        "raw_pdf",
        "response_body",
        "screenshot",
        "session_artifact",
        "session_file",
        "session_state",
        "storage_state",
        "trace",
        "trace_zip",
    }
)

_MUTATION_KEYS = frozenset(
    {
        "active_agent_state_mutation",
        "active_guardrail_mutation",
        "active_monitoring_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_source_mutation",
        "active_source_registry_mutation",
        "active_surface_registry_mutation",
        "agent_state_mutation",
        "apply_guardrail_changes",
        "guardrail_mutation",
        "guardrail_mutation_enabled",
        "monitoring_mutation",
        "monitoring_mutation_enabled",
        "mutates_active_agent_state",
        "mutates_active_guardrails",
        "mutates_active_monitoring",
        "mutates_active_prompts",
        "mutates_active_release_state",
        "mutates_active_source_registry",
        "mutates_active_sources",
        "mutates_active_surface_registry",
        "mutates_agent_state",
        "mutates_guardrails",
        "mutates_monitoring",
        "mutates_prompts",
        "mutates_release_state",
        "mutates_source_registry",
        "mutates_sources",
        "mutates_surface_registry",
        "prompt_mutation",
        "prompt_mutation_enabled",
        "release_state_mutation",
        "release_state_mutation_enabled",
        "source_mutation",
        "source_registry_mutation",
        "source_registry_mutation_enabled",
        "surface_registry_mutation",
        "surface_registry_mutation_enabled",
        "update_guardrails",
        "update_prompts",
        "update_source_registry",
        "update_surface_registry",
    }
)

_PRIVATE_TEXT = (
    "authenticated fact",
    "authenticated value",
    "captcha",
    "cookie",
    "credential",
    "mfa",
    "password",
    "private devhub value",
    "private fact",
    "private user value",
    "session token",
)

_RAW_ARTIFACT_TEXT = (
    ".har",
    ".trace",
    "downloaded document",
    "raw body",
    "raw crawl",
    "raw html",
    "raw pdf",
    "screenshot",
    "storage_state.json",
    "trace.zip",
)

_LIVE_EXECUTION_TEXT = (
    "called devhub",
    "called live llm",
    "clicked devhub",
    "crawler completed",
    "devhub live run completed",
    "executed crawler",
    "executed devhub",
    "executed llm",
    "executed processor",
    "filled devhub",
    "live crawler",
    "live devhub",
    "live llm",
    "live processor",
    "opened devhub",
    "processor completed",
    "ran crawler",
    "ran devhub",
    "ran llm",
    "ran processor",
)

_OUTCOME_TEXT = (
    "approval guaranteed",
    "approval is guaranteed",
    "guarantee approval",
    "guaranteed approval",
    "guaranteed permit",
    "legal advice",
    "legal outcome guaranteed",
    "permit will be approved",
    "will be approved",
    "will pass inspection",
)

_FINAL_ACTION_TEXT = (
    "cancel inspection",
    "cancel permit",
    "cancellation completed",
    "certify acknowledgement",
    "enable cancellation",
    "enable payment",
    "enable scheduling",
    "enable submission",
    "enable upload",
    "final payment",
    "final submit",
    "official upload enabled",
    "paid fee",
    "payment submitted",
    "schedule inspection",
    "scheduled inspection",
    "submit application",
    "submit payment",
    "submitted application",
    "submitted permit",
    "upload correction",
    "upload corrections",
    "uploaded correction",
    "uploaded documents",
)


@dataclass(frozen=True)
class GuardrailPatchApplicationPreviewV2HardeningResult:
    ok: bool
    errors: tuple[str, ...]


def validate_guardrail_patch_application_preview_v2_hardening(
    packet: Mapping[str, Any],
) -> GuardrailPatchApplicationPreviewV2HardeningResult:
    errors: list[str] = []
    if packet.get("preview_type") != _PREVIEW_TYPE:
        errors.append(f"preview_type must be {_PREVIEW_TYPE}")

    previews = _dicts(packet.get("guardrail_fixture_patch_previews"))
    if not previews:
        errors.append("guardrail_fixture_patch_previews must be non-empty")
    for index, preview in enumerate(previews):
        _validate_preview(index, preview, errors)

    _validate_rollback_checkpoints(packet.get("rollback_checkpoints"), errors)
    _reject_unsafe_content(packet, "$", errors)
    return GuardrailPatchApplicationPreviewV2HardeningResult(not errors, tuple(errors))


def require_guardrail_patch_application_preview_v2_hardening(packet: Mapping[str, Any]) -> None:
    result = validate_guardrail_patch_application_preview_v2_hardening(packet)
    if not result.ok:
        raise ValueError("invalid hardened guardrail patch application preview v2: " + "; ".join(result.errors))


def _validate_preview(index: int, preview: Mapping[str, Any], errors: list[str]) -> None:
    path = f"guardrail_fixture_patch_previews[{index}]"
    _validate_citations(f"{path}.citations", preview.get("citations"), errors)
    _validate_rows(path, "before_predicate_rows", preview.get("before_predicate_rows"), errors)
    _validate_rows(path, "after_predicate_rows", preview.get("after_predicate_rows"), errors)
    _validate_rows(path, "blocked_consequential_action_checks", preview.get("blocked_consequential_action_checks"), errors)
    _validate_rows(path, "explanation_template_deltas", preview.get("explanation_template_deltas"), errors)
    if not _text(preview.get("rollback_checkpoint")):
        errors.append(f"{path}.rollback_checkpoint must be present")


def _validate_rows(path: str, field: str, value: Any, errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append(f"{path}.{field} must be non-empty")
        return
    for index, row in enumerate(rows):
        row_path = f"{path}.{field}[{index}]"
        _validate_citations(f"{row_path}.citations", row.get("citations"), errors)


def _validate_rollback_checkpoints(value: Any, errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append("rollback_checkpoints must be non-empty")
        return
    for index, row in enumerate(rows):
        path = f"rollback_checkpoints[{index}]"
        if not _text(row.get("checkpoint_id")) or not _text(row.get("summary")):
            errors.append(f"{path} must include checkpoint_id and summary")
        _validate_citations(f"{path}.citations", row.get("citations"), errors)


def _validate_citations(path: str, value: Any, errors: list[str]) -> None:
    rows = _dicts(value)
    if not rows:
        errors.append(f"{path} must be non-empty")
        return
    for index, row in enumerate(rows):
        row_path = f"{path}[{index}]"
        if not any(_text(row.get(key)) for key in _CITATION_KEYS):
            errors.append(f"{row_path} must include a citation identifier, source id, URL, packet field, or document id")
        url = _text(row.get("url"))
        if url and "@" in url.split("//", 1)[-1].split("/", 1)[0]:
            errors.append(f"{row_path}.url authenticated URLs are not allowed")


def _reject_unsafe_content(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            normalized = str(key).lower().replace("-", "_")
            if normalized in _PROHIBITED_KEYS and _present(child):
                errors.append(f"{child_path} raw crawl, PDF, session, browser, private, or authenticated artifacts are not allowed")
            if normalized in _MUTATION_KEYS and _active(child):
                errors.append(f"{child_path} active guardrail, prompt, source, surface-registry, monitoring, release-state, or agent-state mutation flags are not allowed")
            _reject_unsafe_content(child, child_path, errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_unsafe_content(child, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        lowered = " ".join(value.lower().split())
        if any(term in lowered for term in _PRIVATE_TEXT):
            errors.append(f"{path} contains prohibited private, credential, session, or authenticated fact language")
        if any(term in lowered for term in _RAW_ARTIFACT_TEXT):
            errors.append(f"{path} contains prohibited raw crawl, PDF, session, or browser artifact language")
        if any(term in lowered for term in _LIVE_EXECUTION_TEXT):
            errors.append(f"{path} contains prohibited live LLM, DevHub, crawler, or processor execution claim")
        if any(term in lowered for term in _OUTCOME_TEXT):
            errors.append(f"{path} contains prohibited legal or permitting outcome guarantee")
        if any(term in lowered for term in _FINAL_ACTION_TEXT):
            errors.append(f"{path} contains prohibited final submission, payment, upload, scheduling, or cancellation language")


def _dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


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
        return value.strip().lower() in {"active", "enabled", "true", "yes"}
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return False
