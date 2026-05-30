"""Validation for post-release monitoring readiness packets.

The validator is intentionally structural and conservative. Readiness packets are
commit-safe planning artifacts; they must describe cited monitoring checks,
escalation and rollback readiness, and offline validation only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class ReadinessFinding:
    """A single readiness validation failure."""

    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ReadinessValidationResult:
    """Validation result for a monitoring readiness packet."""

    findings: tuple[ReadinessFinding, ...]

    @property
    def ok(self) -> bool:
        return not self.findings


_RAW_ARTIFACT_KEY_FRAGMENTS = (
    "raw_body",
    "raw_html",
    "raw_response",
    "response_body",
    "download_ref",
    "download_url",
    "download_path",
    "downloaded_document",
    "archive_ref",
    "archive_artifact_ref",
    "archive_path",
    "warc",
    "har",
    "trace",
    "screenshot",
)

_PRIVATE_ARTIFACT_KEY_FRAGMENTS = (
    "auth_state",
    "browser_state",
    "cookie",
    "credential",
    "devhub_session",
    "local_private_path",
    "mfa",
    "password",
    "playwright_state",
    "private_artifact",
    "session_artifact",
    "session_state",
    "storage_state",
    "token",
)

_PRIVATE_VALUE_FRAGMENTS = (
    "/.daemon/",
    "auth-state",
    "cookies.json",
    "har.zip",
    "playwright/.auth",
    "session.json",
    "storage_state",
    "trace.zip",
)

_LIVE_EXECUTION_KEY_FRAGMENTS = (
    "crawler_executed",
    "devhub_executed",
    "devhub_run",
    "live_crawl",
    "live_crawler",
    "live_devhub",
    "live_llm",
    "llm_executed",
    "processor_executed",
    "processor_run",
)

_LIVE_EXECUTION_TEXT_FRAGMENTS = (
    "executed live crawler",
    "live crawler executed",
    "ran live crawler",
    "executed processor",
    "processor executed",
    "ran processor",
    "executed devhub",
    "devhub automation executed",
    "ran devhub",
    "executed llm",
    "llm executed",
    "ran llm",
)

_GUARANTEE_TEXT_FRAGMENTS = (
    "approval is guaranteed",
    "guarantee approval",
    "guarantee permit approval",
    "guaranteed approval",
    "guaranteed legal outcome",
    "legally guaranteed",
    "permit approval guaranteed",
    "will be approved",
    "will pass inspection",
    "will receive permit",
)

_MUTATION_DOMAINS = (
    "source",
    "source_registry",
    "requirement",
    "process",
    "guardrail",
    "prompt",
    "surface_registry",
    "surface-registry",
    "release_state",
    "release-state",
)

_MUTATION_ACTIONS = (
    "active",
    "apply",
    "commit",
    "mutate",
    "mutation",
    "publish",
    "set",
    "update",
    "write",
)

_OFFLINE_COMMAND_FORBIDDEN_FRAGMENTS = (
    "crawl",
    "devhub",
    "llm",
    "playwright",
    "processor",
    "scrape",
    "wget",
    "curl",
)


class ReadinessValidationError(ValueError):
    """Raised when a readiness packet fails validation."""

    def __init__(self, findings: Sequence[ReadinessFinding]) -> None:
        self.findings = tuple(findings)
        rendered = "; ".join(
            f"{finding.code} at {finding.path}: {finding.message}"
            for finding in self.findings
        )
        super().__init__(rendered)


def validate_post_release_monitoring_readiness_packet(
    packet: Mapping[str, Any],
) -> ReadinessValidationResult:
    """Validate a post-release monitoring readiness packet.

    The accepted shape is deliberately flexible so supervisor output can evolve,
    but the guardrails are strict: checks need citations, escalation thresholds,
    rollback owners, offline commands, and no private/live/mutation claims.
    """

    findings: list[ReadinessFinding] = []

    if not isinstance(packet, Mapping):
        return ReadinessValidationResult(
            (
                ReadinessFinding(
                    "packet_not_mapping",
                    "$",
                    "readiness packet must be a mapping",
                ),
            )
        )

    checks = packet.get("monitoring_checks")
    if not isinstance(checks, Sequence) or isinstance(checks, (str, bytes)) or not checks:
        findings.append(
            ReadinessFinding(
                "missing_monitoring_checks",
                "$.monitoring_checks",
                "packet must include at least one monitoring check",
            )
        )
    else:
        for index, check in enumerate(checks):
            check_path = f"$.monitoring_checks[{index}]"
            if not isinstance(check, Mapping):
                findings.append(
                    ReadinessFinding(
                        "invalid_monitoring_check",
                        check_path,
                        "monitoring check must be a mapping",
                    )
                )
                continue
            if not _has_citation(check):
                findings.append(
                    ReadinessFinding(
                        "uncited_monitoring_check",
                        check_path,
                        "monitoring check must include citations or source evidence ids",
                    )
                )
            if not _has_threshold(check):
                findings.append(
                    ReadinessFinding(
                        "missing_escalation_threshold",
                        check_path,
                        "monitoring check must include an escalation threshold",
                    )
                )

    if not _has_packet_thresholds(packet):
        findings.append(
            ReadinessFinding(
                "missing_escalation_thresholds",
                "$.escalation_thresholds",
                "packet must include escalation thresholds",
            )
        )

    if not _has_rollback_owner(packet):
        findings.append(
            ReadinessFinding(
                "missing_rollback_owner",
                "$.rollback.owner",
                "packet must identify rollback owner or owners",
            )
        )

    offline_commands = packet.get("offline_validation_commands")
    if not _has_offline_commands(offline_commands):
        findings.append(
            ReadinessFinding(
                "missing_offline_validation_commands",
                "$.offline_validation_commands",
                "packet must include offline validation commands",
            )
        )
    else:
        findings.extend(_validate_offline_commands(offline_commands))

    for path, key, value in _walk(packet):
        normalized_key = _normalize(str(key))
        if _contains_any(normalized_key, _RAW_ARTIFACT_KEY_FRAGMENTS):
            findings.append(
                ReadinessFinding(
                    "raw_body_download_or_archive_reference",
                    path,
                    "readiness packet must not reference raw bodies, downloads, archives, HARs, traces, or screenshots",
                )
            )
        if _contains_any(normalized_key, _PRIVATE_ARTIFACT_KEY_FRAGMENTS):
            findings.append(
                ReadinessFinding(
                    "private_or_session_artifact",
                    path,
                    "readiness packet must not reference private, auth, credential, token, or session artifacts",
                )
            )
        if _is_truthy(value) and _contains_any(normalized_key, _LIVE_EXECUTION_KEY_FRAGMENTS):
            findings.append(
                ReadinessFinding(
                    "live_execution_claim",
                    path,
                    "readiness packet must not claim live crawler, processor, DevHub, or LLM execution",
                )
            )
        if _is_truthy(value) and _is_active_mutation_flag(normalized_key):
            findings.append(
                ReadinessFinding(
                    "active_mutation_flag",
                    path,
                    "readiness packet must not enable source, requirement, process, guardrail, prompt, surface registry, or release-state mutation",
                )
            )
        if isinstance(value, str):
            normalized_value = _normalize(value)
            if _contains_any(normalized_value, _PRIVATE_VALUE_FRAGMENTS):
                findings.append(
                    ReadinessFinding(
                        "private_or_session_artifact",
                        path,
                        "readiness packet must not reference private/session artifact paths or files",
                    )
                )
            if _contains_any(normalized_value, _LIVE_EXECUTION_TEXT_FRAGMENTS):
                findings.append(
                    ReadinessFinding(
                        "live_execution_claim",
                        path,
                        "readiness packet must not claim live crawler, processor, DevHub, or LLM execution",
                    )
                )
            if _contains_any(normalized_value, _GUARANTEE_TEXT_FRAGMENTS):
                findings.append(
                    ReadinessFinding(
                        "legal_or_permitting_outcome_guarantee",
                        path,
                        "readiness packet must not guarantee legal, permitting, review, inspection, or approval outcomes",
                    )
                )

    return ReadinessValidationResult(tuple(findings))


def assert_post_release_monitoring_readiness_packet(packet: Mapping[str, Any]) -> None:
    """Raise if the readiness packet is not acceptable."""

    result = validate_post_release_monitoring_readiness_packet(packet)
    if not result.ok:
        raise ReadinessValidationError(result.findings)


def _has_citation(check: Mapping[str, Any]) -> bool:
    for field in ("citations", "citation_spans", "source_evidence_ids", "source_ids"):
        value = check.get(field)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and value:
            return all(isinstance(item, str) and item.strip() for item in value)
    return False


def _has_threshold(check: Mapping[str, Any]) -> bool:
    for field in ("escalation_threshold", "threshold", "alert_threshold"):
        value = check.get(field)
        if isinstance(value, str) and value.strip():
            return True
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
        if isinstance(value, Mapping) and value:
            return True
    return False


def _has_packet_thresholds(packet: Mapping[str, Any]) -> bool:
    value = packet.get("escalation_thresholds")
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return bool(value)
    return False


def _has_rollback_owner(packet: Mapping[str, Any]) -> bool:
    rollback = packet.get("rollback")
    candidates: list[Any] = [packet.get("rollback_owner"), packet.get("rollback_owners")]
    if isinstance(rollback, Mapping):
        candidates.extend([rollback.get("owner"), rollback.get("owners")])
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return True
        if isinstance(candidate, Sequence) and not isinstance(candidate, (str, bytes)):
            if any(isinstance(item, str) and item.strip() for item in candidate):
                return True
    return False


def _has_offline_commands(value: Any) -> bool:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return False
    return any(_command_text(command).strip() for command in value)


def _validate_offline_commands(commands: Sequence[Any]) -> tuple[ReadinessFinding, ...]:
    findings: list[ReadinessFinding] = []
    for index, command in enumerate(commands):
        text = _normalize(_command_text(command))
        path = f"$.offline_validation_commands[{index}]"
        if not text:
            findings.append(
                ReadinessFinding(
                    "invalid_offline_validation_command",
                    path,
                    "offline validation command must be a non-empty string or argv list",
                )
            )
        if _contains_any(text, _OFFLINE_COMMAND_FORBIDDEN_FRAGMENTS):
            findings.append(
                ReadinessFinding(
                    "non_offline_validation_command",
                    path,
                    "offline validation commands must not invoke crawlers, processors, DevHub, Playwright, LLMs, curl, or wget",
                )
            )
    return tuple(findings)


def _command_text(command: Any) -> str:
    if isinstance(command, str):
        return command
    if isinstance(command, Sequence) and not isinstance(command, (str, bytes)):
        parts = [str(part) for part in command if isinstance(part, (str, int, float))]
        return " ".join(parts)
    return ""


def _walk(value: Any, path: str = "$", key: str = "$") -> Iterable[tuple[str, str, Any]]:
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            child_path = f"{path}.{child_key_text}"
            yield child_path, child_key_text, child_value
            yield from _walk(child_value, child_path, child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child_value in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, key, child_value
            yield from _walk(child_value, child_path, key)


def _normalize(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _contains_any(value: str, fragments: Sequence[str]) -> bool:
    return any(fragment in value for fragment in fragments)


def _is_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "enabled", "active"}
    if isinstance(value, (int, float)):
        return value != 0
    return bool(value) and not isinstance(value, (Mapping, Sequence))


def _is_active_mutation_flag(normalized_key: str) -> bool:
    return any(domain in normalized_key for domain in _MUTATION_DOMAINS) and any(
        action in normalized_key for action in _MUTATION_ACTIONS
    )
