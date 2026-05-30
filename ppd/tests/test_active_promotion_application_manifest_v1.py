from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from ppd.agent_readiness.active_promotion_application_manifest_v1 import (
    ActivePromotionApplicationManifestV1Error,
    require_active_promotion_application_manifest_v1_valid,
    validate_active_promotion_application_manifest_v1,
)


_FIXTURE_PATH = Path(__file__).parent / 'fixtures' / 'active_promotion_application_manifest_v1.json'


def _fixture() -> dict[str, Any]:
    return json.loads(_FIXTURE_PATH.read_text(encoding='utf-8'))


def test_active_promotion_application_manifest_v1_accepts_fixture() -> None:
    result = validate_active_promotion_application_manifest_v1(_fixture())

    assert result.valid, result.problems
    require_active_promotion_application_manifest_v1_valid(_fixture())


@pytest.mark.parametrize(
    'section, expected_problem',
    [
        ('target_fixture_family_rows', 'missing_target_fixture_family_rows'),
        ('source_inactive_artifact_references', 'missing_source_inactive_artifact_references'),
        ('destination_active_artifact_placeholders', 'missing_destination_active_artifact_placeholders'),
        ('expected_checksum_placeholders', 'missing_expected_checksum_placeholders'),
        ('ordered_validation_replay_inventory', 'missing_ordered_validation_replay_inventory'),
        ('rollback_checkpoint_references', 'missing_rollback_checkpoint_references'),
        ('reviewer_approval_placeholders', 'missing_reviewer_approval_placeholders'),
    ],
)
def test_active_promotion_application_manifest_v1_rejects_missing_required_sections(section: str, expected_problem: str) -> None:
    manifest = _fixture()
    manifest[section] = []

    result = validate_active_promotion_application_manifest_v1(manifest)

    assert not result.valid
    assert expected_problem in result.problems


def test_active_promotion_application_manifest_v1_rejects_missing_target_row_references() -> None:
    manifest = _fixture()
    row = copy.deepcopy(manifest['target_fixture_family_rows'][0])
    row.pop('source_artifact_ref')
    row.pop('destination_artifact_placeholder')
    row.pop('expected_checksum_placeholder')
    row.pop('validation_replay_id')
    row.pop('rollback_checkpoint_ref')
    row.pop('reviewer_approval_placeholder')
    manifest['target_fixture_family_rows'] = [row]

    result = validate_active_promotion_application_manifest_v1(manifest)

    assert not result.valid
    assert 'target_fixture_family_rows[0]:missing_source_artifact_ref' in result.problems
    assert 'target_fixture_family_rows[0]:missing_destination_artifact_placeholder' in result.problems
    assert 'target_fixture_family_rows[0]:missing_expected_checksum_placeholder' in result.problems
    assert 'target_fixture_family_rows[0]:missing_validation_replay_id' in result.problems
    assert 'target_fixture_family_rows[0]:missing_rollback_checkpoint_ref' in result.problems
    assert 'target_fixture_family_rows[0]:missing_reviewer_approval_placeholder' in result.problems


def test_active_promotion_application_manifest_v1_rejects_unlinked_placeholders() -> None:
    manifest = _fixture()
    manifest['target_fixture_family_rows'][0]['source_artifact_ref'] = 'inactive-artifact://missing'
    manifest['target_fixture_family_rows'][0]['destination_artifact_placeholder'] = 'active-artifact-placeholder://missing'
    manifest['target_fixture_family_rows'][0]['expected_checksum_placeholder'] = 'sha256:PLACEHOLDER_MISSING'
    manifest['target_fixture_family_rows'][0]['validation_replay_id'] = 'replay-missing'
    manifest['target_fixture_family_rows'][0]['rollback_checkpoint_ref'] = 'rollback-checkpoint://missing'
    manifest['target_fixture_family_rows'][0]['reviewer_approval_placeholder'] = 'reviewer-approval://missing'

    result = validate_active_promotion_application_manifest_v1(manifest)

    assert not result.valid
    assert any(problem.endswith(':missing_referenced_placeholder') for problem in result.problems)


def test_active_promotion_application_manifest_v1_rejects_unordered_replay_inventory() -> None:
    manifest = _fixture()
    manifest['ordered_validation_replay_inventory'][1]['order'] = 3

    result = validate_active_promotion_application_manifest_v1(manifest)

    assert not result.valid
    assert 'ordered_validation_replay_inventory:order_must_be_contiguous_from_one' in result.problems


@pytest.mark.parametrize(
    'field_path, value, expected_fragment',
    [
        (('private_artifact',), 'private applicant data', 'forbidden_artifact_key'),
        (('notes',), 'contains authenticated session material', 'session_or_browser_artifact'),
        (('notes',), 'attached screenshots and HAR file', 'screenshot_trace_har_or_auth_file'),
        (('notes',), 'raw crawl and downloaded data were retained', 'raw_crawl_pdf_or_downloaded_data'),
        (('notes',), 'promotion executed and release complete', 'live_execution_or_release_claim'),
        (('notes',), 'permit guaranteed with no legal risk', 'legal_or_permitting_outcome_guarantee'),
        (('notes',), 'agent will submit permit and enter payment', 'consequential_action_language'),
        (('active_artifact_mutated',), True, 'forbidden_mutation_flag'),
        (('prompt_mutation_requested',), True, 'forbidden_mutation_flag'),
        (('release_state_updated',), True, 'forbidden_mutation_flag'),
        (('fixture_mutated',), True, 'forbidden_mutation_flag'),
        (('agent_state_changed',), True, 'forbidden_mutation_flag'),
    ],
)
def test_active_promotion_application_manifest_v1_rejects_forbidden_content(
    field_path: tuple[str, ...],
    value: Any,
    expected_fragment: str,
) -> None:
    manifest = _fixture()
    target = manifest
    for field in field_path[:-1]:
        target = target.setdefault(field, {})
    target[field_path[-1]] = value

    result = validate_active_promotion_application_manifest_v1(manifest)

    assert not result.valid
    assert any(expected_fragment in problem for problem in result.problems)


def test_active_promotion_application_manifest_v1_require_raises() -> None:
    manifest = _fixture()
    manifest['reviewer_approval_placeholders'] = []

    with pytest.raises(ActivePromotionApplicationManifestV1Error):
        require_active_promotion_application_manifest_v1_valid(manifest)
