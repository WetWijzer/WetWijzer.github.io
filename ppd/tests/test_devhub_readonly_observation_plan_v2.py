from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ppd.devhub_readonly_observation_plan_v2 import (
    ALLOWED_OBSERVATION_FIELDS,
    build_devhub_readonly_observation_plan_v2,
    require_devhub_readonly_observation_plan_v2,
    validate_devhub_readonly_observation_plan_v2,
)

FIXTURE_DIR = Path(__file__).parent / 'fixtures' / 'devhub_readonly_observation_plan_v2'


def _load_json(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding='utf-8'))


def _valid_plan() -> dict:
    return build_devhub_readonly_observation_plan_v2(_load_json('source_readiness_packet_v2.json'))


def _problem_text(packet: dict) -> str:
    result = validate_devhub_readonly_observation_plan_v2(packet)
    assert not result.valid
    return '; '.join(result.errors)


def test_build_devhub_readonly_observation_plan_v2_matches_fixture() -> None:
    readiness = _load_json('source_readiness_packet_v2.json')
    expected = _load_json('expected_plan_v2.json')

    assert build_devhub_readonly_observation_plan_v2(readiness) == expected


def test_plan_is_fixture_first_and_read_only() -> None:
    plan = _valid_plan()

    assert plan['devhub_access'] == 'not_opened'
    assert plan['browser_artifacts'] == 'not_created'
    assert plan['official_action_scope'] == 'blocked'
    assert plan['allowed_observation_fields'] == ALLOWED_OBSERVATION_FIELDS
    assert all(row['synthetic_status'] == 'planned_not_observed' for row in plan['ordered_synthetic_read_only_surface_rows'])
    assert all(row['manual_login_required_before_live_use'] for row in plan['ordered_synthetic_read_only_surface_rows'])
    assert all(value is True for value in plan['forbidden_browser_artifact_attestations'].values())
    require_devhub_readonly_observation_plan_v2(plan)


def test_plan_rejects_invalid_readiness_packet() -> None:
    readiness = _load_json('source_readiness_packet_v2.json')
    readiness['devhub_access'] = 'opened_live'

    with pytest.raises(ValueError, match='invalid attended DevHub read-only observation readiness packet v2'):
        build_devhub_readonly_observation_plan_v2(readiness)


@pytest.mark.parametrize(
    ('field', 'expected'),
    [
        ('ordered_synthetic_read_only_surface_rows', 'ordered_synthetic_read_only_surface_rows must be a non-empty list'),
        ('manual_login_handoff_reminders', 'manual_login_handoff_reminders must be a non-empty list'),
        ('allowed_observation_fields', 'allowed_observation_fields must be a non-empty list'),
        ('redaction_review_placeholders', 'redaction_review_placeholders must be a non-empty list'),
        ('timeout_and_manual_handoff_notes', 'timeout_and_manual_handoff_notes must be a non-empty list'),
        ('exact_offline_validation_commands', 'exact_offline_validation_commands must be a non-empty list'),
    ],
)
def test_plan_rejects_missing_required_sections(field: str, expected: str) -> None:
    plan = _valid_plan()
    plan[field] = []

    assert expected in _problem_text(plan)


def test_plan_rejects_unordered_surface_rows() -> None:
    plan = _valid_plan()
    plan['ordered_synthetic_read_only_surface_rows'][0]['order'] = 3

    assert 'ordered_synthetic_read_only_surface_rows must use contiguous order values' in _problem_text(plan)


def test_plan_rejects_surface_row_live_observation_status() -> None:
    plan = _valid_plan()
    plan['ordered_synthetic_read_only_surface_rows'][0]['synthetic_status'] = 'observed_live'

    assert 'synthetic_status must remain planned_not_observed' in _problem_text(plan)


def test_plan_rejects_changed_allowed_observation_fields() -> None:
    plan = _valid_plan()
    plan['allowed_observation_fields'].append('private_account_value')

    assert 'allowed_observation_fields must match' in _problem_text(plan)


def test_plan_rejects_manual_login_automation() -> None:
    plan = _valid_plan()
    plan['manual_login_handoff_reminders'][0]['automation_allowed'] = True

    assert 'automation_allowed must be false' in _problem_text(plan)


def test_plan_rejects_missing_forbidden_artifact_attestation() -> None:
    plan = _valid_plan()
    plan['forbidden_browser_artifact_attestations']['no_har_files'] = False

    problems = _problem_text(plan)

    assert 'missing true forbidden browser artifact attestations' in problems
    assert 'no_har_files' in problems


def test_plan_rejects_filled_redaction_review_placeholder() -> None:
    plan = _valid_plan()
    plan['redaction_review_placeholders'][0]['reviewer_confirmation'] = 'confirmed'

    assert 'reviewer_confirmation must remain empty' in _problem_text(plan)


def test_plan_rejects_changed_validation_commands() -> None:
    plan = _valid_plan()
    plan['exact_offline_validation_commands'].append(['python3', 'ppd/devhub/live_browser.py'])

    assert 'exact_offline_validation_commands must match' in _problem_text(plan)


@pytest.mark.parametrize(
    ('field', 'value', 'expected'),
    [
        ('auth_state', 'storage-state.json', 'private DevHub session'),
        ('screenshot_path', 'screen.png', 'private DevHub session'),
        ('trace_path', 'trace.zip', 'private DevHub session'),
        ('har_path', 'network.har', 'private DevHub session'),
        ('raw_authenticated_capture', 'private page html', 'private DevHub session'),
        ('downloaded_document_path', '/downloads/permit.pdf', 'private DevHub session'),
        ('live_claim', 'opened DevHub and observed live', 'live DevHub access'),
        ('automated_login_claim', 'scripted login completes sign-in', 'automated login, MFA'),
        ('official_claim', 'submission completed', 'completed consequential DevHub actions'),
        ('active_devhub_surface_update', True, 'active DevHub, surface, guardrail'),
        ('account_write_mutation', 'enabled', 'active DevHub, surface, guardrail'),
    ],
)
def test_plan_rejects_private_artifacts_live_claims_and_mutations(field: str, value: object, expected: str) -> None:
    plan = _valid_plan()
    plan['unsafe_probe'] = {field: value}

    assert expected in _problem_text(plan)


def test_validation_does_not_mutate_input() -> None:
    plan = _valid_plan()
    before = copy.deepcopy(plan)

    assert validate_devhub_readonly_observation_plan_v2(plan).valid
    assert plan == before
