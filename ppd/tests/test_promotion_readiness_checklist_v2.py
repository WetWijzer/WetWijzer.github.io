from __future__ import annotations

import copy
from pathlib import Path

from ppd.agent_readiness.promotion_readiness_checklist_v2 import (
    CONSUMED_PACKET_KEYS,
    REQUIRED_ATTESTATIONS,
    build_from_fixture_path,
    build_promotion_readiness_checklist_v2,
    load_json_fixture,
    validate_promotion_readiness_checklist_v2,
)

FIXTURE_DIR = Path(__file__).parent / 'fixtures' / 'promotion_readiness_checklist_v2'


def _valid_checklist() -> dict:
    return build_from_fixture_path(FIXTURE_DIR / 'source_packets.json', reviewer_owner='fixture-promotion-reviewer')


def test_builds_cited_ordered_promotion_readiness_checklist_v2() -> None:
    checklist = _valid_checklist()

    assert checklist['packet_type'] == 'ppd.promotion_readiness_checklist.v2'
    assert checklist['packet_version'] == 'v2'
    assert checklist['fixture_first'] is True
    assert checklist['metadata_only'] is True
    assert list(checklist['consumes']) == list(CONSUMED_PACKET_KEYS)
    assert checklist['attestations'] == REQUIRED_ATTESTATIONS

    checks = checklist['ordered_readiness_checks']
    assert [row['source_packet'] for row in checks] == list(CONSUMED_PACKET_KEYS)
    assert [row['order'] for row in checks] == [1, 2, 3, 4, 5]
    for index, row in enumerate(checks):
        assert row['citations']
        assert row['required_result'] == 'ready_for_manual_offline_review'
        assert row['reviewer_owner'] == 'fixture-promotion-reviewer'
        assert row['rollback_note']
        if index == 0:
            assert row['depends_on_check_ids'] == []
        else:
            assert row['depends_on_check_ids'] == [previous['readiness_check_id'] for previous in checks[:index]]

    assert checklist['unresolved_blocker_rows']
    assert any(row['blocker_id'] == 'blocker-missing-site-plan-fixture' for row in checklist['unresolved_blocker_rows'])
    assert len(checklist['fixture_family_inspection_targets']) == len(CONSUMED_PACKET_KEYS)
    for target in checklist['fixture_family_inspection_targets']:
        assert target['fixture_path'].startswith('ppd/tests/fixtures/')
        assert target['citations']
        assert target['inspection_focus']
    assert checklist['rollback_checkpoints']
    assert ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'] in checklist['validation_command_inventory']
    assert validate_promotion_readiness_checklist_v2(checklist) == []


def test_builder_does_not_mutate_source_packets() -> None:
    source_packets = load_json_fixture(FIXTURE_DIR / 'source_packets.json')
    original = copy.deepcopy(source_packets)

    checklist = build_promotion_readiness_checklist_v2(source_packets)

    assert checklist['checklist_id'] == 'fixture-first-promotion-readiness-checklist-v2'
    assert source_packets == original


def test_validator_rejects_missing_cited_ordered_readiness_check_fields() -> None:
    checklist = _valid_checklist()
    row = checklist['ordered_readiness_checks'][0]
    row.pop('readiness_check_id')
    row['order'] = 99
    row['citations'] = []
    row['source_packet'] = 'unknown'
    row['required_result'] = ''
    row['reviewer_owner'] = ''
    row['rollback_note'] = ''

    errors = validate_promotion_readiness_checklist_v2(checklist)

    assert any('readiness_check_id is required' in error for error in errors)
    assert any('order must be 1' in error for error in errors)
    assert any('citations is required' in error for error in errors)
    assert any('source_packet must name a consumed packet' in error for error in errors)
    assert any('required_result is required' in error for error in errors)
    assert any('reviewer_owner is required' in error for error in errors)
    assert any('rollback_note is required' in error for error in errors)


def test_validator_rejects_missing_per_family_readiness_checks_and_inspection_targets() -> None:
    checklist = _valid_checklist()
    checklist['ordered_readiness_checks'] = checklist['ordered_readiness_checks'][:-1]
    checklist['fixture_family_inspection_targets'] = checklist['fixture_family_inspection_targets'][:-1]

    errors = validate_promotion_readiness_checklist_v2(checklist)

    assert any('ordered_readiness_checks must contain one cited check per consumed packet' in error for error in errors)
    assert any('ordered_readiness_checks missing source_packet offline_acceptance_rehearsal_summary_v1' in error for error in errors)
    assert any('fixture_family_inspection_targets must contain one inspection target per consumed fixture family' in error for error in errors)
    assert any('fixture_family_inspection_targets missing fixture_family offline_acceptance_rehearsal_summary_v1' in error for error in errors)


def test_validator_rejects_incomplete_blockers_fixture_targets_rollbacks_and_commands() -> None:
    checklist = _valid_checklist()
    checklist['unresolved_blocker_rows'][0]['blocker_id'] = ''
    checklist['unresolved_blocker_rows'][0]['summary'] = ''
    checklist['unresolved_blocker_rows'][0]['citations'] = []
    checklist['fixture_family_inspection_targets'][0]['fixture_path'] = 'tests/fixtures/outside.json'
    checklist['fixture_family_inspection_targets'][0]['inspection_focus'] = []
    checklist['fixture_family_inspection_targets'][0]['reviewer_owner'] = ''
    checklist['rollback_checkpoints'][0]['checkpoint_status'] = 'done'
    checklist['rollback_checkpoints'][0]['rollback_scope'] = ''
    checklist['rollback_checkpoints'][0]['rollback_note'] = ''
    checklist['validation_command_inventory'].append(['python3', ''])
    checklist['validation_command_inventory'] = [command for command in checklist['validation_command_inventory'] if command != ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test']]

    errors = validate_promotion_readiness_checklist_v2(checklist)

    assert any('blocker_id is required' in error for error in errors)
    assert any('unresolved_blocker_rows[0].summary is required' in error for error in errors)
    assert any('unresolved_blocker_rows[0].citations is required' in error for error in errors)
    assert any('fixture_path must stay under ppd/tests/fixtures' in error for error in errors)
    assert any('inspection_focus is required' in error for error in errors)
    assert any('fixture_family_inspection_targets[0].reviewer_owner is required' in error for error in errors)
    assert any('checkpoint_status must be available or manual_confirmation_required' in error for error in errors)
    assert any('rollback_scope is required' in error for error in errors)
    assert any('rollback_checkpoints[0].rollback_note is required' in error for error in errors)
    assert any('validation_command_inventory' in error and 'argv list' in error for error in errors)
    assert any('validation_command_inventory must include ppd daemon self-test command' in error for error in errors)


def test_validator_rejects_missing_blocker_handling_active_state_checkpoint_and_inventory() -> None:
    checklist = _valid_checklist()
    checklist['unresolved_blocker_rows'] = []
    checklist['rollback_checkpoints'] = [row for row in checklist['rollback_checkpoints'] if row['checkpoint_id'] != 'promotion-readiness-v2-active-state-unchanged']
    checklist['validation_command_inventory'] = []

    errors = validate_promotion_readiness_checklist_v2(checklist)

    assert any('unresolved_blocker_rows must contain at least one blocker or none-reported row' in error for error in errors)
    assert any('unresolved_blocker_rows must document unresolved blocker handling' in error for error in errors)
    assert any('rollback_checkpoints must include active-state-unchanged checkpoint' in error for error in errors)
    assert any('validation_command_inventory must contain commands' in error for error in errors)


def test_validator_rejects_missing_attestations_and_consumed_packet_refs() -> None:
    checklist = _valid_checklist()
    checklist['consumes']['process_model_impact_proposal_v1'] = ''
    checklist['attestations']['no_live_crawl'] = False
    checklist['attestations']['no_devhub'] = False
    checklist['attestations']['no_private_artifact'] = False
    checklist['attestations']['no_official_action'] = False
    checklist['attestations']['no_active_promotion'] = False

    errors = validate_promotion_readiness_checklist_v2(checklist)

    assert 'consumes.process_model_impact_proposal_v1 is required' in errors
    assert 'attestations.no_live_crawl must be True' in errors
    assert 'attestations.no_devhub must be True' in errors
    assert 'attestations.no_private_artifact must be True' in errors
    assert 'attestations.no_official_action must be True' in errors
    assert 'attestations.no_active_promotion must be True' in errors


def test_validator_rejects_forbidden_artifacts_guarantees_execution_language_and_promotion_flags() -> None:
    checklist = _valid_checklist()
    checklist['ordered_readiness_checks'][0]['summary'] = 'raw PDF downloaded document with approval guaranteed and agent will submit.'
    checklist['ordered_readiness_checks'][1]['summary'] = 'authenticated artifact with session cookie and browser state.'
    checklist['ordered_readiness_checks'][2]['summary'] = 'live execution completed and promotion executed.'
    checklist['private_artifact'] = 'blocked'
    checklist['active_promotion'] = True
    checklist['rollback_checkpoints'][0]['active_guardrail_mutation'] = True
    checklist['rollback_checkpoints'][1]['active_requirement_mutated'] = True
    checklist['rollback_checkpoints'][2]['process_model_mutated'] = True
    checklist['rollback_checkpoints'][3]['prompt_mutated'] = True
    checklist['rollback_checkpoints'][4]['release_state_mutated'] = True
    checklist['rollback_checkpoints'][5]['agent_state_mutated'] = True

    errors = validate_promotion_readiness_checklist_v2(checklist)

    assert any('raw_or_download_artifact' in error for error in errors)
    assert any('outcome_guarantee' in error for error in errors)
    assert any('consequential_action_execution_language' in error for error in errors)
    assert any('authenticated_artifact' in error for error in errors)
    assert any('session_artifact' in error for error in errors)
    assert any('browser_artifact' in error for error in errors)
    assert any('live_execution_or_promotion_claim' in error for error in errors)
    assert any('forbidden_artifact_key' in error for error in errors)
    assert any('forbidden_live_official_or_promotion_flag' in error for error in errors)
    assert any('active_mutation_flag' in error for error in errors)
