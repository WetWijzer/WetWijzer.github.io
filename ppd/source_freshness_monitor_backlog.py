from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator


PROHIBITED_COMMAND_TOKENS = (
    'curl',
    'wget',
    'requests',
    'httpx',
    'scrapy',
    'selenium',
    'playwright',
)

RAW_BODY_KEYS = {
    'raw_body',
    'raw_html',
    'document_body',
    'downloaded_document',
    'downloaded_data',
    'downloaded_pdf',
    'pdf_bytes',
    'pdf_content',
    'raw_pdf',
    'crawl_output',
    'crawl_response_body',
    'warc_path',
}

PRIVATE_ARTIFACT_KEYS = {
    'auth_state',
    'authenticated_artifact',
    'browser_context',
    'browser_trace',
    'cookie',
    'cookies',
    'devhub_session',
    'har',
    'har_path',
    'local_private_path',
    'mfa_token',
    'password',
    'private_artifact',
    'screenshot',
    'session',
    'session_state',
    'session_state_path',
    'storage_state',
    'trace',
    'trace_path',
}

PRIVATE_VALUE_TOKENS = (
    '.har',
    'trace.zip',
    'storage_state',
    'storage state',
    'session cookie',
    'bearer ',
    'authorization:',
    '/users/',
    'c:\\users\\',
    'authenticated devhub',
)

LIVE_CRAWL_KEYS = {
    'capture_finished_at',
    'capture_started_at',
    'captured_at',
    'content_hash',
    'crawl_completed_at',
    'crawl_result',
    'fetch_status',
    'fetched_at',
    'http_status',
    'live_crawl_status',
    'response_headers',
}

LIVE_CRAWL_VALUE_TOKENS = (
    'live crawl completed',
    'fetched from',
    'downloaded from',
    'captured response',
    'http 200',
    'crawl succeeded',
)

OUTCOME_GUARANTEE_TOKENS = (
    'guarantee approval',
    'guarantees approval',
    'guaranteed approval',
    'will be approved',
    'permit will issue',
    'ensures permit issuance',
    'legal advice',
    'legally sufficient',
)

CONSEQUENTIAL_ACTION_TOKENS = (
    'submit the permit',
    'submit application',
    'submit-payment',
    'submit payment',
    'pay fee',
    'pay fees',
    'schedule inspection',
    'cancel inspection',
    'cancel permit',
    'upload corrections',
    'upload plans',
    'certify application',
    'final submission',
)

MUTATION_DOMAINS = (
    'source',
    'document',
    'requirement',
    'process',
    'guardrail',
    'release_state',
    'agent_state',
)

MUTATION_KEY_TOKENS = (
    'mutation',
    'mutate',
    'write',
    'apply',
    'promote',
    'publish',
    'activate',
)


def load_packet(path: str | Path) -> dict[str, Any]:
    packet_path = Path(path)
    with packet_path.open('r', encoding='utf-8') as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError('freshness monitor packet must be a JSON object')
    return data


def validate_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if packet.get('version') != 1:
        errors.append('version must be 1')

    required_lists = (
        'source_anchors',
        'freshness_schedules',
        'impacted_ids',
        'synthetic_change_categories',
        'offline_validation_commands',
        'work_items',
    )
    for key in required_lists:
        if not isinstance(packet.get(key), list) or not packet.get(key):
            errors.append(f'{key} must be a non-empty list')

    _scan_for_prohibited_content(packet, 'packet', errors)

    anchors = packet.get('source_anchors', [])
    anchor_ids = _unique_ids(anchors, 'source_anchors', errors)
    for anchor in anchors if isinstance(anchors, list) else []:
        if not isinstance(anchor, dict):
            errors.append('source_anchors entries must be objects')
            continue
        url = anchor.get('official_url')
        anchor_id = anchor.get('id')
        if not isinstance(url, str) or not url.startswith('https://'):
            errors.append(f'source anchor {anchor_id} must use an https official_url')
        if anchor.get('crawl_policy') != 'metadata_only_no_body_persistence':
            errors.append(f'source anchor {anchor_id} must be metadata-only')
        citation = anchor.get('citation')
        if not isinstance(citation, dict):
            errors.append(f'source anchor {anchor_id} must include source citation')
        else:
            if citation.get('url') != url:
                errors.append(f'source anchor {anchor_id} citation url must match official_url')
            if not isinstance(citation.get('verified_on'), str) or not citation.get('verified_on'):
                errors.append(f'source anchor {anchor_id} citation must include verified_on')
            if not isinstance(citation.get('label'), str) or not citation.get('label'):
                errors.append(f'source anchor {anchor_id} citation must include label')

    schedules = packet.get('freshness_schedules', [])
    schedule_ids = _unique_ids(schedules, 'freshness_schedules', errors)
    allowed_cadences = {'daily', 'weekly', 'monthly', 'quarterly', 'event_driven'}
    for schedule in schedules if isinstance(schedules, list) else []:
        if not isinstance(schedule, dict):
            errors.append('freshness_schedules entries must be objects')
            continue
        if schedule.get('anchor_id') not in anchor_ids:
            errors.append(f"schedule {schedule.get('id')} references unknown anchor_id")
        if schedule.get('cadence') not in allowed_cadences:
            errors.append(f"schedule {schedule.get('id')} has unsupported cadence")

    impacted_ids: set[str] = set()
    for item in packet.get('impacted_ids', []) if isinstance(packet.get('impacted_ids'), list) else []:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str):
            errors.append('impacted_ids entries must have string id')
            continue
        if item['id'] in impacted_ids:
            errors.append(f"duplicate impacted id {item['id']}")
        impacted_ids.add(item['id'])
        if item.get('kind') not in {'requirement', 'process', 'guardrail'}:
            errors.append(f"impacted id {item['id']} has unsupported kind")

    category_ids = _unique_ids(packet.get('synthetic_change_categories', []), 'synthetic_change_categories', errors)
    command_ids = _unique_ids(packet.get('offline_validation_commands', []), 'offline_validation_commands', errors)
    for command in packet.get('offline_validation_commands', []) if isinstance(packet.get('offline_validation_commands'), list) else []:
        if not isinstance(command, dict):
            errors.append('offline_validation_commands entries must be objects')
            continue
        argv = command.get('argv')
        if not isinstance(argv, list) or not argv or not all(isinstance(part, str) for part in argv):
            errors.append(f"offline command {command.get('id')} must have string argv list")
            continue
        if command.get('network') is not False:
            errors.append(f"offline command {command.get('id')} must set network false")
        lowered = ' '.join(argv).lower()
        for token in PROHIBITED_COMMAND_TOKENS:
            if token in lowered:
                errors.append(f"offline command {command.get('id')} contains live automation token {token}")

    work_items = packet.get('work_items', [])
    seen_orders: list[int] = []
    for item in work_items if isinstance(work_items, list) else []:
        if not isinstance(item, dict):
            errors.append('work_items entries must be objects')
            continue
        order = item.get('order')
        if not isinstance(order, int):
            errors.append(f"work item {item.get('id')} must have integer order")
        else:
            seen_orders.append(order)
        _require_known(item, 'anchor_ids', anchor_ids, errors)
        _require_known(item, 'schedule_ids', schedule_ids, errors)
        _require_known(item, 'synthetic_change_category_ids', category_ids, errors)
        _require_known(item, 'impacted_ids', impacted_ids, errors)
        _require_known(item, 'offline_validation_command_ids', command_ids, errors)
        if item.get('promotion_policy') != 'do_not_promote_source_changes':
            errors.append(f"work item {item.get('id')} must not promote source changes")

    if seen_orders and sorted(seen_orders) != list(range(1, len(seen_orders) + 1)):
        errors.append('work_items order must be contiguous starting at 1')

    return errors


def assert_valid_packet(packet: dict[str, Any]) -> None:
    errors = validate_packet(packet)
    if errors:
        raise AssertionError('freshness monitor packet invalid: ' + '; '.join(errors))


def _unique_ids(items: Any, label: str, errors: list[str]) -> set[str]:
    ids: set[str] = set()
    if not isinstance(items, list):
        return ids
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str):
            errors.append(f'{label} entries must have string id')
            continue
        if item['id'] in ids:
            errors.append(f"duplicate {label} id {item['id']}")
        ids.add(item['id'])
    return ids


def _require_known(item: dict[str, Any], key: str, known_ids: set[str], errors: list[str]) -> None:
    values = item.get(key)
    if not isinstance(values, list) or not values:
        errors.append(f"work item {item.get('id')} must include non-empty {key}")
        return
    for value in values:
        if value not in known_ids:
            errors.append(f"work item {item.get('id')} references unknown {key} value {value}")


def _scan_for_prohibited_content(value: Any, path: str, errors: list[str]) -> None:
    for child_path, key, child in _walk(value, path):
        normalized_key = _normalize_key(key)
        if normalized_key in RAW_BODY_KEYS:
            errors.append(f'raw crawl/PDF/downloaded data is not allowed at {child_path}')
        if normalized_key in PRIVATE_ARTIFACT_KEYS:
            errors.append(f'private/authenticated/session/browser artifact is not allowed at {child_path}')
        if normalized_key in LIVE_CRAWL_KEYS:
            errors.append(f'live crawl claim is not allowed at {child_path}')
        if _is_mutation_key(normalized_key):
            errors.append(f'active mutation flag is not allowed at {child_path}')
        if isinstance(child, str):
            lowered = child.lower()
            if any(token in lowered for token in PRIVATE_VALUE_TOKENS):
                errors.append(f'private/authenticated/session/browser artifact is not allowed at {child_path}')
            if any(token in lowered for token in LIVE_CRAWL_VALUE_TOKENS):
                errors.append(f'live crawl claim is not allowed at {child_path}')
            if any(token in lowered for token in OUTCOME_GUARANTEE_TOKENS):
                errors.append(f'legal or permitting outcome guarantee is not allowed at {child_path}')
            if any(token in lowered for token in CONSEQUENTIAL_ACTION_TOKENS):
                errors.append(f'consequential action language is not allowed at {child_path}')


def _walk(value: Any, path: str) -> Iterator[tuple[str, str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_path = f'{path}.{key_text}'
            yield child_path, key_text, child
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f'{path}[{index}]'
            yield child_path, '', child
            yield from _walk(child, child_path)


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace('-', '_').replace(' ', '_')


def _is_mutation_key(normalized_key: str) -> bool:
    if not any(domain in normalized_key for domain in MUTATION_DOMAINS):
        return False
    return any(token in normalized_key for token in MUTATION_KEY_TOKENS)


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        raise SystemExit('usage: python3 ppd/source_freshness_monitor_backlog.py PACKET.json')
    assert_valid_packet(load_packet(sys.argv[1]))
