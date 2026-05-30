'''Fixture-first attended DevHub read-only observation readiness packet v2.

This module consumes an inactive release activation checklist fixture and produces
an offline-only readiness packet for a later attended DevHub read-only
observation. It does not create browser state, authenticate, open DevHub, store
private artifacts, or perform official actions.
'''

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
import re
from typing import Any

PACKET_VERSION = 'attended-devhub-readonly-observation-readiness-packet-v2'
EXPECTED_CHECKLIST_ID = 'inactive-release-activation-checklist-v2'

OFFLINE_VALIDATION_COMMANDS: list[list[str]] = [
    ['python3', '-m', 'py_compile', 'ppd/devhub_attended_readonly_observation_readiness_packet_v2.py'],
    ['python3', '-m', 'pytest', 'ppd/tests/test_devhub_attended_readonly_observation_readiness_packet_v2.py'],
    ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'],
]

_REQUIRED_TOP_LEVEL_LISTS = (
    'ordered_attended_session_prerequisites',
    'manual_login_handoff_placeholders',
    'read_only_surface_observation_placeholders',
    'redaction_checklist_placeholders',
    'action_boundary_reminders',
    'exact_offline_validation_commands',
)
_REQUIRED_REDACTION_IDS = {
    'credentials_and_tokens_absent',
    'session_artifacts_absent',
    'private_values_redacted',
    'screenshots_traces_har_absent',
}
_REQUIRED_BOUNDARY_IDS = {
    'read_only_only',
    'manual_login_only',
    'no_official_actions',
    'no_private_artifacts',
}
_FORBIDDEN_KEY_RE = re.compile(
    r'(^|_)(auth[_-]?state|browser[_-]?(artifact|context|state|trace)|cookie|credential|downloaded?[_-]?(artifact|document|path|file)|har|password|private[_-]?(artifact|path|value)|raw[_-]?(body|content|crawl|download|html|text)|session[_-]?(artifact|cookie|path|state|storage)|screenshot|storage[_-]?state|token|trace)(_|$)',
    re.IGNORECASE,
)
_FORBIDDEN_VALUE_RE = re.compile(
    r'(^(file|session)://|/(tmp|var/folders|private|home)/|\\users\\|\.har$|trace\.zip$|storage-state\.json$|cookies?\.json$|/downloads?/|/sessions?/|private session|browser trace|auth state)',
    re.IGNORECASE,
)
_LIVE_ACCESS_RE = re.compile(
    r'\b(live devhub|opened devhub|accessed devhub|logged in|authenticated session|browser session created|manual login completed|captured live|observed live)\b',
    re.IGNORECASE,
)
_AUTOMATED_LOGIN_RE = re.compile(
    r'\b(automated|auto|scripted|bot|headless|programmatic)\b.{0,40}\b(login|sign[- ]?in|mfa|captcha|password|credential|otp|one[- ]?time code|security prompt)\b|\b(login|sign[- ]?in|mfa|captcha|password|credential|otp|one[- ]?time code|security prompt)\b.{0,40}\b(automated|auto|scripted|bot|headless|programmatic)\b',
    re.IGNORECASE,
)
_OFFICIAL_ACTION_RE = re.compile(
    r'\b(submitted|submission completed|paid fee|payment completed|scheduled inspection|cancelled inspection|canceled inspection|certified application|uploaded corrections|uploaded plans|purchased permit|changed account)\b',
    re.IGNORECASE,
)
_GUARANTEE_RE = re.compile(
    r'\b(guarantee[ds]?|ensure[ds]?|promise[ds]?|will be approved|approval guaranteed|permit guaranteed|legally compliant|legal certainty|binding legal advice|no risk of denial|must approve|cannot deny)\b',
    re.IGNORECASE,
)
_MUTATION_KEY_RE = re.compile(
    r'(^|_)(active|apply|mutate|promote|update|write).*(devhub|surface|source|guardrail|prompt|contract|release)(_|$)|(^|_)(devhub|surface|source|guardrail|prompt|contract|release).*(active|apply|mutate|promote|update|write)(_|$)',
    re.IGNORECASE,
)
_ACTIVE_VALUES = {'active', 'applied', 'changed', 'enabled', 'true', 'updated', 'yes'}


@dataclass(frozen=True)
class AttendedDevhubReadonlyObservationReadinessPacketV2ValidationResult:
    valid: bool
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return self.valid

    def as_dict(self) -> dict[str, Any]:
        return {'valid': self.valid, 'errors': list(self.errors)}


def build_attended_devhub_readonly_observation_readiness_packet_v2(checklist: dict[str, Any]) -> dict[str, Any]:
    '''Build a deterministic readiness packet from an inactive checklist fixture.'''

    checklist_id = _required_str(checklist, 'checklist_id')
    if checklist_id != EXPECTED_CHECKLIST_ID:
        raise ValueError(f'expected checklist_id {EXPECTED_CHECKLIST_ID!r}, got {checklist_id!r}')
    if _required_str(checklist, 'status') != 'inactive':
        raise ValueError('attended DevHub read-only readiness packet v2 only consumes inactive checklists')

    activation_items = _required_list(checklist, 'activation_items')
    source_groups = _required_list(checklist, 'source_groups')

    packet = {
        'packet_version': PACKET_VERSION,
        'packet_id': 'fixture-first-attended-devhub-readonly-observation-readiness-v2',
        'source_checklist_id': checklist_id,
        'source_checklist_status': 'inactive',
        'release': _required_str(checklist, 'release'),
        'generated_from_fixture_at': _required_str(checklist, 'generated_at'),
        'mode': 'fixture_first_offline_readiness',
        'devhub_access': 'not_requested',
        'browser_artifacts': 'not_created',
        'official_action_scope': 'blocked',
        'ordered_attended_session_prerequisites': [
            {
                'order': index,
                'checklist_item_id': _required_str(item, 'item_id'),
                'title': _required_str(item, 'title'),
                'source_scope': _required_str(item, 'source_scope'),
                'readiness_gate': item.get('readiness_gate', 'manual_review_required'),
                'status': 'pending_attended_readonly_review',
                'requires_user_attendance': True,
                'blocks_devhub_observation_until_resolved': True,
            }
            for index, item in enumerate(activation_items, start=1)
        ],
        'manual_login_handoff_placeholders': [
            {
                'order': 1,
                'handoff_id': 'operator-visible-browser-start',
                'status': 'placeholder_pending_attended_session',
                'required_before_observation': True,
                'operator_note': 'Open only a user-visible browser during a later attended session.',
            },
            {
                'order': 2,
                'handoff_id': 'user-completes-portlandoregon-sign-in',
                'status': 'placeholder_pending_user_action',
                'required_before_observation': True,
                'operator_note': 'The user completes sign-in prompts manually; this packet stores no sign-in material.',
            },
        ],
        'read_only_surface_observation_placeholders': [
            {
                'order': index,
                'surface_group_id': _required_str(group, 'source_group_id'),
                'canonical_hosts': _required_list(group, 'canonical_hosts'),
                'surface_scope': 'attended_devhub_read_only_review',
                'observation_status': 'placeholder_not_observed',
                'expected_capture_fields': ['page_heading', 'landmark_roles', 'link_or_button_names', 'status_text_labels'],
                'reviewer_notes': None,
            }
            for index, group in enumerate(source_groups, start=1)
        ],
        'redaction_checklist_placeholders': [
            {'order': 1, 'redaction_id': 'credentials_and_tokens_absent', 'status': 'required_before_acceptance', 'reviewer_confirmation': None},
            {'order': 2, 'redaction_id': 'session_artifacts_absent', 'status': 'required_before_acceptance', 'reviewer_confirmation': None},
            {'order': 3, 'redaction_id': 'private_values_redacted', 'status': 'required_before_acceptance', 'reviewer_confirmation': None},
            {'order': 4, 'redaction_id': 'screenshots_traces_har_absent', 'status': 'required_before_acceptance', 'reviewer_confirmation': None},
        ],
        'action_boundary_reminders': [
            {'order': 1, 'boundary_id': 'read_only_only', 'statement': 'Observe account-scoped pages only after user attendance; do not edit page data.'},
            {'order': 2, 'boundary_id': 'manual_login_only', 'statement': 'The user handles credentials, MFA, CAPTCHA, and account prompts manually.'},
            {'order': 3, 'boundary_id': 'no_official_actions', 'statement': 'Do not upload, submit, certify, pay, schedule, cancel, purchase, withdraw, or change account settings.'},
            {'order': 4, 'boundary_id': 'no_private_artifacts', 'statement': 'Do not create or commit auth state, screenshots, traces, HAR files, raw page captures, or private session artifacts.'},
        ],
        'exact_offline_validation_commands': deepcopy(OFFLINE_VALIDATION_COMMANDS),
    }
    require_attended_devhub_readonly_observation_readiness_packet_v2(packet)
    return packet


def validate_attended_devhub_readonly_observation_readiness_packet_v2(
    packet: Mapping[str, Any],
) -> AttendedDevhubReadonlyObservationReadinessPacketV2ValidationResult:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return AttendedDevhubReadonlyObservationReadinessPacketV2ValidationResult(False, ('packet must be an object',))

    if packet.get('packet_version') != PACKET_VERSION:
        errors.append(f'packet_version must be {PACKET_VERSION}')
    if packet.get('mode') != 'fixture_first_offline_readiness':
        errors.append('mode must be fixture_first_offline_readiness')
    if packet.get('devhub_access') != 'not_requested':
        errors.append('devhub_access must be not_requested')
    if packet.get('browser_artifacts') != 'not_created':
        errors.append('browser_artifacts must be not_created')
    if packet.get('official_action_scope') != 'blocked':
        errors.append('official_action_scope must be blocked')

    for field in _REQUIRED_TOP_LEVEL_LISTS:
        if not _non_empty_list(packet.get(field)):
            errors.append(f'{field} must be a non-empty list')

    _validate_prerequisites(errors, packet.get('ordered_attended_session_prerequisites'))
    _validate_manual_login(errors, packet.get('manual_login_handoff_placeholders'))
    _validate_surface_placeholders(errors, packet.get('read_only_surface_observation_placeholders'))
    _validate_redaction_placeholders(errors, packet.get('redaction_checklist_placeholders'))
    _validate_action_boundaries(errors, packet.get('action_boundary_reminders'))
    _validate_validation_commands(errors, packet.get('exact_offline_validation_commands'))
    _validate_recursive_safety(errors, packet)
    return AttendedDevhubReadonlyObservationReadinessPacketV2ValidationResult(not errors, tuple(errors))


def require_attended_devhub_readonly_observation_readiness_packet_v2(packet: Mapping[str, Any]) -> None:
    result = validate_attended_devhub_readonly_observation_readiness_packet_v2(packet)
    if not result.valid:
        raise ValueError('invalid attended DevHub read-only observation readiness packet v2: ' + '; '.join(result.errors))


def _validate_prerequisites(errors: list[str], value: Any) -> None:
    for index, item in enumerate(_mapping_sequence(value)):
        prefix = f'ordered_attended_session_prerequisites[{index}]'
        for field in ('checklist_item_id', 'title', 'source_scope', 'readiness_gate', 'status'):
            if not _text(item.get(field)):
                errors.append(f'{prefix}.{field} must be present')
        if item.get('requires_user_attendance') is not True:
            errors.append(f'{prefix}.requires_user_attendance must be true')
        if item.get('blocks_devhub_observation_until_resolved') is not True:
            errors.append(f'{prefix}.blocks_devhub_observation_until_resolved must be true')


def _validate_manual_login(errors: list[str], value: Any) -> None:
    for index, item in enumerate(_mapping_sequence(value)):
        prefix = f'manual_login_handoff_placeholders[{index}]'
        if not _text(item.get('handoff_id')):
            errors.append(f'{prefix}.handoff_id must be present')
        if item.get('status') not in {'placeholder_pending_attended_session', 'placeholder_pending_user_action'}:
            errors.append(f'{prefix}.status must remain a placeholder')
        if item.get('required_before_observation') is not True:
            errors.append(f'{prefix}.required_before_observation must be true')


def _validate_surface_placeholders(errors: list[str], value: Any) -> None:
    for index, item in enumerate(_mapping_sequence(value)):
        prefix = f'read_only_surface_observation_placeholders[{index}]'
        if not _text(item.get('surface_group_id')):
            errors.append(f'{prefix}.surface_group_id must be present')
        if not _string_list(item.get('canonical_hosts')):
            errors.append(f'{prefix}.canonical_hosts must be non-empty')
        if item.get('surface_scope') != 'attended_devhub_read_only_review':
            errors.append(f'{prefix}.surface_scope must be attended_devhub_read_only_review')
        if item.get('observation_status') != 'placeholder_not_observed':
            errors.append(f'{prefix}.observation_status must remain placeholder_not_observed')
        if not _string_list(item.get('expected_capture_fields')):
            errors.append(f'{prefix}.expected_capture_fields must be non-empty')


def _validate_redaction_placeholders(errors: list[str], value: Any) -> None:
    rows = _mapping_sequence(value)
    present = {_text(item.get('redaction_id')) for item in rows}
    for missing in sorted(_REQUIRED_REDACTION_IDS.difference(present)):
        errors.append(f'missing redaction checklist placeholder: {missing}')
    for index, item in enumerate(rows):
        prefix = f'redaction_checklist_placeholders[{index}]'
        if item.get('status') != 'required_before_acceptance':
            errors.append(f'{prefix}.status must be required_before_acceptance')
        if item.get('reviewer_confirmation') is not None:
            errors.append(f'{prefix}.reviewer_confirmation must remain empty')


def _validate_action_boundaries(errors: list[str], value: Any) -> None:
    rows = _mapping_sequence(value)
    present = {_text(item.get('boundary_id')) for item in rows}
    for missing in sorted(_REQUIRED_BOUNDARY_IDS.difference(present)):
        errors.append(f'missing action-boundary reminder: {missing}')
    for index, item in enumerate(rows):
        prefix = f'action_boundary_reminders[{index}]'
        if not _text(item.get('statement')):
            errors.append(f'{prefix}.statement must be present')


def _validate_validation_commands(errors: list[str], value: Any) -> None:
    commands = _command_sequence(value)
    if not commands:
        return
    if commands != OFFLINE_VALIDATION_COMMANDS:
        errors.append('exact_offline_validation_commands must match the allowed offline validation command list')


def _validate_recursive_safety(errors: list[str], packet: Mapping[str, Any]) -> None:
    for path, value in _walk(packet):
        key = path.rsplit('.', 1)[-1].split('[', 1)[0]
        normalized_key = key.lower().replace('-', '_')
        if _allowed_boundary_path(path) or _allowed_redaction_placeholder_path(path):
            continue
        if _FORBIDDEN_KEY_RE.search(normalized_key) and _truthy_or_text(value):
            errors.append(f'{path} must not include private DevHub session, browser, screenshot, trace, HAR, raw, credential, or downloaded artifacts')
        if _MUTATION_KEY_RE.search(normalized_key) and _active_value(value):
            errors.append(f'{path} must not set active DevHub surface, guardrail, source, prompt, contract, or release-state mutation flags')
        if isinstance(value, str):
            stripped = value.strip()
            if _FORBIDDEN_VALUE_RE.search(stripped):
                errors.append(f'{path} must not reference private DevHub session, browser, screenshot, trace, HAR, raw, credential, or downloaded artifacts')
            if _LIVE_ACCESS_RE.search(value):
                errors.append(f'{path} must not claim live DevHub access or authenticated observation')
            if _AUTOMATED_LOGIN_RE.search(value):
                errors.append(f'{path} must not claim automated login, MFA, CAPTCHA, password, credential, OTP, or security-prompt handling')
            if _OFFICIAL_ACTION_RE.search(value):
                errors.append(f'{path} must not claim consequential official actions')
            if _GUARANTEE_RE.search(value):
                errors.append(f'{path} must not guarantee legal compliance, permit approval, or permitting outcomes')


def _required_str(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f'{key} must be a non-empty string')
    return value


def _required_list(data: Mapping[str, Any], key: str) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f'{key} must be a non-empty list')
    return value


def _non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _command_sequence(value: Any) -> list[list[str]]:
    if not isinstance(value, list):
        return []
    commands: list[list[str]] = []
    for command in value:
        if not isinstance(command, list) or not command:
            return []
        parts: list[str] = []
        for part in command:
            if not isinstance(part, str) or not part:
                return []
            parts.append(part)
        commands.append(parts)
    return commands


def _string_list(value: Any) -> set[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return set()
    return {item.strip() for item in value if isinstance(item, str) and item.strip()}


def _walk(value: Any, path: str = 'packet') -> list[tuple[str, Any]]:
    rows = [(path, value)]
    if isinstance(value, Mapping):
        for key, child in value.items():
            rows.extend(_walk(child, f'{path}.{key}'))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(_walk(child, f'{path}[{index}]'))
    return rows


def _allowed_boundary_path(path: str) -> bool:
    return '.action_boundary_reminders[' in path and path.endswith('.statement')


def _allowed_redaction_placeholder_path(path: str) -> bool:
    return '.redaction_checklist_placeholders[' in path and path.endswith('.redaction_id')


def _active_value(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in _ACTIVE_VALUES
    return False


def _truthy_or_text(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return bool(value.strip())
    return value is not None


def _text(value: Any) -> str:
    if value is None:
        return ''
    return str(value).strip()
