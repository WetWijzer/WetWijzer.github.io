'''Guardrail bundle impact proposal v1 validation for PP&D fixtures.'''

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

JsonObject = dict[str, Any]

IMPACT_CATEGORIES: tuple[str, ...] = ('predicate', 'explanation_template')
MUTATION_TARGETS: tuple[str, ...] = (
    'source',
    'document',
    'requirement',
    'process',
    'guardrail',
    'prompt',
    'release_state',
    'agent_state',
)
MUTATION_CONTAINERS: tuple[str, ...] = (
    'mutation_policy',
    'mutation_flags',
    'active_mutation_flags',
    'no_active_mutation_attestations',
)

_BLOCKED_TEXT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ('private_artifact', re.compile(r'\b(private artifact|private devhub|private upload|private value|applicant[-_ ]specific|customer[-_ ]specific|case[-_ ]specific)\b', re.IGNORECASE)),
    ('authenticated_artifact', re.compile(r'\b(authenticated page|authenticated artifact|auth state|logged[-_ ]in page|signed[-_ ]in page|devhub home)\b', re.IGNORECASE)),
    ('session_artifact', re.compile(r'\b(session token|session cookie|cookie|credential|password|storage[-_ ]state|local[-_ ]storage|access token|refresh token)\b', re.IGNORECASE)),
    ('browser_artifact', re.compile(r'\b(playwright trace|browser trace|har file|\.har\b|screenshot|screen shot|browser[-_ ]state|cdp log|video artifact)\b', re.IGNORECASE)),
    ('raw_crawl_or_download_artifact', re.compile(r'\b(raw[-_ ]?(crawl|html|body|response|capture|pdf|data)|warc|downloaded[-_ ]?(data|document|pdf)|pdf[-_ ]?download)\b', re.IGNORECASE)),
)
_OUTCOME_GUARANTEE_PATTERN = re.compile(
    r'\b(guarantee[sd]?|approval guaranteed|permit guaranteed|issuance guaranteed|will be approved|will receive approval|permit will issue|legally compliant|legal compliance guaranteed|no legal risk|definitely qualifies)\b',
    re.IGNORECASE,
)
_CONSEQUENTIAL_EXECUTION_PATTERN = re.compile(
    r'\b((agent|automation|system|worker|proposal|we)\s+(will|should|can|may|must)?\s*(submit|certify|attest|acknowledge|upload|pay|purchase|schedule|cancel|withdraw|reactivate|create account|reset password|complete mfa|solve captcha|finalize)|click\s+(submit|pay|certify|acknowledge|upload|finalize)|enter\s+payment|execute\s+(submission|payment|upload|certification)|perform\s+(submission|payment|upload|certification)|schedule\s+(an\s+)?inspection|cancel\s+(the\s+)?permit)\b',
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GuardrailBundleImpactProposalFinding:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class GuardrailBundleImpactProposalValidationResult:
    ok: bool
    findings: tuple[GuardrailBundleImpactProposalFinding, ...]


class GuardrailBundleImpactProposalValidationError(ValueError):
    def __init__(self, result: GuardrailBundleImpactProposalValidationResult) -> None:
        self.result = result
        detail = '; '.join(f'{finding.code} at {finding.path}' for finding in result.findings)
        super().__init__(detail or 'invalid guardrail bundle impact proposal v1')


def load_json_fixture(path: str | Path) -> JsonObject:
    fixture_path = Path(path)
    with fixture_path.open('r', encoding='utf-8') as fixture_file:
        loaded = json.load(fixture_file)
    if not isinstance(loaded, dict):
        raise ValueError(f'Expected JSON object fixture at {fixture_path}')
    return loaded


def validate_guardrail_bundle_impact_proposal_v1(proposal: Mapping[str, Any]) -> GuardrailBundleImpactProposalValidationResult:
    findings: list[GuardrailBundleImpactProposalFinding] = []
    if not isinstance(proposal, Mapping):
        findings.append(GuardrailBundleImpactProposalFinding('proposal_not_mapping', '$', 'proposal must be an object'))
        return GuardrailBundleImpactProposalValidationResult(False, tuple(findings))

    if not _non_empty_sequence(proposal.get('affected_guardrail_bundle_ids')):
        findings.append(GuardrailBundleImpactProposalFinding('missing_affected_guardrail_bundle_ids', '$.affected_guardrail_bundle_ids', 'affected guardrail bundle IDs are required'))
    if not _non_empty_sequence(proposal.get('affected_process_ids')):
        findings.append(GuardrailBundleImpactProposalFinding('missing_affected_process_ids', '$.affected_process_ids', 'affected process IDs are required'))
    if not _non_empty_sequence(proposal.get('affected_requirement_ids')):
        findings.append(GuardrailBundleImpactProposalFinding('missing_affected_requirement_ids', '$.affected_requirement_ids', 'affected requirement IDs are required'))
    if not _non_empty_sequence(proposal.get('dependency_order')):
        findings.append(GuardrailBundleImpactProposalFinding('missing_dependency_order', '$.dependency_order', 'top-level dependency order is required'))
    if not _non_empty_text(proposal.get('reviewer_owner')):
        findings.append(GuardrailBundleImpactProposalFinding('missing_reviewer_owner', '$.reviewer_owner', 'reviewer owner is required'))
    if not _non_empty_text(proposal.get('rollback_note')):
        findings.append(GuardrailBundleImpactProposalFinding('missing_rollback_note', '$.rollback_note', 'rollback note is required'))

    rows = proposal.get('proposed_impacts')
    observed_categories: set[str] = set()
    row_ids: list[str] = []
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        findings.append(GuardrailBundleImpactProposalFinding('missing_impact_rows', '$.proposed_impacts', 'at least one impact row is required'))
    else:
        for index, row in enumerate(rows):
            path = f'$.proposed_impacts[{index}]'
            if not isinstance(row, Mapping):
                findings.append(GuardrailBundleImpactProposalFinding('impact_row_not_mapping', path, 'impact row must be an object'))
                continue
            row_id = row.get('impact_id')
            if isinstance(row_id, str) and row_id.strip():
                row_ids.append(row_id)
            category = row.get('category')
            if isinstance(category, str):
                observed_categories.add(category)
            if category not in IMPACT_CATEGORIES:
                findings.append(GuardrailBundleImpactProposalFinding('missing_predicate_or_explanation_template_category', path + '.category', 'row category must be predicate or explanation_template'))
            if not _non_empty_sequence(row.get('citations')):
                findings.append(GuardrailBundleImpactProposalFinding('uncited_impact_row', path + '.citations', 'impact row must include citations'))
            if not _non_empty_sequence(row.get('affected_guardrail_bundle_ids')):
                findings.append(GuardrailBundleImpactProposalFinding('missing_affected_guardrail_bundle_ids', path + '.affected_guardrail_bundle_ids', 'impact row must name affected guardrail bundles'))
            if not _non_empty_sequence(row.get('affected_process_ids')):
                findings.append(GuardrailBundleImpactProposalFinding('missing_affected_process_ids', path + '.affected_process_ids', 'impact row must name affected processes'))
            if not _non_empty_sequence(row.get('affected_requirement_ids')):
                findings.append(GuardrailBundleImpactProposalFinding('missing_affected_requirement_ids', path + '.affected_requirement_ids', 'impact row must name affected requirements'))
            if row.get('dependency_order') is None:
                findings.append(GuardrailBundleImpactProposalFinding('missing_dependency_order', path + '.dependency_order', 'impact row dependency order is required'))
            if not _non_empty_text(row.get('reviewer_owner')):
                findings.append(GuardrailBundleImpactProposalFinding('missing_reviewer_owner', path + '.reviewer_owner', 'impact row reviewer owner is required'))
            if not _non_empty_text(row.get('rollback_note')):
                findings.append(GuardrailBundleImpactProposalFinding('missing_rollback_note', path + '.rollback_note', 'impact row rollback note is required'))
    missing_categories = sorted(set(IMPACT_CATEGORIES) - observed_categories)
    if missing_categories:
        findings.append(GuardrailBundleImpactProposalFinding('missing_predicate_or_explanation_template_category', '$.proposed_impacts', 'missing required categories: ' + ', '.join(missing_categories)))
    dependency_order = proposal.get('dependency_order')
    if row_ids and isinstance(dependency_order, Sequence) and not isinstance(dependency_order, (str, bytes)):
        if list(dependency_order) != row_ids:
            findings.append(GuardrailBundleImpactProposalFinding('dependency_order_mismatch', '$.dependency_order', 'dependency order must list impact IDs in row order'))

    _reject_prohibited_text(proposal, '$', findings)
    _reject_active_mutation_flags(proposal, findings)
    return GuardrailBundleImpactProposalValidationResult(not findings, tuple(findings))


def assert_valid_guardrail_bundle_impact_proposal_v1(proposal: Mapping[str, Any]) -> None:
    result = validate_guardrail_bundle_impact_proposal_v1(proposal)
    if not result.ok:
        raise GuardrailBundleImpactProposalValidationError(result)


def finding_codes(result: GuardrailBundleImpactProposalValidationResult) -> tuple[str, ...]:
    return tuple(finding.code for finding in result.findings)


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and len(value) > 0


def _iter_text_leaves(value: Any, path: str) -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            yield from _iter_text_leaves(child, f'{path}.{key}')
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            yield from _iter_text_leaves(child, f'{path}[{index}]')


def _reject_prohibited_text(value: Any, path: str, findings: list[GuardrailBundleImpactProposalFinding]) -> None:
    for text_path, text in _iter_text_leaves(value, path):
        for code, pattern in _BLOCKED_TEXT_PATTERNS:
            if pattern.search(text):
                findings.append(GuardrailBundleImpactProposalFinding(code, text_path, 'proposal must not reference private, authenticated, session, browser, raw crawl, PDF download, or downloaded data artifacts'))
                break
        if _OUTCOME_GUARANTEE_PATTERN.search(text):
            findings.append(GuardrailBundleImpactProposalFinding('outcome_guarantee', text_path, 'proposal must not guarantee legal, permitting, approval, issuance, or risk outcomes'))
        if _CONSEQUENTIAL_EXECUTION_PATTERN.search(text):
            findings.append(GuardrailBundleImpactProposalFinding('consequential_action_execution_language', text_path, 'proposal must not direct execution of consequential official, financial, account, upload, scheduling, cancellation, or certification actions'))


def _reject_active_mutation_flags(proposal: Mapping[str, Any], findings: list[GuardrailBundleImpactProposalFinding]) -> None:
    for container_name in MUTATION_CONTAINERS:
        value = proposal.get(container_name)
        if value is None:
            continue
        if not isinstance(value, Mapping):
            findings.append(GuardrailBundleImpactProposalFinding('mutation_flags_not_mapping', f'$.{container_name}', 'mutation flags must be an object when present'))
            continue
        _scan_mutation_mapping(value, f'$.{container_name}', findings)


def _scan_mutation_mapping(mapping: Mapping[str, Any], path: str, findings: list[GuardrailBundleImpactProposalFinding]) -> None:
    for raw_key, value in mapping.items():
        child_path = f'{path}.{raw_key}'
        if isinstance(value, Mapping):
            _scan_mutation_mapping(value, child_path, findings)
            continue
        key = str(raw_key).strip().lower().replace('-', '_').replace(' ', '_')
        normalized = key.removeprefix('mutates_active_').removeprefix('active_').removeprefix('mutates_').removesuffix('_fixtures').removesuffix('_models').removesuffix('s')
        target_match = any(target == normalized or target in normalized for target in MUTATION_TARGETS)
        mutation_named = 'mutat' in key or key.startswith('active_') or path.endswith('mutation_flags') or path.endswith('active_mutation_flags')
        active = value is True or (isinstance(value, str) and value.strip().lower() in {'true', 'active', 'yes', '1'})
        if target_match and mutation_named and active:
            findings.append(GuardrailBundleImpactProposalFinding('active_mutation_flag', child_path, 'active source, document, requirement, process, guardrail, prompt, release-state, or agent-state mutation flags are rejected'))
