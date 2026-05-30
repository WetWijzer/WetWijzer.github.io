from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.devhub_attended_readonly_observation_readiness_packet_v2 import (
    build_attended_devhub_readonly_observation_readiness_packet_v2,
    require_attended_devhub_readonly_observation_readiness_packet_v2,
    validate_attended_devhub_readonly_observation_readiness_packet_v2,
)

FIXTURE_DIR = Path(__file__).parent / 'fixtures' / 'devhub_attended_readonly_observation_readiness_packet_v2'


def _load_json(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding='utf-8'))


def _valid_packet() -> dict:
    return build_attended_devhub_readonly_observation_readiness_packet_v2(_load_json('inactive_release_activation_checklist_v2.json'))


def _problem_text(packet: dict) -> str:
    result = validate_attended_devhub_readonly_observation_readiness_packet_v2(packet)
    assert not result.valid
    return '; '.join(result.errors)


def test_build_attended_devhub_readonly_observation_readiness_packet_v2_matches_fixture() -> None:
    checklist = _load_json('inactive_release_activation_checklist_v2.json')
    expected = _load_json('expected_packet.json')

    packet = build_attended_devhub_readonly_observation_readiness_packet_v2(checklist)

    assert packet == expected


def test_attended_devhub_readonly_observation_readiness_packet_v2_is_fixture_first() -> None:
    packet = _valid_packet()

    assert packet['devhub_access'] == 'not_requested'
    assert packet['browser_artifacts'] == 'not_created'
    assert packet['official_action_scope'] == 'blocked'
    assert all(item['requires_user_attendance'] for item in packet['ordered_attended_session_prerequisites'])
    require_attended_devhub_readonly_observation_readiness_packet_v2(packet)


def test_attended_devhub_readonly_observation_readiness_packet_v2_rejects_active_checklist() -> None:
    checklist = _load_json('inactive_release_activation_checklist_v2.json')
    checklist['status'] = 'active'

    with pytest.raises(ValueError, match='only consumes inactive checklists'):
        build_attended_devhub_readonly_observation_readiness_packet_v2(checklist)


@pytest.mark.parametrize(
    ('field', 'expected'),
    [
        ('ordered_attended_session_prerequisites', 'ordered_attended_session_prerequisites must be a non-empty list'),
        ('manual_login_handoff_placeholders', 'manual_login_handoff_placeholders must be a non-empty list'),
        ('read_only_surface_observation_placeholders', 'read_only_surface_observation_placeholders must be a non-empty list'),
        ('redaction_checklist_placeholders', 'redaction_checklist_placeholders must be a non-empty list'),
        ('action_boundary_reminders', 'action_boundary_reminders must be a non-empty list'),
        ('exact_offline_validation_commands', 'exact_offline_validation_commands must be a non-empty list'),
    ],
)
def test_attended_devhub_readonly_observation_readiness_packet_v2_rejects_missing_sections(field: str, expected: str) -> None:
    packet = _valid_packet()
    packet[field] = []

    assert expected in _problem_text(packet)


def test_attended_devhub_readonly_observation_readiness_packet_v2_rejects_missing_attended_prerequisite_fields() -> None:
    packet = _valid_packet()
    packet['ordered_attended_session_prerequisites'][0].pop('checklist_item_id')
    packet['ordered_attended_session_prerequisites'][0]['requires_user_attendance'] = False

    problems = _problem_text(packet)

    assert 'checklist_item_id must be present' in problems
    assert 'requires_user_attendance must be true' in problems


def test_attended_devhub_readonly_observation_readiness_packet_v2_rejects_missing_manual_login_placeholder() -> None:
    packet = _valid_packet()
    packet['manual_login_handoff_placeholders'][0].pop('handoff_id')

    assert 'handoff_id must be present' in _problem_text(packet)


def test_attended_devhub_readonly_observation_readiness_packet_v2_rejects_non_placeholder_manual_login_status() -> None:
    packet = _valid_packet()
    packet['manual_login_handoff_placeholders'][0]['status'] = 'manual_login_completed'

    assert 'status must remain a placeholder' in _problem_text(packet)


def test_attended_devhub_readonly_observation_readiness_packet_v2_rejects_missing_surface_capture_fields() -> None:
    packet = _valid_packet()
    packet['read_only_surface_observation_placeholders'][0]['expected_capture_fields'] = []

    assert 'expected_capture_fields must be non-empty' in _problem_text(packet)


def test_attended_devhub_readonly_observation_readiness_packet_v2_rejects_observed_surface_status() -> None:
    packet = _valid_packet()
    packet['read_only_surface_observation_placeholders'][0]['observation_status'] = 'observed_live'

    assert 'observation_status must remain placeholder_not_observed' in _problem_text(packet)


def test_attended_devhub_readonly_observation_readiness_packet_v2_rejects_missing_redaction_placeholder() -> None:
    packet = _valid_packet()
    packet['redaction_checklist_placeholders'] = packet['redaction_checklist_placeholders'][:1]

    problems = _problem_text(packet)

    assert 'missing redaction checklist placeholder' in problems
    assert 'session_artifacts_absent' in problems


def test_attended_devhub_readonly_observation_readiness_packet_v2_rejects_filled_redaction_confirmation() -> None:
    packet = _valid_packet()
    packet['redaction_checklist_placeholders'][0]['reviewer_confirmation'] = 'confirmed'

    assert 'reviewer_confirmation must remain empty' in _problem_text(packet)


def test_attended_devhub_readonly_observation_readiness_packet_v2_rejects_missing_action_boundary() -> None:
    packet = _valid_packet()
    packet['action_boundary_reminders'] = packet['action_boundary_reminders'][:1]

    problems = _problem_text(packet)

    assert 'missing action-boundary reminder' in problems
    assert 'no_official_actions' in problems


def test_attended_devhub_readonly_observation_readiness_packet_v2_rejects_modified_validation_commands() -> None:
    packet = _valid_packet()
    packet['exact_offline_validation_commands'].append(['python3', 'ppd/devhub/live_observation.py'])

    assert 'exact_offline_validation_commands must match' in _problem_text(packet)


@pytest.mark.parametrize(
    ('field', 'value', 'expected'),
    [
        ('auth_state', 'storage-state.json', 'private DevHub session'),
        ('screenshot_path', 'screen.png', 'private DevHub session'),
        ('trace_path', 'trace.zip', 'private DevHub session'),
        ('har_path', 'network.har', 'private DevHub session'),
        ('downloaded_document_path', '/downloads/permit.pdf', 'private DevHub session'),
        ('raw_page_capture', 'private authenticated page', 'private DevHub session'),
        ('session_artifact', 'private session bundle', 'private DevHub session'),
        ('live_claim', 'opened DevHub and observed live', 'live DevHub access'),
        ('official_claim', 'submission completed', 'consequential official actions'),
        ('automated_login_claim', 'scripted login completes the PortlandOregon sign-in', 'automated login, MFA'),
        ('automated_mfa_claim', 'programmatic MFA OTP handling is ready', 'automated login, MFA'),
        ('guarantee_claim', 'this packet ensures permit approval', 'must not guarantee legal compliance'),
        ('legal_claim', 'this is binding legal advice and legally compliant', 'must not guarantee legal compliance'),
        ('active_devhub_surface_update', True, 'active DevHub surface, guardrail, source, prompt, contract, or release-state mutation'),
        ('active_guardrail_update', 'enabled', 'active DevHub surface, guardrail, source, prompt, contract, or release-state mutation'),
        ('active_source_update', True, 'active DevHub surface, guardrail, source, prompt, contract, or release-state mutation'),
        ('active_prompt_update', True, 'active DevHub surface, guardrail, source, prompt, contract, or release-state mutation'),
        ('active_contract_update', True, 'active DevHub surface, guardrail, source, prompt, contract, or release-state mutation'),
        ('active_release_update', True, 'active DevHub surface, guardrail, source, prompt, contract, or release-state mutation'),
    ],
)
def test_attended_devhub_readonly_observation_readiness_packet_v2_rejects_unsafe_values(
    field: str,
    value: object,
    expected: str,
) -> None:
    packet = _valid_packet()
    packet['unsafe_probe'] = {field: value}

    assert expected in _problem_text(packet)


def test_attended_devhub_readonly_observation_readiness_packet_v2_validation_does_not_mutate_input() -> None:
    packet = _valid_packet()
    before = copy.deepcopy(packet)

    assert validate_attended_devhub_readonly_observation_readiness_packet_v2(packet).valid
    assert packet == before
