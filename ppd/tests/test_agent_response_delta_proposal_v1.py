from __future__ import annotations

import copy
from pathlib import Path

from ppd.logic.agent_response_delta_proposal_v1 import (
    AFFECTED_FIXTURE_FAMILIES,
    DELTA_CATEGORIES,
    build_agent_response_delta_proposal_v1,
    build_from_fixture_paths,
    load_json_fixture,
    validate_agent_response_delta_proposal_v1,
)

FIXTURE_DIR = Path(__file__).parent / 'fixtures' / 'agent_response_delta_proposal_v1'


def _valid_proposal() -> dict:
    return build_from_fixture_paths(
        guardrail_bundle_impact_proposal_path=FIXTURE_DIR / 'guardrail_bundle_impact_proposal_v1.json',
        user_gap_analysis_impact_proposal_path=FIXTURE_DIR / 'user_gap_analysis_impact_proposal_v1.json',
        guarded_agent_response_acceptance_packet_path=FIXTURE_DIR / 'guarded_agent_response_acceptance_packet_v1.json',
        reviewer_owner='fixture-response-reviewer',
    )


def test_builds_cited_agent_response_deltas_for_required_categories() -> None:
    proposal = _valid_proposal()

    assert proposal['proposal_version'] == 'v1'
    assert proposal['fixture_first'] is True
    assert proposal['metadata_only'] is True
    assert proposal['affected_fixture_families'] == list(AFFECTED_FIXTURE_FAMILIES)
    assert proposal['affected_case_ids'] == ['case-demo-adu-001']
    assert proposal['affected_process_ids'] == ['process-detached-adu-devhub-v1']
    assert proposal['affected_guardrail_bundle_ids'] == ['guardrail-detached-adu-devhub-v1']
    assert proposal['affected_user_gap_analysis_ids'] == ['user_gap_analysis_impact_proposal_v1:case-demo-adu-001']

    categories = [delta['delta_category'] for delta in proposal['proposed_deltas']]
    assert categories == list(DELTA_CATEGORIES)

    for expected_order, delta in enumerate(proposal['proposed_deltas'], start=1):
        assert delta['dependency_order'] == expected_order
        assert delta['reviewer_owner'] == 'fixture-response-reviewer'
        assert delta['rollback_note']
        assert delta['offline_validation_commands']
        assert delta['citations']
        assert delta['affected_fixture_families'] == list(AFFECTED_FIXTURE_FAMILIES)
        assert delta['affected_case_ids'] == ['case-demo-adu-001']
        assert delta['affected_process_ids'] == ['process-detached-adu-devhub-v1']
        assert delta['affected_guardrail_bundle_ids'] == ['guardrail-detached-adu-devhub-v1']
        assert delta['affected_user_gap_analysis_ids'] == ['user_gap_analysis_impact_proposal_v1:case-demo-adu-001']
        assert delta['affected_user_gap_impact_ids']
        assert delta['expected_outcome'] in {'pass', 'block', 'refusal'}

    refusal = next(delta for delta in proposal['proposed_deltas'] if delta['delta_category'] == 'refusal')
    assert refusal['expected_outcome'] == 'refusal'
    assert 'guardrail:exact-confirmation-submit' in refusal['citations']
    assert refusal['proposed_agent_facing_delta']['acceptance_example_kinds'] == ['blocked_official_actions']

    blocked_action = next(delta for delta in proposal['proposed_deltas'] if delta['delta_category'] == 'blocked_action')
    assert blocked_action['expected_outcome'] == 'block'
    assert validate_agent_response_delta_proposal_v1(proposal) == []


def test_builder_does_not_mutate_input_fixtures() -> None:
    guardrail = load_json_fixture(FIXTURE_DIR / 'guardrail_bundle_impact_proposal_v1.json')
    user_gap = load_json_fixture(FIXTURE_DIR / 'user_gap_analysis_impact_proposal_v1.json')
    acceptance = load_json_fixture(FIXTURE_DIR / 'guarded_agent_response_acceptance_packet_v1.json')
    original_guardrail = copy.deepcopy(guardrail)
    original_user_gap = copy.deepcopy(user_gap)
    original_acceptance = copy.deepcopy(acceptance)

    proposal = build_agent_response_delta_proposal_v1(
        guardrail_bundle_impact_proposal=guardrail,
        user_gap_analysis_impact_proposal=user_gap,
        guarded_agent_response_acceptance_packet=acceptance,
    )

    for flag in (
        'mutates_prompts',
        'mutates_active_prompts',
        'mutates_active_guardrails',
        'mutates_process_models',
        'mutates_user_gap_fixtures',
        'mutates_release_state',
        'mutates_agent_state',
        'mutates_user_facing_production_behavior',
    ):
        assert proposal['mutation_policy'][flag] is False
    assert guardrail == original_guardrail
    assert user_gap == original_user_gap
    assert acceptance == original_acceptance


def test_validator_rejects_uncited_or_incomplete_delta_rows() -> None:
    proposal = _valid_proposal()
    row = proposal['proposed_deltas'][0]
    row.pop('citations')
    row.pop('affected_fixture_families')
    row.pop('affected_guardrail_bundle_ids')
    row.pop('affected_user_gap_analysis_ids')
    row.pop('affected_user_gap_impact_ids')
    row.pop('delta_category')
    row.pop('expected_outcome')
    row.pop('dependency_order')
    row.pop('reviewer_owner')
    row.pop('rollback_note')

    errors = validate_agent_response_delta_proposal_v1(proposal)

    assert any('citations is required' in error for error in errors)
    assert any('affected_fixture_families is required' in error for error in errors)
    assert any('affected_guardrail_bundle_ids is required' in error for error in errors)
    assert any('affected_user_gap_analysis_ids is required' in error for error in errors)
    assert any('affected_user_gap_impact_ids is required' in error for error in errors)
    assert any('delta_category must be a supported' in error for error in errors)
    assert any('expected_outcome must be pass, block, or refusal' in error for error in errors)
    assert any('dependency_order is required' in error for error in errors)
    assert any('reviewer_owner is required' in error for error in errors)
    assert any('rollback_note is required' in error for error in errors)


def test_validator_rejects_missing_top_level_review_dependency_and_fixture_family_metadata() -> None:
    proposal = _valid_proposal()
    proposal['affected_fixture_families'] = []
    proposal['affected_guardrail_bundle_ids'] = []
    proposal['affected_user_gap_analysis_ids'] = []
    proposal['dependency_order'] = []
    proposal['reviewer_owner'] = ''
    proposal['rollback_note'] = ''

    errors = validate_agent_response_delta_proposal_v1(proposal)

    assert 'affected_fixture_families is required' in errors
    assert 'affected_guardrail_bundle_ids is required' in errors
    assert 'affected_user_gap_analysis_ids is required' in errors
    assert 'dependency_order is required' in errors
    assert 'reviewer_owner is required' in errors
    assert 'rollback_note is required' in errors


def test_validator_rejects_missing_expected_outcome_and_bad_dependency_order() -> None:
    proposal = _valid_proposal()
    proposal['proposed_deltas'][0]['expected_outcome'] = 'approve'
    proposal['dependency_order'] = list(reversed(proposal['dependency_order']))

    errors = validate_agent_response_delta_proposal_v1(proposal)

    assert any('expected_outcome must be pass, block, or refusal' in error for error in errors)
    assert any('dependency_order must list proposed delta ids in row order' in error for error in errors)


def test_validator_rejects_private_authenticated_session_browser_raw_guarantee_and_execution_language() -> None:
    proposal = _valid_proposal()
    proposal['proposed_deltas'][0]['summary'] = 'private applicant-specific artifact'
    proposal['proposed_deltas'][1]['summary'] = 'authenticated page snapshot'
    proposal['proposed_deltas'][2]['summary'] = 'session cookie value'
    proposal['proposed_deltas'][3]['summary'] = 'Playwright trace archive'
    proposal['proposed_deltas'][4]['summary'] = 'raw PDF download artifact'
    proposal['proposed_deltas'][5]['summary'] = 'Approval guaranteed and agent will submit the permit request.'

    errors = validate_agent_response_delta_proposal_v1(proposal)

    assert any('private_artifact' in error for error in errors)
    assert any('authenticated_artifact' in error for error in errors)
    assert any('session_artifact' in error for error in errors)
    assert any('browser_artifact' in error for error in errors)
    assert any('raw_crawl_or_download_artifact' in error for error in errors)
    assert any('outcome_guarantee' in error for error in errors)
    assert any('consequential_action_execution_language' in error for error in errors)


def test_validator_rejects_active_prompt_guardrail_process_user_gap_release_and_agent_state_flags() -> None:
    blocked_flags = {
        'mutates_active_prompts': True,
        'mutates_active_guardrails': True,
        'mutates_process_models': True,
        'mutates_user_gap_fixtures': True,
        'mutates_release_state': True,
        'mutates_agent_state': True,
    }

    for key, value in blocked_flags.items():
        proposal = _valid_proposal()
        proposal['mutation_policy'][key] = value
        errors = validate_agent_response_delta_proposal_v1(proposal)
        assert any('active_mutation_flag' in error for error in errors)


def test_validator_rejects_nested_active_mutation_flags() -> None:
    proposal = _valid_proposal()
    proposal['proposed_deltas'][0]['proposed_agent_facing_delta']['prompt_mutation_active'] = True
    proposal['proposed_deltas'][1]['proposed_agent_facing_delta']['user_gap_mutation_active'] = True

    errors = validate_agent_response_delta_proposal_v1(proposal)

    assert any('prompt_mutation_active' in error for error in errors)
    assert any('user_gap_mutation_active' in error for error in errors)
