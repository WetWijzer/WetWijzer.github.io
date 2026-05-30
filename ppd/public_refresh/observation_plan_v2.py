'''Fixture-first public refresh observation plan v2.

This module consumes the public refresh readiness packet v2 and emits ordered
per-source observation rows for official PP&D public anchors. It performs no
network access, downloads, DevHub access, registry mutation, or crawl-output
persistence.
'''

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from ppd.public_refresh.readiness_packet_v2 import require_public_refresh_readiness_packet_v2

PACKET_TYPE = 'ppd.public_refresh.observation_plan.v2'
PACKET_VERSION = 'public-refresh-observation-plan-v2'

OFFICIAL_PPD_ANCHORS: list[dict[str, str]] = [
    {'anchor_id': 'ppd-bureau-landing', 'label': 'PP&D bureau landing page', 'url': 'https://www.portland.gov/ppd'},
    {'anchor_id': 'online-permitting-tools', 'label': 'Online permitting tools overview', 'url': 'https://www.portland.gov/ppd/how-use-online-permitting-tools'},
    {'anchor_id': 'devhub-public-portal', 'label': 'DevHub public portal', 'url': 'https://devhub.portlandoregon.gov'},
    {'anchor_id': 'devhub-faq', 'label': 'DevHub FAQ', 'url': 'https://www.portland.gov/ppd/devhub-faqs'},
    {'anchor_id': 'devhub-sign-guide', 'label': 'DevHub account and sign-in guide', 'url': 'https://www.portland.gov/ppd/devhub-sign-guide'},
    {'anchor_id': 'apply-for-permits', 'label': 'Apply for permits', 'url': 'https://www.portland.gov/ppd/get-permit/apply-permits'},
    {'anchor_id': 'devhub-submit-permit-application-guide', 'label': 'DevHub permit application guide', 'url': 'https://www.portland.gov/ppd/devhub-guide-submit-permit-application'},
    {'anchor_id': 'submit-plans-online', 'label': 'Submit Plans Online / Single PDF Process', 'url': 'https://www.portland.gov/ppd/get-permit/submit-plans-online'},
    {'anchor_id': 'permit-applications-forms-index', 'label': 'Permit applications and forms index', 'url': 'https://www.portland.gov/ppd/brochures-forms-handouts/permits-and-inspections-applications'},
    {'anchor_id': 'spp-file-naming-standards', 'label': 'File naming standards and PDF preparation', 'url': 'https://www.portland.gov/ppd/spp-file-naming-standards-preparing-pdfs'},
    {'anchor_id': 'fee-payment-guide', 'label': 'Fee payment guide', 'url': 'https://www.portland.gov/ppd/documents/how-pay-fees/download'},
    {'anchor_id': 'portland-maps-public-references', 'label': 'Portland Maps public references where linked from PP&D guidance', 'url': 'https://www.portlandmaps.com'},
]

ALLOWED_HOSTS = {
    'www.portland.gov',
    'devhub.portlandoregon.gov',
    'www.portlandoregon.gov',
    'www.portlandmaps.com',
}

EXACT_OFFLINE_VALIDATION_COMMANDS: list[list[str]] = [
    ['python3', '-m', 'py_compile', 'ppd/public_refresh/observation_plan_v2.py'],
    ['python3', '-m', 'pytest', 'ppd/tests/test_public_refresh_observation_plan_v2.py'],
    ['python3', 'ppd/daemon/ppd_daemon.py', '--self-test'],
]

_REQUIRED_ROW_FIELDS = {
    'content_hash',
    'last_seen_at',
    'freshness_status',
    'affected_requirement_ids',
    'affected_guardrail_bundle_ids',
}
_REQUIRED_ATTESTATIONS = {'no_raw_public_body_commits', 'metadata_only_fixture_scope'}
_ALLOWED_DISABLED_VALUES = {'', 'false', 'disabled', 'not_allowed', 'not_requested', 'not_touched', 'no', 'none'}
_PRIVATE_KEY_MARKERS = ('auth', 'browser', 'cookie', 'credential', 'download', 'har', 'password', 'private', 'raw', 'session', 'screenshot', 'storage', 'token', 'trace', 'warc')
_PRIVATE_VALUE_MARKERS = ('file://', 'session://', 'warc://', 'crawl://', 'archive://', '/raw/', '/download/', '/downloads/', '/session/', '/sessions/', 'trace.zip', '.har', '.warc', '.warc.gz', 'raw crawl output', 'raw response body', 'downloaded document', 'private session', 'browser trace', 'auth state', 'storage-state.json')
_LIVE_CLAIM_MARKERS = ('live crawl', 'live recrawl', 'fetched live', 'downloaded live', 'network access ran', 'crawler executed', 'captured live')
_ACTION_MARKERS = ('submit application', 'submit permit', 'pay fee', 'schedule inspection', 'upload correction', 'certify acknowledgement', 'purchase permit', 'cancel permit')
_GUARANTEE_MARKERS = ('guaranteed approval', 'permit will issue', 'will be approved', 'legal advice', 'ensures compliance', 'no legal risk', 'permitting guarantee', 'guaranteed permit')
_MUTATION_SUBJECTS = ('source', 'requirement', 'process', 'guardrail', 'release_state')
_MUTATION_TERMS = ('mutation', 'mutated', 'mutate', 'write', 'update', 'enabled', 'allowed')


@dataclass(frozen=True)
class PublicRefreshObservationPlanV2ValidationResult:
    valid: bool
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return self.valid

    def as_dict(self) -> dict[str, Any]:
        return {'valid': self.valid, 'errors': list(self.errors)}


def build_public_refresh_observation_plan_v2(readiness_packet: Mapping[str, Any]) -> dict[str, Any]:
    require_public_refresh_readiness_packet_v2(readiness_packet)
    policy_by_group = _policy_placeholders_by_group(readiness_packet)
    freshness_by_group = _freshness_placeholders_by_group(readiness_packet)
    attestation_ids = [str(item['attestation_id']) for item in readiness_packet['raw_body_non_persistence_attestations']]
    observation_rows = [
        _observation_row(order=index, anchor=anchor, policy_by_group=policy_by_group, freshness_by_group=freshness_by_group, attestation_ids=attestation_ids)
        for index, anchor in enumerate(OFFICIAL_PPD_ANCHORS, start=1)
    ]
    plan = {
        'packet_type': PACKET_TYPE,
        'packet_version': PACKET_VERSION,
        'packet_id': 'fixture-first-public-refresh-observation-plan-v2',
        'source_readiness_packet_id': readiness_packet.get('packet_id'),
        'source_readiness_packet_version': readiness_packet.get('packet_version'),
        'generated_from_fixture_at': readiness_packet.get('generated_from_fixture_at'),
        'fixture_first': True,
        'network_access': 'not_requested',
        'document_downloads': 'not_allowed',
        'devhub_scope': 'not_touched',
        'crawl_output_storage': 'not_allowed',
        'raw_body_persistence': 'not_allowed',
        'active_source_registry_changes': 'not_allowed',
        'active_requirement_registry_changes': 'not_allowed',
        'active_process_registry_changes': 'not_allowed',
        'active_guardrail_registry_changes': 'not_allowed',
        'official_anchor_count': len(OFFICIAL_PPD_ANCHORS),
        'ordered_public_refresh_observation_rows': observation_rows,
        'no_raw_body_persistence_attestations': [
            {'attestation_id': attestation_id, 'source_readiness_packet_id': readiness_packet.get('packet_id'), 'applies_to_all_observation_rows': True, 'status': 'carried_forward_from_readiness_packet'}
            for attestation_id in attestation_ids
        ],
        'exact_offline_validation_commands': deepcopy(EXACT_OFFLINE_VALIDATION_COMMANDS),
    }
    require_public_refresh_observation_plan_v2(plan)
    return plan


def validate_public_refresh_observation_plan_v2(packet: Mapping[str, Any]) -> PublicRefreshObservationPlanV2ValidationResult:
    errors: list[str] = []
    if not isinstance(packet, Mapping):
        return PublicRefreshObservationPlanV2ValidationResult(False, ('packet must be an object',))
    if packet.get('packet_type') != PACKET_TYPE:
        errors.append(f'packet_type must be {PACKET_TYPE}')
    if packet.get('packet_version') != PACKET_VERSION:
        errors.append(f'packet_version must be {PACKET_VERSION}')
    if packet.get('fixture_first') is not True:
        errors.append('fixture_first must be true')
    for field in ('network_access', 'document_downloads', 'devhub_scope', 'crawl_output_storage', 'raw_body_persistence', 'active_source_registry_changes', 'active_requirement_registry_changes', 'active_process_registry_changes', 'active_guardrail_registry_changes'):
        if packet.get(field) not in {'not_requested', 'not_allowed', 'not_touched'}:
            errors.append(f'{field} must remain disabled')
    rows = _mapping_sequence(packet.get('ordered_public_refresh_observation_rows'))
    if len(rows) != len(OFFICIAL_PPD_ANCHORS):
        errors.append('ordered_public_refresh_observation_rows must cover every official PP&D anchor')
    if packet.get('official_anchor_count') != len(OFFICIAL_PPD_ANCHORS):
        errors.append('official_anchor_count must match official anchors')
    if [row.get('order') for row in rows] != list(range(1, len(rows) + 1)):
        errors.append('ordered_public_refresh_observation_rows must be contiguous and ordered')
    if [str(row.get('official_anchor_url', '')) for row in rows] != [anchor['url'] for anchor in OFFICIAL_PPD_ANCHORS]:
        errors.append('ordered_public_refresh_observation_rows must preserve the official PP&D anchor order')
    for index, row in enumerate(rows):
        _validate_row(errors, index, row)
    attestations = _mapping_sequence(packet.get('no_raw_body_persistence_attestations'))
    attestation_ids = {str(item.get('attestation_id', '')) for item in attestations}
    missing = sorted(_REQUIRED_ATTESTATIONS.difference(attestation_ids))
    if missing:
        errors.append('no_raw_body_persistence_attestations missing: ' + ', '.join(missing))
    for index, item in enumerate(attestations):
        if item.get('applies_to_all_observation_rows') is not True:
            errors.append(f'no_raw_body_persistence_attestations[{index}].applies_to_all_observation_rows must be true')
    if _command_sequence(packet.get('exact_offline_validation_commands')) != EXACT_OFFLINE_VALIDATION_COMMANDS:
        errors.append('exact_offline_validation_commands must match the observation plan v2 offline command list')
    _validate_recursive_safety(errors, packet)
    return PublicRefreshObservationPlanV2ValidationResult(not errors, tuple(errors))


def require_public_refresh_observation_plan_v2(packet: Mapping[str, Any]) -> None:
    result = validate_public_refresh_observation_plan_v2(packet)
    if not result.valid:
        raise ValueError('invalid public refresh observation plan v2: ' + '; '.join(result.errors))


def _observation_row(*, order: int, anchor: Mapping[str, str], policy_by_group: Mapping[str, Mapping[str, Any]], freshness_by_group: Mapping[str, Mapping[str, Any]], attestation_ids: Sequence[str]) -> dict[str, Any]:
    url = anchor['url']
    source_group_id = _source_group_id(url)
    policy = policy_by_group.get(source_group_id, {})
    freshness = freshness_by_group.get(source_group_id, {})
    return {
        'order': order,
        'observation_row_id': f'public-refresh-observation-v2:{order:03d}:{anchor["anchor_id"]}',
        'official_anchor_id': anchor['anchor_id'],
        'official_anchor_label': anchor['label'],
        'official_anchor_url': url,
        'source_group_id': source_group_id,
        'canonical_url_placeholder': 'placeholder_canonical_url_pending_metadata_capture',
        'allowlist_decision_placeholder': policy.get('allowlist_review_status', 'placeholder_pending_human_review'),
        'robots_decision_placeholder': policy.get('robots_review_status', 'placeholder_pending_human_review'),
        'expected_freshness_signal_placeholders': {'comparison_status': freshness.get('comparison_status', 'placeholder_not_run'), 'current_manifest_ref': freshness.get('current_manifest_ref', 'placeholder_current_manifest_ref'), 'candidate_manifest_ref': freshness.get('candidate_manifest_ref', 'placeholder_candidate_manifest_ref'), 'expected_signal_fields': list(freshness.get('expected_comparison_fields', sorted(_REQUIRED_ROW_FIELDS)))},
        'no_raw_body_persistence_attestation_ids': list(attestation_ids),
        'observation_status': 'placeholder_not_run',
        'metadata_only': True,
        'network_request_performed': False,
        'document_download_performed': False,
        'raw_body_persisted': False,
        'crawl_output_stored': False,
        'active_registry_mutated': False,
    }


def _policy_placeholders_by_group(readiness_packet: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {str(item['source_group_id']): item for item in _mapping_sequence(readiness_packet.get('allowlist_and_robots_review_placeholders')) if item.get('source_group_id')}


def _freshness_placeholders_by_group(readiness_packet: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {str(item['source_group_id']): item for item in _mapping_sequence(readiness_packet.get('source_freshness_comparison_placeholders')) if item.get('source_group_id')}


def _source_group_id(url: str) -> str:
    host = urlparse(url).hostname or ''
    if host == 'devhub.portlandoregon.gov':
        return 'devhub_public_guidance'
    return 'portland_gov_ppd_public_guidance'


def _validate_row(errors: list[str], index: int, row: Mapping[str, Any]) -> None:
    prefix = f'ordered_public_refresh_observation_rows[{index}]'
    for field in ('observation_row_id', 'official_anchor_id', 'official_anchor_label', 'official_anchor_url', 'source_group_id', 'canonical_url_placeholder', 'allowlist_decision_placeholder', 'robots_decision_placeholder', 'expected_freshness_signal_placeholders', 'no_raw_body_persistence_attestation_ids', 'observation_status'):
        if field in {'expected_freshness_signal_placeholders', 'no_raw_body_persistence_attestation_ids'}:
            continue
        if not _text(row.get(field)):
            errors.append(f'{prefix}.{field} must be present')
    parsed = urlparse(_text(row.get('official_anchor_url')))
    if parsed.scheme != 'https' or parsed.hostname not in ALLOWED_HOSTS:
        errors.append(f'{prefix}.official_anchor_url must be an allowlisted HTTPS public URL')
    if not _text(row.get('canonical_url_placeholder')).startswith('placeholder_'):
        errors.append(f'{prefix}.canonical_url_placeholder must remain a placeholder')
    for field in ('allowlist_decision_placeholder', 'robots_decision_placeholder'):
        if 'placeholder' not in _text(row.get(field)):
            errors.append(f'{prefix}.{field} must remain a decision placeholder')
    signals = row.get('expected_freshness_signal_placeholders')
    if not isinstance(signals, Mapping):
        errors.append(f'{prefix}.expected_freshness_signal_placeholders must be an object')
    else:
        missing = sorted(_REQUIRED_ROW_FIELDS.difference(_string_set(signals.get('expected_signal_fields'))))
        if missing:
            errors.append(f'{prefix}.expected_freshness_signal_placeholders.expected_signal_fields missing: {", ".join(missing)}')
        if _text(signals.get('comparison_status')) != 'placeholder_not_run':
            errors.append(f'{prefix}.expected_freshness_signal_placeholders.comparison_status must be placeholder_not_run')
    missing_attestations = sorted(_REQUIRED_ATTESTATIONS.difference(_string_set(row.get('no_raw_body_persistence_attestation_ids'))))
    if missing_attestations:
        errors.append(f'{prefix}.no_raw_body_persistence_attestation_ids missing: {", ".join(missing_attestations)}')
    for false_field in ('network_request_performed', 'document_download_performed', 'raw_body_persisted', 'crawl_output_stored', 'active_registry_mutated'):
        if row.get(false_field) is not False:
            errors.append(f'{prefix}.{false_field} must be false')
    if row.get('metadata_only') is not True:
        errors.append(f'{prefix}.metadata_only must be true')


def _validate_recursive_safety(errors: list[str], value: Any, path: str = 'packet') -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.lower().replace('-', '_')
            child_path = f'{path}.{key_text}'
            if normalized_key not in {'raw_body_persistence', 'raw_body_persisted', 'no_raw_body_persistence_attestation_ids', 'no_raw_body_persistence_attestations'}:
                if _private_artifact_key(normalized_key) and _truthy_or_text(child):
                    errors.append(f'{child_path} must not include private, browser, raw, download, session, or crawl-output artifacts')
            if _active_mutation_key(normalized_key) and _mutation_flag_enabled(child):
                errors.append(f'{child_path} must not enable active source, requirement, process, guardrail, or release-state mutation')
            if normalized_key in {'network_request_performed', 'document_download_performed', 'raw_body_persisted', 'crawl_output_stored', 'active_registry_mutated'} and child is not False:
                errors.append(f'{child_path} must be false')
            _validate_recursive_safety(errors, child, child_path)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            _validate_recursive_safety(errors, child, f'{path}[{index}]')
        return
    if isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in _PRIVATE_VALUE_MARKERS):
            errors.append(f'{path} must not reference private, browser, raw, download, session, or crawl-output artifacts')
        if any(marker in lowered for marker in _LIVE_CLAIM_MARKERS):
            errors.append(f'{path} must not claim live crawl or network execution')
        if any(marker in lowered for marker in _ACTION_MARKERS):
            errors.append(f'{path} must not use consequential official action language')
        if any(marker in lowered for marker in _GUARANTEE_MARKERS):
            errors.append(f'{path} must not guarantee legal or permitting outcomes')
        if _active_mutation_text(lowered):
            errors.append(f'{path} must not reference active source, requirement, process, guardrail, or release-state mutation')


def _private_artifact_key(key: str) -> bool:
    parts = [part for part in key.split('_') if part]
    return any(marker in parts for marker in _PRIVATE_KEY_MARKERS)


def _active_mutation_key(key: str) -> bool:
    parts = [part for part in key.split('_') if part]
    compact = key.replace('_registry', '')
    if not any(subject in compact for subject in _MUTATION_SUBJECTS):
        return False
    return any(term in parts or compact.endswith('_' + term) for term in _MUTATION_TERMS)


def _active_mutation_text(text: str) -> bool:
    normalized = text.replace('-', '_')
    if not any(subject in normalized for subject in _MUTATION_SUBJECTS):
        return False
    return any(term in normalized for term in ('active', 'enable', 'enabled', 'apply', 'write', 'mutate', 'mutation'))


def _mutation_flag_enabled(value: Any) -> bool:
    if isinstance(value, bool):
        return value is True
    if isinstance(value, str):
        return value.strip().lower() not in _ALLOWED_DISABLED_VALUES
    if isinstance(value, Mapping):
        return any(value.get(key) is True for key in ('enabled', 'allowed', 'active', 'mutates', 'mutation_enabled'))
    return value is not None


def _mapping_sequence(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _command_sequence(value: Any) -> list[list[str]]:
    if not isinstance(value, list):
        return []
    commands: list[list[str]] = []
    for command in value:
        if not isinstance(command, list) or not command:
            return []
        parts: list[str] = []
        for part in command:
            if not isinstance(part, str) or not part:
                return []
            parts.append(part)
        commands.append(parts)
    return commands


def _string_set(value: Any) -> set[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return set()
    return {item.strip() for item in value if isinstance(item, str) and item.strip()}


def _truthy_or_text(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return bool(value.strip())
    return value is not None


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ''
