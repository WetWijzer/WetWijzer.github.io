from copy import deepcopy
from pathlib import Path

import pytest

from ppd.public_source_refresh_metadata_intake_packet import (
    PublicSourceRefreshMetadataIntakePacketError,
    build_public_source_refresh_metadata_intake_packet,
    load_fixture_packet,
    validate_public_source_refresh_metadata_intake_packet,
)

FIXTURE_DIR = Path(__file__).parent / 'fixtures' / 'public_source_refresh_metadata_intake'


def _build_packet() -> dict:
    return build_public_source_refresh_metadata_intake_packet(load_fixture_packet(FIXTURE_DIR / 'inputs.json'))


def test_builds_fixture_first_metadata_intake_packet() -> None:
    packet = _build_packet()

    assert packet['packet_type'] == 'ppd.public_source_refresh_metadata_intake_packet.v1'
    assert packet['fixture_first'] is True
    assert packet['metadata_only'] is True
    assert packet['consumed_packets'][0]['kind'] == 'public_source_refresh_launch_rehearsal_transcript_packet'
    assert {row['intake_status'] for row in packet['per_source_intake_statuses']} == {
        'accepted_metadata_only',
        'skipped_metadata_only',
    }


def test_metadata_intake_records_redirect_hash_content_type_and_freshness() -> None:
    packet = _build_packet()

    summaries = packet['redirect_hash_content_type_summaries']
    assert summaries[0]['redirect_chain'] == ['https://www.portland.gov/code']
    assert summaries[0]['content_hash_status'] == 'present'
    assert summaries[0]['content_type'] == 'text/html; charset=utf-8'
    assert summaries[1]['content_hash_status'] == 'not_captured'

    freshness = {row['source_batch_id']: row for row in packet['freshness_signals']}
    assert freshness['portland-auditor-code-library']['hash_changed'] is True
    assert freshness['portland-auditor-code-library']['requires_reviewer_review'] is True
    assert freshness['devhub-public-portal']['freshness_status'] == 'skipped_pending_operator_review'


def test_metadata_intake_records_skip_reasons_and_attestations() -> None:
    packet = _build_packet()
    result = validate_public_source_refresh_metadata_intake_packet(packet)

    assert result.ready is True
    assert packet['skipped_source_reasons'] == [
        {
            'source_batch_id': 'devhub-public-portal',
            'source_id': 'devhub-public-portal',
            'canonical_url': 'https://devhub.portlandoregon.gov',
            'skipped_reason': 'operator_not_selected_for_metadata_only_capture',
            'citation_refs': ['public-source-refresh-launch-rehearsal-transcript-20260529-fixture-first'],
            'reviewer_owner': 'ppd-public-source-refresh-rehearsal-reviewer',
        }
    ]
    assert packet['attestations'] == {
        'no-raw-body': True,
        'no-download': True,
        'no-processor': True,
        'no-registry-mutation': True,
        'no-schedule-mutation': True,
    }
    assert packet['execution_boundaries']['registry_mutation_allowed'] is False
    assert packet['execution_boundaries']['schedule_mutation_allowed'] is False


def test_metadata_intake_rejects_raw_body_or_download_claims() -> None:
    packet = _build_packet()
    packet['per_source_intake_statuses'][0]['document_downloaded'] = True

    result = validate_public_source_refresh_metadata_intake_packet(packet)

    assert result.ready is False
    assert any('document_downloaded' in problem for problem in result.problems)


def test_metadata_intake_rejects_unsafe_capture_records_before_build() -> None:
    inputs = load_fixture_packet(FIXTURE_DIR / 'inputs.json')
    inputs['synthetic_metadata_only_capture_records'][0]['raw_body'] = 'not allowed'

    with pytest.raises(PublicSourceRefreshMetadataIntakePacketError):
        build_public_source_refresh_metadata_intake_packet(inputs)


@pytest.mark.parametrize(
    ('mutator', 'expected_problem'),
    [
        (lambda packet: packet['per_source_intake_statuses'][0].update({'citation_refs': []}), 'citation_refs is required'),
        (lambda packet: packet['redirect_hash_content_type_summaries'][0].pop('content_type'), 'content_type is required'),
        (lambda packet: packet['skipped_source_reasons'].clear(), 'skipped_source_reasons must cover every skipped intake source_batch_id'),
        (lambda packet: packet['freshness_signals'].pop(), 'freshness_signals must match intake status count'),
        (lambda packet: packet['per_source_intake_statuses'][0].update({'reviewer_owner': ''}), 'reviewer_owner is required'),
    ],
)
def test_metadata_intake_rejects_missing_required_review_metadata(mutator, expected_problem: str) -> None:
    packet = _build_packet()
    mutator(packet)

    result = validate_public_source_refresh_metadata_intake_packet(packet)

    assert result.ready is False
    assert any(expected_problem in problem for problem in result.problems)


@pytest.mark.parametrize(
    ('field_name', 'field_value', 'expected_problem'),
    [
        ('raw_body_ref', 'raw-artifacts/body.html', 'raw, download, or archive'),
        ('download_ref', 'downloaded-documents/form.pdf', 'raw, download, or archive'),
        ('archive_artifact_ref', 'warc://public-capture.warc', 'raw, download, or archive'),
        ('storage_state', 'storage_state/session.json', 'private or session'),
        ('live_crawler_executed', True, 'must be false or empty'),
        ('processor_invoked', True, 'must not be true'),
        ('active_source_registry_mutation', True, 'must be false or empty'),
        ('active_schedule_mutation', True, 'must be false or empty'),
        ('active_requirement_mutation', True, 'must be false or empty'),
        ('active_guardrail_mutation', True, 'must be false or empty'),
        ('active_monitoring_mutation', True, 'must be false or empty'),
        ('active_release_state_mutation', True, 'must be false or empty'),
        ('operator_note', 'Permit will be approved by PP&D.', 'legal or permitting outcome guarantee'),
    ],
)
def test_metadata_intake_rejects_artifacts_execution_guarantees_and_mutation_flags(field_name: str, field_value, expected_problem: str) -> None:
    packet = _build_packet()
    packet['per_source_intake_statuses'][0][field_name] = field_value

    result = validate_public_source_refresh_metadata_intake_packet(packet)

    assert result.ready is False
    assert any(expected_problem in problem for problem in result.problems)


def test_metadata_intake_rejects_private_or_authenticated_urls() -> None:
    packet = deepcopy(_build_packet())
    packet['redirect_hash_content_type_summaries'][0]['requested_url'] = 'https://devhub.portlandoregon.gov/login'

    result = validate_public_source_refresh_metadata_intake_packet(packet)

    assert result.ready is False
    assert any('must not target authenticated paths' in problem for problem in result.problems)
