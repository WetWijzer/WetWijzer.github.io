from __future__ import annotations

import json
from pathlib import Path

from ppd.logic.fixture_first_guardrail_bundle_impact_proposal_v1 import (
    build_guardrail_bundle_impact_proposal_v1,
    finding_codes,
    require_valid_guardrail_bundle_impact_proposal_v1,
    validate_guardrail_bundle_impact_proposal_v1,
)


FIXTURE_DIR = Path(__file__).parent / 'fixtures' / 'fixture_first_guardrail_bundle_impact_proposal_v1'


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def _source_packets() -> dict:
    return _load_json(FIXTURE_DIR / 'source_packets.json')


def _load_source_packet(relative_path: str) -> dict:
    return _load_json((FIXTURE_DIR / relative_path).resolve())


def _build_packet() -> dict:
    source_packets = _source_packets()
    paths = source_packets['input_fixture_paths']
    return build_guardrail_bundle_impact_proposal_v1(
        _load_source_packet(paths['process_model_impact_proposal_v1']),
        _load_source_packet(paths['requirement_formalization_candidate_packet_v1']),
        [_load_source_packet(path) for path in paths['guardrail_bundle_fixtures']],
        generated_at=source_packets['generated_at'],
        reviewer_owner=source_packets['reviewer_owner'],
    )


def test_builds_fixture_first_guardrail_bundle_impact_proposal_v1() -> None:
    packet = _build_packet()
    source_packets = _source_packets()

    assert packet['packet_type'] == 'fixture_first_guardrail_bundle_impact_proposal_v1'
    assert packet['packet_mode'] == 'proposal_only_no_compile_no_promotion'
    assert packet['reviewer_owner'] == source_packets['reviewer_owner']
    assert packet['affected_guardrail_bundle_ids'] == source_packets['expected_affected_guardrail_bundle_ids']
    assert validate_guardrail_bundle_impact_proposal_v1(packet) == []
    require_valid_guardrail_bundle_impact_proposal_v1(packet)


def test_packet_contains_all_required_impact_row_types_with_citations() -> None:
    packet = _build_packet()
    row_types = {row['impact_type'] for row in packet['impact_rows']}

    assert row_types == {
        'proposed_predicate',
        'explanation_template',
        'exact_confirmation',
        'refused_action',
        'reversible_action',
        'temporal_rule',
    }
    assert all(row['affected_guardrail_bundle_ids'] for row in packet['impact_rows'])
    assert all(row['affected_process_ids'] for row in packet['impact_rows'])
    assert all(row['affected_requirement_ids'] for row in packet['impact_rows'])
    assert all(row['source_evidence_ids'] for row in packet['impact_rows'])
    assert all(row['citations'] for row in packet['impact_rows'])
    assert all(row['activation_allowed'] is False for row in packet['impact_rows'])


def test_packet_records_dependency_order_rollback_and_offline_validation_commands() -> None:
    packet = _build_packet()

    assert packet['dependency_order'] == [
        'validate_process_model_impact_proposal_v1',
        'validate_requirement_formalization_candidate_packet_v1',
        'load_existing_guardrail_bundle_fixtures',
        'review_guardrail_bundle_impact_rows',
        'defer_compile_or_promotion_to_later_human_review',
    ]
    assert 'existing guardrail bundle fixtures unchanged' in packet['rollback_note']
    assert ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'] in packet['offline_validation_commands']
    assert all(isinstance(command, list) for command in packet['offline_validation_commands'])


def test_rejects_active_mutation_and_uncited_rows() -> None:
    packet = _build_packet()
    packet['no_active_mutation_attestations']['mutated_active_guardrail_bundle'] = True
    packet['impact_rows'][0]['citations'] = []
    packet['impact_rows'][0]['source_evidence_ids'] = []
    packet['active_guardrail_bundle_patch'] = {'unsafe': True}

    codes = finding_codes(validate_guardrail_bundle_impact_proposal_v1(packet))

    assert 'attestation_not_false' in codes
    assert 'uncited_impact_row' in codes
    assert 'active_mutation_output' in codes
