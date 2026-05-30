from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any

PACKET_TYPE = "ppd.guardrail_refresh_regression_matrix.v2"

_PASS_FAIL_DISPOSITIONS = {"pass", "fail", "expected_pass", "expected_fail"}

_PRIVATE_KEYS = {
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

_MUTATION_KEYS = {
    "active_agent_state_mutation",
    "active_guardrail_mutation",
    "active_monitoring_mutation",
    "active_prompt_mutation",
    "active_release_state_mutation",
    "active_surface_registry_mutation",
    "agent_state_mutation",
    "guardrail_mutation",
    "monitoring_mutation",
    "prompt_mutation",
    "release_state_mutation",
    "surface_registry_mutation",
}

_RAW_ARTIFACT_KEY_RE = re.compile(
    r"(^|_)(auth_state|browser_state|browser_trace|download_path|har|local_path|raw_artifact|raw_body|raw_crawl|raw_html|raw_pdf|raw_session|screenshot|session_artifact|session_path|session_state|trace|warc_path)(_|$)",
    re.IGNORECASE,
)
_RAW_ARTIFACT_VALUE_RE = re.compile(
    r"(^file://|^/(home|private|tmp|var/folders)/|^[A-Za-z]:\\Users\\|\\Users\\|\.har$|\.warc(\.gz)?$|/downloads?/|/raw/|/sessions?/|auth state|browser trace|downloaded document|raw crawl|raw pdf|session artifact)",
    re.IGNORECASE,
)
_LIVE_EXECUTION_RE = re.compile(
    r"\b(live llm|llm executed|called llm|live devhub|opened devhub|clicked devhub|browser executed|ran browser|crawler executed|live crawl|ran crawler|processor executed|processor execution|ran processor)\b",
    re.IGNORECASE,
)
_OUTCOME_GUARANTEE_RE = re.compile(
    r"\b(guarantee[sd]?|will be approved|will approve|approval is assured|permit will issue|permit must issue|legally valid|legal outcome|no legal risk|cannot be denied|ensures issuance|ensures approval)\b",
    re.IGNORECASE,
)
_FINAL_ACTION_RE = re.compile(
    r"\b(final submit|submit final|submit the application|complete submission|pay the fee|make payment|submit payment|upload corrections|upload to devhub|schedule inspection|cancel permit|cancel the application)\b",
    re.IGNORECASE,
)
_LOCAL_PRIVATE_PATH_RE = re.compile(
    r"(^file://|^/home/[^/]+/|^/Users/[^/]+/|^/private/|^/tmp/|^[A-Za-z]:\\Users\\[^\\]+\\)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GuardrailRefreshRegressionMatrixV2ValidationResult:
    valid: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "problems": list(self.problems)}


def load_guardrail_refresh_regression_matrix_v2_packet(path: str | Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("guardrail refresh regression matrix v2 packet must be an object")
    assert_valid_guardrail_refresh_regression_matrix_v2_packet(raw)
    return raw


def validate_guardrail_refresh_regression_matrix_v2_packet(packet: Mapping[str, Any]) -> GuardrailRefreshRegressionMatrixV2ValidationResult:
    if not isinstance(packet, Mapping):
        return GuardrailRefreshRegressionMatrixV2ValidationResult(False, ("packet must be an object",))

    problems: list[str] = []
    if packet.get("packet_type") != PACKET_TYPE:
        problems.append(f"packet_type must be {PACKET_TYPE}")
    if packet.get("fixture_only") is not True:
        problems.append("fixture_only must be true")
    if packet.get("live_execution_allowed") is not False:
        problems.append("live_execution_allowed must be false")

    evidence_ids = set(_string_list(packet.get("source_evidence_ids")))
    if not evidence_ids:
        problems.append("source_evidence_ids must be a non-empty list")

    reviewer_owners = set(_string_list(packet.get("reviewer_owners")))
    if not reviewer_owners:
        problems.append("reviewer_owners must be a non-empty list")

    rollback_notes = _text(packet.get("rollback_notes"))
    if not rollback_notes:
        problems.append("rollback_notes must be present")

    _validate_scenario_expectations(problems, packet, evidence_ids, reviewer_owners)
    _validate_recursive_rejections(problems, packet)

    return GuardrailRefreshRegressionMatrixV2ValidationResult(not problems, tuple(problems))


def assert_valid_guardrail_refresh_regression_matrix_v2_packet(packet: Mapping[str, Any]) -> None:
    result = validate_guardrail_refresh_regression_matrix_v2_packet(packet)
    if not result.valid:
        raise ValueError("invalid guardrail refresh regression matrix v2 packet: " + "; ".join(result.problems))


def _validate_scenario_expectations(
    problems: list[str],
    packet: Mapping[str, Any],
    evidence_ids: set[str],
    reviewer_owners: set[str],
) -> None:
    scenarios = packet.get("scenario_expectations")
    if not isinstance(scenarios, list) or not scenarios:
        problems.append("scenario_expectations must be a non-empty list")
        return

    for index, scenario in enumerate(scenarios):
        path = f"scenario_expectations[{index}]"
        if not isinstance(scenario, Mapping):
            problems.append(f"{path} must be an object")
            continue
        if not _text(scenario.get("scenario_id")):
            problems.append(f"{path}.scenario_id must be present")
        if not _text(scenario.get("expectation")):
            problems.append(f"{path}.expectation must be present")
        disposition = _text(scenario.get("expected_disposition")).lower()
        if disposition not in _PASS_FAIL_DISPOSITIONS:
            problems.append(f"{path}.expected_disposition must be pass or fail")
        scenario_rollback = _text(scenario.get("rollback_notes") or scenario.get("rollback_note"))
        if not scenario_rollback:
            problems.append(f"{path}.rollback_notes must be present")
        owner = _text(scenario.get("reviewer_owner"))
        if not owner:
            problems.append(f"{path}.reviewer_owner must be present")
        elif reviewer_owners and owner not in reviewer_owners:
            problems.append(f"{path}.reviewer_owner must be listed in reviewer_owners")
        citations = _string_list(scenario.get("source_evidence_ids"))
        if not citations:
            problems.append(f"{path}.source_evidence_ids must cite scenario expectations")
        for citation in citations:
            if evidence_ids and citation not in evidence_ids:
                problems.append(f"{path}.source_evidence_ids cites unknown evidence id {citation}")


def _validate_recursive_rejections(problems: list[str], value: Any, path: str = "$", key_name: str = "") -> None:
    if isinstance(value, Mapping):
        classification = _text(value.get("privacy_classification") or value.get("privacy") or value.get("auth_scope")).lower()
        if classification in _PRIVATE_CLASSIFICATIONS:
            problems.append(f"{path} must not include private or authenticated facts")
        mutation_flags = value.get("mutation_flags")
        if isinstance(mutation_flags, Mapping):
            for flag, flag_value in mutation_flags.items():
                normalized_flag = _normalize_key(flag)
                if normalized_flag in _MUTATION_KEYS and flag_value is True:
                    problems.append(f"{path}.mutation_flags.{flag} must be false")
        for key, child in value.items():
            normalized_key = _normalize_key(key)
            child_path = f"{path}.{key}"
            if normalized_key in _PRIVATE_KEYS and child not in (None, "", [], {}):
                problems.append(f"{child_path} must not include private or authenticated facts")
            if _RAW_ARTIFACT_KEY_RE.search(normalized_key) and child not in (None, "", [], {}):
                problems.append(f"{child_path} must not reference raw session, browser, crawl, download, WARC, or local artifacts")
            if _is_active_mutation_flag(normalized_key, child):
                problems.append(f"{child_path} must not set active mutation flags")
            _validate_recursive_rejections(problems, child, child_path, normalized_key)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _validate_recursive_rejections(problems, child, f"{path}[{index}]", key_name)
    elif isinstance(value, str):
        stripped = value.strip()
        if _RAW_ARTIFACT_VALUE_RE.search(stripped):
            problems.append(f"{path} must not reference raw session, browser, crawl, download, WARC, or local artifacts")
        if _LOCAL_PRIVATE_PATH_RE.search(stripped):
            problems.append(f"{path} must not include local private paths")
        if _LIVE_EXECUTION_RE.search(stripped):
            problems.append(f"{path} must not claim live LLM, DevHub, browser, crawler, or processor execution")
        if _OUTCOME_GUARANTEE_RE.search(stripped):
            problems.append(f"{path} must not guarantee legal or permitting outcomes")
        if _FINAL_ACTION_RE.search(stripped):
            problems.append(f"{path} must not include final submission, payment, upload, scheduling, or cancellation language")
        if key_name in {"path", "file_path", "local_file_path", "private_file_path"} and _LOCAL_PRIVATE_PATH_RE.search(stripped):
            problems.append(f"{path} must not include local private paths")


def _is_active_mutation_flag(normalized_key: str, value: Any) -> bool:
    if value is not True:
        return False
    if normalized_key.startswith("no_active_"):
        return False
    if normalized_key in _MUTATION_KEYS:
        return True
    if normalized_key.startswith("active_") and "mutation" in normalized_key:
        return True
    if normalized_key.endswith("_mutation_enabled"):
        return True
    return False


def _normalize_key(value: Any) -> str:
    return str(value).strip().lower().replace("-", "_")


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
