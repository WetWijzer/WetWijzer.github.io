from __future__ import annotations

import json
from pathlib import Path

import pytest

from ppd.crawler.processor_handoff_packet import (
    build_processor_handoff_packet,
    validate_processor_handoff_packet,
)

FIXTURE_PATH = Path(__file__).parent / 'fixtures' / 'processor_handoff_packet' / 'reviewed_public_crawl_requests.json'


def _fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding='utf-8'))


def test_builds_metadata_only_processor_handoff_packet_from_reviewed_requests() -> None:
    fixture = _fixture()

    packet = build_processor_handoff_packet(
        fixture['reviewedRequests'],
        generated_at=fixture['generatedAt'],
        processor_expectation=fixture['processorExpectation'],
    )

    assert validate_processor_handoff_packet(packet) == []
    assert packet['schemaVersion'] == 1
    assert len(packet['processorContractInputs']) == 2

    first = packet['processorContractInputs'][0]
    assert first['requestMetadata']['requestId'] == 'reviewed-request-001'
    assert first['requestMetadata']['publicOnly'] is True
    assert first['rateLimitBucket'] == 'public-host:www.portland.gov'
    assert first['processorExpectation']['name'] == 'ipfs_datasets_py.web_archive_processor'
    assert first['processorExpectation']['version'] == '2026.05-fixture'
    assert first['processorArguments']['metadataOnly'] is True
    assert first['processorArguments']['persistRawBody'] is False
    assert first['processorArguments']['downloadDocuments'] is False
    assert first['normalizedDocumentPlaceholder']['documentId'] == 'normalized-placeholder-ppd-online-tools'
    assert first['normalizedDocumentPlaceholder']['contentPersisted'] is False
    assert first['artifactReferences']['metadataOnly'] is True
    assert first['artifactReferences']['rawBodyRef'] is None
    assert first['artifactReferences']['downloadedDocumentRef'] is None


def test_rejects_unreviewed_or_disallowed_public_request() -> None:
    fixture = _fixture()
    request = dict(fixture['reviewedRequests'][0])
    request['robotsPolicy'] = 'disallowed'

    with pytest.raises(ValueError, match='robots_policy must be allowed'):
        build_processor_handoff_packet(
            [request],
            generated_at=fixture['generatedAt'],
            processor_expectation=fixture['processorExpectation'],
        )


def test_rejects_private_devhub_paths_before_processor_contract_input() -> None:
    fixture = _fixture()
    request = dict(fixture['reviewedRequests'][0])
    request['url'] = 'https://devhub.portlandoregon.gov/permits/my/123'
    request['canonicalUrl'] = request['url']

    with pytest.raises(ValueError, match='private DevHub account paths'):
        build_processor_handoff_packet(
            [request],
            generated_at=fixture['generatedAt'],
            processor_expectation=fixture['processorExpectation'],
        )


def test_validator_rejects_raw_artifact_references() -> None:
    fixture = _fixture()
    packet = build_processor_handoff_packet(
        fixture['reviewedRequests'],
        generated_at=fixture['generatedAt'],
        processor_expectation=fixture['processorExpectation'],
    )
    packet['processorContractInputs'][0]['artifactReferences']['rawBodyRef'] = 'raw/ppd-online-tools.html'

    errors = validate_processor_handoff_packet(packet)

    assert any('rawBodyRef must be null' in error for error in errors)


def test_validator_rejects_live_body_material_in_processor_arguments() -> None:
    fixture = _fixture()
    packet = build_processor_handoff_packet(
        fixture['reviewedRequests'],
        generated_at=fixture['generatedAt'],
        processor_expectation=fixture['processorExpectation'],
    )
    packet['processorContractInputs'][0]['processorArguments']['html'] = ''

    errors = validate_processor_handoff_packet(packet)

    assert any('processorArguments.html is not allowed' in error for error in errors)
