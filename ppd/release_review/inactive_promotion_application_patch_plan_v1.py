'''Fixture-first inactive promotion application patch plan v1.

This module composes an inactive release application dry-run plan v1 with an
inactive release application reviewer packet v1. The output is an ordered,
metadata-only patch plan for fixture-family review. It does not apply patches,
edit active artifacts, change prompts, update release state, crawl sources, use
DevHub, or perform official actions.
'''

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Mapping, Sequence

from ppd.release.inactive_reviewer_packet_v1 import validate_inactive_release_application_reviewer_packet_v1
from ppd.release_review.inactive_application_dry_run_plan_v1 import (
    INACTIVE_RELEASE_APPLICATION_DRY_RUN_PLAN_V1_PACKET_TYPE,
    SELF_TEST_COMMAND,
    validate_inactive_release_application_dry_run_plan_v1,
)


INACTIVE_PROMOTION_APPLICATION_PATCH_PLAN_V1_PACKET_TYPE = 'ppd.release_review.inactive_promotion_application_patch_plan.v1'

_MUTATION_FLAGS = (
    'active_artifact_mutation_enabled',
    'active_fixture_mutation_enabled',
    'active_prompt_mutation_enabled',
    'active_release_state_mutation_enabled',
    'active_agent_state_mutation_enabled',
    'artifact_mutation_enabled',
    'fixture_mutation_enabled',
    'prompt_mutation_enabled',
    'release_state_mutation_enabled',
    'agent_state_mutation_enabled',
    'live_source_crawl_enabled',
    'devhub_access_enabled',
    'official_action_enabled',
    'patch_application_enabled',
)

_REQUIRED_SECTIONS = (
    'file_family_patch_rows',
    'source_fixture_references',
    'prerequisite_validation_replay_inventory',
    'reviewer_approval_placeholders',
    'rollback_plan_references',
)

_PRIVATE_OR_RAW_KEY_TOKENS = (
    'auth',
    'authenticated',
    'browser',
    'cookie',
    'credential',
    'download',
    'downloaded',
    'har',
    'password',
    'private',
    'raw',
    'raw_body',
    'raw_crawl',
    'raw_download',
    'raw_html',
    'raw_pdf',
    'screenshot',
    'session',
    'storage_state',
    'trace',
)

_ACTIVE_OR_LIVE_KEY_TOKENS = (
    'active_artifact_mutation',
    'active_fixture_mutation',
    'active_prompt_mutation',
    'active_release_state_mutation',
    'active_agent_state_mutation',
    'artifact_mutation_enabled',
    'fixture_mutation_enabled',
    'prompt_mutation_enabled',
    'release_state_mutation_enabled',
    'agent_state_mutation_enabled',
    'live_source_crawl_enabled',
    'devhub_access_enabled',
    'official_action_enabled',
    'patch_application_enabled',
)

_PRIVATE_OR_RAW_PATH_TOKENS = (
    '/.auth/',
    '/auth-state/',
    '/authenticated/',
    '/storage-state/',
    '/session/',
    '/sessions/',
    '/cookies/',
    '/browser-state/',
    '/playwright-report/',
    '/screenshot/',
    '/screenshots/',
    '/trace/',
    '/traces/',
    '/har/',
    '/raw/',
    '/crawl/',
    '/crawls/',
    '/download/',
    '/downloads/',
    '/downloaded/',
)

_PRIVATE_OR_RAW_EXTENSIONS = (
    '.auth',
    '.cookie',
    '.cookies',
    '.har',
    '.trace',
    '.zip',
    '.png',
    '.jpg',
    '.jpeg',
    '.webp',
    '.mp4',
    '.webm',
    '.warc',
    '.pdf',
    '.html',
    '.htm',
    '.mhtml',
    '.bin',
    '.dat',
)

_FORBIDDEN_TEXT_TOKENS = (
    'live crawl',
    'live execution',
    'executed live',
    'applied to active',
    'patch applied',
    'patch-applied',
    'applied patch',
    'changes were applied',
    'changes have been applied',
    'release-complete',
    'release complete',
    'release completed',
    'release state updated',
    'guaranteed approval',
    'guaranteed permit',
    'guarantees approval',
    'will be approved',
    'will be accepted',
    'permit will issue',
    'permit will be issued',
    'permit will be approved',
    'legal outcome',
    'permitting outcome',
    'approval is certain',
    'approval is assured',
    'submit permit',
    'submit the permit',
    'submit application',
    'submit payment',
    'certify acknowledgement',
    'upload correction',
    'upload corrections',
    'schedule inspection',
    'cancel permit',
    'withdraw permit',
    'pay fee',
    'pay fees',
    'final payment',
    'purchase permit',
    'create account',
)

_FORBIDDEN_VALIDATION_COMMAND_PARTS = (
    'curl',
    'wget',
    'playwright',
    'devhub',
    'browser',
    'session',
    'auth',
    'storage-state',
    'trace',
    'har',
    'screenshot',
    'download',
    'raw',
    'crawl-live',
    '--live',
    'submit',
    'upload',
    'payment',
    'pay',
    'schedule',
    'cancel',
    'certify',
)


@dataclass(frozen=True)
class InactivePromotionApplicationPatchPlanFinding:
    '''A deterministic validation finding for patch plan v1.'''

    code: str
    message: str
    location: str


def build_inactive_promotion_application_patch_plan_v1(
    inactive_release_application_dry_run_plan_v1: Mapping[str, Any],
    inactive_release_application_reviewer_packet_v1: Mapping[str, Any],
) -> dict[str, Any]:
    '''Build a non-applying fixture-family patch plan from validated inputs.'''

    dry_run_findings = validate_inactive_release_application_dry_run_plan_v1(inactive_release_application_dry_run_plan_v1)
    if dry_run_findings:
        summary = '; '.join(f'{finding.code} at {finding.location}' for finding in dry_run_findings)
        raise ValueError(f'inactive release application dry-run plan v1 is not valid: {summary}')

    reviewer_result = validate_inactive_release_application_reviewer_packet_v1(inactive_release_application_reviewer_packet_v1)
    if not reviewer_result.ok:
        summary = '; '.join(f'{error.code} at {error.path}' for error in reviewer_result.errors)
        raise ValueError(f'inactive release application reviewer packet v1 is not valid: {summary}')

    patch_rows = _file_family_patch_rows(
        inactive_release_application_dry_run_plan_v1,
        inactive_release_application_reviewer_packet_v1,
    )
    source_refs = _source_fixture_references(patch_rows)
    validation_inventory = _validation_replay_inventory(
        inactive_release_application_dry_run_plan_v1,
        inactive_release_application_reviewer_packet_v1,
    )
    rollback_refs = _rollback_plan_references(inactive_release_application_dry_run_plan_v1)

    plan: dict[str, Any] = {
        'packet_type': INACTIVE_PROMOTION_APPLICATION_PATCH_PLAN_V1_PACKET_TYPE,
        'packet_version': 'v1',
        'fixture_first': True,
        'dry_run_only': True,
        'metadata_only': True,
        'patch_application_status': 'not_applied',
        'consumed_input_packet_refs': {
            'inactive_release_application_dry_run_plan_v1': str(
                inactive_release_application_dry_run_plan_v1.get('packet_type')
                or INACTIVE_RELEASE_APPLICATION_DRY_RUN_PLAN_V1_PACKET_TYPE
            ),
            'inactive_release_application_reviewer_packet_v1': str(
                inactive_release_application_reviewer_packet_v1.get('packet_version')
                or 'inactive-release-application-reviewer-packet-v1'
            ),
        },
        'file_family_patch_rows': patch_rows,
        'source_fixture_references': source_refs,
        'prerequisite_validation_replay_inventory': validation_inventory,
        'reviewer_approval_placeholders': _reviewer_approval_placeholders(
            inactive_release_application_dry_run_plan_v1,
            inactive_release_application_reviewer_packet_v1,
            patch_rows,
        ),
        'rollback_plan_references': rollback_refs,
        'non_application_attestations': {
            'applies_patches': False,
            'edits_active_artifacts': False,
            'changes_prompts': False,
            'updates_release_state': False,
            'uses_live_sources': False,
            'uses_devhub': False,
            'performs_official_actions': False,
        },
    }
    for flag in _MUTATION_FLAGS:
        plan[flag] = False

    assert_valid_inactive_promotion_application_patch_plan_v1(plan)
    return plan


def validate_inactive_promotion_application_patch_plan_v1(
    plan: Mapping[str, Any],
) -> list[InactivePromotionApplicationPatchPlanFinding]:
    findings: list[InactivePromotionApplicationPatchPlanFinding] = []

    if plan.get('packet_type') != INACTIVE_PROMOTION_APPLICATION_PATCH_PLAN_V1_PACKET_TYPE:
        findings.append(_finding('invalid-packet-type', 'Packet type must identify inactive promotion application patch plan v1.', 'packet_type'))
    for field in ('fixture_first', 'dry_run_only', 'metadata_only'):
        if plan.get(field) is not True:
            findings.append(_finding('missing-fixture-first-attestation', 'Fixture-first dry-run attestations must be true.', field))
    if plan.get('patch_application_status') != 'not_applied':
        findings.append(_finding('patch-application-not-blocked', 'Patch application status must remain not_applied.', 'patch_application_status'))
    for flag in _MUTATION_FLAGS:
        if plan.get(flag) is not False:
            findings.append(_finding('mutation-or-live-flag-enabled', 'Patch application, active mutation, live source, DevHub, and official action flags must be false.', flag))
    for section in _REQUIRED_SECTIONS:
        if not _sequence(plan.get(section)):
            findings.append(_finding('missing-required-section', 'Patch plan section must be a non-empty list.', section))

    _validate_consumed_refs(plan.get('consumed_input_packet_refs'), findings)
    _validate_patch_rows(plan.get('file_family_patch_rows'), findings)
    _validate_source_refs(plan.get('source_fixture_references'), findings)
    _validate_validation_inventory(plan.get('prerequisite_validation_replay_inventory'), findings)
    _validate_reviewer_placeholders(plan.get('reviewer_approval_placeholders'), findings)
    _validate_rollback_refs(plan.get('rollback_plan_references'), findings)
    _validate_attestations(plan.get('non_application_attestations'), findings)
    _validate_cross_references(plan, findings)
    _scan_for_forbidden_content(plan, findings)

    return findings


def assert_valid_inactive_promotion_application_patch_plan_v1(plan: Mapping[str, Any]) -> None:
    findings = validate_inactive_promotion_application_patch_plan_v1(plan)
    if findings:
        summary = '; '.join(f'{finding.code} at {finding.location}' for finding in findings)
        raise ValueError(f'inactive promotion application patch plan v1 validation failed: {summary}')


def _file_family_patch_rows(dry_run_plan: Mapping[str, Any], reviewer_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    inventory_rows = [row for row in _sequence(dry_run_plan.get('fixture_family_change_inventory')) if isinstance(row, Mapping)]
    reviewer_rows = [row for row in _sequence(reviewer_packet.get('reviewer_comparison_rows')) if isinstance(row, Mapping)]
    rollback_ids = [str(row.get('checkpoint_id')) for row in _sequence(dry_run_plan.get('rollback_checkpoints')) if isinstance(row, Mapping) and row.get('checkpoint_id')]
    gate_ids = [str(row.get('gate_id')) for row in _sequence(dry_run_plan.get('preflight_validation_gates')) if isinstance(row, Mapping) and row.get('gate_id')]

    rows: list[dict[str, Any]] = []
    for index, row in enumerate(sorted(inventory_rows, key=lambda item: str(item.get('family_id') or '')), start=1):
        family_id = _slug(str(row.get('family_id') or f'fixture-family-{index}'))
        fixture_refs = sorted(_fixture_refs(row.get('candidate_refs')))
        if not fixture_refs:
            fixture_refs = [f'ppd/tests/fixtures/{family_id}/pending-review-placeholder.json']
        reviewer_refs = [f'reviewer-comparison-row-{position}' for position, _ in enumerate(reviewer_rows, start=1)] or ['reviewer-comparison-row-pending']
        rows.append(
            {
                'order': index,
                'patch_row_id': f'patch-row-{index:03d}-{family_id}',
                'file_family_id': family_id,
                'operation': 'complete_file_replacement_candidate',
                'patch_scope': 'inactive_fixture_family_only',
                'application_status': 'not_applied',
                'active_patch_applied': False,
                'source_fixture_refs': fixture_refs,
                'source_dry_run_plan_refs': ['fixture_family_change_inventory', *gate_ids],
                'reviewer_packet_refs': reviewer_refs,
                'expected_before_checksum': f'sha256:pending-before-{family_id}',
                'expected_after_checksum': f'sha256:pending-after-{family_id}',
                'prerequisite_validation_refs': gate_ids or ['gate-validation-replay-commands-present'],
                'reviewer_approval_ref': f'reviewer-approval-{index:03d}-{family_id}',
                'rollback_plan_refs': rollback_ids or ['rollback-discard-dry-run-plan'],
            }
        )
    return rows


def _source_fixture_references(patch_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in patch_rows:
        for fixture_ref in _fixture_refs(row.get('source_fixture_refs')):
            if fixture_ref in seen:
                continue
            seen.add(fixture_ref)
            refs.append(
                {
                    'fixture_ref_id': f'source-fixture-{len(refs) + 1:03d}',
                    'fixture_path': fixture_ref,
                    'file_family_id': str(row.get('file_family_id') or 'unknown'),
                    'read_mode': 'committed_fixture_reference_only',
                    'expected_checksum': f'sha256:pending-source-{_slug(fixture_ref)}',
                }
            )
    return refs


def _validation_replay_inventory(dry_run_plan: Mapping[str, Any], reviewer_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    commands = _commands(dry_run_plan.get('validation_commands')) + _commands(reviewer_packet.get('validation_commands'))
    if not any(command == SELF_TEST_COMMAND for command in commands):
        commands.insert(0, list(SELF_TEST_COMMAND))
    unique_commands: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for command in commands:
        command_key = tuple(command)
        if command_key not in seen:
            seen.add(command_key)
            unique_commands.append(command)
    return [
        {
            'replay_id': f'validation-replay-{index:03d}',
            'command': command,
            'replay_status': 'pending_replay',
            'required_before': 'any_separate_future_patch_application',
            'source_refs': ['inactive_release_application_dry_run_plan_v1', 'inactive_release_application_reviewer_packet_v1'],
        }
        for index, command in enumerate(unique_commands, start=1)
    ]


def _reviewer_approval_placeholders(
    dry_run_plan: Mapping[str, Any],
    reviewer_packet: Mapping[str, Any],
    patch_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    dry_run_placeholders = [row for row in _sequence(dry_run_plan.get('reviewer_approval_placeholders')) if isinstance(row, Mapping)]
    reviewer_gate_rows = [row for row in _sequence(reviewer_packet.get('prerequisite_gate_acknowledgements')) if isinstance(row, Mapping)]
    placeholders: list[dict[str, Any]] = []
    for index, row in enumerate(patch_rows, start=1):
        family_id = str(row.get('file_family_id') or f'fixture-family-{index}')
        placeholders.append(
            {
                'approval_id': str(row.get('reviewer_approval_ref') or f'reviewer-approval-{index:03d}'),
                'file_family_id': family_id,
                'approval_status': 'pending_reviewer_approval',
                'required_before': 'any_separate_future_patch_application',
                'source_refs': [
                    str(item.get('approval_id') or 'dry-run-approval-placeholder')
                    for item in dry_run_placeholders
                ] or ['dry-run-approval-placeholder'],
                'reviewer_gate_refs': [
                    str(item.get('gate') or f'reviewer-gate-{position}')
                    for position, item in enumerate(reviewer_gate_rows, start=1)
                ] or ['reviewer-gate-placeholder'],
            }
        )
    return placeholders


def _rollback_plan_references(dry_run_plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    checkpoints = [row for row in _sequence(dry_run_plan.get('rollback_checkpoints')) if isinstance(row, Mapping)]
    for index, row in enumerate(checkpoints, start=1):
        refs.append(
            {
                'rollback_ref_id': str(row.get('checkpoint_id') or f'rollback-ref-{index:03d}'),
                'source_checkpoint_ref': str(row.get('checkpoint_id') or f'rollback-checkpoint-{index:03d}'),
                'active_changes_to_rollback': False,
                'rollback_status': 'ready_no_patch_applied',
                'verification_commands': _commands(row.get('verification_commands')) or [list(SELF_TEST_COMMAND)],
            }
        )
    return refs


def _validate_consumed_refs(value: Any, findings: list[InactivePromotionApplicationPatchPlanFinding]) -> None:
    if not isinstance(value, Mapping):
        findings.append(_finding('missing-consumed-input-refs', 'Consumed input packet refs must be an object.', 'consumed_input_packet_refs'))
        return
    if value.get('inactive_release_application_dry_run_plan_v1') != INACTIVE_RELEASE_APPLICATION_DRY_RUN_PLAN_V1_PACKET_TYPE:
        findings.append(_finding('missing-dry-run-input-ref', 'Dry-run plan input ref is required.', 'consumed_input_packet_refs.inactive_release_application_dry_run_plan_v1'))
    if not str(value.get('inactive_release_application_reviewer_packet_v1') or '').strip():
        findings.append(_finding('missing-reviewer-input-ref', 'Reviewer packet input ref is required.', 'consumed_input_packet_refs.inactive_release_application_reviewer_packet_v1'))


def _validate_patch_rows(value: Any, findings: list[InactivePromotionApplicationPatchPlanFinding]) -> None:
    rows = _sequence(value)
    seen_ids: set[str] = set()
    expected_order = 1
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            findings.append(_finding('invalid-patch-row', 'Patch rows must be objects.', f'file_family_patch_rows[{index}]'))
            continue
        if row.get('order') != expected_order:
            findings.append(_finding('invalid-patch-row-order', 'Patch rows must be ordered consecutively from 1.', f'file_family_patch_rows[{index}].order'))
        expected_order += 1
        row_id = str(row.get('patch_row_id') or '')
        if not row_id:
            findings.append(_finding('missing-patch-row-id', 'Patch row id is required.', f'file_family_patch_rows[{index}].patch_row_id'))
        elif row_id in seen_ids:
            findings.append(_finding('duplicate-patch-row-id', 'Patch row ids must be unique.', f'file_family_patch_rows[{index}].patch_row_id'))
        seen_ids.add(row_id)
        if row.get('operation') != 'complete_file_replacement_candidate':
            findings.append(_finding('invalid-patch-operation', 'Patch rows must describe complete file replacement candidates.', f'file_family_patch_rows[{index}].operation'))
        if row.get('patch_scope') != 'inactive_fixture_family_only':
            findings.append(_finding('invalid-patch-scope', 'Patch rows must stay scoped to inactive fixture families.', f'file_family_patch_rows[{index}].patch_scope'))
        if row.get('application_status') != 'not_applied' or row.get('active_patch_applied') is not False:
            findings.append(_finding('patch-row-applied', 'Patch rows must remain not applied.', f'file_family_patch_rows[{index}].application_status'))
        for field in ('source_fixture_refs', 'source_dry_run_plan_refs', 'reviewer_packet_refs', 'prerequisite_validation_refs', 'rollback_plan_refs'):
            if not _sequence(row.get(field)):
                findings.append(_finding('missing-patch-row-reference', 'Patch rows require source, reviewer, validation, and rollback references.', f'file_family_patch_rows[{index}].{field}'))
        for field in ('expected_before_checksum', 'expected_after_checksum'):
            if not str(row.get(field) or '').startswith('sha256:pending-'):
                findings.append(_finding('missing-expected-checksum-placeholder', 'Expected checksum placeholders must use sha256:pending-* values.', f'file_family_patch_rows[{index}].{field}'))
        for fixture_ref in _fixture_refs(row.get('source_fixture_refs')):
            if not fixture_ref.startswith('ppd/tests/fixtures/'):
                findings.append(_finding('source-fixture-outside-ppd-tests', 'Source fixture refs must stay under ppd/tests/fixtures/.', f'file_family_patch_rows[{index}].source_fixture_refs'))


def _validate_source_refs(value: Any, findings: list[InactivePromotionApplicationPatchPlanFinding]) -> None:
    for index, row in enumerate(_sequence(value)):
        if not isinstance(row, Mapping):
            findings.append(_finding('invalid-source-fixture-reference', 'Source fixture references must be objects.', f'source_fixture_references[{index}]'))
            continue
        fixture_path = str(row.get('fixture_path') or '')
        if not fixture_path.startswith('ppd/tests/fixtures/'):
            findings.append(_finding('source-fixture-outside-ppd-tests', 'Source fixture references must stay under ppd/tests/fixtures/.', f'source_fixture_references[{index}].fixture_path'))
        if row.get('read_mode') != 'committed_fixture_reference_only':
            findings.append(_finding('invalid-source-fixture-read-mode', 'Source fixtures must be referenced only from committed fixtures.', f'source_fixture_references[{index}].read_mode'))
        if not str(row.get('expected_checksum') or '').startswith('sha256:pending-source-'):
            findings.append(_finding('missing-source-checksum-placeholder', 'Source fixture checksum placeholders are required.', f'source_fixture_references[{index}].expected_checksum'))


def _validate_validation_inventory(value: Any, findings: list[InactivePromotionApplicationPatchPlanFinding]) -> None:
    commands = []
    for index, row in enumerate(_sequence(value)):
        if not isinstance(row, Mapping):
            findings.append(_finding('invalid-validation-replay-row', 'Validation replay rows must be objects.', f'prerequisite_validation_replay_inventory[{index}]'))
            continue
        command = _command(row.get('command'))
        if not command:
            findings.append(_finding('missing-validation-command', 'Validation replay rows require argv commands.', f'prerequisite_validation_replay_inventory[{index}].command'))
        elif _unsafe_validation_command(command):
            findings.append(_finding('unsafe-validation-command', 'Validation replay commands must be deterministic offline commands and must not invoke live, DevHub, browser, auth, crawl, upload, submit, payment, or scheduling behavior.', f'prerequisite_validation_replay_inventory[{index}].command'))
        commands.append(command)
        if row.get('replay_status') != 'pending_replay':
            findings.append(_finding('validation-replay-not-pending', 'Validation replay rows must remain pending.', f'prerequisite_validation_replay_inventory[{index}].replay_status'))
        if not _sequence(row.get('source_refs')):
            findings.append(_finding('missing-validation-source-ref', 'Validation replay rows need source refs.', f'prerequisite_validation_replay_inventory[{index}].source_refs'))
    if SELF_TEST_COMMAND not in commands:
        findings.append(_finding('missing-self-test-replay', 'Validation replay inventory must include the PP&D daemon self-test command.', 'prerequisite_validation_replay_inventory'))


def _validate_reviewer_placeholders(value: Any, findings: list[InactivePromotionApplicationPatchPlanFinding]) -> None:
    for index, row in enumerate(_sequence(value)):
        if not isinstance(row, Mapping):
            findings.append(_finding('invalid-reviewer-approval-placeholder', 'Reviewer approval placeholders must be objects.', f'reviewer_approval_placeholders[{index}]'))
            continue
        for field in ('approval_id', 'file_family_id', 'approval_status', 'required_before', 'source_refs', 'reviewer_gate_refs'):
            if field in {'source_refs', 'reviewer_gate_refs'}:
                if not _sequence(row.get(field)):
                    findings.append(_finding('missing-reviewer-approval-field', 'Reviewer approval placeholders require source refs.', f'reviewer_approval_placeholders[{index}].{field}'))
            elif not str(row.get(field) or '').strip():
                findings.append(_finding('missing-reviewer-approval-field', 'Reviewer approval placeholder field is required.', f'reviewer_approval_placeholders[{index}].{field}'))
        if row.get('approval_status') != 'pending_reviewer_approval':
            findings.append(_finding('reviewer-approval-not-pending', 'Reviewer approvals must remain pending placeholders.', f'reviewer_approval_placeholders[{index}].approval_status'))


def _validate_rollback_refs(value: Any, findings: list[InactivePromotionApplicationPatchPlanFinding]) -> None:
    for index, row in enumerate(_sequence(value)):
        if not isinstance(row, Mapping):
            findings.append(_finding('invalid-rollback-reference', 'Rollback plan references must be objects.', f'rollback_plan_references[{index}]'))
            continue
        for field in ('rollback_ref_id', 'source_checkpoint_ref', 'rollback_status', 'verification_commands'):
            if field == 'verification_commands':
                commands = _commands(row.get(field))
                if not commands:
                    findings.append(_finding('missing-rollback-reference-field', 'Rollback references require verification commands.', f'rollback_plan_references[{index}].{field}'))
                for command_index, command in enumerate(commands):
                    if _unsafe_validation_command(command):
                        findings.append(_finding('unsafe-validation-command', 'Rollback verification commands must be deterministic offline commands.', f'rollback_plan_references[{index}].verification_commands[{command_index}]'))
            elif not str(row.get(field) or '').strip():
                findings.append(_finding('missing-rollback-reference-field', 'Rollback reference field is required.', f'rollback_plan_references[{index}].{field}'))
        if row.get('active_changes_to_rollback') is not False:
            findings.append(_finding('rollback-active-change-claim', 'Rollback references must declare no active changes to rollback.', f'rollback_plan_references[{index}].active_changes_to_rollback'))


def _validate_attestations(value: Any, findings: list[InactivePromotionApplicationPatchPlanFinding]) -> None:
    if not isinstance(value, Mapping):
        findings.append(_finding('missing-non-application-attestations', 'Non-application attestations are required.', 'non_application_attestations'))
        return
    for field in ('applies_patches', 'edits_active_artifacts', 'changes_prompts', 'updates_release_state', 'uses_live_sources', 'uses_devhub', 'performs_official_actions'):
        if value.get(field) is not False:
            findings.append(_finding('non-application-attestation-not-false', 'Non-application attestation values must be false.', f'non_application_attestations.{field}'))


def _validate_cross_references(plan: Mapping[str, Any], findings: list[InactivePromotionApplicationPatchPlanFinding]) -> None:
    patch_rows = [row for row in _sequence(plan.get('file_family_patch_rows')) if isinstance(row, Mapping)]
    source_paths = {
        str(row.get('fixture_path') or '')
        for row in _sequence(plan.get('source_fixture_references'))
        if isinstance(row, Mapping)
    }
    approval_ids = {
        str(row.get('approval_id') or '')
        for row in _sequence(plan.get('reviewer_approval_placeholders'))
        if isinstance(row, Mapping)
    }
    rollback_ids = {
        str(row.get('rollback_ref_id') or '')
        for row in _sequence(plan.get('rollback_plan_references'))
        if isinstance(row, Mapping)
    }

    for index, row in enumerate(patch_rows):
        for fixture_ref in _fixture_refs(row.get('source_fixture_refs')):
            if fixture_ref not in source_paths:
                findings.append(_finding('missing-source-fixture-reference', 'Every patch row source fixture ref must have a source_fixture_references row.', f'file_family_patch_rows[{index}].source_fixture_refs'))
        approval_ref = str(row.get('reviewer_approval_ref') or '')
        if approval_ref and approval_ref not in approval_ids:
            findings.append(_finding('missing-reviewer-approval-placeholder', 'Every patch row reviewer approval ref must have a pending reviewer approval placeholder.', f'file_family_patch_rows[{index}].reviewer_approval_ref'))
        for rollback_ref in [str(item) for item in _sequence(row.get('rollback_plan_refs')) if str(item)]:
            if rollback_ref not in rollback_ids:
                findings.append(_finding('missing-rollback-plan-reference', 'Every patch row rollback ref must have a rollback plan reference.', f'file_family_patch_rows[{index}].rollback_plan_refs'))


def _scan_for_forbidden_content(value: Any, findings: list[InactivePromotionApplicationPatchPlanFinding], location: str = 'plan') -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.lower().replace('-', '_')
            child_location = f'{location}.{key_text}'
            if _truthy(child) and any(token in normalized_key for token in _PRIVATE_OR_RAW_KEY_TOKENS):
                findings.append(_finding('private-or-raw-artifact-reference', 'Patch plan must not include private, browser, raw crawl, PDF, or downloaded artifacts.', child_location))
            if _truthy(child) and any(token in normalized_key for token in _ACTIVE_OR_LIVE_KEY_TOKENS):
                findings.append(_finding('mutation-or-live-flag-enabled', 'Active artifact, prompt, release-state, fixture, agent-state, live, DevHub, official action, and patch application flags must be false.', child_location))
            _scan_for_forbidden_content(child, findings, child_location)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _scan_for_forbidden_content(child, findings, f'{location}[{index}]')
    elif isinstance(value, str):
        normalized_path = '/' + PurePosixPath(value.replace(chr(92), '/')).as_posix().lower().lstrip('/')
        if _unsafe_path(normalized_path):
            findings.append(_finding('private-or-raw-artifact-reference', 'Patch plan must not reference private, browser, raw crawl, PDF, or downloaded artifacts.', location))
        if _forbidden_text(value):
            findings.append(_finding('forbidden-release-or-official-action-language', 'Patch plan must not claim live work, applied status, outcome guarantees, or consequential actions.', location))


def _fixture_refs(value: Any) -> list[str]:
    refs: list[str] = []
    for item in _sequence(value):
        if isinstance(item, str) and item.strip():
            refs.append(PurePosixPath(item.strip().replace(chr(92), '/')).as_posix())
    return refs


def _commands(value: Any) -> list[list[str]]:
    commands: list[list[str]] = []
    for item in _sequence(value):
        command = _command(item)
        if command:
            commands.append(command)
    return commands


def _command(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    command = [str(part) for part in value if isinstance(part, str) and part.strip()]
    return command if len(command) == len(value) and command else []


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return value
    return ()


def _truthy(value: Any) -> bool:
    if value is None or value is False or value == '':
        return False
    if isinstance(value, Mapping) and not value:
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and not value:
        return False
    return True


def _unsafe_path(normalized_path: str) -> bool:
    return any(token in normalized_path for token in _PRIVATE_OR_RAW_PATH_TOKENS) or normalized_path.endswith(_PRIVATE_OR_RAW_EXTENSIONS)


def _forbidden_text(value: str) -> bool:
    lowered = ' '.join(value.lower().replace('_', ' ').replace('-', ' ').split())
    compact = value.lower().replace('_', '-').strip()
    return any(token in lowered or token in compact for token in _FORBIDDEN_TEXT_TOKENS)


def _unsafe_validation_command(command: Sequence[str]) -> bool:
    normalized = ' '.join(command).lower()
    return any(part in normalized for part in _FORBIDDEN_VALIDATION_COMMAND_PARTS)


def _slug(value: str) -> str:
    chars = [char.lower() if char.isalnum() else '-' for char in value.strip()]
    slug = ''.join(chars).strip('-')
    while '--' in slug:
        slug = slug.replace('--', '-')
    return slug or 'unknown'


def _finding(code: str, message: str, location: str) -> InactivePromotionApplicationPatchPlanFinding:
    return InactivePromotionApplicationPatchPlanFinding(code=code, message=message, location=location)
