from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

from ppd.source_observation_patch_application_preview_v2 import (
    build_source_observation_patch_application_preview_v2_from_fixture,
    validate_source_observation_patch_application_preview_v2,
)
from ppd.validation.offline_patch_migration_approval_matrix_v2 import (
    validate_offline_patch_migration_approval_matrix_v2,
)

PACKET_TYPE = 'ppd.inactive_source_fixture_migration_packet.v2'
PACKET_VERSION = 2

REQUIRED_ATTESTATIONS = {
    'no_live_crawl': True,
    'no_download': True,
    'no_processor': True,
    'no_raw_body': True,
    'no_active_source_registry_mutation': True,
}

OFFLINE_VALIDATION_COMMANDS = [
    ['python3', '-m', 'py_compile', 'ppd/inactive_source_fixture_migration_packet_v2.py'],
    ['python3', '-m', 'pytest', 'ppd/tests/test_inactive_source_fixture_migration_packet_v2.py'],
    ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'],
]

_ALLOWED_URL_HOSTS = {
    'www.portland.gov',
    'portland.gov',
    'devhub.portlandoregon.gov',
    'www.portlandoregon.gov',
    'portlandoregon.gov',
    'www.portlandmaps.com',
    'portlandmaps.com',
}

_PROHIBITED_KEYS = {
    'archive_artifact',
    'archive_artifact_ref',
    'archive_path',
    'auth_state',
    'browser_artifact',
    'browser_context',
    'browser_storage_state',
    'body',
    'cookies',
    'download_path',
    'downloaded_document',
    'har',
    'har_path',
    'raw_archive',
    'raw_body',
    'raw_crawl',
    'raw_download',
    'raw_html',
    'raw_pdf',
    'response_body',
    'screenshot',
    'screenshot_path',
    'session_state',
    'storage_state',
    'trace',
    'trace_path',
}

_MUTATION_KEYS = {
    'active_agent_state_mutation',
    'active_guardrail_mutation',
    'active_monitoring_mutation',
    'active_process_mutation',
    'active_prompt_mutation',
    'active_release_state_mutation',
    'active_requirement_mutation',
    'active_schedule_mutation',
    'active_source_mutation',
    'active_source_registry_mutation',
    'agent_state_mutation',
    'guardrail_mutation',
    'monitoring_mutation',
    'process_mutation',
    'prompt_mutation',
    'release_state_mutation',
    'requirement_mutation',
    'schedule_mutation',
    'source_mutation',
    'source_registry_mutation_enabled',
}

_PROHIBITED_TEXT_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r'\bactive\s+(?:source|schedule|requirement|process|guardrail|prompt|monitoring|release[- ]state|agent[- ]state)\b.{0,80}\b(?:mutat|updated|promot|writ|replac)',
        r'\b(?:mutat|updated|promot|writ|replac)\b.{0,80}\bactive\s+(?:source|schedule|requirement|process|guardrail|prompt|monitoring|release[- ]state|agent[- ]state)\b',
        r'\b(?:live|public)\s+(?:crawl|crawler|recrawl)\s+(?:completed|finished|ran|succeeded)',
        r'\bprocessor\s+(?:completed|finished|ran|succeeded)',
        r'\braw\s+(?:body|html|pdf|crawl|download)\s+(?:persisted|stored|saved|captured)',
        r'\bdownloaded\s+(?:document|pdf|file)',
        r'\b(?:browser|session|trace|har|screenshot)\s+artifact',
        r'\bguarantee(?:d|s)?\s+(?:permit|approval|issuance|inspection|legal|outcome)',
        r'\b(?:permit|application|inspection)\s+(?:will|shall)\s+be\s+(?:approved|issued|accepted|granted)',
        r'\blegal\s+(?:advice|determination|conclusion|guarantee)',
    )
)

_AUTHENTICATED_URL_PATTERN = re.compile(
    r'/(?:login|sign[-_]?in|register|account|dashboard|my[-_]?permits|profile|checkout|payment|upload|submit)(?:/|$)',
    re.IGNORECASE,
)


def load_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'expected JSON object at {path}')
    return data


def build_inactive_source_fixture_migration_packet_v2_from_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    fixture = load_json(fixture_path)
    base = fixture_path.parent
    preview_fixture = base / _required_text(fixture, 'source_observation_patch_application_preview_v2_fixture')
    matrix_fixture = base / _required_text(fixture, 'offline_patch_migration_approval_matrix_v2_fixture')
    preview = build_source_observation_patch_application_preview_v2_from_fixture(preview_fixture)
    matrix = load_json(matrix_fixture)
    return build_inactive_source_fixture_migration_packet_v2(preview, matrix)


def build_inactive_source_fixture_migration_packet_v2(
    source_observation_patch_application_preview_v2: Mapping[str, Any],
    offline_patch_migration_approval_matrix_v2: Mapping[str, Any],
) -> dict[str, Any]:
    preview_result = validate_source_observation_patch_application_preview_v2(source_observation_patch_application_preview_v2)
    if not preview_result.ok:
        raise ValueError('invalid source observation patch application preview v2: ' + '; '.join(preview_result.errors))

    matrix_result = validate_offline_patch_migration_approval_matrix_v2(offline_patch_migration_approval_matrix_v2)
    if not matrix_result.ok:
        raise ValueError('invalid offline patch migration approval matrix v2: ' + '; '.join(error.code for error in matrix_result.errors))

    approval_rows = _approval_rows(offline_patch_migration_approval_matrix_v2)
    approved_rows = [row for row in approval_rows if _text(row.get('decision')).lower() == 'approve']
    if not approved_rows:
        raise ValueError('offline patch migration approval matrix v2 must include at least one approve row')

    previews = _dicts(source_observation_patch_application_preview_v2.get('source_registry_fixture_patch_previews'))
    patch_rows: list[dict[str, Any]] = []
    checksum_rows: list[dict[str, Any]] = []
    rollback_rows: list[dict[str, Any]] = []

    for preview_index, preview in enumerate(previews):
        source_id = _required_text(preview, 'source_id')
        reviewer_owner = _required_text(preview, 'reviewer_owner')
        citations = _dicts(preview.get('citations'))
        before_rows = _dicts(preview.get('before_metadata_rows'))
        after_rows = _dicts(preview.get('after_metadata_rows'))
        approval = approved_rows[preview_index % len(approved_rows)]
        approval_id = _row_id(approval, preview_index)

        for row_index, after_row in enumerate(after_rows):
            metadata_key = _required_text(after_row, 'metadata_key')
            before_row = _matching_before_row(before_rows, metadata_key)
            patch_row = {
                'patch_row_id': f'inactive-source-fixture-{_slug(source_id)}-{_slug(metadata_key)}',
                'source_id': source_id,
                'metadata_key': metadata_key,
                'before_metadata_value': _text(before_row.get('metadata_value')) or 'current_fixture_value_retained',
                'after_metadata_value': _required_text(after_row, 'metadata_value'),
                'row_state': 'inactive_fixture_only_source_registry_metadata_patch',
                'fixture_only': True,
                'active_source_registry_mutation': False,
                'source_registry_fixture_patch': True,
                'reviewer_owner': reviewer_owner,
                'approval_row_id': approval_id,
                'approval_decision': 'approve',
                'citations': _merge_citations(citations, _dicts(after_row.get('citations')), _citation_strings(approval)),
            }
            patch_rows.append(patch_row)
            checksum_rows.append(
                {
                    'checksum_id': f'checksum-{_slug(source_id)}-{_slug(metadata_key)}',
                    'source_id': source_id,
                    'metadata_key': metadata_key,
                    'before_fixture_checksum': _checksum(before_row),
                    'after_fixture_checksum': _checksum(after_row),
                    'patch_row_id': patch_row['patch_row_id'],
                    'reviewer_owner': reviewer_owner,
                    'citations': patch_row['citations'],
                }
            )
            if row_index == 0:
                rollback_rows.append(
                    {
                        'checkpoint_id': f'rollback-inactive-source-fixture-{_slug(source_id)}',
                        'source_id': source_id,
                        'summary': _required_text(preview, 'rollback_checkpoint'),
                        'rollback_action': 'discard_fixture_only_patch_rows_and_rebuild_from_source_preview',
                        'active_registry_unchanged': True,
                        'reviewer_owner': reviewer_owner,
                        'citations': citations,
                    }
                )

    packet = {
        'packet_type': PACKET_TYPE,
        'packet_version': PACKET_VERSION,
        'packet_id': 'inactive-source-fixture-migration-packet-v2',
        'mode': 'fixture_first_inactive_source_registry_metadata_patch_rows_only',
        'consumes': {
            'source_observation_patch_application_preview_v2': _text(source_observation_patch_application_preview_v2.get('preview_type')),
            'offline_patch_migration_approval_matrix_v2': 'offline_patch_migration_approval_matrix_v2',
        },
        'cited_fixture_only_source_registry_metadata_patch_rows': patch_rows,
        'before_after_fixture_checksums': checksum_rows,
        'rollback_checkpoints': rollback_rows,
        'reviewer_owner_fields': _reviewer_owner_fields(patch_rows),
        'offline_validation_commands': list(OFFLINE_VALIDATION_COMMANDS),
        'attestations': dict(REQUIRED_ATTESTATIONS),
    }
    validate_inactive_source_fixture_migration_packet_v2(packet)
    return packet


def validate_inactive_source_fixture_migration_packet_v2(packet: Mapping[str, Any]) -> None:
    if packet.get('packet_type') != PACKET_TYPE:
        raise ValueError(f'packet_type must be {PACKET_TYPE}')
    if packet.get('packet_version') != PACKET_VERSION:
        raise ValueError('packet_version must be 2')
    if packet.get('mode') != 'fixture_first_inactive_source_registry_metadata_patch_rows_only':
        raise ValueError('mode must be fixture_first_inactive_source_registry_metadata_patch_rows_only')
    if packet.get('attestations') != REQUIRED_ATTESTATIONS:
        raise ValueError('required no-live/no-download/no-processor/no-raw-body/no-active-source-registry-mutation attestations are missing')

    patch_rows = _dicts(packet.get('cited_fixture_only_source_registry_metadata_patch_rows'))
    checksum_rows = _dicts(packet.get('before_after_fixture_checksums'))
    rollback_rows = _dicts(packet.get('rollback_checkpoints'))
    owner_rows = _dicts(packet.get('reviewer_owner_fields'))
    commands = packet.get('offline_validation_commands')
    if not patch_rows:
        raise ValueError('cited fixture-only source-registry metadata patch rows must be non-empty')
    if not checksum_rows:
        raise ValueError('before/after fixture checksums must be non-empty')
    if not rollback_rows:
        raise ValueError('rollback checkpoints must be non-empty')
    if not owner_rows:
        raise ValueError('reviewer-owner fields must be non-empty')
    if not isinstance(commands, list) or not commands or not all(isinstance(command, list) and command for command in commands):
        raise ValueError('offline validation commands must be non-empty command arrays')

    patch_ids = {_required_text(row, 'patch_row_id') for row in patch_rows}
    checksum_patch_ids: set[str] = set()
    for index, row in enumerate(patch_rows):
        path = f'cited_fixture_only_source_registry_metadata_patch_rows[{index}]'
        for field in ('source_id', 'metadata_key', 'after_metadata_value', 'reviewer_owner', 'approval_row_id'):
            if not _text(row.get(field)):
                raise ValueError(f'{path}.{field} must be present')
        if row.get('fixture_only') is not True:
            raise ValueError(f'{path}.fixture_only must be true')
        if row.get('source_registry_fixture_patch') is not True:
            raise ValueError(f'{path}.source_registry_fixture_patch must be true')
        if row.get('active_source_registry_mutation') is not False:
            raise ValueError(f'{path}.active_source_registry_mutation must be false')
        if not _citations(row):
            raise ValueError(f'{path}.citations must be non-empty')

    for index, row in enumerate(checksum_rows):
        path = f'before_after_fixture_checksums[{index}]'
        patch_row_id = _text(row.get('patch_row_id'))
        if patch_row_id not in patch_ids:
            raise ValueError(f'{path}.patch_row_id must reference a patch row')
        checksum_patch_ids.add(patch_row_id)
        for field in ('before_fixture_checksum', 'after_fixture_checksum'):
            checksum = _text(row.get(field))
            if len(checksum) != 64 or not all(char in '0123456789abcdef' for char in checksum.lower()):
                raise ValueError(f'{path}.{field} must be a sha256 hex checksum')
        if not _citations(row):
            raise ValueError(f'{path}.citations must be non-empty')
    missing_checksum_ids = sorted(patch_ids - checksum_patch_ids)
    if missing_checksum_ids:
        raise ValueError('before/after fixture checksums must cover every source fixture row: ' + ', '.join(missing_checksum_ids))

    for index, row in enumerate(rollback_rows):
        path = f'rollback_checkpoints[{index}]'
        if row.get('active_registry_unchanged') is not True:
            raise ValueError(f'{path}.active_registry_unchanged must be true')
        if not _text(row.get('checkpoint_id')) or not _text(row.get('summary')):
            raise ValueError(f'{path} must include checkpoint_id and summary')
        if not _citations(row):
            raise ValueError(f'{path}.citations must be non-empty')

    for index, row in enumerate(owner_rows):
        if not _citations(row):
            raise ValueError(f'reviewer_owner_fields[{index}].citations must be non-empty')

    _reject_unsafe_content(packet, '$')


def _approval_rows(matrix: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = matrix.get('approval_rows') or matrix.get('approvals') or matrix.get('rows') or matrix.get('matrix')
    if isinstance(rows, Sequence) and not isinstance(rows, (str, bytes, bytearray)):
        return [row for row in rows if isinstance(row, Mapping)]
    return []


def _matching_before_row(before_rows: list[dict[str, Any]], metadata_key: str) -> Mapping[str, Any]:
    for row in before_rows:
        if _text(row.get('metadata_key')) == metadata_key:
            return row
    return before_rows[0] if before_rows else {'metadata_value': 'current_fixture_value_retained'}


def _reviewer_owner_fields(patch_rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for patch_row in patch_rows:
        key = (_text(patch_row.get('reviewer_owner')), _text(patch_row.get('source_id')))
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                'owner_field_id': f'owner-{_slug(key[0])}-{_slug(key[1])}',
                'reviewer_owner': key[0],
                'source_id': key[1],
                'patch_row_ids': [row['patch_row_id'] for row in patch_rows if _text(row.get('reviewer_owner')) == key[0] and _text(row.get('source_id')) == key[1]],
                'citations': _citations(patch_row),
            }
        )
    return rows


def _merge_citations(*groups: Any) -> list[Any]:
    merged: list[Any] = []
    seen: set[str] = set()
    for group in groups:
        values = group if isinstance(group, list) else [group]
        for value in values:
            if value in (None, '', [], {}):
                continue
            marker = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
            if marker not in seen:
                seen.add(marker)
                merged.append(value)
    return merged


def _citation_strings(row: Mapping[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ('citations', 'citation_ids', 'source_evidence_ids', 'evidence', 'source_refs'):
        value = row.get(key)
        if isinstance(value, list):
            values.extend(str(item) for item in value if str(item).strip())
        elif isinstance(value, str) and value.strip():
            values.append(value.strip())
    return values


def _citations(row: Mapping[str, Any]) -> list[Any]:
    value = row.get('citations')
    return value if isinstance(value, list) and value else []


def _row_id(row: Mapping[str, Any], index: int) -> str:
    for key in ('approval_row_id', 'row_id', 'id'):
        value = _text(row.get(key))
        if value:
            return value
    return f'approval-row-{index + 1}'


def _checksum(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def _reject_unsafe_content(value: Any, path: str) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f'{path}.{key}'
            normalized = _normalize_key(key)
            if normalized in _PROHIBITED_KEYS and child not in (None, '', [], {}, False):
                raise ValueError(f'{child_path} is prohibited raw/download/archive/browser artifact content')
            if normalized in _MUTATION_KEYS and child not in (None, '', [], {}, False):
                raise ValueError(f'{child_path} contains an active source, schedule, requirement, process, guardrail, prompt, monitoring, release-state, or agent-state mutation flag')
            if normalized == 'mutation_flags':
                _reject_mutation_flags(child, child_path)
            _reject_unsafe_content(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_unsafe_content(child, f'{path}[{index}]')
    elif isinstance(value, str):
        _reject_unsafe_text(value, path)
        _reject_unsafe_url(value, path)


def _reject_mutation_flags(value: Any, path: str) -> None:
    if not isinstance(value, Mapping):
        return
    blocked = {
        'source',
        'source_registry',
        'schedule',
        'requirement',
        'process',
        'guardrail',
        'prompt',
        'monitoring',
        'release_state',
        'agent_state',
        'active_source',
        'active_schedule',
        'active_requirement',
        'active_process',
        'active_guardrail',
        'active_prompt',
        'active_monitoring',
        'active_release_state',
        'active_agent_state',
    }
    for key, child in value.items():
        normalized = _normalize_key(key)
        if normalized in blocked and child not in (None, '', [], {}, False):
            raise ValueError(f'{path}.{key} contains an active source, schedule, requirement, process, guardrail, prompt, monitoring, release-state, or agent-state mutation flag')


def _reject_unsafe_text(value: str, path: str) -> None:
    for pattern in _PROHIBITED_TEXT_PATTERNS:
        if pattern.search(value):
            raise ValueError(f'{path} contains prohibited live, processor, raw-artifact, legal outcome guarantee, or active mutation language')


def _reject_unsafe_url(value: str, path: str) -> None:
    parsed = urlparse(value.strip())
    if parsed.scheme not in {'http', 'https'}:
        return
    host = (parsed.hostname or '').lower()
    if host not in _ALLOWED_URL_HOSTS:
        raise ValueError(f'{path} contains non-allowlisted URL host: {host}')
    combined = parsed.path + ('?' + parsed.query if parsed.query else '')
    if _AUTHENTICATED_URL_PATTERN.search(combined) or re.search(r'\b(?:token|session|auth|password|credential|mfa)=', parsed.query, re.IGNORECASE):
        raise ValueError(f'{path} contains authenticated or account-scoped URL')


def _normalize_key(key: Any) -> str:
    return str(key).strip().lower().replace('-', '_').replace(' ', '_')


def _dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ''


def _required_text(mapping: Mapping[str, Any], key: str) -> str:
    value = _text(mapping.get(key))
    if not value:
        raise ValueError(f'{key} must be present')
    return value


def _slug(value: str) -> str:
    cleaned = ''.join(char.lower() if char.isalnum() else '-' for char in value)
    return '-'.join(part for part in cleaned.split('-') if part) or 'item'
