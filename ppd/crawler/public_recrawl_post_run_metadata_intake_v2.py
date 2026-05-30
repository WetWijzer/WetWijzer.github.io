from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from ppd.crawler.public_recrawl_operator_packet_v2 import validate_public_recrawl_operator_packet_v2


PACKET_TYPE = 'ppd_public_recrawl_post_run_metadata_intake_v2_packet'
PACKET_VERSION = 2

_REQUIRED_ATTESTATIONS = (
    'no_live_crawl',
    'no_processor',
    'no_raw_body',
    'no_download',
    'no_source_registry_mutation',
)
_CAPTURE_PLACEHOLDER_FIELDS = (
    'requested_url',
    'final_url',
    'redirect_chain',
    'http_status',
    'content_type',
    'content_hash',
    'previous_content_hash',
)
_FORBIDDEN_TRUE_KEYS = {
    'live_crawl_performed',
    'live_network_invoked',
    'processor_invoked',
    'raw_body_persisted',
    'document_downloaded',
    'source_registry_mutated',
    'registry_mutated',
    'schedule_mutated',
}


@dataclass(frozen=True)
class PublicRecrawlPostRunMetadataIntakeV2ValidationResult:
    valid: bool
    errors: tuple[str, ...]


class PublicRecrawlPostRunMetadataIntakeV2PacketError(ValueError):
    pass


def build_public_recrawl_post_run_metadata_intake_v2_packet(
    operator_packet_v2: Mapping[str, Any],
    source_refresh_runbook: Mapping[str, Any],
    source_refresh_metadata_intake_fixture: Mapping[str, Any],
    *,
    packet_id: str = 'fixture-public-recrawl-post-run-metadata-intake-v2-001',
    generated_at: str = '2026-05-29T00:00:00Z',
) -> dict[str, Any]:
    operator_issues = validate_public_recrawl_operator_packet_v2(operator_packet_v2)
    if operator_issues:
        issue_codes = ', '.join(getattr(issue, 'code', str(issue)) for issue in operator_issues)
        raise PublicRecrawlPostRunMetadataIntakeV2PacketError('operator packet v2 is not safe: ' + issue_codes)

    runbook_candidates = _runbook_candidates_by_url(source_refresh_runbook)
    capture_records = _capture_records_by_key(source_refresh_metadata_intake_fixture)
    reviewer_owner_fields = dict(source_refresh_runbook.get('reviewer_owner_fields', {}))
    decisions: list[dict[str, Any]] = []
    skipped_reasons: list[dict[str, Any]] = []

    for batch in _sequence(operator_packet_v2.get('seed_batches')):
        if not isinstance(batch, Mapping):
            continue
        batch_citations = _text_list(batch.get('source_evidence_ids'))
        for seed in _sequence(batch.get('seeds')):
            if not isinstance(seed, Mapping):
                continue
            url = _text(seed.get('url'))
            candidate = runbook_candidates.get(url, {})
            source_id = _text(candidate.get('source_id'), _source_id_from_url(url))
            capture = capture_records.get(source_id) or capture_records.get(url) or {}
            skipped_reason = _text(
                capture.get('skipped_reason'),
                'not_skipped_metadata_placeholder' if _text(capture.get('content_hash')) else 'metadata_placeholder_pending_capture',
            )
            citations = _dedupe(
                batch_citations
                + _text_list(seed.get('source_evidence_ids'))
                + _policy_citations(candidate)
                + _text_list(capture.get('citation_refs'))
            )
            decision = {
                'decision_id': 'captured-url-decision-' + _stable_token(source_id or url),
                'source_id': source_id,
                'canonical_url': _text(candidate.get('canonical_url'), url),
                'requested_url': _text(capture.get('requested_url'), url),
                'decision': 'metadata_placeholder_captured' if _text(capture.get('content_hash')) else 'skipped_metadata_placeholder',
                'source_evidence_ids': citations,
                'robots_decision': seed.get('robots_decision', {}),
                'metadata_only': True,
                'capture_placeholder': _capture_placeholder(capture, url),
                'skipped_reason': skipped_reason,
                'reviewer_owner_fields': {
                    'primary_reviewer': _text(reviewer_owner_fields.get('primary_reviewer'), 'ppd_public_sources_reviewer'),
                    'backup_reviewer': _text(reviewer_owner_fields.get('backup_reviewer'), 'ppd_guardrails_reviewer'),
                    'review_queue': _text(reviewer_owner_fields.get('review_queue'), 'public-recrawl-post-run-metadata-intake'),
                    'capture_reviewer_owner': _text(capture.get('reviewer_owner'), _text(reviewer_owner_fields.get('primary_reviewer'), 'ppd_public_sources_reviewer')),
                },
                'live_crawl_performed': False,
                'processor_invoked': False,
                'raw_body_persisted': False,
                'document_downloaded': False,
                'source_registry_mutated': False,
            }
            decisions.append(decision)
            if skipped_reason != 'not_skipped_metadata_placeholder':
                skipped_reasons.append({
                    'source_id': source_id,
                    'canonical_url': decision['canonical_url'],
                    'skipped_reason': skipped_reason,
                    'source_evidence_ids': citations,
                    'reviewer_owner': decision['reviewer_owner_fields']['capture_reviewer_owner'],
                })

    packet = {
        'packet_type': PACKET_TYPE,
        'packet_version': PACKET_VERSION,
        'packet_id': packet_id,
        'generated_at': generated_at,
        'fixture_first': True,
        'metadata_only': True,
        'input_packet_refs': {
            'operator_packet_type': _text(operator_packet_v2.get('packetType')),
            'operator_schema_version': operator_packet_v2.get('schemaVersion'),
            'source_refresh_runbook_packet_type': _text(source_refresh_runbook.get('packet_type')),
            'source_refresh_runbook_packet_version': _text(source_refresh_runbook.get('packet_version')),
            'source_refresh_metadata_intake_packet_id': _text(source_refresh_metadata_intake_fixture.get('packet_id')),
        },
        'captured_url_decisions': decisions,
        'skipped_source_reasons': skipped_reasons,
        'reviewer_owner_fields': reviewer_owner_fields,
        'offline_validation_commands': [
            ['python3', '-m', 'py_compile', 'ppd/crawler/public_recrawl_post_run_metadata_intake_v2.py'],
            ['python3', '-m', 'pytest', 'ppd/tests/test_public_recrawl_post_run_metadata_intake_v2.py'],
            ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'],
        ],
        'attestations': {
            'no_live_crawl': True,
            'no_processor': True,
            'no_raw_body': True,
            'no_download': True,
            'no_source_registry_mutation': True,
            'no_live_crawl_note': 'Fixture packet contains metadata placeholders only and performs no network IO.',
            'no_processor_note': 'Fixture packet does not invoke archival, extraction, or processor code.',
            'no_raw_body_note': 'Fixture packet stores no response bodies or raw HTML.',
            'no_download_note': 'Fixture packet stores no downloaded documents.',
            'no_source_registry_mutation_note': 'Fixture packet makes no source registry or schedule changes.',
        },
        'side_effects': {
            'live_crawl_performed': False,
            'live_network_invoked': False,
            'processor_invoked': False,
            'raw_body_persisted': False,
            'document_downloaded': False,
            'source_registry_mutated': False,
            'registry_mutated': False,
            'schedule_mutated': False,
        },
        'intake_summary': {
            'captured_url_decision_count': len(decisions),
            'skipped_source_reason_count': len(skipped_reasons),
            'metadata_only': True,
            'live_crawl_performed': False,
            'processor_invoked': False,
            'raw_body_persisted': False,
            'document_downloaded': False,
            'source_registry_mutated': False,
        },
    }
    require_valid_public_recrawl_post_run_metadata_intake_v2_packet(packet)
    return packet


def validate_public_recrawl_post_run_metadata_intake_v2_packet(packet: Mapping[str, Any]) -> PublicRecrawlPostRunMetadataIntakeV2ValidationResult:
    errors: list[str] = []
    if packet.get('packet_type') != PACKET_TYPE:
        errors.append('packet_type must be ' + PACKET_TYPE)
    if packet.get('packet_version') != PACKET_VERSION:
        errors.append('packet_version must be 2')
    if not _text(packet.get('packet_id')):
        errors.append('packet_id is required')
    if not _text(packet.get('generated_at')).endswith('Z'):
        errors.append('generated_at must be an ISO UTC timestamp ending in Z')
    for key in ('fixture_first', 'metadata_only'):
        if packet.get(key) is not True:
            errors.append(key + ' must be true')
    _collect_forbidden_true_values(packet, '$', errors)

    decisions = _require_list(packet.get('captured_url_decisions'), 'captured_url_decisions', errors)
    if not decisions:
        errors.append('captured_url_decisions must include at least one decision')
    for index, decision in enumerate(decisions):
        prefix = 'captured_url_decisions[' + str(index) + ']'
        if not isinstance(decision, Mapping):
            errors.append(prefix + ' must be an object')
            continue
        for key in ('decision_id', 'source_id', 'canonical_url', 'requested_url', 'decision', 'skipped_reason'):
            if not _text(decision.get(key)):
                errors.append(prefix + '.' + key + ' is required')
        if not _text_list(decision.get('source_evidence_ids')):
            errors.append(prefix + '.source_evidence_ids must cite at least one source')
        if decision.get('metadata_only') is not True:
            errors.append(prefix + '.metadata_only must be true')
        placeholder = decision.get('capture_placeholder')
        if not isinstance(placeholder, Mapping):
            errors.append(prefix + '.capture_placeholder must be an object')
        else:
            for field in _CAPTURE_PLACEHOLDER_FIELDS:
                if field not in placeholder:
                    errors.append(prefix + '.capture_placeholder.' + field + ' is required')
        owners = decision.get('reviewer_owner_fields')
        if not isinstance(owners, Mapping):
            errors.append(prefix + '.reviewer_owner_fields must be an object')
        else:
            for key in ('primary_reviewer', 'backup_reviewer', 'review_queue', 'capture_reviewer_owner'):
                if not _text(owners.get(key)):
                    errors.append(prefix + '.reviewer_owner_fields.' + key + ' is required')
        for key in ('live_crawl_performed', 'processor_invoked', 'raw_body_persisted', 'document_downloaded', 'source_registry_mutated'):
            if decision.get(key) is not False:
                errors.append(prefix + '.' + key + ' must be false')

    skipped = _require_list(packet.get('skipped_source_reasons'), 'skipped_source_reasons', errors)
    for index, row in enumerate(skipped):
        prefix = 'skipped_source_reasons[' + str(index) + ']'
        if not isinstance(row, Mapping):
            errors.append(prefix + ' must be an object')
            continue
        for key in ('source_id', 'canonical_url', 'skipped_reason', 'reviewer_owner'):
            if not _text(row.get(key)):
                errors.append(prefix + '.' + key + ' is required')
        if not _text_list(row.get('source_evidence_ids')):
            errors.append(prefix + '.source_evidence_ids must cite at least one source')

    commands = _require_list(packet.get('offline_validation_commands'), 'offline_validation_commands', errors)
    if not commands:
        errors.append('offline_validation_commands must include at least one command')
    for index, command in enumerate(commands):
        if not isinstance(command, Sequence) or isinstance(command, (str, bytes, bytearray)) or not command:
            errors.append('offline_validation_commands[' + str(index) + '] must be a non-empty argv list')

    attestations = packet.get('attestations')
    if not isinstance(attestations, Mapping):
        errors.append('attestations must be an object')
    else:
        for key in _REQUIRED_ATTESTATIONS:
            if attestations.get(key) is not True:
                errors.append('attestations.' + key + ' must be true')

    summary = packet.get('intake_summary')
    if not isinstance(summary, Mapping):
        errors.append('intake_summary must be an object')
    else:
        if summary.get('captured_url_decision_count') != len(decisions):
            errors.append('intake_summary.captured_url_decision_count must match captured_url_decisions')
        if summary.get('skipped_source_reason_count') != len(skipped):
            errors.append('intake_summary.skipped_source_reason_count must match skipped_source_reasons')
        if summary.get('metadata_only') is not True:
            errors.append('intake_summary.metadata_only must be true')
        for key in ('live_crawl_performed', 'processor_invoked', 'raw_body_persisted', 'document_downloaded', 'source_registry_mutated'):
            if summary.get(key) is not False:
                errors.append('intake_summary.' + key + ' must be false')

    return PublicRecrawlPostRunMetadataIntakeV2ValidationResult(valid=not errors, errors=tuple(dict.fromkeys(errors)))


def require_valid_public_recrawl_post_run_metadata_intake_v2_packet(packet: Mapping[str, Any]) -> None:
    result = validate_public_recrawl_post_run_metadata_intake_v2_packet(packet)
    if not result.valid:
        raise PublicRecrawlPostRunMetadataIntakeV2PacketError('; '.join(result.errors))


def _runbook_candidates_by_url(runbook: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows: dict[str, Mapping[str, Any]] = {}
    for candidate in _sequence(runbook.get('candidate_sources')):
        if isinstance(candidate, Mapping):
            url = _text(candidate.get('canonical_url'))
            if url:
                rows[url] = candidate
    return rows


def _capture_records_by_key(intake_fixture: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows: dict[str, Mapping[str, Any]] = {}
    for capture in _sequence(intake_fixture.get('synthetic_metadata_only_capture_records')):
        if isinstance(capture, Mapping):
            for key in (_text(capture.get('source_id')), _text(capture.get('canonical_url')), _text(capture.get('requested_url'))):
                if key:
                    rows[key] = capture
    return rows


def _capture_placeholder(capture: Mapping[str, Any], fallback_url: str) -> dict[str, Any]:
    return {
        'requested_url': _text(capture.get('requested_url'), fallback_url),
        'final_url': _text(capture.get('final_url'), fallback_url),
        'redirect_chain': list(_sequence(capture.get('redirect_chain'))) or [fallback_url],
        'http_status': capture.get('http_status'),
        'content_type': _text(capture.get('content_type'), 'metadata_only_pending_capture'),
        'content_hash': _text(capture.get('content_hash')),
        'previous_content_hash': _text(capture.get('previous_content_hash')),
    }


def _policy_citations(candidate: Mapping[str, Any]) -> list[str]:
    citations: list[str] = []
    for key in ('robots_policy', 'policy_evidence', 'rate_limit_window'):
        value = candidate.get(key)
        if isinstance(value, Mapping):
            citations.append(_text(value.get('evidence_ref')))
    return [citation for citation in citations if citation]


def _collect_forbidden_true_values(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            nested_path = path + '.' + key_text
            if key_text in _FORBIDDEN_TRUE_KEYS and nested is not False:
                errors.append(nested_path + ' must be false')
            _collect_forbidden_true_values(nested, nested_path, errors)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, nested in enumerate(value):
            _collect_forbidden_true_values(nested, path + '[' + str(index) + ']', errors)


def _require_list(value: Any, field: str, errors: list[str]) -> list[Any]:
    if isinstance(value, list):
        return value
    errors.append(field + ' must be a list')
    return []


def _sequence(value: Any) -> Sequence[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return value
    return ()


def _text(value: Any, default: str = '') -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _text_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [_text(item) for item in value if _text(item)]
    return []


def _dedupe(values: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _source_id_from_url(url: str) -> str:
    parsed = urlparse(url)
    return _stable_token(parsed.netloc + parsed.path)


def _stable_token(value: str) -> str:
    return ''.join(character.lower() if character.isalnum() else '-' for character in value).strip('-') or 'unknown'


__all__ = [
    'PACKET_TYPE',
    'PACKET_VERSION',
    'PublicRecrawlPostRunMetadataIntakeV2PacketError',
    'PublicRecrawlPostRunMetadataIntakeV2ValidationResult',
    'build_public_recrawl_post_run_metadata_intake_v2_packet',
    'require_valid_public_recrawl_post_run_metadata_intake_v2_packet',
    'validate_public_recrawl_post_run_metadata_intake_v2_packet',
]
