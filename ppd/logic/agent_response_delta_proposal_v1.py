from __future__ import annotations

import argparse
import copy
import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

JsonObject = dict[str, Any]

DELTA_CATEGORIES: tuple[str, ...] = (
    'agent_facing_explanation',
    'refusal',
    'missing_information',
    'stale_evidence',
    'blocked_action',
    'next_safe_action',
)

EXPECTED_OUTCOMES: tuple[str, ...] = ('pass', 'block', 'refusal')

AFFECTED_FIXTURE_FAMILIES: tuple[str, ...] = (
    'guardrail_bundle_impact_proposal_v1',
    'user_gap_analysis_impact_proposal_v1',
    'guarded_agent_response_acceptance_packet_v1',
    'agent_response_delta_proposal_v1',
)

DEFAULT_OFFLINE_VALIDATION_COMMANDS: list[list[str]] = [
    ['python3', '-m', 'py_compile', 'ppd/logic/agent_response_delta_proposal_v1.py'],
    ['python3', '-m', 'pytest', 'ppd/tests/test_agent_response_delta_proposal_v1.py'],
    ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'],
]

_CATEGORY_TO_USER_GAP_CATEGORIES: dict[str, tuple[str, ...]] = {
    'agent_facing_explanation': ('required_user_facts', 'missing_documents'),
    'refusal': ('blocked_actions', 'required_confirmations'),
    'missing_information': ('required_user_facts', 'missing_documents'),
    'stale_evidence': ('stale_or_conflicting_evidence',),
    'blocked_action': ('blocked_actions', 'required_confirmations'),
    'next_safe_action': ('next_safe_actions',),
}

_CATEGORY_TO_ACCEPTANCE_EXAMPLES: dict[str, tuple[str, ...]] = {
    'agent_facing_explanation': ('reversible_draft_limits', 'next_safe_read_only_steps'),
    'refusal': ('blocked_official_actions',),
    'missing_information': ('missing_facts',),
    'stale_evidence': ('stale_conflicting_evidence',),
    'blocked_action': ('blocked_official_actions',),
    'next_safe_action': ('next_safe_read_only_steps',),
}

_CATEGORY_TO_EXPECTED_OUTCOME: dict[str, str] = {
    'agent_facing_explanation': 'pass',
    'refusal': 'refusal',
    'missing_information': 'pass',
    'stale_evidence': 'pass',
    'blocked_action': 'block',
    'next_safe_action': 'pass',
}

_BLOCKED_TEXT_NEEDLES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ('private_artifact', ('private artifact', 'private devhub', 'private upload', 'private value', 'applicant-specific', 'customer-specific', 'case-specific')),
    ('authenticated_artifact', ('authenticated page', 'authenticated artifact', 'auth state', 'logged-in page', 'signed-in page', 'devhub home')),
    ('session_artifact', ('session token', 'session cookie', 'cookie', 'credential', 'password', 'storage state', 'local storage', 'access token', 'refresh token')),
    ('browser_artifact', ('playwright trace', 'browser trace', 'har file', '.har', 'screenshot', 'screen shot', 'browser state', 'cdp log', 'video artifact')),
    ('raw_crawl_or_download_artifact', ('raw crawl', 'raw html', 'raw body', 'raw response', 'raw capture', 'raw pdf', 'warc', 'downloaded data', 'downloaded document', 'downloaded pdf', 'pdf download')),
)

_OUTCOME_GUARANTEE_NEEDLES: tuple[str, ...] = (
    'guaranteed',
    'approval guaranteed',
    'permit guaranteed',
    'issuance guaranteed',
    'will be approved',
    'will receive approval',
    'permit will issue',
    'legally compliant',
    'legal compliance guaranteed',
    'no legal risk',
    'definitely qualifies',
)

_CONSEQUENTIAL_EXECUTION_NEEDLES: tuple[str, ...] = (
    'agent will submit',
    'agent will certify',
    'agent will upload',
    'agent will pay',
    'agent will schedule',
    'agent will cancel',
    'automation will submit',
    'system will submit',
    'worker will submit',
    'proposal will submit',
    'we will submit',
    'click submit',
    'click pay',
    'click certify',
    'click upload',
    'enter payment',
    'execute submission',
    'execute payment',
    'execute upload',
    'execute certification',
    'perform submission',
    'perform payment',
    'perform upload',
    'perform certification',
    'schedule inspection',
    'cancel permit',
    'submit permit',
    'upload official',
    'pay fee',
)

_REQUIRED_FALSE_MUTATION_FLAGS: tuple[str, ...] = (
    'mutates_prompts',
    'mutates_active_prompts',
    'mutates_active_guardrails',
    'mutates_process_models',
    'mutates_user_gap_fixtures',
    'mutates_release_state',
    'mutates_agent_state',
    'mutates_user_facing_production_behavior',
)

_MUTATION_DOMAIN_WORDS: tuple[str, ...] = (
    'prompt',
    'guardrail',
    'process',
    'user_gap',
    'release_state',
    'agent_state',
)


class AgentResponseDeltaProposalV1Error(ValueError):
    def __init__(self, findings: Iterable[str]) -> None:
        self.findings = tuple(findings)
        super().__init__('invalid agent response delta proposal v1: ' + '; '.join(self.findings))


def load_json_fixture(path: str | Path) -> JsonObject:
    fixture_path = Path(path)
    loaded = json.loads(fixture_path.read_text(encoding='utf-8'))
    if not isinstance(loaded, dict):
        raise ValueError(f'Expected JSON object fixture at {fixture_path}')
    return loaded


def build_agent_response_delta_proposal_v1(
    *,
    guardrail_bundle_impact_proposal: Mapping[str, Any],
    user_gap_analysis_impact_proposal: Mapping[str, Any],
    guarded_agent_response_acceptance_packet: Mapping[str, Any],
    reviewer_owner: str = 'ppd-agent-readiness-reviewer',
    rollback_note: str = 'Discard this fixture-first proposal packet and rerun offline validation; no prompts, active guardrails, process models, user-gap fixtures, agent state, release state, or user-facing production behavior are changed.',
    offline_validation_commands: list[list[str]] | None = None,
) -> JsonObject:
    guardrail_input = copy.deepcopy(dict(guardrail_bundle_impact_proposal))
    gap_input = copy.deepcopy(dict(user_gap_analysis_impact_proposal))
    acceptance_input = copy.deepcopy(dict(guarded_agent_response_acceptance_packet))
    commands = copy.deepcopy(offline_validation_commands or DEFAULT_OFFLINE_VALIDATION_COMMANDS)

    case_id = _first_string(_first_from_sequence(gap_input.get('affected_case_ids')), acceptance_input.get('case_id'), 'unknown_case')
    process_id = _first_string(_first_from_sequence(gap_input.get('affected_process_ids')), acceptance_input.get('process_id'), guardrail_input.get('process_id'), 'unknown_process')
    guardrail_bundle_id = _first_string(_first_from_sequence(gap_input.get('affected_guardrail_bundle_ids')), acceptance_input.get('guardrail_bundle_id'), guardrail_input.get('guardrail_bundle_id'), 'unknown_guardrail_bundle')
    user_gap_proposal_id = _first_string(gap_input.get('proposal_id'), gap_input.get('impact_proposal_id'), 'user_gap_analysis_impact_proposal_v1_fixture')

    previous_delta_ids: list[str] = []
    deltas: list[JsonObject] = []
    for order, category in enumerate(DELTA_CATEGORIES, start=1):
        delta_id = f'ardp-v1-{case_id}-{order:02d}-{category}'.replace(' ', '_')
        deltas.append(
            {
                'delta_id': delta_id,
                'delta_category': category,
                'expected_outcome': _CATEGORY_TO_EXPECTED_OUTCOME[category],
                'summary': _delta_summary(category, acceptance_input, gap_input),
                'proposed_agent_facing_delta': _proposed_delta(category, acceptance_input, gap_input),
                'citations': _collect_citations(category, guardrail_input, gap_input, acceptance_input),
                'affected_fixture_families': list(AFFECTED_FIXTURE_FAMILIES),
                'affected_case_ids': [case_id],
                'affected_process_ids': [process_id],
                'affected_guardrail_bundle_ids': [guardrail_bundle_id],
                'affected_user_gap_analysis_ids': [user_gap_proposal_id],
                'affected_user_gap_impact_ids': _impact_ids_for_categories(gap_input, _CATEGORY_TO_USER_GAP_CATEGORIES[category]),
                'dependency_order': order,
                'depends_on_delta_ids': list(previous_delta_ids),
                'reviewer_owner': reviewer_owner,
                'rollback_note': rollback_note,
                'offline_validation_commands': copy.deepcopy(commands),
            }
        )
        previous_delta_ids.append(delta_id)

    proposal = {
        'proposal_id': f'agent_response_delta_proposal_v1:{case_id}',
        'proposal_version': 'v1',
        'fixture_first': True,
        'metadata_only': True,
        'source_inputs': {
            'guardrail_bundle_impact_proposal_id': _first_string(guardrail_input.get('proposal_id'), guardrail_input.get('impact_proposal_id'), 'guardrail_bundle_impact_proposal_v1_fixture'),
            'user_gap_analysis_impact_proposal_id': user_gap_proposal_id,
            'guarded_agent_response_acceptance_packet_type': _first_string(acceptance_input.get('packet_type'), 'guarded_agent_response_acceptance_packet_v1_fixture'),
        },
        'affected_fixture_families': list(AFFECTED_FIXTURE_FAMILIES),
        'affected_case_ids': [case_id],
        'affected_process_ids': [process_id],
        'affected_guardrail_bundle_ids': [guardrail_bundle_id],
        'affected_user_gap_analysis_ids': [user_gap_proposal_id],
        'reviewer_owner': reviewer_owner,
        'rollback_note': rollback_note,
        'proposed_deltas': deltas,
        'dependency_order': [delta['delta_id'] for delta in deltas],
        'offline_validation_commands': commands,
        'mutation_policy': {flag: False for flag in _REQUIRED_FALSE_MUTATION_FLAGS},
    }
    assert_valid_agent_response_delta_proposal_v1(proposal)
    return proposal


def build_from_fixture_paths(
    *,
    guardrail_bundle_impact_proposal_path: str | Path,
    user_gap_analysis_impact_proposal_path: str | Path,
    guarded_agent_response_acceptance_packet_path: str | Path,
    reviewer_owner: str = 'ppd-agent-readiness-reviewer',
) -> JsonObject:
    return build_agent_response_delta_proposal_v1(
        guardrail_bundle_impact_proposal=load_json_fixture(guardrail_bundle_impact_proposal_path),
        user_gap_analysis_impact_proposal=load_json_fixture(user_gap_analysis_impact_proposal_path),
        guarded_agent_response_acceptance_packet=load_json_fixture(guarded_agent_response_acceptance_packet_path),
        reviewer_owner=reviewer_owner,
    )


def validate_agent_response_delta_proposal_v1(proposal: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    if not isinstance(proposal, Mapping):
        return ['proposal must be an object']

    if proposal.get('proposal_version') != 'v1':
        findings.append('proposal_version must be v1')
    if proposal.get('fixture_first') is not True:
        findings.append('fixture_first must be true')
    if proposal.get('metadata_only') is not True:
        findings.append('metadata_only must be true')
    for field in ('affected_fixture_families', 'affected_case_ids', 'affected_process_ids', 'affected_guardrail_bundle_ids', 'affected_user_gap_analysis_ids', 'dependency_order', 'offline_validation_commands'):
        if not _non_empty_sequence(proposal.get(field)):
            findings.append(f'{field} is required')
    if not _non_empty_text(proposal.get('reviewer_owner')):
        findings.append('reviewer_owner is required')
    if not _non_empty_text(proposal.get('rollback_note')):
        findings.append('rollback_note is required')

    rows = proposal.get('proposed_deltas')
    if not _non_empty_sequence(rows):
        findings.append('proposed_deltas must contain at least one row')
    else:
        seen_categories: list[str] = []
        seen_delta_ids: list[str] = []
        for index, row in enumerate(rows):
            path = f'proposed_deltas[{index}]'
            if not isinstance(row, Mapping):
                findings.append(f'{path} must be an object')
                continue
            category = row.get('delta_category')
            if category not in DELTA_CATEGORIES:
                findings.append(f'{path}.delta_category must be a supported v1 delta category')
            else:
                seen_categories.append(str(category))
            delta_id = row.get('delta_id')
            if _non_empty_text(delta_id):
                seen_delta_ids.append(str(delta_id))
            for field in ('delta_id', 'summary', 'reviewer_owner', 'rollback_note'):
                if not _non_empty_text(row.get(field)):
                    findings.append(f'{path}.{field} is required')
            for field in ('citations', 'affected_fixture_families', 'affected_case_ids', 'affected_process_ids', 'affected_guardrail_bundle_ids', 'affected_user_gap_analysis_ids', 'affected_user_gap_impact_ids', 'offline_validation_commands'):
                if not _non_empty_sequence(row.get(field)):
                    findings.append(f'{path}.{field} is required')
            if row.get('expected_outcome') not in EXPECTED_OUTCOMES:
                findings.append(f'{path}.expected_outcome must be pass, block, or refusal')
            if not isinstance(row.get('dependency_order'), int):
                findings.append(f'{path}.dependency_order is required')
            if not isinstance(row.get('proposed_agent_facing_delta'), Mapping):
                findings.append(f'{path}.proposed_agent_facing_delta must be an object')
        if tuple(seen_categories) != DELTA_CATEGORIES:
            findings.append('proposed_deltas must preserve the v1 category dependency order')
        if _non_empty_sequence(proposal.get('dependency_order')) and list(proposal.get('dependency_order', [])) != seen_delta_ids:
            findings.append('dependency_order must list proposed delta ids in row order')

    _reject_prohibited_text(proposal, findings)
    _reject_active_mutation_flags(proposal, findings)
    return _dedupe_strings(findings)


def assert_valid_agent_response_delta_proposal_v1(proposal: Mapping[str, Any]) -> None:
    findings = validate_agent_response_delta_proposal_v1(proposal)
    if findings:
        raise AgentResponseDeltaProposalV1Error(findings)


def _first_from_sequence(value: Any) -> Any:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and value:
        return value[0]
    return None


def _first_string(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return 'unknown'


def _non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and len(value) > 0


def _collect_citations(category: str, guardrail_input: JsonObject, gap_input: JsonObject, acceptance_input: JsonObject) -> list[str]:
    citations: list[str] = []
    citations.extend(_citations_for_categories(guardrail_input, _CATEGORY_TO_USER_GAP_CATEGORIES[category]))
    citations.extend(_citations_for_categories(gap_input, _CATEGORY_TO_USER_GAP_CATEGORIES[category]))
    citations.extend(_citations_for_examples(acceptance_input, _CATEGORY_TO_ACCEPTANCE_EXAMPLES[category]))
    citations.append(f'guardrail_bundle_impact_proposal:{_first_string(guardrail_input.get('proposal_id'), 'fixture')}:{category}')
    citations.append(f'user_gap_analysis_impact_proposal:{_first_string(gap_input.get('proposal_id'), 'fixture')}:{category}')
    citations.append(f'guarded_agent_response_acceptance_packet:{_first_string(acceptance_input.get('packet_type'), 'fixture')}:{category}')
    return _dedupe_strings(citations)


def _citations_for_categories(packet: Mapping[str, Any], categories: Iterable[str]) -> list[str]:
    wanted = set(categories)
    citations: list[str] = []
    for row in packet.get('proposed_impacts', []):
        if not isinstance(row, Mapping) or row.get('category') not in wanted:
            continue
        citations.extend(_sequence_strings(row.get('citations')))
    citations.extend(_sequence_strings(packet.get('source_evidence_ids')))
    return citations


def _citations_for_examples(packet: Mapping[str, Any], example_kinds: Iterable[str]) -> list[str]:
    wanted = set(example_kinds)
    citations: list[str] = []
    for row in packet.get('final_response_examples', []):
        if not isinstance(row, Mapping) or row.get('example_kind') not in wanted:
            continue
        citations.extend(_sequence_strings(row.get('citations')))
    return citations


def _impact_ids_for_categories(packet: Mapping[str, Any], categories: Iterable[str]) -> list[str]:
    wanted = set(categories)
    impact_ids: list[str] = []
    for row in packet.get('proposed_impacts', []):
        if isinstance(row, Mapping) and row.get('category') in wanted and _non_empty_text(row.get('impact_id')):
            impact_ids.append(str(row['impact_id']))
    return _dedupe_strings(impact_ids)


def _sequence_strings(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _dedupe_strings(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = str(value).strip()
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
    return result


def _matching_examples(packet: Mapping[str, Any], category: str) -> list[JsonObject]:
    wanted = set(_CATEGORY_TO_ACCEPTANCE_EXAMPLES[category])
    examples: list[JsonObject] = []
    for row in packet.get('final_response_examples', []):
        if isinstance(row, Mapping) and row.get('example_kind') in wanted:
            examples.append(copy.deepcopy(dict(row)))
    return examples


def _matching_gap_rows(packet: Mapping[str, Any], category: str) -> list[JsonObject]:
    wanted = set(_CATEGORY_TO_USER_GAP_CATEGORIES[category])
    rows: list[JsonObject] = []
    for row in packet.get('proposed_impacts', []):
        if isinstance(row, Mapping) and row.get('category') in wanted:
            rows.append(copy.deepcopy(dict(row)))
    return rows


def _delta_summary(category: str, acceptance_input: JsonObject, gap_input: JsonObject) -> str:
    example_count = len(_matching_examples(acceptance_input, category))
    gap_count = len(_matching_gap_rows(gap_input, category))
    return f'Propose cited {category.replace('_', ' ')} response delta from {example_count} acceptance example(s) and {gap_count} user-gap impact row(s).'


def _proposed_delta(category: str, acceptance_input: JsonObject, gap_input: JsonObject) -> JsonObject:
    return {
        'response_delta_kind': category,
        'acceptance_example_kinds': [row.get('example_kind') for row in _matching_examples(acceptance_input, category)],
        'acceptance_final_responses': [row.get('final_response') for row in _matching_examples(acceptance_input, category) if row.get('final_response')],
        'user_gap_impact_ids': [row.get('impact_id') for row in _matching_gap_rows(gap_input, category) if row.get('impact_id')],
        'proposal_scope': 'review_only_candidate_delta',
    }


def _iter_text_leaves(value: Any, path: str) -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            yield from _iter_text_leaves(child, f'{path}.{key}')
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            yield from _iter_text_leaves(child, f'{path}[{index}]')


def _reject_prohibited_text(value: Any, findings: list[str]) -> None:
    for text_path, text in _iter_text_leaves(value, '$'):
        lowered = text.lower()
        for code, needles in _BLOCKED_TEXT_NEEDLES:
            if any(needle in lowered for needle in needles):
                findings.append(f'{code} at {text_path}')
                break
        if any(needle in lowered for needle in _OUTCOME_GUARANTEE_NEEDLES):
            findings.append(f'outcome_guarantee at {text_path}')
        if any(needle in lowered for needle in _CONSEQUENTIAL_EXECUTION_NEEDLES):
            findings.append(f'consequential_action_execution_language at {text_path}')


def _reject_active_mutation_flags(value: Mapping[str, Any], findings: list[str]) -> None:
    mutation_policy = value.get('mutation_policy')
    if mutation_policy is None:
        findings.append('mutation_policy is required')
    elif not isinstance(mutation_policy, Mapping):
        findings.append('mutation_policy must be an object')
    else:
        for flag in _REQUIRED_FALSE_MUTATION_FLAGS:
            if mutation_policy.get(flag) is not False:
                findings.append(f'active_mutation_flag at mutation_policy.{flag}')
    _reject_recursive_active_mutation_flags(value, '$', findings)


def _reject_recursive_active_mutation_flags(value: Any, path: str, findings: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f'{path}.{key}'
            if _is_mutation_flag_key(str(key)) and child is not False:
                findings.append(f'active_mutation_flag at {child_path}')
            _reject_recursive_active_mutation_flags(child, child_path, findings)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _reject_recursive_active_mutation_flags(child, f'{path}[{index}]', findings)


def _is_mutation_flag_key(key: str) -> bool:
    normalized = key.lower().replace('-', '_')
    if normalized in _REQUIRED_FALSE_MUTATION_FLAGS:
        return True
    if not any(domain in normalized for domain in _MUTATION_DOMAIN_WORDS):
        return False
    return any(token in normalized for token in ('mutate', 'mutation', 'active'))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Build PP&D agent response delta proposal v1 from fixtures.')
    parser.add_argument('--guardrail-bundle-impact-proposal', required=True)
    parser.add_argument('--user-gap-analysis-impact-proposal', required=True)
    parser.add_argument('--guarded-agent-response-acceptance-packet', required=True)
    parser.add_argument('--reviewer-owner', default='ppd-agent-readiness-reviewer')
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    proposal = build_from_fixture_paths(
        guardrail_bundle_impact_proposal_path=args.guardrail_bundle_impact_proposal,
        user_gap_analysis_impact_proposal_path=args.user_gap_analysis_impact_proposal,
        guarded_agent_response_acceptance_packet_path=args.guarded_agent_response_acceptance_packet,
        reviewer_owner=args.reviewer_owner,
    )
    print(json.dumps(proposal, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
