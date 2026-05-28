from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlsplit

FIXTURE_PATH = Path(__file__).parent / 'fixtures' / 'public_source_frontier' / 'ppd_fixture_frontier_packet.json'

ALLOWED_HOSTS = {'www.portland.gov', 'devhub.portlandoregon.gov', 'www.portlandoregon.gov', 'www.portlandmaps.com'}
OFFICIAL_ANCHORS = {
    'https://www.portland.gov/ppd',
    'https://www.portland.gov/ppd/how-use-online-permitting-tools',
    'https://devhub.portlandoregon.gov',
    'https://www.portland.gov/ppd/devhub-faqs',
    'https://www.portland.gov/ppd/devhub-sign-guide',
    'https://www.portland.gov/ppd/get-permit/apply-permits',
    'https://www.portland.gov/ppd/devhub-guide-submit-permit-application',
    'https://www.portland.gov/ppd/get-permit/submit-plans-online',
    'https://www.portland.gov/ppd/brochures-forms-handouts/permits-and-inspections-applications',
    'https://www.portland.gov/ppd/spp-file-naming-standards-preparing-pdfs',
    'https://www.portland.gov/ppd/documents/how-pay-fees/download',
    'https://www.portlandmaps.com',
}
SKIP_REASONS = {'outside_allowlist', 'unsupported_scheme', 'private_authenticated', 'disallowed_by_robots_or_policy', 'raw_download_not_permitted', 'too_large', 'unsupported_content_type'}
CRAWL_FREQUENCIES = {'daily', 'every_few_days', 'weekly', 'monthly', 'manual_review', 'none'}
FORBIDDEN_KEYS = {'body', 'rawBody', 'raw_body', 'responseBody', 'response_body', 'html', 'text', 'content', 'bytes', 'archivePath', 'archive_path', 'warcPath', 'warc_path', 'downloadPath', 'download_path', 'documentPath', 'document_path', 'pdfPath', 'pdf_path', 'screenshot', 'trace', 'har', 'cookie', 'authState', 'auth_state'}


def load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding='utf-8'))


def canonicalize_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname:
        return url.strip()
    path = parsed.path or ''
    if path != '/':
        path = path.rstrip('/')
    return parsed._replace(scheme=parsed.scheme.lower(), netloc=parsed.hostname.lower(), path=path, fragment='').geturl()


def walk(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def test_frontier_packet_is_fixture_only_and_metadata_only() -> None:
    packet = load_fixture()
    metadata = packet['metadata']

    assert metadata['fixture_only'] is True
    assert metadata['no_live_network'] is True
    assert metadata['no_raw_body_persistence'] is True
    assert metadata['metadata_only_outputs'] is True
    assert set(metadata['allowed_hosts']) == ALLOWED_HOSTS
    assert set(metadata['skip_reasons']) == SKIP_REASONS

    for key, value in walk(packet):
        assert key not in FORBIDDEN_KEYS
        if isinstance(value, str):
            lowered = value.lower()
            assert '/home/' not in lowered
            assert '/tmp/' not in lowered
            assert 'password' not in lowered
            assert 'cookie' not in lowered


def test_frontier_starts_from_all_official_ppd_anchors() -> None:
    packet = load_fixture()
    anchor_urls = {anchor['canonical_url'] for anchor in packet['official_anchors']}

    assert anchor_urls == OFFICIAL_ANCHORS
    assert len(packet['official_anchors']) == 12
    for anchor in packet['official_anchors']:
        assert canonicalize_url(anchor['canonical_url']) == anchor['canonical_url']
        assert anchor['crawl_frequency_candidate'] in CRAWL_FREQUENCIES


def test_frontier_records_source_page_evidence_and_link_text() -> None:
    packet = load_fixture()
    evidence_ids = {item['evidence_id'] for item in packet['source_page_evidence']}

    assert evidence_ids
    for item in packet['source_page_evidence']:
        assert item['source_page_url']
        assert item['observed_link_texts']

    for record in packet['frontier']:
        assert record['source_page_evidence_id'] in evidence_ids
        assert record['source_page_url']
        assert record['link_text']
        assert record['crawl_frequency_candidate'] in CRAWL_FREQUENCIES


def test_allowlist_decisions_skip_reasons_and_canonical_hosts_are_explicit() -> None:
    packet = load_fixture()
    skipped = [record for record in packet['frontier'] if record['allowlist_decision'] == 'skip']

    assert skipped
    assert {'raw_download_not_permitted', 'private_authenticated', 'outside_allowlist', 'unsupported_scheme'}.issubset({record['skip_reason'] for record in skipped})

    for record in packet['frontier']:
        parsed = urlsplit(record['canonical_url'])
        assert canonicalize_url(record['canonical_url']) == record['canonical_url']
        assert record['host'] == (parsed.hostname or '').lower()
        if record['allowlist_decision'] == 'allow':
            assert record['host'] in ALLOWED_HOSTS
            assert record['skip_reason'] is None
        else:
            assert record['skip_reason'] in SKIP_REASONS


def test_metadata_only_discovery_outputs_do_not_authorize_downloads() -> None:
    packet = load_fixture()

    for record in packet['frontier']:
        output = record['metadata_only_discovery_output']
        assert output['artifact_ref'].startswith('metadata://ppd/source-frontier/')
        assert output['metadata_only'] is True
        assert output['manifest_only'] is True
        assert output['no_raw_body_persisted'] is True
        assert output['no_downloaded_documents'] is True
        assert output['persist_raw_body'] is False
        assert output['store_raw_response'] is False
        assert output['download_documents'] is False
