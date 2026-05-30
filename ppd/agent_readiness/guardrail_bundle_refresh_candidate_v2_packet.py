from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.guardrail_bundle_refresh_candidate_packet.v2"
CANDIDATE_STATUS = "candidate_packet_only_not_applied"

_REQUIRED_TRUE_ATTESTATIONS = {
    "fixture_first",
    "candidate_packet_only",
    "no_active_guardrail_mutation",
    "no_active_prompt_mutation",
    "no_active_surface_registry_mutation",
    "no_active_monitoring_mutation",
    "no_release_state_mutation",
    "no_active_agent_state_mutation",
}

_REQUIRED_FALSE_ATTESTATIONS = {
    "active_guardrail_mutation",
    "active_prompt_mutation",
    "active_surface_registry_mutation",
    "active_monitoring_mutation",
    "release_state_mutation",
    "active_agent_state_mutation",
    "guardrail_delta_applied",
    "prompt_updated",
    "surface_registry_updated",
    "monitoring_state_updated",
    "release_state_updated",
    "agent_state_updated",
}

_PRIVATE_FACT_KEYS = {
    "account_number",
    "address",
    "auth_state",
    "authenticated_case_facts",
    "case_facts",
    "cookie",
    "cookies",
    "credential",
    "credentials",
    "email",
    "known_facts",
    "password",
    "payment_details",
    "phone",
    "private_case_facts",
    "private_facts",
    "private_values",
    "raw_value",
    "session_cookie",
    "session_state",
    "token",
    "user_case_facts",
    "user_input",
}

_PRIVATE_CLASSIFICATIONS = {
    "authenticated",
    "case_private",
    "confidential",
    "devhub_authenticated",
    "devhub_authenticated_private",
    "private",
    "restricted",
    "user_private",
}

_MUTATION_DOMAINS = {
    "agent_state",
    "agent-state",
    "guardrail",
    "monitoring",
    "prompt",
    "release_state",
    "release-state",
    "surface_registry",
    "surface-registry",
}

_CONSEQUENTIAL_CLASSES = {
    "cancellation",
    "certification",
    "financial",
    "inspection_scheduling",
    "payment",
    "scheduling",
    "submission",
    "upload",
    "upload_to_official_record",
}

_RAW_ARTIFACT_KEY_RE = re.compile(
    r"(^|_)(raw[_-]?(crawl|body|pdf|html|text|artifact)?|crawl[_-]?output|pdf[_-]?(path|artifact|download|bytes)?|download[_-]?(ref|url|path)?|session[_-]?(artifact|path|trace|state)?|auth[_-]?state|browser[_-]?state|har|trace|screenshot|warc[_-]?(ref|path)?|local[_-]?path)(_|$)",
    re.IGNORECASE,
)
_RAW_ARTIFACT_VALUE_RE = re.compile(
    r"(^(file|crawl|archive|warc|session)://|/(tmp|var/folders|private|home)/|\\users\\|\.warc(\.gz)?$|\.har$|/raw/|/downloads?/|/archives?/|/sessions?/|raw crawl|raw pdf|downloaded document|session artifact|browser trace|auth state)",
    re.IGNORECASE,
)
_LIVE_EXECUTION_RE = re.compile(
    r"\b(live llm|llm executed|called llm|devhub executed|live devhub|opened devhub|clicked devhub|crawler executed|live crawl|ran crawler|processor execution|processor executed|ran processor|live processor)\b",
    re.IGNORECASE,
)
_OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?|will be approved|will approve|approval is assured|permit will issue|permit must issue|legally valid|legal outcome|no legal risk|cannot be denied|ensures issuance|ensures approval)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GuardrailBundleRefreshCandidateV2ValidationResult:
    valid: bool
    problems: tuple[str, ...]


def load_guardrail_bundle_refresh_candidate_v2_fixture(path: str | Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("fixture must be a JSON object")
    assert_valid_guardrail_bundle_refresh_candidate_v2_packet(raw)
    return raw


def validate_guardrail_bundle_refresh_candidate_v2_packet(packet: Mapping[str, Any]) -> GuardrailBundleRefreshCandidateV2ValidationResult:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return GuardrailBundleRefreshCandidateV2ValidationResult(False, ("packet must be an object",))

    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("fixture_only") is not True:
        problems.append("fixture_only must be true")
    if packet.get("candidate_status") != CANDIDATE_STATUS:
        problems.append("candidate_status must keep the candidate unapplied")
    if not _string_list(packet.get("affected_process_ids")):
        problems.append("affected_process_ids must be a non-empty list")
    if not _string_list(packet.get("affected_requirement_ids")):
        problems.append("affected_requirement_ids must be a non-empty list")
    if not _string_list(packet.get("source_evidence_ids")):
        problems.append("source_evidence_ids must be a non-empty list")

    _validate_candidate_predicates(problems, packet)
    _validate_reviewer_owners(problems, packet)
    _validate_attestations(problems, packet)
    _validate_recursive_policy_rejections(problems, packet)
    return GuardrailBundleRefreshCandidateV2ValidationResult(not problems, tuple(problems))


def assert_valid_guardrail_bundle_refresh_candidate_v2_packet(packet: Mapping[str, Any]) -> None:
    result = validate_guardrail_bundle_refresh_candidate_v2_packet(packet)
    if not result.valid:
        raise ValueError("invalid guardrail bundle refresh candidate v2 packet: " + "; ".join(result.problems))


def _validate_candidate_predicates(problems: list[str], packet: Mapping[str, Any]) -> None:
    predicates = packet.get("predicate_candidates")
    if not isinstance(predicates, list) or not predicates:
        problems.append("predicate_candidates must be a non-empty list")
        return
    for index, predicate in enumerate(_mapping_sequence(predicates)):
        if not _text(predicate.get("predicate_id")):
            problems.append(f"predicate_candidates[{index}] lacks predicate_id")
        if not _text(predicate.get("operation")):
            problems.append(f"predicate_candidates[{index}] lacks operation")
        if not _string_list(predicate.get("source_evidence_ids")):
            problems.append(f"predicate_candidates[{index}] lacks source_evidence_ids")
        if not _string_list(predicate.get("affected_process_ids")):
            problems.append(f"predicate_candidates[{index}] lacks affected_process_ids")
        if not _string_list(predicate.get("affected_requirement_ids")):
            problems.append(f"predicate_candidates[{index}] lacks affected_requirement_ids")
        if not _text(predicate.get("reviewer_owner")):
            problems.append(f"predicate_candidates[{index}] lacks reviewer_owner")
        checkpoint = predicate.get("checkpoint_expectations") if isinstance(predicate.get("checkpoint_expectations"), Mapping) else {}
        if not checkpoint:
            problems.append(f"predicate_candidates[{index}] lacks checkpoint_expectations")
        if not _string_list(checkpoint.get("reversible_action_predicates")):
            problems.append(f"predicate_candidates[{index}] lacks reversible_action_predicates checkpoint expectations")
        if not _string_list(checkpoint.get("exact_confirmation_predicates")):
            problems.append(f"predicate_candidates[{index}] lacks exact_confirmation_predicates checkpoint expectations")
        if predicate.get("activation_allowed") is not False:
            problems.append(f"predicate_candidates[{index}] must keep activation_allowed false")


def _validate_reviewer_owners(problems: list[str], packet: Mapping[str, Any]) -> None:
    owners = packet.get("reviewer_owners")
    if not isinstance(owners, list) or not owners:
        problems.append("reviewer_owners must be a non-empty list")
        return
    for index, owner in enumerate(_mapping_sequence(owners)):
        if not _text(owner.get("reviewer_owner_id")):
            problems.append(f"reviewer_owners[{index}] lacks reviewer_owner_id")
        if owner.get("approval_status") != "pending_human_review":
            problems.append(f"reviewer_owners[{index}] must be pending_human_review")
        if not _string_list(owner.get("source_evidence_ids")):
            problems.append(f"reviewer_owners[{index}] lacks source_evidence_ids")


def _validate_attestations(problems: list[str], packet: Mapping[str, Any]) -> None:
    attestations = packet.get("attestations") if isinstance(packet.get("attestations"), Mapping) else {}
    for key in sorted(_REQUIRED_TRUE_ATTESTATIONS):
        if attestations.get(key) is not True:
            problems.append(f"attestations.{key} must be true")
    for key in sorted(_REQUIRED_FALSE_ATTESTATIONS):
        if attestations.get(key) is not False:
            problems.append(f"attestations.{key} must be false")
    if not _string_list(attestations.get("source_evidence_ids")):
        problems.append("attestations.source_evidence_ids must cite fixture evidence")


def _validate_recursive_policy_rejections(problems: list[str], packet: Mapping[str, Any]) -> None:
    for path, value in _walk(packet):
        key = path.rsplit(".", 1)[-1]
        normalized_key = key.lower().replace("-", "_")
        if normalized_key in _PRIVATE_FACT_KEYS and value:
            problems.append(f"{path} must not include private or authenticated facts")
        if _RAW_ARTIFACT_KEY_RE.search(normalized_key):
            problems.append(f"{path} must not reference raw crawl, PDF, session, browser, WARC, download, or local artifacts")
        if isinstance(value, Mapping):
            classification = _text(value.get("privacy_classification") or value.get("privacy") or value.get("auth_scope")).lower()
            if classification in _PRIVATE_CLASSIFICATIONS:
                problems.append(f"{path} must not include private or authenticated facts")
            mutation_flags = value.get("mutation_flags")
            if isinstance(mutation_flags, Mapping):
                for flag, flag_value in mutation_flags.items():
                    if str(flag).lower() in _MUTATION_DOMAINS and flag_value is True:
                        problems.append(f"{path}.mutation_flags.{flag} must be false")
            if _is_enabled_consequential_control(value):
                problems.append(f"{path} must not enable consequential controls")
        if isinstance(value, str):
            stripped = value.strip()
            if _RAW_ARTIFACT_VALUE_RE.search(stripped):
                problems.append(f"{path} must not reference raw crawl, PDF, session, browser, WARC, download, or local artifacts")
            if _LIVE_EXECUTION_RE.search(stripped):
                problems.append(f"{path} must not claim live LLM, DevHub, crawler, or processor execution")
            if _OUTCOME_GUARANTEE_RE.search(stripped):
                problems.append(f"{path} must not guarantee legal or permitting outcomes")
        if _is_active_mutation_flag(normalized_key, value):
            problems.append(f"{path} must not set active mutation flags")


def _is_enabled_consequential_control(value: Mapping[str, Any]) -> bool:
    control_class = _text(value.get("action_class") or value.get("control_class") or value.get("risk_class") or value.get("consequential_control"))
    normalized_class = control_class.lower().replace("-", "_")
    if normalized_class not in _CONSEQUENTIAL_CLASSES:
        return False
    return value.get("enabled") is True or value.get("activation_allowed") is True or value.get("allowed") is True


def _is_active_mutation_flag(normalized_key: str, value: Any) -> bool:
    if value is not True:
        return False
    if normalized_key.startswith("no_active_"):
        return False
    if normalized_key in _REQUIRED_FALSE_ATTESTATIONS:
        return True
    if normalized_key.startswith("active_") and "mutation" in normalized_key:
        return True
    if normalized_key in {"guardrail", "prompt", "surface_registry", "monitoring", "release_state", "agent_state"}:
        return True
    return False


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _walk(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            items.append((path, child))
            items.extend(_walk(child, path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            items.append((path, child))
            items.extend(_walk(child, path))
    return items


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
