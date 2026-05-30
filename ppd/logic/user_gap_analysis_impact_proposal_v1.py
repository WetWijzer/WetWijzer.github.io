"""Fixture-first impact proposal builder and validator for PP&D user gap analysis v1."""

from __future__ import annotations

import argparse
import copy
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

JsonObject = dict[str, Any]

IMPACT_CATEGORIES: tuple[str, ...] = (
    "required_user_facts",
    "matched_documents",
    "missing_documents",
    "stale_or_conflicting_evidence",
    "required_confirmations",
    "blocked_actions",
    "next_safe_actions",
)

CATEGORY_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "required_user_facts": ("required_user_facts", "missing_facts", "known_facts"),
    "matched_documents": ("matched_documents",),
    "missing_documents": ("missing_documents",),
    "stale_or_conflicting_evidence": ("stale_evidence", "conflicting_evidence"),
    "required_confirmations": ("required_confirmations",),
    "blocked_actions": ("blocked_actions",),
    "next_safe_actions": ("next_safe_actions",),
}

DEFAULT_OFFLINE_VALIDATION_COMMANDS: list[list[str]] = [
    ["python3", "-m", "py_compile", "ppd/logic/user_gap_analysis_impact_proposal_v1.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_user_gap_analysis_impact_proposal_v1.py"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

_BLOCKED_ARTIFACT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_artifact", re.compile(r"\b(private artifact|private devhub|private upload|private value|applicant[-_ ]specific|customer[-_ ]specific|case[-_ ]specific)\b", re.IGNORECASE)),
    ("authenticated_artifact", re.compile(r"\b(authenticated page|authenticated artifact|auth state|logged[-_ ]in page|signed[-_ ]in page|devhub home)\b", re.IGNORECASE)),
    ("session_artifact", re.compile(r"\b(session token|session cookie|cookie|credential|password|storage[-_ ]state|local[-_ ]storage|access token|refresh token)\b", re.IGNORECASE)),
    ("browser_artifact", re.compile(r"\b(playwright trace|browser trace|har file|\.har\b|screenshot|screen shot|browser[-_ ]state|cdp log|video artifact)\b", re.IGNORECASE)),
    ("raw_crawl_or_download_artifact", re.compile(r"\b(raw[-_ ]?(crawl|html|body|response|capture|pdf)|warc|downloaded[-_ ]?(data|document|pdf)|pdf[-_ ]?download)\b", re.IGNORECASE)),
)

_OUTCOME_GUARANTEE_PATTERN = re.compile(
    r"\b(guarantee[sd]?|approval guaranteed|permit guaranteed|issuance guaranteed|will be approved|will receive approval|permit will issue|legally compliant|legal compliance guaranteed|no legal risk|definitely qualifies)\b",
    re.IGNORECASE,
)

_CONSEQUENTIAL_EXECUTION_PATTERN = re.compile(
    r"\b((agent|automation|system|worker|proposal|we)\s+(will|should|can|may|must)?\s*(submit|certify|attest|acknowledge|upload|pay|purchase|schedule|cancel|withdraw|reactivate|create account|reset password|complete mfa|solve captcha|finalize)|click\s+(submit|pay|certify|acknowledge|upload|finalize)|enter\s+payment|execute\s+(submission|payment|upload|certification)|perform\s+(submission|payment|upload|certification)|schedule\s+(an\s+)?inspection|cancel\s+(the\s+)?permit)\b",
    re.IGNORECASE,
)

_MUTATION_TARGETS = (
    "user_gap",
    "source",
    "document",
    "requirement",
    "process",
    "guardrail",
    "prompt",
    "release_state",
    "agent_state",
)

_MUTATION_CONTAINERS = (
    "mutation_policy",
    "mutation_flags",
    "no_active_mutation_attestations",
    "active_mutation_flags",
)


@dataclass(frozen=True)
class UserGapAnalysisImpactProposalFinding:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class UserGapAnalysisImpactProposalValidationResult:
    ok: bool
    findings: tuple[UserGapAnalysisImpactProposalFinding, ...]


class UserGapAnalysisImpactProposalValidationError(ValueError):
    def __init__(self, result: UserGapAnalysisImpactProposalValidationResult) -> None:
        self.result = result
        detail = "; ".join(f"{finding.code} at {finding.path}" for finding in result.findings)
        super().__init__(detail or "invalid user gap analysis impact proposal v1")


def load_json_fixture(path: str | Path) -> JsonObject:
    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as fixture_file:
        loaded = json.load(fixture_file)
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected JSON object fixture at {fixture_path}")
    return loaded


def build_user_gap_analysis_impact_proposal_v1(
    *,
    process_model_impact_proposal: JsonObject,
    guardrail_bundle_impact_proposal: JsonObject,
    user_gap_analysis: JsonObject,
    reviewer_owner: str = "ppd-agent-readiness-reviewer",
    rollback_note: str = (
        "Discard this fixture-first proposal packet and rerun offline validation; no active "
        "user-gap fixtures, process models, guardrails, prompts, release state, or agent state "
        "are mutated by this builder."
    ),
    offline_validation_commands: list[list[str]] | None = None,
) -> JsonObject:
    process_input = copy.deepcopy(process_model_impact_proposal)
    guardrail_input = copy.deepcopy(guardrail_bundle_impact_proposal)
    gap_input = copy.deepcopy(user_gap_analysis)

    case_id = _required_string(gap_input, "case_id")
    process_id = _required_string(gap_input, "process_id")
    guardrail_bundle_id = _first_string(
        gap_input.get("guardrail_bundle_id"),
        guardrail_input.get("guardrail_bundle_id"),
        process_input.get("guardrail_bundle_id"),
        "unknown_guardrail_bundle",
    )
    process_proposal_id = _first_string(process_input.get("proposal_id"), process_input.get("impact_proposal_id"), "process_model_impact_proposal_v1_fixture")
    guardrail_proposal_id = _first_string(guardrail_input.get("proposal_id"), guardrail_input.get("impact_proposal_id"), "guardrail_bundle_impact_proposal_v1_fixture")

    proposed_impacts: list[JsonObject] = []
    previous_impact_ids: list[str] = []
    for order, category in enumerate(IMPACT_CATEGORIES, start=1):
        raw_items = _collect_category_items(gap_input, category)
        citations = _dedupe_strings(
            _collect_item_citations(raw_items)
            + _collect_supporting_citations(
                category=category,
                process_model_impact_proposal=process_input,
                guardrail_bundle_impact_proposal=guardrail_input,
            )
            + [f"user_gap_analysis:{case_id}:{category}"]
        )
        impact_id = f"ugaip-v1-{case_id}-{order:02d}-{category}".replace(" ", "_")
        proposed_impacts.append(
            {
                "impact_id": impact_id,
                "category": category,
                "summary": _category_summary(category, raw_items),
                "proposed_impacts": _normalize_items(raw_items),
                "citations": citations,
                "affected_case_ids": [case_id],
                "affected_process_ids": [process_id],
                "affected_guardrail_bundle_ids": [guardrail_bundle_id],
                "dependency_order": order,
                "depends_on_impact_ids": list(previous_impact_ids),
                "reviewer_owner": reviewer_owner,
                "rollback_note": rollback_note,
                "offline_validation_commands": copy.deepcopy(offline_validation_commands or DEFAULT_OFFLINE_VALIDATION_COMMANDS),
            }
        )
        previous_impact_ids.append(impact_id)

    proposal = {
        "proposal_id": f"user_gap_analysis_impact_proposal_v1:{case_id}",
        "proposal_version": "v1",
        "fixture_first": True,
        "source_inputs": {
            "process_model_impact_proposal_id": process_proposal_id,
            "guardrail_bundle_impact_proposal_id": guardrail_proposal_id,
            "user_gap_analysis_case_id": case_id,
        },
        "affected_case_ids": [case_id],
        "affected_process_ids": [process_id],
        "affected_guardrail_bundle_ids": [guardrail_bundle_id],
        "reviewer_owner": reviewer_owner,
        "rollback_note": rollback_note,
        "proposed_impacts": proposed_impacts,
        "dependency_order": [impact["impact_id"] for impact in proposed_impacts],
        "offline_validation_commands": copy.deepcopy(offline_validation_commands or DEFAULT_OFFLINE_VALIDATION_COMMANDS),
        "mutation_policy": {
            "mutates_active_user_gap_fixtures": False,
            "mutates_sources": False,
            "mutates_documents": False,
            "mutates_requirements": False,
            "mutates_process_models": False,
            "mutates_guardrails": False,
            "mutates_prompts": False,
            "mutates_release_state": False,
            "mutates_agent_state": False,
        },
    }
    assert_valid_user_gap_analysis_impact_proposal_v1(proposal)
    return proposal


def build_from_fixture_paths(
    *,
    process_model_impact_proposal_path: str | Path,
    guardrail_bundle_impact_proposal_path: str | Path,
    user_gap_analysis_path: str | Path,
    reviewer_owner: str = "ppd-agent-readiness-reviewer",
) -> JsonObject:
    return build_user_gap_analysis_impact_proposal_v1(
        process_model_impact_proposal=load_json_fixture(process_model_impact_proposal_path),
        guardrail_bundle_impact_proposal=load_json_fixture(guardrail_bundle_impact_proposal_path),
        user_gap_analysis=load_json_fixture(user_gap_analysis_path),
        reviewer_owner=reviewer_owner,
    )


def validate_user_gap_analysis_impact_proposal_v1(proposal: Mapping[str, Any]) -> UserGapAnalysisImpactProposalValidationResult:
    findings: list[UserGapAnalysisImpactProposalFinding] = []
    if not isinstance(proposal, Mapping):
        findings.append(UserGapAnalysisImpactProposalFinding("proposal_not_mapping", "$", "proposal must be an object"))
        return UserGapAnalysisImpactProposalValidationResult(False, tuple(findings))

    if not _non_empty_sequence(proposal.get("affected_case_ids")):
        findings.append(UserGapAnalysisImpactProposalFinding("missing_affected_case_ids", "$.affected_case_ids", "affected case IDs are required"))
    if not _non_empty_sequence(proposal.get("affected_process_ids")):
        findings.append(UserGapAnalysisImpactProposalFinding("missing_affected_process_ids", "$.affected_process_ids", "affected process IDs are required"))
    if not _non_empty_sequence(proposal.get("affected_guardrail_bundle_ids")):
        findings.append(UserGapAnalysisImpactProposalFinding("missing_affected_guardrail_bundle_ids", "$.affected_guardrail_bundle_ids", "affected guardrail bundle IDs are required"))
    if not _non_empty_sequence(proposal.get("dependency_order")):
        findings.append(UserGapAnalysisImpactProposalFinding("missing_dependency_order", "$.dependency_order", "top-level dependency order is required"))
    if not _non_empty_text(proposal.get("reviewer_owner")):
        findings.append(UserGapAnalysisImpactProposalFinding("missing_reviewer_owner", "$.reviewer_owner", "reviewer owner is required"))
    if not _non_empty_text(proposal.get("rollback_note")):
        findings.append(UserGapAnalysisImpactProposalFinding("missing_rollback_note", "$.rollback_note", "rollback note is required"))

    rows = proposal.get("proposed_impacts")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        findings.append(UserGapAnalysisImpactProposalFinding("missing_impact_rows", "$.proposed_impacts", "at least one impact row is required"))
    else:
        for index, row in enumerate(rows):
            path = f"$.proposed_impacts[{index}]"
            if not isinstance(row, Mapping):
                findings.append(UserGapAnalysisImpactProposalFinding("impact_row_not_mapping", path, "impact row must be an object"))
                continue
            category = row.get("category")
            if category not in IMPACT_CATEGORIES:
                findings.append(UserGapAnalysisImpactProposalFinding("missing_gap_or_action_expectation_category", path + ".category", "row category must be a v1 gap or action expectation category"))
            if not _non_empty_sequence(row.get("citations")):
                findings.append(UserGapAnalysisImpactProposalFinding("uncited_impact_row", path + ".citations", "impact row must include citations"))
            if not _non_empty_sequence(row.get("affected_case_ids")):
                findings.append(UserGapAnalysisImpactProposalFinding("missing_affected_case_ids", path + ".affected_case_ids", "impact row must name affected cases"))
            if not _non_empty_sequence(row.get("affected_process_ids")):
                findings.append(UserGapAnalysisImpactProposalFinding("missing_affected_process_ids", path + ".affected_process_ids", "impact row must name affected processes"))
            if not _non_empty_sequence(row.get("affected_guardrail_bundle_ids")):
                findings.append(UserGapAnalysisImpactProposalFinding("missing_affected_guardrail_bundle_ids", path + ".affected_guardrail_bundle_ids", "impact row must name affected guardrail bundles"))
            if row.get("dependency_order") is None:
                findings.append(UserGapAnalysisImpactProposalFinding("missing_dependency_order", path + ".dependency_order", "impact row dependency order is required"))
            if not _non_empty_text(row.get("reviewer_owner")):
                findings.append(UserGapAnalysisImpactProposalFinding("missing_reviewer_owner", path + ".reviewer_owner", "impact row reviewer owner is required"))
            if not _non_empty_text(row.get("rollback_note")):
                findings.append(UserGapAnalysisImpactProposalFinding("missing_rollback_note", path + ".rollback_note", "impact row rollback note is required"))

    _reject_prohibited_text(proposal, "$", findings)
    _reject_active_mutation_flags(proposal, findings)
    return UserGapAnalysisImpactProposalValidationResult(not findings, tuple(findings))


def assert_valid_user_gap_analysis_impact_proposal_v1(proposal: Mapping[str, Any]) -> None:
    result = validate_user_gap_analysis_impact_proposal_v1(proposal)
    if not result.ok:
        raise UserGapAnalysisImpactProposalValidationError(result)


def finding_codes(result: UserGapAnalysisImpactProposalValidationResult) -> tuple[str, ...]:
    return tuple(finding.code for finding in result.findings)


def _required_string(mapping: JsonObject, key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Expected non-empty string field: {key}")
    return value.strip()


def _first_string(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unknown"


def _collect_category_items(user_gap_analysis: JsonObject, category: str) -> list[Any]:
    items: list[Any] = []
    for field_name in CATEGORY_FIELD_MAP[category]:
        value = user_gap_analysis.get(field_name, [])
        if isinstance(value, dict):
            for fact_key, fact_value in sorted(value.items()):
                items.append({"field": field_name, "key": fact_key, "value": fact_value})
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    normalized = dict(item)
                    normalized.setdefault("field", field_name)
                    items.append(normalized)
                else:
                    items.append({"field": field_name, "value": item})
        elif value:
            items.append({"field": field_name, "value": value})
    return items


def _normalize_items(items: Iterable[Any]) -> list[JsonObject]:
    normalized: list[JsonObject] = []
    for index, item in enumerate(items, start=1):
        normalized_item = copy.deepcopy(item) if isinstance(item, dict) else {"value": item}
        normalized_item.setdefault("item_id", f"item-{index:02d}")
        normalized.append(normalized_item)
    return normalized


def _collect_item_citations(items: Iterable[Any]) -> list[str]:
    citations: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        for key in ("citation", "citation_id", "evidence_id", "source_evidence_id"):
            value = item.get(key)
            if isinstance(value, str):
                citations.append(value)
        for key in ("citations", "evidence_ids", "source_evidence_ids"):
            value = item.get(key)
            if isinstance(value, list):
                citations.extend(str(entry) for entry in value if str(entry).strip())
    return citations


def _collect_supporting_citations(*, category: str, process_model_impact_proposal: JsonObject, guardrail_bundle_impact_proposal: JsonObject) -> list[str]:
    citations: list[str] = []
    citations.extend(_citations_for_category(process_model_impact_proposal, category))
    citations.extend(_citations_for_category(guardrail_bundle_impact_proposal, category))
    for source_name, source in (("process_model_impact_proposal", process_model_impact_proposal), ("guardrail_bundle_impact_proposal", guardrail_bundle_impact_proposal)):
        source_id = _first_string(source.get("proposal_id"), source.get("impact_proposal_id"), source_name)
        citations.append(f"{source_name}:{source_id}:{category}")
    return citations


def _citations_for_category(source: JsonObject, category: str) -> list[str]:
    citations: list[str] = []
    for item in source.get("proposed_impacts", []):
        if not isinstance(item, dict) or item.get("category") not in (category, "all", None):
            continue
        value = item.get("citations")
        if isinstance(value, list):
            citations.extend(str(entry) for entry in value if str(entry).strip())
    for key in ("citations", "source_evidence_ids"):
        value = source.get(key)
        if isinstance(value, list):
            citations.extend(str(entry) for entry in value if str(entry).strip())
    return citations


def _category_summary(category: str, items: list[Any]) -> str:
    readable = category.replace("_", " ")
    if items:
        return f"Propose {len(items)} cited impact item(s) for {readable}."
    return f"No cited impact items proposed for {readable}; preserve explicit empty review state."


def _dedupe_strings(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = str(value).strip()
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
    return result


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and len(value) > 0


def _iter_text_leaves(value: Any, path: str) -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            yield from _iter_text_leaves(child, f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            yield from _iter_text_leaves(child, f"{path}[{index}]")


def _reject_prohibited_text(value: Any, path: str, findings: list[UserGapAnalysisImpactProposalFinding]) -> None:
    for text_path, text in _iter_text_leaves(value, path):
        for code, pattern in _BLOCKED_ARTIFACT_PATTERNS:
            if pattern.search(text):
                findings.append(UserGapAnalysisImpactProposalFinding(code, text_path, "proposal must not reference private, authenticated, session, browser, raw crawl, PDF download, or downloaded data artifacts"))
                break
        if _OUTCOME_GUARANTEE_PATTERN.search(text):
            findings.append(UserGapAnalysisImpactProposalFinding("outcome_guarantee", text_path, "proposal must not guarantee legal, permitting, approval, issuance, or risk outcomes"))
        if _CONSEQUENTIAL_EXECUTION_PATTERN.search(text):
            findings.append(UserGapAnalysisImpactProposalFinding("consequential_action_execution_language", text_path, "proposal must not direct execution of consequential official, financial, account, upload, scheduling, cancellation, or certification actions"))


def _reject_active_mutation_flags(proposal: Mapping[str, Any], findings: list[UserGapAnalysisImpactProposalFinding]) -> None:
    for container_name in _MUTATION_CONTAINERS:
        value = proposal.get(container_name)
        if value is None:
            continue
        if not isinstance(value, Mapping):
            findings.append(UserGapAnalysisImpactProposalFinding("mutation_flags_not_mapping", f"$.{container_name}", "mutation flags must be an object when present"))
            continue
        _scan_mutation_mapping(value, f"$.{container_name}", findings)


def _scan_mutation_mapping(mapping: Mapping[str, Any], path: str, findings: list[UserGapAnalysisImpactProposalFinding]) -> None:
    for raw_key, value in mapping.items():
        child_path = f"{path}.{raw_key}"
        if isinstance(value, Mapping):
            _scan_mutation_mapping(value, child_path, findings)
            continue
        key = str(raw_key).strip().lower().replace("-", "_").replace(" ", "_")
        key = key.removeprefix("mutates_active_").removeprefix("active_").removesuffix("_fixtures").removesuffix("_models").removesuffix("s")
        target_match = any(target == key or target in key for target in _MUTATION_TARGETS)
        mutation_named = "mutat" in key or str(raw_key).strip().lower().startswith("active_") or path.endswith("mutation_flags") or path.endswith("active_mutation_flags")
        active = value is True or (isinstance(value, str) and value.strip().lower() in {"true", "active", "yes", "1"})
        if target_match and mutation_named and active:
            findings.append(UserGapAnalysisImpactProposalFinding("active_mutation_flag", child_path, "active user-gap, source, document, requirement, process, guardrail, prompt, release-state, or agent-state mutation flags are rejected"))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build PP&D user gap analysis impact proposal v1 from fixtures.")
    parser.add_argument("--process-model-impact-proposal", required=True)
    parser.add_argument("--guardrail-bundle-impact-proposal", required=True)
    parser.add_argument("--user-gap-analysis", required=True)
    parser.add_argument("--reviewer-owner", default="ppd-agent-readiness-reviewer")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    proposal = build_from_fixture_paths(
        process_model_impact_proposal_path=args.process_model_impact_proposal,
        guardrail_bundle_impact_proposal_path=args.guardrail_bundle_impact_proposal,
        user_gap_analysis_path=args.user_gap_analysis,
        reviewer_owner=args.reviewer_owner,
    )
    print(json.dumps(proposal, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
