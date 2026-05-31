from __future__ import annotations

import copy
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

PACKET_TYPE = 'ppd.release_readiness_decision_packet.v3'
MODE = 'fixture-first-offline-only'
VALIDATION_COMMANDS = [
    ['python3', '-m', 'py_compile', 'ppd/agent_readiness/release_readiness_decision_packet_v3.py'],
    ['python3', '-m', 'pytest', 'ppd/tests/test_release_readiness_decision_packet_v3.py'],
    ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'],
]

_REQUIRED_SECTIONS = {
    'gate_recommendations': 'missing_gate_recommendations',
    'agent_readiness_replay_references': 'missing_agent_readiness_replay_references',
    'devhub_observation_holds': 'missing_devhub_observation_holds',
    'public_refresh_impact_references': 'missing_public_refresh_impact_references',
    'reviewer_dispositions': 'missing_reviewer_dispositions',
    'rollback_notes': 'missing_rollback_notes',
}
_ALLOWED_RECOMMENDATIONS = {'hold', 'reject', 'needs_review'}
_ALLOWED_DISPOSITIONS = {'hold', 'blocked', 'needs_review', 'approved_for_offline_hold'}
_MUTATION_FIELD_RE = re.compile(r'(^|_)(active_)?(artifact|browser|crawl|devhub|fixture|guardrail|prompt|release_state|agent_state)_(mutation|mutating|update|write|promotion|refresh)(_|$)|(^|_)(mutates|updates|promotes|refreshes|writes)_(artifacts|browser|crawl|devhub|fixtures|guardrails|prompts|release_state|agent_state)(_|$)', re.IGNORECASE)
_PRIVATE_FIELD_RE = re.compile(r'(auth[_-]?state|browser[_-]?(artifact|state)?|cookie|credential|download(ed)?|har|private|raw[_-]?(artifact|body|capture|crawl|data|download|html|pdf)?|screenshot|session[_-]?(artifact|state|storage)?|storage[_-]?state|token|trace)', re.IGNORECASE)
_PRIVATE_TEXT_RE = re.compile(r'(^file://)|(^/home/[^/]+/)|(^/Users/[^/]+/)|(^/tmp/)|(auth[_ -]?state|browser[_ -]?(artifact|state)|cookie|credential|downloaded[_ -]?(artifact|document|file|pdf)|har\b|password|private[_ -]?(artifact|file|path|value)|raw[_ -]?(artifact|body|capture|crawl|data|download|html|pdf)|screenshot|session[_ -]?(artifact|state|storage)|storage[_ -]?state|token|trace[_ -]?(file|zip)?)', re.IGNORECASE)
_OFFICIAL_ACTION_RE = re.compile(r'\b(official action (completed|performed)|submitted|submission completed|paid (the )?fee|payment completed|scheduled (an? )?inspection|cancelled (an? )?inspection|canceled (an? )?inspection|certified (the )?application|uploaded (corrections|plans|documents))\b', re.IGNORECASE)
_LIVE_CLAIM_RE = re.compile(r'\b(live crawl|live devhub|live browser|live run|live execution|ran live|performed live|accessed devhub|logged in to devhub|used authenticated session|devhub claim verified live)\b', re.IGNORECASE)
_GUARANTEE_RE = re.compile(r'\b(guaranteed approval|guaranteed issuance|permit will be approved|permit will be issued|approval is guaranteed|issuance is guaranteed|legal advice|legal guarantee|permitting guarantee)\b', re.IGNORECASE)
_PROMOTION_RE = re.compile(r'\b(release promoted|promotion completed|promoted to active|promoted fixtures|production release complete|active release enabled|ready to promote now)\b', re.IGNORECASE)
_COMMAND_FORBIDDEN_RE = re.compile(r'\b(live|crawl|devhub|playwright|browser|network|auth|session|promote)\b', re.IGNORECASE)


def build_release_readiness_decision_packet_v3(source_packet: Mapping[str, Any]) -> dict[str, Any]:
    source = copy.deepcopy(dict(source_packet))
    _raise_for_unsafe_content(source)
    packet = {
        'packet_type': PACKET_TYPE,
        'packet_id': str(source.get('packet_id') or 'release-readiness-decision-packet-v3'),
        'mode': MODE,
        'decision': 'hold-no-promotion',
        'gate_recommendations': copy.deepcopy(source.get('gate_recommendations', [])),
        'agent_readiness_replay_references': copy.deepcopy(source.get('agent_readiness_replay_references', [])),
        'devhub_observation_holds': copy.deepcopy(source.get('devhub_observation_holds', [])),
        'public_refresh_impact_references': copy.deepcopy(source.get('public_refresh_impact_references', [])),
        'reviewer_dispositions': copy.deepcopy(source.get('reviewer_dispositions', [])),
        'rollback_notes': copy.deepcopy(source.get('rollback_notes', [])),
        'validation_commands': copy.deepcopy(source.get('validation_commands', VALIDATION_COMMANDS)),
        'non_mutation_attestations': {
            'active_mutation_flags_present': False,
            'promotes_release': False,
            'performs_official_actions': False,
            'uses_live_crawl': False,
            'uses_live_devhub': False,
            'stores_private_or_raw_artifacts': False,
        },
    }
    assert_valid_release_readiness_decision_packet_v3(packet)
    return packet


def validate_release_readiness_decision_packet_v3(packet: Mapping[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if packet.get('packet_type') != PACKET_TYPE:
        _issue(issues, 'invalid_packet_type', 'packet_type', f'packet_type must be {PACKET_TYPE}')
    if packet.get('mode') != MODE:
        _issue(issues, 'invalid_mode', 'mode', f'mode must be {MODE}')
    if packet.get('decision') != 'hold-no-promotion':
        _issue(issues, 'invalid_decision', 'decision', 'decision must remain hold-no-promotion')
    for field, code in _REQUIRED_SECTIONS.items():
        rows = packet.get(field)
        if not isinstance(rows, list) or not rows:
            _issue(issues, code, field, f'{field} must be a non-empty list')
        else:
            _validate_section(field, rows, issues)
    commands = packet.get('validation_commands')
    if not isinstance(commands, list) or not commands:
        _issue(issues, 'missing_validation_commands', 'validation_commands', 'validation_commands must be a non-empty list of argv lists')
    else:
        for index, command in enumerate(commands):
            _validate_command(command, f'validation_commands[{index}]', issues)
    _validate_attestations(packet.get('non_mutation_attestations'), issues)
    _scan_for_unsafe_content(packet, '', issues)
    return issues


def assert_valid_release_readiness_decision_packet_v3(packet: Mapping[str, Any]) -> None:
    issues = validate_release_readiness_decision_packet_v3(packet)
    if issues:
        formatted = '; '.join(f"{issue['code']} at {issue['path']}" for issue in issues)
        raise ValueError(f'release readiness decision packet v3 validation failed: {formatted}')


def _validate_section(field: str, rows: Sequence[Any], issues: list[dict[str, str]]) -> None:
    for index, row in enumerate(rows):
        path = f'{field}[{index}]'
        if not isinstance(row, Mapping):
            _issue(issues, 'invalid_section_row', path, 'section rows must be objects')
            continue
        source_ids = row.get('source_evidence_ids')
        if not isinstance(source_ids, list) or not all(_text(item) for item in source_ids):
            _issue(issues, 'missing_source_evidence_ids', f'{path}.source_evidence_ids', 'row requires cited source_evidence_ids')
        if field == 'gate_recommendations' and (not _text(row.get('gate_id')) or row.get('recommendation') not in _ALLOWED_RECOMMENDATIONS):
            _issue(issues, 'invalid_gate_recommendation', path, 'gate recommendation requires gate_id and hold-style recommendation')
        elif field == 'agent_readiness_replay_references' and (not _text(row.get('replay_id')) or not _text(row.get('packet_ref'))):
            _issue(issues, 'invalid_agent_readiness_replay_reference', path, 'agent-readiness replay reference requires replay_id and packet_ref')
        elif field == 'devhub_observation_holds' and (row.get('status') != 'hold' or not _text(row.get('reason'))):
            _issue(issues, 'invalid_devhub_observation_hold', path, 'DevHub observation hold requires hold status and reason')
        elif field == 'public_refresh_impact_references' and (not _text(row.get('impact_id')) or not _text(row.get('packet_ref'))):
            _issue(issues, 'invalid_public_refresh_impact_reference', path, 'public refresh impact reference requires impact_id and packet_ref')
        elif field == 'reviewer_dispositions' and (not _text(row.get('reviewer_id')) or row.get('disposition') not in _ALLOWED_DISPOSITIONS):
            _issue(issues, 'invalid_reviewer_disposition', path, 'reviewer disposition requires reviewer_id and hold-style disposition')
        elif field == 'rollback_notes' and (not _text(row.get('rollback_note_id')) or not _text(row.get('note'))):
            _issue(issues, 'invalid_rollback_note', path, 'rollback note requires rollback_note_id and note')


def _validate_command(command: Any, path: str, issues: list[dict[str, str]]) -> None:
    if not isinstance(command, list) or not command or not all(isinstance(part, str) and part.strip() for part in command):
        _issue(issues, 'invalid_validation_command', path, 'validation command must be a non-empty argv string list')
        return
    if _COMMAND_FORBIDDEN_RE.search(' '.join(command)):
        _issue(issues, 'unsafe_validation_command', path, 'validation command must stay offline and must not invoke live, crawl, DevHub, browser, auth, session, network, or promotion workflows')


def _validate_attestations(value: Any, issues: list[dict[str, str]]) -> None:
    if not isinstance(value, Mapping):
        _issue(issues, 'missing_non_mutation_attestations', 'non_mutation_attestations', 'non-mutation attestations are required')
        return
    for key in ('active_mutation_flags_present', 'promotes_release', 'performs_official_actions', 'uses_live_crawl', 'uses_live_devhub', 'stores_private_or_raw_artifacts'):
        if value.get(key) is not False:
            _issue(issues, 'active_mutation_flag', f'non_mutation_attestations.{key}', 'release readiness decision packet v3 requires false safety attestation flags')


def _raise_for_unsafe_content(value: Any) -> None:
    issues: list[dict[str, str]] = []
    _scan_for_unsafe_content(value, '', issues)
    if issues:
        formatted = '; '.join(f"{issue['code']} at {issue['path']}" for issue in issues)
        raise ValueError(f'unsafe release readiness decision packet v3 source content: {formatted}')


def _scan_for_unsafe_content(value: Any, path: str, issues: list[dict[str, str]]) -> None:
    for child_path, child in _walk(value, path):
        name = _path_name(child_path).lower().replace('-', '_')
        if name and _MUTATION_FIELD_RE.search(name) and _active_value(child):
            _issue(issues, 'active_mutation_flag', child_path, 'active mutation flags are not allowed')
        if name and not name.startswith('no_') and _PRIVATE_FIELD_RE.search(name) and _present_value(child):
            _issue(issues, 'private_or_raw_artifact_field', child_path, 'private, session, browser, raw, or downloaded artifacts are not allowed')
        if isinstance(child, str):
            if _PRIVATE_TEXT_RE.search(child):
                _issue(issues, 'private_or_raw_artifact_text', child_path, 'private, session, browser, raw, or downloaded artifact text is not allowed')
            if _OFFICIAL_ACTION_RE.search(child):
                _issue(issues, 'official_action_completion_claim', child_path, 'official-action completion claims are not allowed')
            if _LIVE_CLAIM_RE.search(child):
                _issue(issues, 'live_crawl_or_devhub_claim', child_path, 'live crawl or DevHub claims are not allowed')
            if _GUARANTEE_RE.search(child):
                _issue(issues, 'legal_or_permitting_guarantee', child_path, 'legal or permitting guarantees are not allowed')
            if _PROMOTION_RE.search(child):
                _issue(issues, 'release_promotion_claim', child_path, 'release promotion claims are not allowed')


def _walk(value: Any, path: str) -> Iterable[tuple[str, Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = str(key) if not path else f'{path}.{key}'
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f'{path}[{index}]')


def _path_name(path: str) -> str:
    return '' if not path else path.rsplit('.', 1)[-1].split('[', 1)[0]


def _active_value(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {'1', 'active', 'enabled', 'true', 'yes'}
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, list):
        return bool(value)
    return False


def _present_value(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, list):
        return bool(value)
    return True


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ''


def _issue(issues: list[dict[str, str]], code: str, path: str, message: str) -> None:
    issues.append({'code': code, 'path': path, 'message': message})


def load_json_object(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('JSON root must be an object')
    return data
