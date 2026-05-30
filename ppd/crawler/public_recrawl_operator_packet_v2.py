"""Safety validation for public recrawl operator packet v2.

The validator is intentionally side-effect free. It checks packet-shaped
mappings before any public recrawl is considered for operator review, processor
handoff, source refresh scheduling, or release promotion.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from urllib.parse import parse_qsl, urlparse


PACKET_TYPE = "ppd_public_recrawl_operator_packet"
PACKET_VERSION = 2

DEFAULT_ALLOWED_HOSTS = frozenset(
    {
        "www.portland.gov",
        "devhub.portlandoregon.gov",
        "www.portlandoregon.gov",
        "www.portlandmaps.com",
    }
)

_URL_KEYS = frozenset(
    {
        "canonical_url",
        "href",
        "requested_url",
        "seed_url",
        "source_url",
        "start_url",
        "target_url",
        "url",
    }
)

_AUTH_QUERY_KEYS = frozenset(
    {
        "access_token",
        "api_key",
        "auth",
        "auth_token",
        "bearer",
        "client_secret",
        "code",
        "credential",
        "jwt",
        "key",
        "oauth",
        "password",
        "private_key",
        "secret",
        "session",
        "session_id",
        "sid",
        "signature",
        "signed",
        "state",
        "token",
    }
)

_AUTHENTICATED_PATH_MARKERS = (
    "/account",
    "/accounts",
    "/admin",
    "/application",
    "/applications",
    "/auth",
    "/cart",
    "/dashboard",
    "/document",
    "/documents",
    "/inspection",
    "/inspections",
    "/login",
    "/logout",
    "/my",
    "/oauth",
    "/password",
    "/payment",
    "/payments",
    "/permit/",
    "/permits/",
    "/private",
    "/profile",
    "/register",
    "/secure",
    "/session",
    "/signin",
    "/sign-in",
    "/sso",
    "/upload",
    "/uploads",
    "/user",
)

_RAW_ARTIFACT_KEYS = frozenset(
    {
        "archive_path",
        "archive_ref",
        "archive_uri",
        "body",
        "content",
        "document_path",
        "download_path",
        "download_ref",
        "downloaded_document_path",
        "har_path",
        "html",
        "local_path",
        "pdf_path",
        "persist_raw_body",
        "raw_body",
        "raw_content",
        "raw_download_ref",
        "raw_html",
        "response_body",
        "save_raw_body",
        "screenshot_path",
        "store_raw_body",
        "text",
        "trace_path",
        "warc_path",
    }
)

_LIVE_OR_PROCESSOR_KEYS = frozenset(
    {
        "allow_live_crawl",
        "allow_live_network",
        "allow_network",
        "execute_live",
        "executed_live_network",
        "invoke_processor",
        "live_crawl",
        "live_execution",
        "live_network",
        "network_enabled",
        "network_invoked",
        "processor_executed",
        "processor_invocation_allowed",
        "processor_invoked",
        "run_live",
        "use_live_network",
    }
)

_MUTATION_KEYS = frozenset(
    {
        "active_guardrail_mutation",
        "active_monitoring_mutation",
        "active_process_mutation",
        "active_prompt_mutation",
        "active_release_state_mutation",
        "active_requirement_mutation",
        "active_schedule_mutation",
        "active_source_mutation",
        "apply_guardrail_updates",
        "apply_monitoring_updates",
        "apply_process_updates",
        "apply_prompt_updates",
        "apply_release_state_updates",
        "apply_requirement_updates",
        "apply_schedule_updates",
        "apply_source_updates",
        "commit_guardrail_changes",
        "commit_monitoring_changes",
        "commit_process_changes",
        "commit_prompt_changes",
        "commit_release_state_changes",
        "commit_requirement_changes",
        "commit_schedule_changes",
        "commit_source_changes",
        "mutate_guardrails",
        "mutate_monitoring",
        "mutate_processes",
        "mutate_prompts",
        "mutate_release_state",
        "mutate_requirements",
        "mutate_schedules",
        "mutate_sources",
        "release_state_mutation",
        "source_registry_mutated",
    }
)

_GUARANTEE_KEYS = frozenset(
    {
        "approval_guarantee",
        "guarantee",
        "guaranteed_outcome",
        "legal_advice_guarantee",
        "outcome_guarantee",
        "permit_approval_guarantee",
        "permitting_guarantee",
    }
)

_GUARANTEE_TEXT_MARKERS = (
    "guarantee approval",
    "guarantee permit",
    "guaranteed approval",
    "guaranteed issuance",
    "guaranteed legal",
    "guaranteed permit",
    "legally guaranteed",
    "permit will be approved",
    "permit will be issued",
    "will receive approval",
    "will receive the permit",
)

_LIVE_TEXT_MARKERS = (
    "live crawl executed",
    "live crawl performed",
    "live network executed",
    "live network performed",
    "processor executed",
    "processor invocation completed",
    "processor invoked",
)

_RAW_TEXT_MARKERS = (
    "raw body persisted",
    "raw html stored",
    "raw response body",
    "downloaded document saved",
    "archive artifact stored",
    "warc path",
)

_REQUIRED_SEED_LIST_KEYS = ("seed_batches", "seedBatches", "source_batches", "sourceBatches")
_REQUIRED_ROBOTS_KEYS = ("robots_decision", "robotsDecision", "skip_decision", "skipDecision")
_CITATION_KEYS = ("citations", "citation_ids", "source_evidence_ids", "sourceEvidenceIds", "evidence")


@dataclass(frozen=True)
class PublicRecrawlOperatorPacketV2Issue:
    """A deterministic validation issue for a public recrawl operator packet."""

    code: str
    message: str
    path: str = "$"


def validate_public_recrawl_operator_packet_v2(
    packet: Mapping[str, Any],
    *,
    allowed_hosts: Iterable[str] = DEFAULT_ALLOWED_HOSTS,
) -> list[PublicRecrawlOperatorPacketV2Issue]:
    """Return validation issues for public recrawl operator packet v2."""

    if not isinstance(packet, Mapping):
        return [PublicRecrawlOperatorPacketV2Issue("invalid_packet", "packet must be a mapping")]

    allowed = frozenset(host.lower() for host in allowed_hosts)
    issues: list[PublicRecrawlOperatorPacketV2Issue] = []

    if packet.get("packetType") != PACKET_TYPE:
        issues.append(
            PublicRecrawlOperatorPacketV2Issue(
                "invalid_packet_type",
                f"packetType must be {PACKET_TYPE}",
                "$.packetType",
            )
        )
    if packet.get("schemaVersion") != PACKET_VERSION:
        issues.append(
            PublicRecrawlOperatorPacketV2Issue(
                "invalid_schema_version",
                "schemaVersion must be 2",
                "$.schemaVersion",
            )
        )

    seed_batches = _seed_batches(packet)
    if not seed_batches:
        issues.append(
            PublicRecrawlOperatorPacketV2Issue(
                "missing_seed_batches",
                "packet must include at least one cited public seed batch",
                "$.seed_batches",
            )
        )
    for batch_index, batch in enumerate(seed_batches):
        batch_path = f"$.seed_batches[{batch_index}]"
        if not isinstance(batch, Mapping):
            issues.append(PublicRecrawlOperatorPacketV2Issue("invalid_seed_batch", "seed batch must be an object", batch_path))
            continue
        if not _has_citation(batch):
            issues.append(
                PublicRecrawlOperatorPacketV2Issue(
                    "uncited_seed_batch",
                    "each seed batch must include source evidence citations",
                    batch_path,
                )
            )
        seeds = batch.get("seeds")
        if not isinstance(seeds, list) or not seeds:
            issues.append(PublicRecrawlOperatorPacketV2Issue("missing_seeds", "seed batch must include seeds", f"{batch_path}.seeds"))
            continue
        for seed_index, seed in enumerate(seeds):
            seed_path = f"{batch_path}.seeds[{seed_index}]"
            if not isinstance(seed, Mapping):
                issues.append(PublicRecrawlOperatorPacketV2Issue("invalid_seed", "seed must be an object", seed_path))
                continue
            if not _has_citation(seed):
                issues.append(
                    PublicRecrawlOperatorPacketV2Issue(
                        "uncited_seed",
                        "each seed URL must include source evidence citations",
                        seed_path,
                    )
                )
            if not _has_robots_or_skip_decision(seed):
                issues.append(
                    PublicRecrawlOperatorPacketV2Issue(
                        "missing_robots_or_skip_decision",
                        "each seed must include a robots decision or explicit skip decision",
                        seed_path,
                    )
                )

    _collect_recursive_issues(packet, issues, "$", allowed)
    return _dedupe_issues(issues)


def assert_public_recrawl_operator_packet_v2_is_safe(packet: Mapping[str, Any], **kwargs: Any) -> None:
    """Raise ValueError if the packet contains unsafe public recrawl content."""

    issues = validate_public_recrawl_operator_packet_v2(packet, **kwargs)
    if issues:
        detail = "; ".join(f"{issue.code} at {issue.path}: {issue.message}" for issue in issues)
        raise ValueError(detail)


def issue_codes(issues: Iterable[PublicRecrawlOperatorPacketV2Issue]) -> set[str]:
    """Return issue codes for tests and daemon diagnostics."""

    return {issue.code for issue in issues}


def _seed_batches(packet: Mapping[str, Any]) -> list[Any]:
    for key in _REQUIRED_SEED_LIST_KEYS:
        value = packet.get(key)
        if isinstance(value, list):
            return value
    return []


def _has_citation(value: Mapping[str, Any]) -> bool:
    for key in _CITATION_KEYS:
        citation_value = value.get(key)
        if isinstance(citation_value, str) and citation_value.strip():
            return True
        if isinstance(citation_value, list) and any(isinstance(item, str) and item.strip() for item in citation_value):
            return True
        if isinstance(citation_value, list) and any(isinstance(item, Mapping) and item for item in citation_value):
            return True
    return False


def _has_robots_or_skip_decision(seed: Mapping[str, Any]) -> bool:
    for key in _REQUIRED_ROBOTS_KEYS:
        decision = seed.get(key)
        if isinstance(decision, str) and decision.strip():
            return True
        if isinstance(decision, Mapping):
            status = decision.get("decision") or decision.get("status") or decision.get("result")
            if isinstance(status, str) and status.strip():
                return True
            if decision.get("allowed") is True or decision.get("skipped") is True:
                return True
    return False


def _collect_recursive_issues(
    value: Any,
    issues: list[PublicRecrawlOperatorPacketV2Issue],
    path: str,
    allowed_hosts: frozenset[str],
) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = _normalize_key(key_text)
            child_path = f"{path}.{key_text}"
            if normalized in _URL_KEYS and isinstance(child, str):
                _append_url_issues(child, issues, child_path, allowed_hosts)
            if normalized in _RAW_ARTIFACT_KEYS and _has_value(child):
                issues.append(
                    PublicRecrawlOperatorPacketV2Issue(
                        "raw_body_download_or_archive_reference",
                        "operator packet v2 must not include raw body, download, archive, or local artifact references",
                        child_path,
                    )
                )
            if normalized in _LIVE_OR_PROCESSOR_KEYS and _truthy_or_enabled(child):
                issues.append(
                    PublicRecrawlOperatorPacketV2Issue(
                        "live_crawl_or_processor_execution_claim",
                        "operator packet v2 must not claim live crawl or processor execution",
                        child_path,
                    )
                )
            if normalized in _MUTATION_KEYS and _truthy_or_enabled(child):
                issues.append(
                    PublicRecrawlOperatorPacketV2Issue(
                        "active_state_mutation_flag",
                        "operator packet v2 must not enable active source, schedule, requirement, process, guardrail, prompt, monitoring, or release-state mutation",
                        child_path,
                    )
                )
            if normalized in _GUARANTEE_KEYS and _truthy_or_enabled(child):
                issues.append(
                    PublicRecrawlOperatorPacketV2Issue(
                        "legal_or_permitting_outcome_guarantee",
                        "operator packet v2 must not guarantee legal or permitting outcomes",
                        child_path,
                    )
                )
            _collect_recursive_issues(child, issues, child_path, allowed_hosts)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _collect_recursive_issues(child, issues, f"{path}[{index}]", allowed_hosts)
    elif isinstance(value, str):
        if _looks_like_url(value):
            _append_url_issues(value, issues, path, allowed_hosts)
        lowered = value.strip().lower()
        if any(marker in lowered for marker in _LIVE_TEXT_MARKERS):
            issues.append(
                PublicRecrawlOperatorPacketV2Issue(
                    "live_crawl_or_processor_execution_claim",
                    "operator packet v2 must not claim live crawl or processor execution",
                    path,
                )
            )
        if any(marker in lowered for marker in _RAW_TEXT_MARKERS):
            issues.append(
                PublicRecrawlOperatorPacketV2Issue(
                    "raw_body_download_or_archive_reference",
                    "operator packet v2 must not include raw body, download, archive, or local artifact references",
                    path,
                )
            )
        if any(marker in lowered for marker in _GUARANTEE_TEXT_MARKERS):
            issues.append(
                PublicRecrawlOperatorPacketV2Issue(
                    "legal_or_permitting_outcome_guarantee",
                    "operator packet v2 must not guarantee legal or permitting outcomes",
                    path,
                )
            )


def _append_url_issues(
    url: str,
    issues: list[PublicRecrawlOperatorPacketV2Issue],
    path: str,
    allowed_hosts: frozenset[str],
) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        issues.append(
            PublicRecrawlOperatorPacketV2Issue(
                "unsupported_url",
                "public recrawl URLs must be absolute HTTP(S) URLs",
                path,
            )
        )
        return

    if parsed.hostname.lower() not in allowed_hosts:
        issues.append(
            PublicRecrawlOperatorPacketV2Issue(
                "outside_allowlist_url",
                "public recrawl URLs must stay inside the PP&D public host allowlist",
                path,
            )
        )

    if _is_authenticated_or_private_url(parsed):
        issues.append(
            PublicRecrawlOperatorPacketV2Issue(
                "authenticated_or_private_url",
                "public recrawl URLs must not include credentials, tokens, or authenticated/private paths",
                path,
            )
        )


def _is_authenticated_or_private_url(parsed: Any) -> bool:
    if parsed.username or parsed.password:
        return True
    path = (parsed.path or "").lower()
    if any(path == marker.rstrip("/") or path.startswith(marker) for marker in _AUTHENTICATED_PATH_MARKERS):
        return True
    query_keys = {_normalize_key(key) for key, _value in parse_qsl(parsed.query, keep_blank_values=True)}
    return bool(query_keys.intersection(_AUTH_QUERY_KEYS))


def _truthy_or_enabled(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        normalized = _normalize_key(value)
        return normalized in {"1", "active", "allow", "allowed", "apply", "committed", "enabled", "execute", "executed", "live", "mutate", "promote", "true", "yes"}
    if isinstance(value, Mapping):
        return any(_truthy_or_enabled(child) for child in value.values())
    if isinstance(value, list):
        return any(_truthy_or_enabled(child) for child in value)
    return False


def _has_value(value: Any) -> bool:
    if value is False or value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and _normalize_key(value) not in {"false", "metadata_only", "none", "not_persisted", "redacted"}
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return bool(value)


def _looks_like_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def _normalize_key(value: str) -> str:
    return value.strip().replace("-", "_").replace(" ", "_").lower()


def _dedupe_issues(
    issues: list[PublicRecrawlOperatorPacketV2Issue],
) -> list[PublicRecrawlOperatorPacketV2Issue]:
    seen: set[tuple[str, str]] = set()
    unique: list[PublicRecrawlOperatorPacketV2Issue] = []
    for issue in issues:
        key = (issue.code, issue.path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(issue)
    return unique
