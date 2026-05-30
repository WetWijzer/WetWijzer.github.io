"""Validation for PP&D public crawl frontier expansion plans.

The v1 plan is intentionally metadata-only. It may propose public URLs for later
policy preflight, but it must not carry private browser/session material, raw page
bodies, downloaded artifacts, completion claims, legal outcome promises, or flags
that mutate active PP&D state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse


PLAN_VERSION = "public_crawl_frontier_expansion_plan_v1"

ALLOWLISTED_HOSTS = frozenset(
    {
        "www.portland.gov",
        "devhub.portlandoregon.gov",
        "www.portlandoregon.gov",
        "www.portlandmaps.com",
    }
)

DECISIONS = frozenset({"allow", "skip"})

RAW_OR_DOWNLOADED_KEYS = frozenset(
    {
        "raw_body",
        "raw_html",
        "html_body",
        "response_body",
        "body",
        "content",
        "downloaded_artifact",
        "downloaded_artifact_ref",
        "downloaded_file",
        "download_path",
        "local_download_path",
        "raw_download",
        "raw_download_ref",
        "raw_archive_ref",
        "warc_path",
        "archive_artifact_ref",
        "artifact_path",
    }
)

PRIVATE_OR_BROWSER_KEYS = frozenset(
    {
        "cookie",
        "cookies",
        "credential",
        "credentials",
        "password",
        "session",
        "session_id",
        "session_state",
        "storage_state",
        "auth_state",
        "auth_token",
        "access_token",
        "refresh_token",
        "csrf_token",
        "trace",
        "trace_path",
        "har",
        "har_path",
        "screenshot",
        "screenshot_path",
        "browser_context",
        "playwright_state",
        "private_file_path",
    }
)

PROCESSOR_COMPLETION_KEYS = frozenset(
    {
        "processor_completed",
        "processor_complete",
        "processor_completion_claim",
        "completed_by_processor",
        "archive_completed",
        "crawl_completed",
        "extraction_completed",
        "processor_result_complete",
    }
)

MUTATION_FLAG_KEYS = frozenset(
    {
        "mutate_source_registry",
        "source_registry_mutation",
        "mutate_sources",
        "writes_sources",
        "mutate_crawl_frontier",
        "crawl_frontier_mutation",
        "writes_crawl_frontier",
        "mutate_archive",
        "archive_mutation",
        "writes_archive",
        "mutate_requirements",
        "requirement_mutation",
        "writes_requirements",
        "mutate_guardrails",
        "guardrail_mutation",
        "writes_guardrails",
        "mutate_release_state",
        "release_state_mutation",
        "writes_release_state",
        "mutate_agent_state",
        "agent_state_mutation",
        "writes_agent_state",
    }
)

AUTHENTICATED_PATH_MARKERS = (
    "/login",
    "/logout",
    "/signin",
    "/sign-in",
    "/register",
    "/account",
    "/accounts",
    "/profile",
    "/dashboard",
    "/my-permits",
    "/mypermits",
    "/my-requests",
    "/cart",
    "/checkout",
    "/payment",
    "/payments",
    "/secure",
    "/private",
    "/permit/application",
    "/permit/submit",
    "/inspection/schedule",
)

AUTHENTICATED_QUERY_KEYS = frozenset(
    {
        "token",
        "session",
        "sessionid",
        "auth",
        "code",
        "state",
        "saml",
        "ticket",
        "jwt",
    }
)

OUTCOME_GUARANTEE_PHRASES = (
    "guarantee approval",
    "approval is guaranteed",
    "permit approval guaranteed",
    "permit will be approved",
    "will be approved",
    "guaranteed permit",
    "guaranteed issuance",
    "issuance is guaranteed",
    "legal compliance guaranteed",
    "guarantees code compliance",
    "guarantee code compliance",
)


@dataclass(frozen=True)
class FrontierPlanFinding:
    code: str
    message: str
    path: str


def validate_frontier_expansion_plan_v1(plan: Mapping[str, Any]) -> list[FrontierPlanFinding]:
    """Return validation findings for a public crawl frontier expansion plan."""

    findings: list[FrontierPlanFinding] = []

    if plan.get("version") != PLAN_VERSION:
        findings.append(
            FrontierPlanFinding(
                "invalid_plan_version",
                f"plan version must be {PLAN_VERSION}",
                "version",
            )
        )

    candidates = plan.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        findings.append(
            FrontierPlanFinding(
                "missing_candidates",
                "plan must include at least one candidate",
                "candidates",
            )
        )
        candidates = []

    _scan_for_forbidden_material(plan, findings, "$")

    for index, candidate in enumerate(candidates):
        candidate_path = f"candidates[{index}]"
        if not isinstance(candidate, Mapping):
            findings.append(
                FrontierPlanFinding(
                    "invalid_candidate",
                    "candidate must be an object",
                    candidate_path,
                )
            )
            continue

        url = candidate.get("url")
        if not isinstance(url, str) or not url.strip():
            findings.append(
                FrontierPlanFinding("missing_url", "candidate must include a URL", f"{candidate_path}.url")
            )
        else:
            _validate_public_https_url(url, findings, f"{candidate_path}.url")

        source_page_url = _first_string(
            candidate,
            ("source_page_url", "source_url", "from_source_url", "discovered_on_url"),
        )
        provenance = candidate.get("provenance")
        if source_page_url is None and isinstance(provenance, Mapping):
            source_page_url = _first_string(
                provenance,
                ("source_page_url", "source_url", "from_source_url", "discovered_on_url"),
            )

        if source_page_url is None:
            findings.append(
                FrontierPlanFinding(
                    "missing_source_page_provenance",
                    "candidate must identify the public source page that exposed the URL",
                    candidate_path,
                )
            )
        else:
            _validate_public_https_url(source_page_url, findings, f"{candidate_path}.source_page_url")

        if not _has_citation(candidate):
            findings.append(
                FrontierPlanFinding(
                    "uncited_candidate",
                    "candidate must include at least one citation or source evidence id",
                    candidate_path,
                )
            )

        decision = _extract_decision(candidate)
        if decision not in DECISIONS:
            findings.append(
                FrontierPlanFinding(
                    "missing_allow_skip_decision",
                    "candidate decision must be allow or skip",
                    candidate_path,
                )
            )
        elif decision == "skip" and not _first_string(candidate, ("skip_reason", "reason")):
            findings.append(
                FrontierPlanFinding(
                    "missing_skip_reason",
                    "skipped candidate must include a skip reason",
                    candidate_path,
                )
            )

    return findings


def assert_valid_frontier_expansion_plan_v1(plan: Mapping[str, Any]) -> None:
    findings = validate_frontier_expansion_plan_v1(plan)
    if findings:
        details = "; ".join(f"{finding.path}: {finding.code}" for finding in findings)
        raise ValueError(f"invalid {PLAN_VERSION}: {details}")


def _validate_public_https_url(url: str, findings: list[FrontierPlanFinding], path: str) -> None:
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()

    if parsed.scheme != "https":
        findings.append(
            FrontierPlanFinding("non_https_url", "public crawl candidates must use HTTPS URLs", path)
        )

    if hostname not in ALLOWLISTED_HOSTS:
        findings.append(
            FrontierPlanFinding(
                "non_allowlisted_url",
                "URL host is outside the PP&D public crawl allowlist",
                path,
            )
        )

    lowered_path = parsed.path.lower()
    if any(marker in lowered_path for marker in AUTHENTICATED_PATH_MARKERS):
        findings.append(
            FrontierPlanFinding(
                "authenticated_or_private_url",
                "URL appears to target authenticated or private workflow state",
                path,
            )
        )

    query_keys = {part.split("=", 1)[0].lower() for part in parsed.query.split("&") if part}
    if query_keys & AUTHENTICATED_QUERY_KEYS:
        findings.append(
            FrontierPlanFinding(
                "authenticated_or_private_url",
                "URL query appears to contain authentication or session state",
                path,
            )
        )


def _scan_for_forbidden_material(
    value: Any,
    findings: list[FrontierPlanFinding],
    path: str,
) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.lower()
            child_path = f"{path}.{key_text}"

            if normalized_key in RAW_OR_DOWNLOADED_KEYS and _is_present(child):
                findings.append(
                    FrontierPlanFinding(
                        "raw_body_or_downloaded_artifact_reference",
                        "frontier plans must not include raw bodies or downloaded artifact references",
                        child_path,
                    )
                )

            if normalized_key in PRIVATE_OR_BROWSER_KEYS and _is_present(child):
                findings.append(
                    FrontierPlanFinding(
                        "private_session_or_browser_artifact",
                        "frontier plans must not include private, session, or browser artifacts",
                        child_path,
                    )
                )

            if normalized_key in PROCESSOR_COMPLETION_KEYS and _truthy_or_completed(child):
                findings.append(
                    FrontierPlanFinding(
                        "processor_completion_claim",
                        "frontier plans must not claim processor, crawl, archive, or extraction completion",
                        child_path,
                    )
                )

            if normalized_key == "processor_status" and str(child).lower() in {"complete", "completed", "success", "succeeded"}:
                findings.append(
                    FrontierPlanFinding(
                        "processor_completion_claim",
                        "frontier plans must not claim processor completion",
                        child_path,
                    )
                )

            if normalized_key in MUTATION_FLAG_KEYS and _truthy_or_completed(child):
                findings.append(
                    FrontierPlanFinding(
                        "active_state_mutation_flag",
                        "frontier plans must not include active state mutation flags",
                        child_path,
                    )
                )

            if isinstance(child, str) and _contains_outcome_guarantee(child):
                findings.append(
                    FrontierPlanFinding(
                        "legal_or_permitting_outcome_guarantee",
                        "frontier plans must not guarantee legal, permitting, approval, or issuance outcomes",
                        child_path,
                    )
                )

            _scan_for_forbidden_material(child, findings, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_for_forbidden_material(child, findings, f"{path}[{index}]")
    elif isinstance(value, str) and _contains_outcome_guarantee(value):
        findings.append(
            FrontierPlanFinding(
                "legal_or_permitting_outcome_guarantee",
                "frontier plans must not guarantee legal, permitting, approval, or issuance outcomes",
                path,
            )
        )


def _contains_outcome_guarantee(text: str) -> bool:
    lowered = " ".join(text.lower().split())
    return any(phrase in lowered for phrase in OUTCOME_GUARANTEE_PHRASES)


def _extract_decision(candidate: Mapping[str, Any]) -> str | None:
    decision = candidate.get("allow_skip_decision", candidate.get("decision"))
    if isinstance(decision, str):
        return decision.strip().lower()
    if isinstance(decision, Mapping):
        action = decision.get("action") or decision.get("decision")
        if isinstance(action, str):
            return action.strip().lower()
    return None


def _has_citation(candidate: Mapping[str, Any]) -> bool:
    for key in ("citations", "citation_spans", "source_citations", "source_evidence_ids"):
        value = candidate.get(key)
        if _non_empty_sequence_or_string(value):
            return True
    evidence = candidate.get("evidence")
    if isinstance(evidence, Mapping):
        return any(
            _non_empty_sequence_or_string(evidence.get(key))
            for key in ("citations", "citation_spans", "source_citations", "source_evidence_ids")
        )
    return False


def _first_string(mapping: Mapping[str, Any], keys: Iterable[str]) -> str | None:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _non_empty_sequence_or_string(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(_is_present(item) for item in value)
    if isinstance(value, tuple):
        return any(_is_present(item) for item in value)
    return False


def _is_present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    return True


def _truthy_or_completed(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "complete", "completed", "success", "succeeded", "write", "mutate"}
    return bool(value)
