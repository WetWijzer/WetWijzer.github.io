"""Fixture-first public source refresh metadata intake packets.

This module consumes a launch rehearsal transcript packet and committed
synthetic metadata-only capture records. It never fetches URLs, downloads
source documents, invokes processors, writes registries, or mutates schedules.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ppd.public_source_refresh_launch_rehearsal_transcript_packet import (
    PACKET_TYPE as LAUNCH_REHEARSAL_PACKET_TYPE,
    require_public_source_refresh_launch_rehearsal_transcript_packet,
)

PACKET_TYPE = 'ppd.public_source_refresh_metadata_intake_packet.v1'
REQUIRED_ATTESTATIONS = (
    'no-raw-body',
    'no-download',
    'no-processor',
    'no-registry-mutation',
    'no-schedule-mutation',
)
ALLOWED_HOSTS = {
    'www.portland.gov',
    'devhub.portlandoregon.gov',
    'www.portlandoregon.gov',
    'www.portlandmaps.com',
}
INTAKE_STATUSES = {'accepted_metadata_only', 'skipped_metadata_only', 'needs_reviewer_resolution'}
STATUS_REQUIRED_METADATA_FIELDS = (
    'intake_id',
    'source_batch_id',
    'source_id',
    'canonical_url',
    'intake_status',
    'freshness_status',
    'reviewer_owner',
    'citation_refs',
    'metadata_only',
)
SUMMARY_REQUIRED_METADATA_FIELDS = (
    'summary_id',
    'source_batch_id',
    'source_id',
    'canonical_url',
    'requested_url',
    'final_url',
    'redirect_chain',
    'redirect_count',
    'content_hash_status',
    'content_type',
    'citation_refs',
)
FRESHNESS_REQUIRED_METADATA_FIELDS = (
    'signal_id',
    'source_batch_id',
    'source_id',
    'canonical_url',
    'checked_at',
    'freshness_status',
    'hash_changed',
    'requires_reviewer_review',
    'citation_refs',
    'reviewer_owner',
)
UNSAFE_TRUE_FLAGS = {
    'archive_artifact_written',
    'document_downloaded',
    'download_allowed',
    'downloaded_documents',
    'live_fetch_allowed',
    'live_fetch_performed',
    'processor_invocation_allowed',
    'processor_invoked',
    'raw_body_persisted',
    'registry_mutated',
    'registry_mutation_allowed',
    'schedule_mutated',
    'schedule_mutation_allowed',
}
UNSAFE_TRUE_FLAG_TOKENS = {
    'activeguardrailmutation',
    'activeguardrailmutationflag',
    'activemonitoringmutation',
    'activemonitoringmutationflag',
    'activeregistrymutation',
    'activeregistrymutationflag',
    'activereleasestatemutation',
    'activereleasestatemutationflag',
    'activerequirementmutation',
    'activerequirementmutationflag',
    'activeschedulemutation',
    'activeschedulemutationflag',
    'activesourceregistrymutation',
    'activesourceregistrymutationflag',
    'archiveartifactwritten',
    'crawlerexecuted',
    'documentdownloaded',
    'documentsdownloaded',
    'downloadallowed',
    'downloadeddocuments',
    'freshnessmonitoringmutated',
    'guardrailmutated',
    'guardrailmutationallowed',
    'livecrawlexecuted',
    'livecrawlerexecuted',
    'livefetchallowed',
    'livefetchperformed',
    'monitoringmutated',
    'monitoringmutationallowed',
    'processorinvocationallowed',
    'processorinvoked',
    'rawbodypersisted',
    'registriesmutated',
    'registrymutated',
    'registrymutationallowed',
    'releasestatemutated',
    'releasestatemutationallowed',
    'requirementmutated',
    'requirementmutationallowed',
    'schedulemutated',
    'schedulemutationallowed',
    'sourceregistrymutated',
    'sourceregistrymutationallowed',
}
RAW_KEYS = {
    'archive_artifact_ref',
    'download_path',
    'download_ref',
    'raw_body',
    'raw_body_path',
    'raw_body_ref',
    'response_body',
    'warc_ref',
}
RAW_KEY_TOKENS = {
    'archiveartifactref',
    'archiveartifacturi',
    'archiveref',
    'bodyref',
    'downloadpath',
    'downloadref',
    'downloaduri',
    'rawbody',
    'rawbodypath',
    'rawbodyref',
    'rawhtml',
    'responsebody',
    'warcref',
}
PRIVATE_KEY_TOKENS = {
    'authstate',
    'browserstorage',
    'cookie',
    'cookies',
    'credential',
    'harref',
    'localstorage',
    'password',
    'privateartifact',
    'screenshotref',
    'sessionartifact',
    'sessioncookie',
    'storagepath',
    'storagestate',
    'traceref',
}
RAW_MARKERS = (
    'archive-artifacts/',
    'archive_artifacts/',
    'downloaded-documents/',
    'downloaded_documents/',
    'raw-artifacts/',
    'raw_artifacts/',
    'raw_body',
    'raw-body',
    'warc://',
    '.warc',
)
PRIVATE_MARKERS = (
    'auth_state',
    'cookies.json',
    'credential',
    'har.zip',
    'localstorage.json',
    'password',
    'session_cookie',
    'storage_state',
    'trace.zip',
)
LEGAL_OR_PERMIT_GUARANTEE_MARKERS = (
    'approval guaranteed',
    'guaranteed approval',
    'guaranteed permit',
    'guarantees approval',
    'guarantees issuance',
    'guarantees permit',
    'issuance guaranteed',
    'legal conclusion',
    'permit guaranteed',
    'permit will be approved',
    'permit will be issued',
    'will be approved by pp&d',
    'will be issued by pp&d',
    'will pass inspection',
)
AUTH_URL_MARKERS = (
    '/account',
    '/admin',
    '/auth',
    '/checkout',
    '/dashboard',
    '/login',
    '/my-permits',
    '/oauth',
    '/payment',
    '/register',
    '/sign-in',
    '/signin',
)


@dataclass(frozen=True)
class PublicSourceRefreshMetadataIntakeValidationResult:
    ready: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {'ready': self.ready, 'problems': list(self.problems)}


class PublicSourceRefreshMetadataIntakePacketError(ValueError):
    pass


def load_fixture_packet(path: str | Path) -> dict[str, Any]:
    with Path(path).open('r', encoding='utf-8') as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ValueError('fixture packet must contain a JSON object')
    return loaded


def build_public_source_refresh_metadata_intake_packet(inputs: Mapping[str, Any]) -> dict[str, Any]:
    input_problems: list[str] = []
    _collect_unsafe_content(inputs, 'inputs', input_problems)
    if input_problems:
        raise PublicSourceRefreshMetadataIntakePacketError('unsafe_public_source_refresh_metadata_intake_inputs: ' + '; '.join(sorted(set(input_problems))))

    transcript = _required_mapping(inputs, 'public_source_refresh_launch_rehearsal_transcript_packet')
    require_public_source_refresh_launch_rehearsal_transcript_packet(transcript)
    captures = _mapping_sequence(inputs.get('synthetic_metadata_only_capture_records'))
    if not captures:
        raise PublicSourceRefreshMetadataIntakePacketError('synthetic_metadata_only_capture_records must be non-empty')

    transcript_id = _packet_id(transcript)
    placeholders = {
        _text(row.get('source_batch_id')): row
        for row in _mapping_sequence(transcript.get('expected_metadata_only_result_placeholders'))
        if _text(row.get('source_batch_id'))
    }
    owners = _mapping(transcript.get('reviewer_owner_fields'))
    intake_statuses = []
    summaries = []
    skipped = []
    freshness = []

    for index, capture in enumerate(captures, start=1):
        source_batch_id = _text(capture.get('source_batch_id')) or f'source-batch-{index}'
        source_id = _text(capture.get('source_id')) or source_batch_id
        canonical_url = _text(capture.get('canonical_url') or capture.get('source_url'))
        placeholder = placeholders.get(source_batch_id, {})
        status = _intake_status(capture, bool(placeholder))
        citations = _text_list(capture.get('citation_refs')) or _text_list(placeholder.get('citation_refs')) or [transcript_id]
        reviewer_owner = _text(capture.get('reviewer_owner')) or _text(owners.get('rehearsal_reviewer'))
        skipped_reason = _text(capture.get('skipped_reason'))

        intake_statuses.append(
            {
                'intake_id': 'metadata-intake-' + _stable_token(source_batch_id),
                'source_batch_id': source_batch_id,
                'source_id': source_id,
                'canonical_url': canonical_url,
                'intake_status': status,
                'skipped_reason': skipped_reason,
                'freshness_status': _text(capture.get('freshness_status')),
                'reviewer_owner': reviewer_owner,
                'citation_refs': citations,
                'metadata_only': True,
                'raw_body_persisted': False,
                'document_downloaded': False,
                'processor_invoked': False,
                'registry_mutated': False,
                'schedule_mutated': False,
            }
        )
        summaries.append(
            {
                'summary_id': 'redirect-hash-content-type-' + _stable_token(source_batch_id),
                'source_batch_id': source_batch_id,
                'source_id': source_id,
                'canonical_url': canonical_url,
                'requested_url': _text(capture.get('requested_url'), canonical_url),
                'final_url': _text(capture.get('final_url'), canonical_url),
                'redirect_chain': _text_list(capture.get('redirect_chain')) or [canonical_url],
                'redirect_count': max(0, len(_text_list(capture.get('redirect_chain'))) - 1),
                'http_status': capture.get('http_status'),
                'content_hash': _text(capture.get('content_hash')),
                'content_hash_status': 'present' if _text(capture.get('content_hash')) else 'not_captured',
                'content_type': _text(capture.get('content_type')) or 'not_captured',
                'citation_refs': citations,
            }
        )
        if status == 'skipped_metadata_only':
            skipped.append(
                {
                    'source_batch_id': source_batch_id,
                    'source_id': source_id,
                    'canonical_url': canonical_url,
                    'skipped_reason': skipped_reason or 'metadata_only_capture_skipped',
                    'citation_refs': citations,
                    'reviewer_owner': reviewer_owner,
                }
            )
        freshness.append(
            {
                'signal_id': 'freshness-signal-' + _stable_token(source_batch_id),
                'source_batch_id': source_batch_id,
                'source_id': source_id,
                'canonical_url': canonical_url,
                'checked_at': _text(capture.get('checked_at')),
                'freshness_status': _text(capture.get('freshness_status')) or 'unknown',
                'previous_content_hash': _text(capture.get('previous_content_hash')),
                'current_content_hash': _text(capture.get('content_hash')),
                'hash_changed': _hash_changed(capture),
                'requires_reviewer_review': status != 'accepted_metadata_only' or _hash_changed(capture),
                'citation_refs': citations,
                'reviewer_owner': reviewer_owner,
            }
        )

    packet = {
        'packet_type': PACKET_TYPE,
        'packet_id': _text(inputs.get('packet_id')) or 'public-source-refresh-metadata-intake-fixture',
        'fixture_first': True,
        'metadata_only': True,
        'consumed_packets': [
            {
                'kind': 'public_source_refresh_launch_rehearsal_transcript_packet',
                'packet_id': transcript_id,
                'packet_type': _text(transcript.get('packet_type')),
                'citation_ref': transcript_id,
            }
        ],
        'per_source_intake_statuses': intake_statuses,
        'redirect_hash_content_type_summaries': summaries,
        'skipped_source_reasons': skipped,
        'freshness_signals': freshness,
        'reviewer_owner_fields': {
            'intake_owner': _text(owners.get('launch_owner')) or 'ppd-public-source-refresh-intake-owner',
            'intake_reviewer': _text(owners.get('rehearsal_reviewer')) or 'ppd-public-source-refresh-intake-reviewer',
            'freshness_owner': _text(owners.get('monitoring_owner')) or 'ppd-public-source-refresh-freshness-owner',
        },
        'attestations': {
            'no-raw-body': True,
            'no-download': True,
            'no-processor': True,
            'no-registry-mutation': True,
            'no-schedule-mutation': True,
        },
        'execution_boundaries': {
            'raw_body_persistence_allowed': False,
            'download_allowed': False,
            'processor_invocation_allowed': False,
            'registry_mutation_allowed': False,
            'schedule_mutation_allowed': False,
        },
    }
    require_public_source_refresh_metadata_intake_packet(packet)
    return packet


def validate_public_source_refresh_metadata_intake_packet(packet: Mapping[str, Any]) -> PublicSourceRefreshMetadataIntakeValidationResult:
    problems: list[str] = []
    if packet.get('packet_type') != PACKET_TYPE:
        problems.append(f'packet_type must be {PACKET_TYPE}')
    if packet.get('fixture_first') is not True:
        problems.append('fixture_first must be true')
    if packet.get('metadata_only') is not True:
        problems.append('metadata_only must be true')

    consumed = _mapping_sequence(packet.get('consumed_packets'))
    if not any(row.get('packet_type') == LAUNCH_REHEARSAL_PACKET_TYPE and _text(row.get('citation_ref')) for row in consumed):
        problems.append('consumed_packets must cite the launch rehearsal transcript packet')

    statuses = _mapping_sequence(packet.get('per_source_intake_statuses'))
    summaries = _mapping_sequence(packet.get('redirect_hash_content_type_summaries'))
    freshness = _mapping_sequence(packet.get('freshness_signals'))
    if not statuses:
        problems.append('per_source_intake_statuses must be non-empty')
    if len(summaries) != len(statuses):
        problems.append('redirect_hash_content_type_summaries must match intake status count')
    if len(freshness) != len(statuses):
        problems.append('freshness_signals must match intake status count')

    status_batches = set()
    skipped_status_batches = set()
    for index, row in enumerate(statuses):
        path = f'per_source_intake_statuses[{index}]'
        _require_fields(row, STATUS_REQUIRED_METADATA_FIELDS, path, problems)
        batch = _require_source_row(row, path, problems)
        if batch:
            status_batches.add(batch)
        if row.get('intake_status') not in INTAKE_STATUSES:
            problems.append(f'{path}.intake_status is invalid')
        if row.get('metadata_only') is not True:
            problems.append(f'{path}.metadata_only must be true')
        if row.get('intake_status') == 'skipped_metadata_only':
            skipped_status_batches.add(batch)
            if not _text(row.get('skipped_reason')):
                problems.append(f'{path}.skipped_reason is required for skipped sources')
        if not _text(row.get('reviewer_owner')):
            problems.append(f'{path}.reviewer_owner is required')
        if not _text(row.get('freshness_status')):
            problems.append(f'{path}.freshness_status is required')
        _require_false_flags(row, path, ('raw_body_persisted', 'document_downloaded', 'processor_invoked', 'registry_mutated', 'schedule_mutated'), problems)

    summary_batches = set()
    for index, row in enumerate(summaries):
        path = f'redirect_hash_content_type_summaries[{index}]'
        _require_fields(row, SUMMARY_REQUIRED_METADATA_FIELDS, path, problems)
        batch = _require_source_row(row, path, problems)
        if batch:
            summary_batches.add(batch)
            if batch not in status_batches:
                problems.append(f'{path}.source_batch_id does not match an intake status')
        if not _text(row.get('content_type')):
            problems.append(f'{path}.content_type is required')
        if row.get('content_hash_status') not in {'present', 'not_captured'}:
            problems.append(f'{path}.content_hash_status is invalid')
        if row.get('content_hash_status') == 'present' and not _text(row.get('content_hash')):
            problems.append(f'{path}.content_hash is required when content_hash_status is present')
        if not isinstance(row.get('redirect_chain'), Sequence) or isinstance(row.get('redirect_chain'), (str, bytes, bytearray)):
            problems.append(f'{path}.redirect_chain must be a list')

    freshness_batches = set()
    for index, row in enumerate(freshness):
        path = f'freshness_signals[{index}]'
        _require_fields(row, FRESHNESS_REQUIRED_METADATA_FIELDS, path, problems)
        batch = _require_source_row(row, path, problems)
        if batch:
            freshness_batches.add(batch)
            if batch not in status_batches:
                problems.append(f'{path}.source_batch_id does not match an intake status')
        if not _text(row.get('freshness_status')):
            problems.append(f'{path}.freshness_status is required')
        if not _text(row.get('checked_at')):
            problems.append(f'{path}.checked_at is required')
        if not isinstance(row.get('hash_changed'), bool):
            problems.append(f'{path}.hash_changed must be boolean')
        if not isinstance(row.get('requires_reviewer_review'), bool):
            problems.append(f'{path}.requires_reviewer_review must be boolean')
        if not _text(row.get('reviewer_owner')):
            problems.append(f'{path}.reviewer_owner is required')

    skipped_reason_batches = set()
    for index, row in enumerate(_mapping_sequence(packet.get('skipped_source_reasons'))):
        path = f'skipped_source_reasons[{index}]'
        batch = _require_source_row(row, path, problems)
        if batch:
            skipped_reason_batches.add(batch)
        if not _text(row.get('skipped_reason')):
            problems.append(f'{path}.skipped_reason is required')
        if not _text(row.get('reviewer_owner')):
            problems.append(f'{path}.reviewer_owner is required')

    if summary_batches != status_batches:
        problems.append('redirect_hash_content_type_summaries must cover every intake status source_batch_id')
    if freshness_batches != status_batches:
        problems.append('freshness_signals must cover every intake status source_batch_id')
    missing_skipped_reason_batches = skipped_status_batches - skipped_reason_batches
    if missing_skipped_reason_batches:
        problems.append('skipped_source_reasons must cover every skipped intake source_batch_id')

    owners = _mapping(packet.get('reviewer_owner_fields'))
    for key in ('intake_owner', 'intake_reviewer', 'freshness_owner'):
        if not _text(owners.get(key)):
            problems.append(f'reviewer_owner_fields lacks {key}')

    attestations = _mapping(packet.get('attestations'))
    for key in REQUIRED_ATTESTATIONS:
        if attestations.get(key) is not True:
            problems.append(f'attestation must be true: {key}')
    boundaries = _mapping(packet.get('execution_boundaries'))
    _require_false_flags(boundaries, 'execution_boundaries', ('raw_body_persistence_allowed', 'download_allowed', 'processor_invocation_allowed', 'registry_mutation_allowed', 'schedule_mutation_allowed'), problems)
    _collect_unsafe_content(packet, 'packet', problems)
    return PublicSourceRefreshMetadataIntakeValidationResult(ready=not problems, problems=tuple(sorted(set(problems))))


def require_public_source_refresh_metadata_intake_packet(packet: Mapping[str, Any]) -> None:
    result = validate_public_source_refresh_metadata_intake_packet(packet)
    if not result.ready:
        raise PublicSourceRefreshMetadataIntakePacketError('invalid_public_source_refresh_metadata_intake_packet: ' + '; '.join(result.problems))


def _intake_status(capture: Mapping[str, Any], placeholder_present: bool) -> str:
    raw_status = _text(capture.get('capture_status') or capture.get('status')).lower()
    if raw_status in {'skipped', 'skip'} or _text(capture.get('skipped_reason')):
        return 'skipped_metadata_only'
    if placeholder_present and _text(capture.get('content_hash')) and _text(capture.get('content_type')):
        return 'accepted_metadata_only'
    return 'needs_reviewer_resolution'


def _hash_changed(capture: Mapping[str, Any]) -> bool:
    previous = _text(capture.get('previous_content_hash'))
    current = _text(capture.get('content_hash'))
    return bool(previous and current and previous != current)


def _require_fields(row: Mapping[str, Any], fields: Sequence[str], path: str, problems: list[str]) -> None:
    for key in fields:
        if key not in row:
            problems.append(f'{path}.{key} is required')


def _require_source_row(row: Mapping[str, Any], path: str, problems: list[str]) -> str:
    batch = _text(row.get('source_batch_id'))
    if not batch:
        problems.append(f'{path}.source_batch_id is required')
    for key in ('source_id', 'canonical_url'):
        if not _text(row.get(key)):
            problems.append(f'{path}.{key} is required')
    if not _text_list(row.get('citation_refs')):
        problems.append(f'{path}.citation_refs is required')
    _validate_public_url(_text(row.get('canonical_url')), f'{path}.canonical_url', problems)
    for key in ('requested_url', 'final_url'):
        if _text(row.get(key)):
            _validate_public_url(_text(row.get(key)), f'{path}.{key}', problems)
    for url in _text_list(row.get('redirect_chain')):
        _validate_public_url(url, f'{path}.redirect_chain', problems)
    return batch


def _require_false_flags(packet: Mapping[str, Any], path: str, keys: Sequence[str], problems: list[str]) -> None:
    for key in keys:
        if packet.get(key) is not False:
            problems.append(f'{path}.{key} must be false')


def _collect_unsafe_content(value: Any, path: str, problems: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = _normalized_key(key_text)
            child_path = f'{path}.{key_text}'
            if key_text in RAW_KEYS:
                problems.append(f'{child_path} is not allowed')
            if normalized_key in RAW_KEY_TOKENS and child not in (None, '', [], {}, False):
                problems.append(f'{child_path} must not contain raw, download, or archive references')
            if normalized_key in PRIVATE_KEY_TOKENS and child not in (None, '', [], {}, False):
                problems.append(f'{child_path} must not contain private or session artifacts')
            if key_text in UNSAFE_TRUE_FLAGS and child is True:
                problems.append(f'{child_path} must not be true')
            if normalized_key in UNSAFE_TRUE_FLAG_TOKENS and child not in (None, '', [], {}, False):
                problems.append(f'{child_path} must be false or empty')
            _collect_unsafe_content(child, child_path, problems)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _collect_unsafe_content(child, f'{path}[{index}]', problems)
    elif isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in RAW_MARKERS):
            problems.append(f'{path} contains a raw, download, or archive artifact reference')
        if any(marker in lowered for marker in PRIVATE_MARKERS):
            problems.append(f'{path} contains a private or session artifact reference')
        if any(marker in lowered for marker in LEGAL_OR_PERMIT_GUARANTEE_MARKERS):
            problems.append(f'{path} contains a legal or permitting outcome guarantee')
        if value.startswith('http://') or value.startswith('https://'):
            _validate_public_url(value, path, problems)


def _validate_public_url(value: str, path: str, problems: list[str]) -> None:
    if not value:
        return
    parsed = urlparse(value)
    if parsed.scheme != 'https':
        problems.append(f'{path} must use https')
    if parsed.username or parsed.password:
        problems.append(f'{path} must not include credentials')
    if parsed.hostname not in ALLOWED_HOSTS:
        problems.append(f'{path} host is not allowlisted')
    lowered = parsed.path.lower()
    if any(marker in lowered for marker in AUTH_URL_MARKERS):
        problems.append(f'{path} must not target authenticated paths')


def _required_mapping(packet: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = packet.get(key)
    if not isinstance(value, Mapping):
        raise PublicSourceRefreshMetadataIntakePacketError(f'{key} must be an object')
    return value


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [item for item in value if isinstance(item, Mapping)]
    return []


def _text(value: Any, fallback: str = '') -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback


def _text_list(value: Any) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return []


def _packet_id(packet: Mapping[str, Any]) -> str:
    for key in ('packet_id', 'packet_type'):
        value = _text(packet.get(key))
        if value:
            return value
    raise PublicSourceRefreshMetadataIntakePacketError('packet lacks packet_id')


def _stable_token(value: str) -> str:
    return ''.join(character.lower() if character.isalnum() else '-' for character in value).strip('-') or 'source'


def _normalized_key(value: str) -> str:
    return ''.join(character for character in value.lower() if character.isalnum())
