from __future__ import annotations

from pathlib import Path

from ppd.logic.guardrail_bundle_impact_proposal import (
    IMPACT_CATEGORIES,
    finding_codes,
    load_json_fixture,
    validate_guardrail_bundle_impact_proposal_v1,
)

FIXTURE_DIR = Path(__file__).parent / 'fixtures' / 'guardrail_bundle_impact_proposal_v1'


def _valid_proposal() -> dict:
    return load_json_fixture(FIXTURE_DIR / 'valid_proposal.json')


def test_valid_fixture_contains_required_categories_and_metadata() -> None:
    proposal = _valid_proposal()

    assert [row['category'] for row in proposal['proposed_impacts']] == list(IMPACT_CATEGORIES)
    assert proposal['dependency_order'] == ['gbip-v1-predicate', 'gbip-v1-explanation-template']
    assert validate_guardrail_bundle_impact_proposal_v1(proposal).ok is True


def test_validator_rejects_uncited_and_incomplete_impact_rows() -> None:
    proposal = _valid_proposal()
    row = proposal['proposed_impacts'][0]
    row.pop('citations')
    row.pop('affected_guardrail_bundle_ids')
    row.pop('affected_process_ids')
    row.pop('affected_requirement_ids')
    row.pop('category')
    row.pop('dependency_order')
    row.pop('reviewer_owner')
    row.pop('rollback_note')

    codes = set(finding_codes(validate_guardrail_bundle_impact_proposal_v1(proposal)))

    assert 'uncited_impact_row' in codes
    assert 'missing_affected_guardrail_bundle_ids' in codes
    assert 'missing_affected_process_ids' in codes
    assert 'missing_affected_requirement_ids' in codes
    assert 'missing_predicate_or_explanation_template_category' in codes
    assert 'missing_dependency_order' in codes
    assert 'missing_reviewer_owner' in codes
    assert 'missing_rollback_note' in codes


def test_validator_rejects_missing_top_level_ids_review_and_dependency_metadata() -> None:
    proposal = _valid_proposal()
    proposal['affected_guardrail_bundle_ids'] = []
    proposal['affected_process_ids'] = []
    proposal['affected_requirement_ids'] = []
    proposal['dependency_order'] = []
    proposal['reviewer_owner'] = ''
    proposal['rollback_note'] = ''

    codes = set(finding_codes(validate_guardrail_bundle_impact_proposal_v1(proposal)))

    assert 'missing_affected_guardrail_bundle_ids' in codes
    assert 'missing_affected_process_ids' in codes
    assert 'missing_affected_requirement_ids' in codes
    assert 'missing_dependency_order' in codes
    assert 'missing_reviewer_owner' in codes
    assert 'missing_rollback_note' in codes


def test_validator_rejects_missing_required_category_and_bad_dependency_order() -> None:
    proposal = _valid_proposal()
    proposal['proposed_impacts'] = proposal['proposed_impacts'][:1]
    proposal['dependency_order'] = ['not-the-row-id']

    codes = set(finding_codes(validate_guardrail_bundle_impact_proposal_v1(proposal)))

    assert 'missing_predicate_or_explanation_template_category' in codes
    assert 'dependency_order_mismatch' in codes


def test_validator_rejects_private_authenticated_session_browser_and_raw_artifacts() -> None:
    cases = [
        ('private applicant-specific artifact', 'private_artifact'),
        ('authenticated page snapshot', 'authenticated_artifact'),
        ('session cookie value', 'session_artifact'),
        ('Playwright trace archive', 'browser_artifact'),
        ('raw PDF download artifact', 'raw_crawl_or_download_artifact'),
    ]

    for text, expected_code in cases:
        proposal = _valid_proposal()
        proposal['proposed_impacts'][0]['summary'] = text
        codes = set(finding_codes(validate_guardrail_bundle_impact_proposal_v1(proposal)))
        assert expected_code in codes


def test_validator_rejects_outcome_guarantees_and_consequential_execution_language() -> None:
    proposal = _valid_proposal()
    proposal['proposed_impacts'][0]['summary'] = 'Approval guaranteed after this review.'
    proposal['proposed_impacts'][1]['summary'] = 'Agent will submit the permit request.'

    codes = set(finding_codes(validate_guardrail_bundle_impact_proposal_v1(proposal)))

    assert 'outcome_guarantee' in codes
    assert 'consequential_action_execution_language' in codes


def test_validator_rejects_active_mutation_flags_for_blocked_targets() -> None:
    blocked_flags = {
        'mutates_sources': True,
        'mutates_documents': True,
        'mutates_requirements': True,
        'mutates_process_models': True,
        'mutates_guardrails': True,
        'mutates_prompts': True,
        'mutates_release_state': True,
        'mutates_agent_state': True,
    }

    for key, value in blocked_flags.items():
        proposal = _valid_proposal()
        proposal['mutation_policy'][key] = value
        codes = set(finding_codes(validate_guardrail_bundle_impact_proposal_v1(proposal)))
        assert 'active_mutation_flag' in codes
