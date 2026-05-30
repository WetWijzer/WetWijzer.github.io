from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Callable

import pytest

from ppd.source_freshness_monitor_backlog import load_packet, validate_packet


FIXTURE_PATH = Path(__file__).parent / 'fixtures' / 'source_freshness_monitor_backlog_v1.json'


def test_fixture_packet_is_valid() -> None:
    packet = load_packet(FIXTURE_PATH)

    assert validate_packet(packet) == []


def test_work_items_are_ordered_and_metadata_only() -> None:
    packet = load_packet(FIXTURE_PATH)

    assert [item['order'] for item in packet['work_items']] == [1, 2, 3]
    assert {anchor['crawl_policy'] for anchor in packet['source_anchors']} == {
        'metadata_only_no_body_persistence'
    }
    assert {item['promotion_policy'] for item in packet['work_items']} == {
        'do_not_promote_source_changes'
    }


def test_validator_rejects_raw_body_persistence_fields() -> None:
    packet = load_packet(FIXTURE_PATH)
    broken = copy.deepcopy(packet)
    broken['source_anchors'][0]['raw_body'] = 'not allowed'

    errors = validate_packet(broken)

    assert any('raw crawl/PDF/downloaded data' in error for error in errors)


def test_validator_rejects_live_automation_commands() -> None:
    packet = load_packet(FIXTURE_PATH)
    broken = copy.deepcopy(packet)
    broken['offline_validation_commands'][0]['argv'] = ['curl', 'https://www.portland.gov/code/33']

    errors = validate_packet(broken)

    assert any('live automation token curl' in error for error in errors)


@pytest.mark.parametrize(
    ('mutate', 'expected'),
    [
        (lambda packet: packet['source_anchors'][0].pop('citation'), 'must include source citation'),
        (lambda packet: packet.__setitem__('freshness_schedules', []), 'freshness_schedules must be a non-empty list'),
        (lambda packet: packet['work_items'][0].__setitem__('impacted_ids', []), 'must include non-empty impacted_ids'),
        (lambda packet: packet.__setitem__('synthetic_change_categories', []), 'synthetic_change_categories must be a non-empty list'),
        (lambda packet: packet.__setitem__('offline_validation_commands', []), 'offline_validation_commands must be a non-empty list'),
        (lambda packet: packet['work_items'][0].__setitem__('session_state_path', 'state.json'), 'private/authenticated/session/browser artifact'),
        (lambda packet: packet['source_anchors'][0].__setitem__('pdf_bytes', 'JVBERi0x'), 'raw crawl/PDF/downloaded data'),
        (lambda packet: packet['source_anchors'][0].__setitem__('live_crawl_status', 'completed'), 'live crawl claim'),
        (lambda packet: packet['work_items'][0].__setitem__('review_note', 'This guarantees approval.'), 'legal or permitting outcome guarantee'),
        (lambda packet: packet['work_items'][0].__setitem__('next_action', 'Submit the permit application.'), 'consequential action language'),
        (lambda packet: packet['work_items'][0].__setitem__('requirement_mutation_enabled', True), 'active mutation flag'),
    ],
)
def test_validator_rejects_incomplete_or_unsafe_backlog_packet_content(
    mutate: Callable[[dict[str, Any]], Any], expected: str
) -> None:
    packet = load_packet(FIXTURE_PATH)
    broken = copy.deepcopy(packet)
    mutate(broken)

    errors = validate_packet(broken)

    assert any(expected in error for error in errors)
