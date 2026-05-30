'''Release rollback rehearsal packet v1 for offline PP&D release review.

The packet is a committed-fixture rehearsal artifact only. It must never carry
private browser/session material, raw crawl output, live execution claims,
outcome guarantees, consequential action language, or active mutation flags.
'''

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from ppd.agent_readiness.inactive_release_decision_packet_v2 import (
    PACKET_TYPE as INACTIVE_DECISION_PACKET_TYPE,
    assert_valid_inactive_release_decision_packet_v2,
)

PACKET_TYPE = 'ppd.release_rollback_rehearsal_packet.v1'

DEFAULT_POST_ROLLBACK_VALIDATION_COMMANDS: tuple[tuple[str, ...], ...] = (
    ('python3', 'ppd/daemon/ppd_daemon.py', '--self-test'),
    ('python3', '-m', 'pytest', 'ppd/tests/test_release_rollback_rehearsal_packet_v1.py'),
)

_REQUIRED_ATTESTATION_FALSE_KEYS = (
    'modifies_active_fixtures',
    'changes_prompts',
    'mutates_release_state',
    'uses_live_sources',
    'accesses_devhub',
    'performs_official_actions',
    'activates_rollback',
)

_MUTATION_KEYS = {
    'active_agent_state_mutation',
    'active_artifact_mutation',
    'active_fixture_mutation',
    'active_guardrail_mutation',
    'active_process_mutation',
    'active_prompt_mutation',
    'active_release_state_mutation',
    'apply_rollback',
    'rollback_activation_enabled',
    'rollback_applied',
    'mutates_agent_state',
    'mutates_artifact',
    'mutates_artifacts',
    'mutates_fixtures',
    'mutates_guardrails',
    'mutates_processes',
    'mutates_prompts',
    'mutates_release_state',
    'promotes_fixtures',
    'updates_agent_state',
    'updates_artifacts',
    'updates_release_state',
}

_ACTIVE_MUTATION_NAME_RE = re.compile(
    r'(^|_)(active_)?(artifact|prompt|release_state|fixture|agent_state)_(mutation|mutating|update|change|promotion|write)(_|$)|'
    r'(^|_)(mutates|updates|changes|promotes)_(artifact|artifacts|prompt|prompts|release_state|fixture|fixtures|agent_state)(_|$)',
    re.IGNORECASE,
)

_FORBIDDEN_FIELD_NAME_RE = re.compile(
    r'(auth(enticated)?[_-]?(artifact|file|state)?|browser[_-]?(artifact|file|state)?|cookie|credential|download(ed)?|har|private|raw[_-]?(artifact|body|capture|crawl|data|download|html|pdf)?|screenshot|session[_-]?(artifact|file|state|storage)?|storage[_-]?state|token|trace)',
    re.IGNORECASE,
)

_FORBIDDEN_TEXT_RE = re.compile(
    r'(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/tmp/)|'
    r'(auth[_ -]?state|authenticated[_ -]?(artifact|file|session)|browser[_ -]?(artifact|file|state)|cookie|credential|har\b|password|private[_ -]?(artifact|file|path|value)|'
    r'raw[_ -]?(artifact|body|capture|crawl|data|download|html|pdf)|downloaded[_ -]?(data|document|pdf)|'
    r'screenshot|session[_ -]?(artifact|file|state|storage)?|storage[_ -]?state|token|trace([._ -]?(file|zip))?)|'
    r'\b(live\s+(crawl|browser|devhub|execution|processor|promotion|run)|crawl\s+live|access\s+devhub|'
    r'promoted\s+(fixtures|release|to)|release\s+(complete|completed|state\s+updated)|rollback\s+(complete|completed|applied|activated)|'
    r'official\s+action\s+performed|legal\s+outcome\s+(is\s+)?guaranteed|guaranteed\s+legal\s+outcome|'
    r'permit(ting)?\s+outcome\s+(is\s+)?guaranteed|permit\s+will\s+be\s+(approved|issued)|'
    r'approval\s+is\s+guaranteed|guaranteed\s+(approval|issuance|permit\s+outcome)|'
    r'payment|pay\s+(the\s+)?fee|submit(ted|s|ting)?\b|submission|schedule\s+(the\s+)?inspection|'
    r'cancel\s+(the\s+)?inspection|certif(y|ication)|upload(s|ed|ing)?\b|make\s+official\s+changes?|'
    r'perform\s+(the\s+)?official\s+action|execute\s+(the\s+)?rollback)\b',
    re.IGNORECASE,
)

_COMMAND_FORBIDDEN_RE = re.compile(r'\b(live|crawl|devhub|playwright|browser|network|auth|session)\b', re.IGNORECASE)


@dataclass(frozen=True)
class ReleaseRollbackRehearsalIssue:
    code: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {'code': self.code, 'path': self.path, 'message': self.message}


@dataclass(frozen=True)
class ReleaseRollbackRehearsalValidationResult:
    ok: bool
    issues: tuple[ReleaseRollbackRehearsalIssue, ...]

    def as_dict(self) -> dict[str, Any]:
        return {'ok': self.ok, 'issues': [issue.as_dict() for issue in self.issues]}


def build_release_rollback_rehearsal_packet_v1(
    inactive_release_decision_packet_v2: Mapping[str, Any],
    *,
    packet_id: str = 'fixture-release-rollback-rehearsal-packet-v1',
    post_rollback_validation_commands: Sequence[Sequence[str]] = DEFAULT_POST_ROLLBACK_VALIDATION_COMMANDS,
) -> dict[str, Any]:
    '''Build a deterministic rollback rehearsal packet from inactive decision v2.'''

    assert_valid_inactive_release_decision_packet_v2(inactive_release_decision_packet_v2)
    _raise_for_unsafe_content(inactive_release_decision_packet_v2)

    pre_commands = _pre_rollback_validation_commands(inactive_release_decision_packet_v2)
    post_commands = [list(command) for command in post_rollback_validation_commands]
    inventory = _affected_fixture_family_inventory(inactive_release_decision_packet_v2)
    acknowledgement_placeholders = _reviewer_acknowledgement_placeholders(inactive_release_decision_packet_v2)
    scenario_rows = _ordered_rollback_scenario_rows(
        inactive_release_decision_packet_v2,
        inventory,
        pre_commands,
        post_commands,
        acknowledgement_placeholders,
    )

    packet = {
        'packet_type': PACKET_TYPE,
        'packet_id': packet_id,
        'fixture_only': True,
        'rollback_rehearsal_only': True,
        'source_inactive_release_decision_packet': {
            'packet_type': INACTIVE_DECISION_PACKET_TYPE,
            'packet_id': str(inactive_release_decision_packet_v2.get('packet_id') or 'inactive-release-decision-packet-v2'),
        },
        'ordered_rollback_scenario_rows': scenario_rows,
        'affected_inactive_fixture_family_inventory': inventory,
        'pre_rollback_validation_commands': pre_commands,
        'post_rollback_validation_commands': post_commands,
        'reviewer_acknowledgement_placeholders': acknowledgement_placeholders,
        'residual_risk_notes': _residual_risk_notes(inactive_release_decision_packet_v2),
        'rollback_rehearsal_attestations': {key: False for key in _REQUIRED_ATTESTATION_FALSE_KEYS},
    }
    assert_valid_release_rollback_rehearsal_packet_v1(packet)
    return packet


def validate_release_rollback_rehearsal_packet_v1(packet: Mapping[str, Any]) -> ReleaseRollbackRehearsalValidationResult:
    issues: list[ReleaseRollbackRehearsalIssue] = []

    if packet.get('packet_type') != PACKET_TYPE:
        issues.append(ReleaseRollbackRehearsalIssue('invalid_packet_type', 'packet_type', f'packet_type must be {PACKET_TYPE}'))
    if packet.get('fixture_only') is not True:
        issues.append(ReleaseRollbackRehearsalIssue('fixture_only_required', 'fixture_only', 'fixture_only must be true'))
    if packet.get('rollback_rehearsal_only') is not True:
        issues.append(ReleaseRollbackRehearsalIssue('rollback_rehearsal_only_required', 'rollback_rehearsal_only', 'rollback rehearsal flag must be true'))

    for field in (
        'ordered_rollback_scenario_rows',
        'affected_inactive_fixture_family_inventory',
        'pre_rollback_validation_commands',
        'post_rollback_validation_commands',
        'reviewer_acknowledgement_placeholders',
        'residual_risk_notes',
    ):
        if not _non_empty_sequence(packet.get(field)):
            issues.append(ReleaseRollbackRehearsalIssue('missing_required_rows', field, f'{field} must be a non-empty list'))

    _validate_scenario_rows(packet.get('ordered_rollback_scenario_rows'), issues)
    _validate_fixture_inventory(packet.get('affected_inactive_fixture_family_inventory'), issues)
    _validate_commands(packet.get('pre_rollback_validation_commands'), 'pre_rollback_validation_commands', issues)
    _validate_commands(packet.get('post_rollback_validation_commands'), 'post_rollback_validation_commands', issues)
    _validate_acknowledgements(packet.get('reviewer_acknowledgement_placeholders'), issues)
    _validate_residual_risks(packet.get('residual_risk_notes'), issues)
    _validate_attestations(packet.get('rollback_rehearsal_attestations'), issues)
    _validate_cross_references(packet, issues)
    _scan_for_unsafe_content(packet, '', issues)

    return ReleaseRollbackRehearsalValidationResult(not issues, tuple(issues))


def assert_valid_release_rollback_rehearsal_packet_v1(packet: Mapping[str, Any]) -> None:
    result = validate_release_rollback_rehearsal_packet_v1(packet)
    if not result.ok:
        formatted = '; '.join(f'{issue.code} at {issue.path}' for issue in result.issues)
        raise ValueError(f'release rollback rehearsal packet v1 validation failed: {formatted}')


def _ordered_rollback_scenario_rows(
    decision_packet: Mapping[str, Any],
    inventory: Sequence[Mapping[str, Any]],
    pre_commands: Sequence[Sequence[str]],
    post_commands: Sequence[Sequence[str]],
    acknowledgements: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    inventory_refs = [str(row.get('fixture_family_id')) for row in inventory]
    acknowledgement_by_reviewer = {str(row.get('reviewer_id')): row for row in acknowledgements}
    default_ack = acknowledgements[0] if acknowledgements else {'acknowledgement_id': 'acknowledgement-pending-reviewer'}
    rows: list[dict[str, Any]] = []

    for index, decision_row in enumerate(_mapping_rows(decision_packet.get('decision_rows'))):
        reviewer_id = str(decision_row.get('reviewer_id') or 'reviewer')
        acknowledgement = acknowledgement_by_reviewer.get(reviewer_id, default_ack)
        decision = str(decision_row.get('decision') or 'hold')
        scenario_kind = 'approve_noop_checkpoint' if decision == 'approve' else 'hold_blocker_checkpoint'
        rows.append(
            {
                'scenario_row_id': f'rollback-scenario-{index + 1}',
                'sequence': index + 1,
                'source_decision_row_id': str(decision_row.get('decision_row_id') or f'decision-row-{index + 1}'),
                'source_decision': decision,
                'scenario_kind': scenario_kind,
                'rollback_state': 'rehearsal_only_no_active_rollback',
                'affected_fixture_family_refs': inventory_refs,
                'pre_rollback_validation_commands': [list(command) for command in pre_commands],
                'rehearsal_steps': _scenario_steps(decision),
                'post_rollback_validation_commands': [list(command) for command in post_commands],
                'reviewer_acknowledgement_placeholder_ref': str(acknowledgement.get('acknowledgement_id') or 'acknowledgement-pending-reviewer'),
                'residual_risk_note_refs': ['residual-risk-manual-review', 'residual-risk-no-active-rollback'],
                'citations': _citations(decision_row),
            }
        )
    return rows


def _scenario_steps(decision: str) -> list[str]:
    if decision == 'approve':
        return [
            'Record that approve rows still require a separate operator decision before any activation path.',
            'Confirm inactive fixture-family checksums remain reference-only in this rehearsal packet.',
            'Confirm no active rollback command is produced by this packet.',
        ]
    return [
        'Carry forward the hold row into rollback readiness review.',
        'Confirm blocker notes remain reviewer-owned placeholders.',
        'Confirm no active rollback command is produced by this packet.',
    ]


def _affected_fixture_family_inventory(decision_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    specs = (
        ('inactive-release-decision-rows', 'decision_rows'),
        ('inactive-blocked-release-reasons', 'blocked_release_reasons'),
        ('inactive-reviewer-signoff-placeholders', 'reviewer_signoff_placeholders'),
        ('inactive-validation-replay-inventory', 'prerequisite_validation_replay_inventory'),
        ('inactive-rollback-plan-references', 'rollback_plan_references'),
    )
    rows: list[dict[str, Any]] = []
    for family_id, source_field in specs:
        source_rows = _mapping_rows(decision_packet.get(source_field))
        rows.append(
            {
                'fixture_family_id': family_id,
                'source_field': source_field,
                'affected_count': len(source_rows),
                'inventory_state': 'inactive_fixture_reference_only',
                'active_fixture_mutation': False,
                'citations': _family_citations(source_rows),
            }
        )
    return rows


def _reviewer_acknowledgement_placeholders(decision_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, signoff in enumerate(_mapping_rows(decision_packet.get('reviewer_signoff_placeholders'))):
        reviewer_id = str(signoff.get('reviewer_id') or f'reviewer-{index + 1}')
        rows.append(
            {
                'acknowledgement_id': f'rollback-acknowledgement-{index + 1}',
                'reviewer_id': reviewer_id,
                'placeholder': 'pending_manual_rollback_rehearsal_acknowledgement',
                'required_before': 'any_separate_operator_rollback_or_release_decision',
                'citations': _citations(signoff),
            }
        )
    return rows


def _residual_risk_notes(decision_packet: Mapping[str, Any]) -> list[dict[str, Any]]:
    notes = [
        {
            'risk_id': 'residual-risk-manual-review',
            'risk': 'Manual reviewer acknowledgement remains pending outside this fixture-only rehearsal packet.',
            'owner_placeholder': 'release-reviewer',
            'disposition': 'carry_forward_to_separate_authorized_review',
            'citations': ['fixture:reviewer-acknowledgement-placeholders'],
        },
        {
            'risk_id': 'residual-risk-no-active-rollback',
            'risk': 'This packet rehearses rollback ordering only and does not activate rollback or mutate release state.',
            'owner_placeholder': 'release-operator',
            'disposition': 'blocked_until_separate_authorized_review',
            'citations': ['fixture:rollback-rehearsal-boundary'],
        },
    ]
    for index, reason in enumerate(_mapping_rows(decision_packet.get('blocked_release_reasons'))):
        notes.append(
            {
                'risk_id': f'residual-risk-blocked-release-{index + 1}',
                'risk': str(reason.get('reason') or 'Blocked release reason remains open.'),
                'owner_placeholder': str(reason.get('owner_placeholder') or 'release-reviewer'),
                'disposition': 'carry_forward_to_separate_authorized_review',
                'citations': _citations(reason),
            }
        )
    return notes


def _pre_rollback_validation_commands(decision_packet: Mapping[str, Any]) -> list[list[str]]:
    commands: list[list[str]] = []
    for row in _mapping_rows(decision_packet.get('prerequisite_validation_replay_inventory')):
        command = row.get('command')
        if _string_sequence(command):
            commands.append(list(command))
    for command in _command_rows(decision_packet.get('offline_validation_commands')):
        commands.append(list(command))
    return _dedupe_commands(commands)


def _validate_scenario_rows(value: Any, issues: list[ReleaseRollbackRehearsalIssue]) -> None:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            if not isinstance(item, Mapping):
                issues.append(ReleaseRollbackRehearsalIssue('invalid_scenario_row', f'ordered_rollback_scenario_rows[{index}]', 'scenario rows must be objects'))
    for index, row in enumerate(_mapping_rows(value)):
        path = f'ordered_rollback_scenario_rows[{index}]'
        if row.get('sequence') != index + 1:
            issues.append(ReleaseRollbackRehearsalIssue('invalid_scenario_sequence', f'{path}.sequence', 'scenario rows must be ordered from 1'))
        if row.get('source_decision') not in {'approve', 'hold'}:
            issues.append(ReleaseRollbackRehearsalIssue('invalid_source_decision', f'{path}.source_decision', 'source decision must be approve or hold'))
        if row.get('rollback_state') != 'rehearsal_only_no_active_rollback':
            issues.append(ReleaseRollbackRehearsalIssue('invalid_rollback_state', f'{path}.rollback_state', 'scenario must remain rehearsal-only'))
        if not _string_sequence(row.get('affected_fixture_family_refs')):
            issues.append(ReleaseRollbackRehearsalIssue('missing_affected_fixture_refs', f'{path}.affected_fixture_family_refs', 'scenario must reference affected inactive fixture families'))
        if not _string_sequence(row.get('rehearsal_steps')):
            issues.append(ReleaseRollbackRehearsalIssue('missing_rehearsal_steps', f'{path}.rehearsal_steps', 'scenario must include ordered rehearsal steps'))
        if not _has_citation(row.get('citations')):
            issues.append(ReleaseRollbackRehearsalIssue('uncited_scenario', f'{path}.citations', 'scenario row must cite fixture evidence'))
        _validate_commands(row.get('pre_rollback_validation_commands'), f'{path}.pre_rollback_validation_commands', issues)
        _validate_commands(row.get('post_rollback_validation_commands'), f'{path}.post_rollback_validation_commands', issues)


def _validate_fixture_inventory(value: Any, issues: list[ReleaseRollbackRehearsalIssue]) -> None:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            if not isinstance(item, Mapping):
                issues.append(ReleaseRollbackRehearsalIssue('invalid_fixture_inventory_row', f'affected_inactive_fixture_family_inventory[{index}]', 'inventory rows must be objects'))
    for index, row in enumerate(_mapping_rows(value)):
        path = f'affected_inactive_fixture_family_inventory[{index}]'
        if not _text(row.get('fixture_family_id')):
            issues.append(ReleaseRollbackRehearsalIssue('missing_fixture_family_id', f'{path}.fixture_family_id', 'fixture family id is required'))
        if row.get('inventory_state') != 'inactive_fixture_reference_only':
            issues.append(ReleaseRollbackRehearsalIssue('invalid_inventory_state', f'{path}.inventory_state', 'inventory must remain inactive reference-only'))
        if not isinstance(row.get('affected_count'), int):
            issues.append(ReleaseRollbackRehearsalIssue('invalid_affected_count', f'{path}.affected_count', 'affected_count must be an integer'))
        if row.get('active_fixture_mutation') is not False:
            issues.append(ReleaseRollbackRehearsalIssue('active_fixture_mutation', f'{path}.active_fixture_mutation', 'active fixture mutation must be false'))
        if not _has_citation(row.get('citations')):
            issues.append(ReleaseRollbackRehearsalIssue('uncited_fixture_inventory', f'{path}.citations', 'inventory row must cite fixture evidence'))


def _validate_acknowledgements(value: Any, issues: list[ReleaseRollbackRehearsalIssue]) -> None:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            if not isinstance(item, Mapping):
                issues.append(ReleaseRollbackRehearsalIssue('invalid_acknowledgement_row', f'reviewer_acknowledgement_placeholders[{index}]', 'acknowledgement rows must be objects'))
    for index, row in enumerate(_mapping_rows(value)):
        path = f'reviewer_acknowledgement_placeholders[{index}]'
        if not _text(row.get('acknowledgement_id')):
            issues.append(ReleaseRollbackRehearsalIssue('missing_acknowledgement_id', f'{path}.acknowledgement_id', 'acknowledgement id is required'))
        if row.get('placeholder') != 'pending_manual_rollback_rehearsal_acknowledgement':
            issues.append(ReleaseRollbackRehearsalIssue('invalid_acknowledgement_placeholder', f'{path}.placeholder', 'acknowledgement must remain pending'))
        if row.get('required_before') != 'any_separate_operator_rollback_or_release_decision':
            issues.append(ReleaseRollbackRehearsalIssue('invalid_acknowledgement_gate', f'{path}.required_before', 'acknowledgement must gate any separate operator decision'))
        if not _has_citation(row.get('citations')):
            issues.append(ReleaseRollbackRehearsalIssue('uncited_acknowledgement', f'{path}.citations', 'acknowledgement must cite fixture evidence'))


def _validate_residual_risks(value: Any, issues: list[ReleaseRollbackRehearsalIssue]) -> None:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, item in enumerate(value):
            if not isinstance(item, Mapping):
                issues.append(ReleaseRollbackRehearsalIssue('invalid_residual_risk_row', f'residual_risk_notes[{index}]', 'residual risk rows must be objects'))
    for index, row in enumerate(_mapping_rows(value)):
        path = f'residual_risk_notes[{index}]'
        if not _text(row.get('risk_id')) or not _text(row.get('risk')):
            issues.append(ReleaseRollbackRehearsalIssue('invalid_residual_risk', path, 'residual risk requires risk_id and risk'))
        if row.get('disposition') not in {'carry_forward_to_separate_authorized_review', 'blocked_until_separate_authorized_review'}:
            issues.append(ReleaseRollbackRehearsalIssue('invalid_residual_risk_disposition', f'{path}.disposition', 'residual risk disposition must remain reviewer-gated'))
        if not _has_citation(row.get('citations')):
            issues.append(ReleaseRollbackRehearsalIssue('uncited_residual_risk', f'{path}.citations', 'residual risk must cite fixture evidence'))


def _validate_attestations(value: Any, issues: list[ReleaseRollbackRehearsalIssue]) -> None:
    if not isinstance(value, Mapping):
        issues.append(ReleaseRollbackRehearsalIssue('missing_rollback_rehearsal_attestations', 'rollback_rehearsal_attestations', 'rollback rehearsal attestations are required'))
        return
    for key in _REQUIRED_ATTESTATION_FALSE_KEYS:
        if value.get(key) is not False:
            issues.append(ReleaseRollbackRehearsalIssue('rollback_attestation_not_false', f'rollback_rehearsal_attestations.{key}', f'{key} must be false'))


def _validate_cross_references(packet: Mapping[str, Any], issues: list[ReleaseRollbackRehearsalIssue]) -> None:
    inventory_ids = {
        str(row.get('fixture_family_id'))
        for row in _mapping_rows(packet.get('affected_inactive_fixture_family_inventory'))
        if _text(row.get('fixture_family_id'))
    }
    acknowledgement_ids = {
        str(row.get('acknowledgement_id'))
        for row in _mapping_rows(packet.get('reviewer_acknowledgement_placeholders'))
        if _text(row.get('acknowledgement_id'))
    }
    risk_ids = {
        str(row.get('risk_id'))
        for row in _mapping_rows(packet.get('residual_risk_notes'))
        if _text(row.get('risk_id'))
    }

    for index, row in enumerate(_mapping_rows(packet.get('ordered_rollback_scenario_rows'))):
        path = f'ordered_rollback_scenario_rows[{index}]'
        refs = {str(item) for item in row.get('affected_fixture_family_refs', []) if isinstance(item, str) and item.strip()}
        if refs and inventory_ids and not refs.issubset(inventory_ids):
            issues.append(ReleaseRollbackRehearsalIssue('unknown_fixture_family_ref', f'{path}.affected_fixture_family_refs', 'scenario references must be present in affected inactive fixture-family inventory'))
        ack_ref = row.get('reviewer_acknowledgement_placeholder_ref')
        if not _text(ack_ref):
            issues.append(ReleaseRollbackRehearsalIssue('missing_acknowledgement_ref', f'{path}.reviewer_acknowledgement_placeholder_ref', 'scenario must reference a reviewer acknowledgement placeholder'))
        elif acknowledgement_ids and str(ack_ref) not in acknowledgement_ids:
            issues.append(ReleaseRollbackRehearsalIssue('unknown_acknowledgement_ref', f'{path}.reviewer_acknowledgement_placeholder_ref', 'scenario acknowledgement reference must exist'))
        risk_refs = {str(item) for item in row.get('residual_risk_note_refs', []) if isinstance(item, str) and item.strip()}
        if not risk_refs:
            issues.append(ReleaseRollbackRehearsalIssue('missing_residual_risk_refs', f'{path}.residual_risk_note_refs', 'scenario must reference residual risk notes'))
        elif risk_ids and not risk_refs.issubset(risk_ids):
            issues.append(ReleaseRollbackRehearsalIssue('unknown_residual_risk_ref', f'{path}.residual_risk_note_refs', 'scenario residual risk references must exist'))


def _validate_commands(value: Any, path: str, issues: list[ReleaseRollbackRehearsalIssue]) -> None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        issues.append(ReleaseRollbackRehearsalIssue('invalid_validation_command_inventory', path, 'validation commands must be a list of argv lists'))
        return
    if not value:
        issues.append(ReleaseRollbackRehearsalIssue('missing_validation_command', path, 'validation commands must be non-empty'))
        return
    for index, command in enumerate(value):
        command_path = f'{path}[{index}]'
        if not _string_sequence(command):
            issues.append(ReleaseRollbackRehearsalIssue('invalid_validation_command', command_path, 'validation command must be an argv string list'))
            continue
        if _COMMAND_FORBIDDEN_RE.search(' '.join(command)):
            issues.append(ReleaseRollbackRehearsalIssue('unsafe_validation_command', command_path, 'validation command must not invoke live, crawler, DevHub, browser, network, auth, or session paths'))


def _raise_for_unsafe_content(value: Any) -> None:
    issues: list[ReleaseRollbackRehearsalIssue] = []
    _scan_for_unsafe_content(value, '', issues)
    if issues:
        formatted = '; '.join(f'{issue.code} at {issue.path}' for issue in issues)
        raise ValueError(f'unsafe release rollback rehearsal content: {formatted}')


def _scan_for_unsafe_content(value: Any, path: str, issues: list[ReleaseRollbackRehearsalIssue]) -> None:
    for child_path, child in _walk(value, path):
        name = _path_name(child_path).lower().replace('-', '_')
        if (name in _MUTATION_KEYS or _ACTIVE_MUTATION_NAME_RE.search(name)) and _active_flag(child):
            issues.append(ReleaseRollbackRehearsalIssue('active_mutation_flag', child_path, 'active mutation, rollback activation, or fixture promotion flags are not allowed'))
        if name and not name.startswith('no_') and _FORBIDDEN_FIELD_NAME_RE.search(name) and _present_value(child):
            issues.append(ReleaseRollbackRehearsalIssue('private_or_raw_artifact_field', child_path, 'packet fields must not carry private/authenticated browser artifacts, screenshots, traces, HAR files, raw crawl/PDF data, or downloads'))
        if isinstance(child, str) and _FORBIDDEN_TEXT_RE.search(child):
            issues.append(ReleaseRollbackRehearsalIssue('unsafe_packet_text', child_path, 'packet text must not reference private artifacts, raw data, live execution, guarantees, consequential actions, rollback completion, or active release mutation'))


def _mapping_rows(value: Any) -> tuple[Mapping[str, Any], ...]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(item for item in value if isinstance(item, Mapping))
    return ()


def _command_rows(value: Any) -> tuple[Sequence[str], ...]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return tuple(item for item in value if _string_sequence(item))
    return ()


def _citations(row: Mapping[str, Any]) -> list[str]:
    citations = row.get('citations')
    if isinstance(citations, str) and citations.strip():
        return [citations.strip()]
    if isinstance(citations, Sequence) and not isinstance(citations, (str, bytes, bytearray)):
        result = [item.strip() for item in citations if isinstance(item, str) and item.strip()]
        if result:
            return result
    return ['fixture:inactive-release-decision-packet-v2']


def _family_citations(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    citations: list[str] = []
    for row in rows:
        citations.extend(_citations(row))
    return sorted(dict.fromkeys(citations)) or ['fixture:inactive-release-decision-packet-v2']


def _has_citation(value: Any) -> bool:
    return bool(_citations({'citations': value}))


def _non_empty_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and bool(value)


def _string_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)) and all(isinstance(item, str) and item.strip() for item in value)


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ''


def _dedupe_commands(commands: Sequence[Sequence[str]]) -> list[list[str]]:
    seen: set[tuple[str, ...]] = set()
    result: list[list[str]] = []
    for command in commands:
        key = tuple(command)
        if key and key not in seen:
            seen.add(key)
            result.append(list(command))
    return result


def _walk(value: Any, path: str) -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = str(key) if not path else f'{path}.{key}'
            yield from _walk(child, child_path)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            yield from _walk(child, f'{path}[{index}]')


def _path_name(path: str) -> str:
    if not path:
        return ''
    return path.rsplit('.', 1)[-1].split('[', 1)[0]


def _active_flag(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {'1', 'active', 'enabled', 'true', 'yes'}
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return False


def _present_value(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return True
