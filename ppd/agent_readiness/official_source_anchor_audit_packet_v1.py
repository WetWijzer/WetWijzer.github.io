from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit

from ppd.source_anchor_matrix import ORIGINAL_PUBLIC_SOURCE_ANCHORS

SCHEMA_VERSION = 'official_source_anchor_audit_packet_v1'
PACKET_ID = 'ppd-official-source-anchor-audit-packet-v1'
REVIEWER_OWNER = 'PP&D public source registry maintainer'
OFFLINE_VALIDATION_COMMANDS = [
    'python3 -m unittest ppd.tests.test_official_source_anchor_audit_packet_v1',
    "python3 -m unittest discover -s ppd/tests -p 'test_*.py'",
]
NO_ACTION_STATEMENTS = [
    'No live crawl has been performed.',
    'No download has been performed.',
    'No processor execution has been performed.',
    'No raw body persistence has been performed.',
    'No source registry mutation has been performed.',
]
ALLOWED_HOSTS = {'www.portland.gov', 'devhub.portlandoregon.gov', 'www.portlandmaps.com', 'www.portlandoregon.gov'}
STALE_STATUSES = {'synthetic_unverified', 'fixture_seed_pending_first_crawl', 'stale', 'unknown', 'missing'}


class OfficialSourceAnchorAuditPacketError(ValueError):
    pass


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _text(value: Any, default: str = '') -> str:
    return default if value is None else str(value)


def _records(section: Any) -> list[Mapping[str, Any]]:
    if isinstance(section, Mapping):
        for key in ('sources', 'anchors', 'records', 'source_registry', 'sourceRegistry'):
            values = section.get(key)
            if isinstance(values, list):
                return [row for row in values if isinstance(row, Mapping)]
    if isinstance(section, list):
        return [row for row in section if isinstance(row, Mapping)]
    return []


def _collect_rows(inputs: Mapping[str, Any], keys: tuple[str, ...]) -> list[Mapping[str, Any]]:
    rows: list[Mapping[str, Any]] = []
    for key in keys:
        rows.extend(_records(inputs.get(key)))
    return rows


def _urls(row: Mapping[str, Any]) -> set[str]:
    values = set()
    for key in ('canonical_url', 'canonicalUrl', 'official_url', 'sourceUrl', 'source_url', 'url'):
        if row.get(key):
            values.add(str(row[key]).rstrip('/'))
    return values


def _source_id(row: Mapping[str, Any], fallback: str) -> str:
    return _text(row.get('source_id') or row.get('id') or row.get('sourceId'), fallback)


def _fixture_ref(row: Mapping[str, Any], fallback: str) -> str:
    for key in ('citation', 'fixture_ref', 'fixture', 'fixture_id', 'source_id', 'id'):
        if row.get(key):
            return str(row[key])
    return fallback


def _date_evidence(rows: list[Mapping[str, Any]]) -> str:
    for row in rows:
        for key in ('visible_date', 'visibleDate', 'retrieved_anchor_date', 'lastSeenAt', 'fetchedAt', 'lastModified', 'generatedAt'):
            if row.get(key):
                return str(row[key])
    return 'missing'


def _freshness(rows: list[Mapping[str, Any]]) -> str:
    for row in rows:
        value = row.get('freshness_status') or row.get('freshnessStatus') or row.get('crawlStatus')
        if value:
            return str(value)
    return 'missing'


def _policy(anchor_url: str, registry_matches: list[Mapping[str, Any]]) -> dict[str, str]:
    host = (urlsplit(anchor_url).hostname or '').lower()
    policy = {
        'allowlist_status': 'allowlisted_public_host' if host in ALLOWED_HOSTS else 'not_allowlisted',
        'robots_policy_status': 'not_checked_fixture_only',
        'processor_policy_status': 'metadata_only_policy_preflight_required',
    }
    for row in registry_matches:
        if row.get('robots_policy_status') or row.get('robotsPolicyStatus'):
            policy['robots_policy_status'] = _text(row.get('robots_policy_status') or row.get('robotsPolicyStatus'))
        if row.get('processor_policy') or row.get('processorPolicy'):
            policy['processor_policy_status'] = _text(row.get('processor_policy') or row.get('processorPolicy'))
    return policy


def build_official_source_anchor_audit_packet_v1(source_inputs: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(source_inputs, Mapping):
        raise TypeError('source_inputs must be an object')
    anchors = [str(url) for url in _as_list(source_inputs.get('original_official_source_anchors'))] or list(ORIGINAL_PUBLIC_SOURCE_ANCHORS)
    registry_rows = _collect_rows(source_inputs, ('committed_source_registry_fixtures', 'source_registry', 'source_registry_fixture', 'official_source_anchor_matrix'))
    index_rows = _collect_rows(source_inputs, ('source_index_fixtures', 'source_index', 'source_index_fixture'))
    handoff = source_inputs.get('human_release_handoff_packet_v1') or {}
    if handoff and not isinstance(handoff, Mapping):
        raise TypeError('human_release_handoff_packet_v1 must be an object')
    owner = _text(source_inputs.get('reviewer_owner'), REVIEWER_OWNER)
    rollback = _text(source_inputs.get('rollback_note'), 'Discard this audit packet and leave committed source registry fixtures unchanged.')
    commands = list(source_inputs.get('offline_validation_commands') or OFFLINE_VALIDATION_COMMANDS)
    gap_rows = []
    for position, anchor_url in enumerate(anchors, start=1):
        normalized = anchor_url.rstrip('/')
        registry_matches = [row for row in registry_rows if normalized in _urls(row)]
        index_matches = [row for row in index_rows if normalized in _urls(row)]
        matched = registry_matches + index_matches
        issues = []
        if not registry_matches:
            issues.append('missing_committed_source_registry_anchor')
        if not index_matches:
            issues.append('missing_source_index_anchor')
        visible_date = _date_evidence(matched)
        freshness = _freshness(matched)
        if visible_date == 'missing' or freshness.lower() in STALE_STATUSES:
            issues.append('stale_visible_date_evidence')
        policy = _policy(anchor_url, registry_matches)
        if policy['allowlist_status'] != 'allowlisted_public_host' or policy['robots_policy_status'] == 'not_checked_fixture_only':
            issues.append('policy_status_needs_review')
        if not issues:
            continue
        citations = sorted({_fixture_ref(row, 'fixture:%d' % position) for row in matched}) or ['original_ppd_official_source_anchor_list']
        if isinstance(handoff, Mapping) and handoff.get('schema_version'):
            citations = sorted(set(citations + ['human_release_handoff_packet_v1']))
        source_ids = sorted({_source_id(row, 'official-anchor-%d' % position) for row in matched}) or ['official-anchor-%d:unregistered' % position]
        gap_rows.append({
            'gap_id': 'official-source-anchor-gap-%02d' % position,
            'anchor_url': anchor_url,
            'issue_types': sorted(set(issues)),
            'visible_date_evidence': visible_date,
            'freshness_status': freshness,
            'allowlist_status': policy['allowlist_status'],
            'robots_policy_status': policy['robots_policy_status'],
            'processor_policy_status': policy['processor_policy_status'],
            'affected_source_ids': source_ids,
            'citations': citations,
            'reviewer_owner': owner,
            'rollback_note': rollback,
            'offline_validation_commands': commands,
        })
    return {
        'schema_version': SCHEMA_VERSION,
        'packet_id': PACKET_ID,
        'fixture_first': True,
        'metadata_only': True,
        'compared_fixture_families': ['original_ppd_official_source_anchor_list', 'committed_source_registry_fixtures', 'source_index_fixtures', 'human_release_handoff_packet_v1'],
        'gap_rows': gap_rows,
        'reviewer_owner': owner,
        'rollback_note': rollback,
        'offline_validation_commands': commands,
        'attestations': {
            'live_crawl_performed': False,
            'download_performed': False,
            'processor_execution_performed': False,
            'raw_body_persisted': False,
            'source_registry_mutated': False,
        },
        'no_action_statements': list(NO_ACTION_STATEMENTS),
    }


def render_official_source_anchor_audit_packet_v1(packet_or_inputs: Mapping[str, Any]) -> str:
    packet = packet_or_inputs
    if packet.get('schema_version') != SCHEMA_VERSION:
        packet = build_official_source_anchor_audit_packet_v1(packet_or_inputs)
    lines = ['Official Source Anchor Audit Packet v1', 'Gap rows: %d' % len(packet['gap_rows'])]
    for row in packet['gap_rows']:
        lines.append('- %s: %s (%s)' % (row['gap_id'], row['anchor_url'], ', '.join(row['issue_types'])))
    lines.append('Offline validation commands:')
    lines.extend('- %s' % command for command in packet['offline_validation_commands'])
    lines.append('Explicit non-action statements:')
    lines.extend('- %s' % statement for statement in packet['no_action_statements'])
    return '\n'.join(lines)


build_packet = build_official_source_anchor_audit_packet_v1
render_packet = render_official_source_anchor_audit_packet_v1


def load_source_inputs(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise TypeError('source inputs fixture must be a JSON object')
    return data


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print('usage: official_source_anchor_audit_packet_v1.py SOURCE_INPUTS_JSON', file=sys.stderr)
        return 2
    print(json.dumps(build_official_source_anchor_audit_packet_v1(load_source_inputs(args[0])), indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
