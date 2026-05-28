"""Fixture-first processor handoff packets for reviewed PP&D crawl requests.

The packet produced here is a local PP&D contract input for the
ipfs_datasets_py processor boundary. It contains only reviewed request
metadata, rate-limit routing, expected processor identity, normalized document
placeholders, and metadata-only artifact references.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping
from urllib.parse import urlparse

ALLOWED_PUBLIC_HOSTS = frozenset(
    {
        'www.portland.gov',
        'devhub.portlandoregon.gov',
        'www.portlandoregon.gov',
        'www.portlandmaps.com',
    }
)

PRIVATE_DEVHUB_PREFIXES = (
    '/account',
    '/accounts',
    '/application',
    '/applications',
    '/cart',
    '/dashboard',
    '/document',
    '/documents',
    '/inspection',
    '/inspections',
    '/my',
    '/payment',
    '/payments',
    '/permit',
    '/permits',
    '/secure',
    '/session',
    '/sessions',
    '/upload',
    '/uploads',
)

RAW_ARTIFACT_KEYS = frozenset(
    {
        'body',
        'raw_body',
        'html',
        'text',
        'content',
        'bytes',
        'archive_path',
        'warc_path',
        'download_path',
        'document_path',
        'pdf_path',
        'local_path',
        'screenshot_path',
        'trace_path',
        'har_path',
    }
)

DEFAULT_PROCESSOR = {
    'name': 'ipfs_datasets_py.web_archive_processor',
    'version': 'expected-by-fixture',
    'module': 'ipfs_datasets_py.processors.web_archiving',
    'operation': 'capture_url_metadata_only',
}


@dataclass(frozen=True)
class ReviewedPublicCrawlRequest:
    request_id: str
    source_id: str
    url: str
    canonical_url: str
    owning_surface: str
    reviewed_at: str
    reviewer: str
    robots_policy: str
    allowlist_policy: str
    source_type: str
    priority: int = 50


@dataclass(frozen=True)
class ProcessorHandoffPacket:
    schema_version: int
    generated_at: str
    processor_contract_inputs: tuple[Mapping[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            'schemaVersion': self.schema_version,
            'generatedAt': self.generated_at,
            'processorContractInputs': [dict(item) for item in self.processor_contract_inputs],
        }


def build_processor_handoff_packet(
    reviewed_requests: list[Mapping[str, Any]],
    *,
    generated_at: str,
    processor_expectation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic metadata-only processor handoff packet."""

    expectation = dict(DEFAULT_PROCESSOR)
    if processor_expectation is not None:
        expectation.update(dict(processor_expectation))

    inputs: list[Mapping[str, Any]] = []
    for index, item in enumerate(reviewed_requests):
        request = _reviewed_request_from_mapping(item)
        bucket = _rate_limit_bucket(request.canonical_url)
        normalized_document_id = f'normalized-placeholder-{request.source_id}'
        inputs.append(
            {
                'inputId': f'processor-input-{index + 1:03d}',
                'requestMetadata': {
                    'requestId': request.request_id,
                    'sourceId': request.source_id,
                    'sourceType': request.source_type,
                    'owningSurface': request.owning_surface,
                    'reviewedAt': request.reviewed_at,
                    'reviewer': request.reviewer,
                    'priority': request.priority,
                    'allowlistPolicy': request.allowlist_policy,
                    'robotsPolicy': request.robots_policy,
                    'publicOnly': True,
                },
                'processorExpectation': dict(expectation),
                'rateLimitBucket': bucket,
                'processorArguments': {
                    'url': request.url,
                    'canonicalUrl': request.canonical_url,
                    'metadataOnly': True,
                    'persistRawBody': False,
                    'downloadDocuments': False,
                    'normalizedDocumentId': normalized_document_id,
                },
                'normalizedDocumentPlaceholder': {
                    'documentId': normalized_document_id,
                    'sourceId': request.source_id,
                    'canonicalUrl': request.canonical_url,
                    'status': 'placeholder_pending_processor_output',
                    'contentPersisted': False,
                    'sections': [],
                    'tables': [],
                    'links': [],
                    'pdfPages': [],
                    'formFields': [],
                },
                'artifactReferences': {
                    'metadataOnly': True,
                    'archiveManifestRef': f'processor_archive_manifests/{request.source_id}.json',
                    'normalizedDocumentRef': f'normalized_documents/{normalized_document_id}.json',
                    'rawBodyRef': None,
                    'downloadedDocumentRef': None,
                },
            }
        )

    packet = ProcessorHandoffPacket(
        schema_version=1,
        generated_at=generated_at,
        processor_contract_inputs=tuple(inputs),
    )
    data = packet.to_dict()
    errors = validate_processor_handoff_packet(data)
    if errors:
        raise ValueError('processor handoff packet failed validation: ' + '; '.join(errors))
    return data


def validate_processor_handoff_packet(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if packet.get('schemaVersion') != 1:
        errors.append('schemaVersion must be 1')
    generated_at = packet.get('generatedAt')
    if not isinstance(generated_at, str) or not generated_at.endswith('Z'):
        errors.append('generatedAt must be an ISO UTC timestamp ending in Z')

    inputs = packet.get('processorContractInputs')
    if not isinstance(inputs, list) or not inputs:
        errors.append('processorContractInputs must be a non-empty list')
        return errors

    seen_input_ids: set[str] = set()
    for index, item in enumerate(inputs):
        if not isinstance(item, Mapping):
            errors.append(f'processorContractInputs[{index}] must be an object')
            continue
        errors.extend(_validate_contract_input(item, index, seen_input_ids))
    return errors


def _validate_contract_input(item: Mapping[str, Any], index: int, seen_input_ids: set[str]) -> list[str]:
    errors: list[str] = []
    input_id = item.get('inputId')
    if not isinstance(input_id, str) or not input_id.strip():
        errors.append(f'input {index}: inputId is required')
    elif input_id in seen_input_ids:
        errors.append(f'input {index}: duplicate inputId {input_id}')
    else:
        seen_input_ids.add(input_id)

    metadata = _mapping(item.get('requestMetadata'))
    expectation = _mapping(item.get('processorExpectation'))
    arguments = _mapping(item.get('processorArguments'))
    placeholder = _mapping(item.get('normalizedDocumentPlaceholder'))
    artifacts = _mapping(item.get('artifactReferences'))
    bucket = item.get('rateLimitBucket')

    errors.extend(_validate_request_metadata(metadata, index))
    errors.extend(_validate_processor_expectation(expectation, index))
    errors.extend(_validate_processor_arguments(arguments, metadata, index))
    errors.extend(_validate_placeholder(placeholder, metadata, arguments, index))
    errors.extend(_validate_artifacts(artifacts, index))
    if not isinstance(bucket, str) or not bucket.startswith('public-host:'):
        errors.append(f'input {index}: rateLimitBucket must be a public-host bucket')
    return errors


def _validate_request_metadata(metadata: Mapping[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    for field in ('requestId', 'sourceId', 'sourceType', 'owningSurface', 'reviewedAt', 'reviewer'):
        if not isinstance(metadata.get(field), str) or not str(metadata.get(field)).strip():
            errors.append(f'input {index}: requestMetadata.{field} is required')
    if metadata.get('publicOnly') is not True:
        errors.append(f'input {index}: requestMetadata.publicOnly must be true')
    if metadata.get('allowlistPolicy') != 'allowlisted_public_source':
        errors.append(f'input {index}: request must be allowlisted before handoff')
    if metadata.get('robotsPolicy') != 'allowed':
        errors.append(f'input {index}: robotsPolicy must be allowed')
    return errors


def _validate_processor_expectation(expectation: Mapping[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    name = expectation.get('name')
    version = expectation.get('version')
    module = expectation.get('module')
    operation = expectation.get('operation')
    if not isinstance(name, str) or not name.strip():
        errors.append(f'input {index}: processorExpectation.name is required')
    if not isinstance(version, str) or not version.strip():
        errors.append(f'input {index}: processorExpectation.version is required')
    if not isinstance(module, str) or not module.startswith('ipfs_datasets_py.'):
        errors.append(f'input {index}: processorExpectation.module must reference ipfs_datasets_py')
    if operation != 'capture_url_metadata_only':
        errors.append(f'input {index}: processorExpectation.operation must be capture_url_metadata_only')
    return errors


def _validate_processor_arguments(arguments: Mapping[str, Any], metadata: Mapping[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    url = arguments.get('url')
    canonical_url = arguments.get('canonicalUrl')
    errors.extend(_validate_public_url(url, f'input {index}: processorArguments.url'))
    errors.extend(_validate_public_url(canonical_url, f'input {index}: processorArguments.canonicalUrl'))
    if arguments.get('metadataOnly') is not True:
        errors.append(f'input {index}: processorArguments.metadataOnly must be true')
    if arguments.get('persistRawBody') is not False:
        errors.append(f'input {index}: processorArguments.persistRawBody must be false')
    if arguments.get('downloadDocuments') is not False:
        errors.append(f'input {index}: processorArguments.downloadDocuments must be false')
    expected_doc = f"normalized-placeholder-{metadata.get('sourceId')}"
    if arguments.get('normalizedDocumentId') != expected_doc:
        errors.append(f'input {index}: normalizedDocumentId must match sourceId placeholder')
    errors.extend(_reject_raw_artifact_keys(arguments, f'input {index}: processorArguments'))
    return errors


def _validate_placeholder(
    placeholder: Mapping[str, Any],
    metadata: Mapping[str, Any],
    arguments: Mapping[str, Any],
    index: int,
) -> list[str]:
    errors: list[str] = []
    if placeholder.get('documentId') != arguments.get('normalizedDocumentId'):
        errors.append(f'input {index}: placeholder documentId must match processor argument')
    if placeholder.get('sourceId') != metadata.get('sourceId'):
        errors.append(f'input {index}: placeholder sourceId must match request metadata')
    if placeholder.get('contentPersisted') is not False:
        errors.append(f'input {index}: placeholder contentPersisted must be false')
    if placeholder.get('status') != 'placeholder_pending_processor_output':
        errors.append(f'input {index}: placeholder status is invalid')
    for field in ('sections', 'tables', 'links', 'pdfPages', 'formFields'):
        if placeholder.get(field) != []:
            errors.append(f'input {index}: placeholder {field} must be an empty list')
    return errors


def _validate_artifacts(artifacts: Mapping[str, Any], index: int) -> list[str]:
    errors: list[str] = []
    if artifacts.get('metadataOnly') is not True:
        errors.append(f'input {index}: artifactReferences.metadataOnly must be true')
    for field in ('archiveManifestRef', 'normalizedDocumentRef'):
        value = artifacts.get(field)
        if not isinstance(value, str) or not value.endswith('.json'):
            errors.append(f'input {index}: artifactReferences.{field} must be a JSON metadata ref')
    for field in ('rawBodyRef', 'downloadedDocumentRef'):
        if artifacts.get(field) is not None:
            errors.append(f'input {index}: artifactReferences.{field} must be null')
    errors.extend(_reject_raw_artifact_keys(artifacts, f'input {index}: artifactReferences'))
    return errors


def _reviewed_request_from_mapping(item: Mapping[str, Any]) -> ReviewedPublicCrawlRequest:
    request = ReviewedPublicCrawlRequest(
        request_id=str(item.get('requestId', item.get('request_id', ''))),
        source_id=str(item.get('sourceId', item.get('source_id', ''))),
        url=str(item.get('url', '')),
        canonical_url=str(item.get('canonicalUrl', item.get('canonical_url', item.get('url', '')))),
        owning_surface=str(item.get('owningSurface', item.get('owning_surface', ''))),
        reviewed_at=str(item.get('reviewedAt', item.get('reviewed_at', ''))),
        reviewer=str(item.get('reviewer', '')),
        robots_policy=str(item.get('robotsPolicy', item.get('robots_policy', ''))),
        allowlist_policy=str(item.get('allowlistPolicy', item.get('allowlist_policy', ''))),
        source_type=str(item.get('sourceType', item.get('source_type', ''))),
        priority=int(item.get('priority', 50)),
    )
    _raise_for_request_errors(request)
    return request


def _raise_for_request_errors(request: ReviewedPublicCrawlRequest) -> None:
    errors: list[str] = []
    for field in ('request_id', 'source_id', 'owning_surface', 'reviewed_at', 'reviewer', 'source_type'):
        if not getattr(request, field).strip():
            errors.append(f'{field} is required')
    errors.extend(_validate_public_url(request.url, 'url'))
    errors.extend(_validate_public_url(request.canonical_url, 'canonical_url'))
    if request.allowlist_policy != 'allowlisted_public_source':
        errors.append('allowlist_policy must be allowlisted_public_source')
    if request.robots_policy != 'allowed':
        errors.append('robots_policy must be allowed')
    if errors:
        raise ValueError('reviewed crawl request is not handoff-ready: ' + '; '.join(errors))


def _validate_public_url(value: Any, field: str) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return [f'{field} must be a non-empty URL string']
    parsed = urlparse(value)
    if parsed.scheme != 'https':
        return [f'{field} must use https']
    host = parsed.hostname or ''
    if host not in ALLOWED_PUBLIC_HOSTS:
        return [f'{field} host is not PP&D allowlisted: {host}']
    if host == 'devhub.portlandoregon.gov':
        path = '/' + parsed.path.strip('/').lower()
        if any(path == prefix or path.startswith(prefix + '/') for prefix in PRIVATE_DEVHUB_PREFIXES):
            return [f'{field} must not reference private DevHub account paths']
    return []


def _rate_limit_bucket(url: str) -> str:
    host = urlparse(url).hostname or 'unknown'
    return f'public-host:{host}'


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _reject_raw_artifact_keys(value: Any, path: str) -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.replace('-', '_').lower()
            child_path = f'{path}.{key_text}'
            if normalized in RAW_ARTIFACT_KEYS:
                errors.append(f'{child_path} is not allowed in metadata-only handoff packets')
            errors.extend(_reject_raw_artifact_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_reject_raw_artifact_keys(child, f'{path}[{index}]'))
    return errors
