from __future__ import annotations

import copy
import json
from pathlib import Path

from ppd.live_dry_run_post_run_triage_packet_v2 import (
    REQUIRED_ATTESTATIONS,
    REQUIRED_DECISIONS,
    REQUIRED_SOURCE_KEYS,
    build_live_dry_run_post_run_triage_packet_v2,
    require_valid_live_dry_run_post_run_triage_packet_v2,
    validate_live_dry_run_post_run_triage_packet_v2,
)


FIXTURE_PATH = Path(__file__).parent / 'fixtures' / 'live_dry_run_post_run_triage_packet_v2' / 'source_packets.json'


def _source_packets() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding='utf-8'))


def _packet() -> dict:
    return build_live_dry_run_post_run_triage_packet_v2(_source_packets())


def test_builds_cited_post_run_triage_packet() -> None:
    packet = _packet()

    assert packet['packet_type'] == 'live-dry-run-post-run-triage-packet'
    assert packet['version'] == 'v2'
    assert packet['mode'] == 'fixture_first_live_dry_run_post_run_triage_only'
    assert packet['fixture_first'] is True
    assert {row['source_key'] for row in packet['consumes']} == set(REQUIRED_SOURCE_KEYS)

    decisions = packet['observation_decisions']
    assert {row['decision'] for row in decisions} == REQUIRED_DECISIONS
    assert all(row['citations'] for row in decisions)
    assert all(row['source_observation_refs'] for row in decisions)
    require_valid_live_dry_run_post_run_triage_packet_v2(packet)


def test_includes_incident_abort_redaction_and_reviewer_owner_fields() -> None:
    packet = _packet()

    assert packet['incident_summaries'][0]['status'] == 'accepted'
    assert packet['incident_summaries'][0]['disposition']
    assert packet['abort_summaries'][0]['status'] == 'escalated_for_reviewer_confirmation'
    assert packet['abort_summaries'][0]['disposition']
    assert 'CAPTCHA' in ' '.join(packet['abort_summaries'][0]['conditions'])
    assert {row['outcome'] for row in packet['artifact_redaction_review_outcomes']} == {
        'accepted_metadata_only',
        'accepted_synthetic_read_only',
        'accepted_briefing_only',
    }
    assert packet['reviewer_owner_fields']['primary_reviewer_owner'] == 'TBD_PP_D_REVIEWER_OWNER'
    assert packet['reviewer_owner_fields']['owner_assignment_status'] == 'placeholder_required_before_promotion'


def test_includes_offline_validation_commands_and_required_attestations() -> None:
    packet = _packet()

    assert ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'] in packet['offline_validation_commands']
    assert packet['attestations'] == {key: True for key in REQUIRED_ATTESTATIONS}
    assert packet['side_effects'] == {
        'live_repeat_performed': False,
        'auth_state_created': False,
        'browser_artifact_created': False,
        'official_action_performed': False,
        'release_state_mutated': False,
    }


def test_validator_rejects_uncited_triage_decision() -> None:
    packet = _packet()
    packet['observation_decisions'][0]['citations'] = []

    result = validate_live_dry_run_post_run_triage_packet_v2(packet)

    assert not result.valid
    assert 'observation_decisions[0].citations must be non-empty' in result.errors
    assert 'observation_decisions uncited statuses: accepted' in result.errors


def test_validator_rejects_missing_decision_status() -> None:
    packet = _packet()
    packet['observation_decisions'] = [
        row for row in packet['observation_decisions'] if row['decision'] != 'escalated'
    ]

    result = validate_live_dry_run_post_run_triage_packet_v2(packet)

    assert not result.valid
    assert 'observation_decisions missing statuses: escalated' in result.errors


def test_validator_rejects_missing_incident_abort_dispositions_and_redaction_outcomes() -> None:
    packet = _packet()
    packet['incident_summaries'][0].pop('status')
    packet['incident_summaries'][0].pop('disposition')
    packet['abort_summaries'][0].pop('status')
    packet['abort_summaries'][0].pop('disposition')
    packet['artifact_redaction_review_outcomes'][0].pop('outcome')

    result = validate_live_dry_run_post_run_triage_packet_v2(packet)

    assert not result.valid
    assert 'incident_summaries[0].disposition or status is required' in result.errors
    assert 'abort_summaries[0].disposition or status is required' in result.errors
    assert 'artifact_redaction_review_outcomes[0].outcome is required' in result.errors


def test_validator_rejects_missing_reviewer_owner_fields() -> None:
    packet = _packet()
    packet['reviewer_owner_fields'].pop('artifact_redaction_owner')

    result = validate_live_dry_run_post_run_triage_packet_v2(packet)

    assert not result.valid
    assert 'reviewer_owner_fields.artifact_redaction_owner is required' in result.errors


def test_validator_rejects_missing_attestation_and_side_effect_claim() -> None:
    packet = _packet()
    packet['attestations']['no_live_repeat'] = False
    packet['side_effects']['release_state_mutated'] = True

    result = validate_live_dry_run_post_run_triage_packet_v2(packet)

    assert not result.valid
    assert 'attestations.no_live_repeat must be true' in result.errors
    assert 'side_effects.release_state_mutated must be false' in result.errors


def test_validator_rejects_private_authenticated_facts_and_raw_artifacts() -> None:
    packet = _packet()
    packet['incident_summaries'][0]['summary'] = 'Authenticated value includes owner@example.test and permit number: 24-123456-000-00-CO.'
    packet['raw_pdf'] = '/tmp/private-upload.pdf'
    packet['session_file'] = 'storage_state.json'

    result = validate_live_dry_run_post_run_triage_packet_v2(packet)

    assert not result.valid
    assert any('private or authenticated facts' in error for error in result.errors)
    assert any('raw crawl, PDF, session, or browser artifacts' in error for error in result.errors)


def test_validator_rejects_live_execution_credential_automation_and_outcome_guarantees() -> None:
    packet = _packet()
    packet['observation_decisions'][0]['summary'] = 'Live DevHub completed after Playwright automated CAPTCHA and permit will be approved.'

    result = validate_live_dry_run_post_run_triage_packet_v2(packet)

    assert not result.valid
    assert any('live execution' in error for error in result.errors)
    assert any('credential, MFA, or CAPTCHA automation language' in error for error in result.errors)
    assert any('guarantee legal or permitting outcomes' in error for error in result.errors)


def test_validator_rejects_final_official_action_language() -> None:
    packet = _packet()
    packet['observation_decisions'][1]['summary'] = 'Final submission and payment completed; uploaded to DevHub and scheduled inspection.'

    result = validate_live_dry_run_post_run_triage_packet_v2(packet)

    assert not result.valid
    assert any('final submission, payment, upload, scheduling, cancellation, or certification language' in error for error in result.errors)


def test_validator_rejects_active_mutation_flags() -> None:
    for flag in (
        'active_source_mutation',
        'active_surface_registry_mutation',
        'prompt_mutation',
        'guardrail_mutation',
        'monitoring_mutation',
        'release_state_mutation',
        'agent_state_mutation',
    ):
        packet = _packet()
        packet[flag] = True

        result = validate_live_dry_run_post_run_triage_packet_v2(packet)

        assert not result.valid
        assert any(flag in error for error in result.errors)


def test_builder_rejects_missing_source_packet() -> None:
    source_packets = copy.deepcopy(_source_packets())
    source_packets.pop('live_dry_run_operator_briefing_packet_v2')

    try:
        build_live_dry_run_post_run_triage_packet_v2(source_packets)
    except ValueError as exc:
        assert 'missing source packets' in str(exc)
    else:
        raise AssertionError('expected missing source packet failure')
