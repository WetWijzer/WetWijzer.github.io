from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


REQUIRED_SCHEMA_ID = 'portland_ppd.active_promotion_application_manifest'
REQUIRED_SCHEMA_VERSION = '1.0.0'

_REQUIRED_SECTIONS: tuple[str, ...] = (
    'target_fixture_family_rows',
    'source_inactive_artifact_references',
    'destination_active_artifact_placeholders',
    'expected_checksum_placeholders',
    'ordered_validation_replay_inventory',
    'rollback_checkpoint_references',
    'reviewer_approval_placeholders',
)

_REQUIRED_ROW_FIELDS: dict[str, tuple[str, ...]] = {
    'target_fixture_family_rows': (
        'row_id',
        'fixture_family',
        'source_packet_id',
        'source_artifact_ref',
        'destination_artifact_placeholder',
        'expected_checksum_placeholder',
        'validation_replay_id',
        'rollback_checkpoint_ref',
        'reviewer_approval_placeholder',
    ),
    'source_inactive_artifact_references': ('artifact_ref', 'artifact_kind', 'status'),
    'destination_active_artifact_placeholders': ('placeholder_ref', 'target_path_placeholder', 'write_policy'),
    'expected_checksum_placeholders': ('artifact_ref', 'algorithm', 'expected'),
    'ordered_validation_replay_inventory': ('order', 'replay_id', 'assertion'),
    'rollback_checkpoint_references': ('checkpoint_ref', 'scope'),
    'reviewer_approval_placeholders': ('placeholder_ref', 'approval_state'),
}

_FORBIDDEN_KEYS: set[str] = {
    'access_token',
    'auth',
    'auth_file',
    'auth_files',
    'auth_state',
    'authenticated_artifact',
    'browser_artifact',
    'browser_context',
    'browser_state',
    'cookie',
    'cookies',
    'credential',
    'credentials',
    'devhub_session',
    'downloaded_artifact',
    'downloaded_data',
    'downloaded_document',
    'downloaded_pdf',
    'har',
    'har_file',
    'har_files',
    'password',
    'private_artifact',
    'raw_body',
    'raw_crawl',
    'raw_crawl_output',
    'raw_data',
    'raw_download',
    'raw_html',
    'raw_pdf',
    'screenshot',
    'screenshots',
    'session',
    'session_artifact',
    'session_state',
    'storage_state',
    'token',
    'trace',
    'trace_file',
    'trace_files',
    'traces',
}

_FORBIDDEN_TEXT: tuple[tuple[str, tuple[str, ...]], ...] = (
    ('private_or_authenticated_artifact', ('private artifact', 'authenticated artifact', 'logged-in page', 'signed-in page', 'private applicant')),
    ('session_or_browser_artifact', ('devhub session', 'authenticated session', 'private session', 'session cookie', 'session artifact', 'browser artifact', 'browser state', 'storage state', 'access token', 'refresh token')),
    ('screenshot_trace_har_or_auth_file', ('screenshot', 'screenshots', 'playwright trace', 'trace file', 'trace.zip', 'har file', '.har', 'auth file', 'auth state')),
    ('raw_crawl_pdf_or_downloaded_data', ('raw crawl', 'raw html', 'raw body', 'raw pdf', 'downloaded data', 'downloaded document', 'downloaded pdf')),
    ('live_execution_or_release_claim', ('live execution', 'live crawl executed', 'live source crawled', 'promotion executed', 'promoted to active', 'promotion complete', 'release complete', 'release-complete')),
    ('legal_or_permitting_outcome_guarantee', ('approval guaranteed', 'guaranteed approval', 'permit guaranteed', 'guaranteed permit', 'will be approved', 'legally compliant', 'no legal risk', 'guaranteed outcome', 'permitting outcome guaranteed', 'legal outcome guaranteed')),
    ('consequential_action_language', ('agent will submit', 'automation will submit', 'click submit', 'click pay', 'enter payment', 'execute payment', 'submit permit', 'perform upload', 'upload official', 'agent will certify', 'agent will upload', 'agent will pay', 'schedule inspection', 'cancel permit')),
)

_MUTATION_DOMAINS: tuple[str, ...] = (
    'active_artifact',
    'active_artifacts',
    'active_prompt',
    'prompt',
    'prompts',
    'release_state',
    'active_release_state',
    'fixture',
    'fixtures',
    'agent_state',
    'active_agent_state',
)

_MUTATION_TERMS: tuple[str, ...] = (
    'mutated',
    'mutation',
    'changed',
    'updated',
    'applied',
    'requested',
)


@dataclass(frozen=True)
class ActivePromotionApplicationManifestV1Result:
    valid: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {'valid': self.valid, 'problems': list(self.problems)}


class ActivePromotionApplicationManifestV1Error(ValueError):
    def __init__(self, problems: tuple[str, ...]) -> None:
        self.problems = problems
        super().__init__('invalid active promotion application manifest v1: ' + '; '.join(problems))


def validate_active_promotion_application_manifest_v1(manifest: Mapping[str, Any]) -> ActivePromotionApplicationManifestV1Result:
    problems: list[str] = []
    if not isinstance(manifest, Mapping):
        return ActivePromotionApplicationManifestV1Result(False, ('manifest_must_be_object',))

    if manifest.get('schema_id') != REQUIRED_SCHEMA_ID:
        problems.append('invalid_schema_id')
    if manifest.get('schema_version') != REQUIRED_SCHEMA_VERSION:
        problems.append('invalid_schema_version')

    for section in _REQUIRED_SECTIONS:
        _validate_required_rows(manifest, section, problems)

    target_rows = _rows(manifest.get('target_fixture_family_rows'))
    source_refs = _field_values(manifest.get('source_inactive_artifact_references'), 'artifact_ref')
    destination_refs = _field_values(manifest.get('destination_active_artifact_placeholders'), 'placeholder_ref')
    checksum_refs = _field_values(manifest.get('expected_checksum_placeholders'), 'expected')
    replay_refs = _field_values(manifest.get('ordered_validation_replay_inventory'), 'replay_id')
    rollback_refs = _field_values(manifest.get('rollback_checkpoint_references'), 'checkpoint_ref')
    reviewer_refs = _field_values(manifest.get('reviewer_approval_placeholders'), 'placeholder_ref')

    _validate_ordered_replay_inventory(manifest.get('ordered_validation_replay_inventory'), problems)
    _validate_reference_prefixes(manifest, problems)

    for index, row in enumerate(target_rows):
        _require_referenced(row.get('source_artifact_ref'), source_refs, f'target_fixture_family_rows[{index}].source_artifact_ref', problems)
        _require_referenced(row.get('destination_artifact_placeholder'), destination_refs, f'target_fixture_family_rows[{index}].destination_artifact_placeholder', problems)
        _require_referenced(row.get('expected_checksum_placeholder'), checksum_refs, f'target_fixture_family_rows[{index}].expected_checksum_placeholder', problems)
        _require_referenced(row.get('validation_replay_id'), replay_refs, f'target_fixture_family_rows[{index}].validation_replay_id', problems)
        _require_referenced(row.get('rollback_checkpoint_ref'), rollback_refs, f'target_fixture_family_rows[{index}].rollback_checkpoint_ref', problems)
        _require_referenced(row.get('reviewer_approval_placeholder'), reviewer_refs, f'target_fixture_family_rows[{index}].reviewer_approval_placeholder', problems)

    _scan_for_forbidden_content(manifest, '$', problems)
    unique = tuple(sorted(dict.fromkeys(problems)))
    return ActivePromotionApplicationManifestV1Result(valid=not unique, problems=unique)


def require_active_promotion_application_manifest_v1_valid(manifest: Mapping[str, Any]) -> None:
    result = validate_active_promotion_application_manifest_v1(manifest)
    if not result.valid:
        raise ActivePromotionApplicationManifestV1Error(result.problems)


def _validate_required_rows(manifest: Mapping[str, Any], section: str, problems: list[str]) -> None:
    rows = manifest.get(section)
    if not isinstance(rows, list) or not rows:
        problems.append('missing_' + section)
        return
    required_fields = _REQUIRED_ROW_FIELDS[section]
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            problems.append(f'{section}[{index}]:row_must_be_object')
            continue
        for field in required_fields:
            if field == 'order':
                if not isinstance(row.get(field), int):
                    problems.append(f'{section}[{index}]:missing_{field}')
            elif not _has_text(row.get(field)):
                problems.append(f'{section}[{index}]:missing_{field}')


def _validate_ordered_replay_inventory(rows_value: Any, problems: list[str]) -> None:
    rows = _rows(rows_value)
    if not rows:
        return
    expected_order = list(range(1, len(rows) + 1))
    actual_order = [row.get('order') for row in rows]
    if actual_order != expected_order:
        problems.append('ordered_validation_replay_inventory:order_must_be_contiguous_from_one')


def _validate_reference_prefixes(manifest: Mapping[str, Any], problems: list[str]) -> None:
    for index, row in enumerate(_rows(manifest.get('source_inactive_artifact_references'))):
        if not _has_prefix(row.get('artifact_ref'), 'inactive-artifact://'):
            problems.append(f'source_inactive_artifact_references[{index}].artifact_ref:must_be_inactive_artifact_ref')
    for index, row in enumerate(_rows(manifest.get('destination_active_artifact_placeholders'))):
        if not _has_prefix(row.get('placeholder_ref'), 'active-artifact-placeholder://'):
            problems.append(f'destination_active_artifact_placeholders[{index}].placeholder_ref:must_be_active_placeholder_ref')
        if row.get('write_policy') != 'placeholder_only_no_write':
            problems.append(f'destination_active_artifact_placeholders[{index}].write_policy:must_be_placeholder_only_no_write')
    for index, row in enumerate(_rows(manifest.get('expected_checksum_placeholders'))):
        if row.get('algorithm') != 'sha256':
            problems.append(f'expected_checksum_placeholders[{index}].algorithm:must_be_sha256')
        if not _has_prefix(row.get('expected'), 'sha256:PLACEHOLDER_'):
            problems.append(f'expected_checksum_placeholders[{index}].expected:must_be_checksum_placeholder')
    for index, row in enumerate(_rows(manifest.get('rollback_checkpoint_references'))):
        if not _has_prefix(row.get('checkpoint_ref'), 'rollback-checkpoint://'):
            problems.append(f'rollback_checkpoint_references[{index}].checkpoint_ref:must_be_rollback_checkpoint_ref')
    for index, row in enumerate(_rows(manifest.get('reviewer_approval_placeholders'))):
        if not _has_prefix(row.get('placeholder_ref'), 'reviewer-approval://'):
            problems.append(f'reviewer_approval_placeholders[{index}].placeholder_ref:must_be_reviewer_approval_placeholder')
        if row.get('approval_state') != 'placeholder_not_approved':
            problems.append(f'reviewer_approval_placeholders[{index}].approval_state:must_be_placeholder_not_approved')


def _require_referenced(value: Any, allowed: set[str], path: str, problems: list[str]) -> None:
    if not isinstance(value, str) or value not in allowed:
        problems.append(path + ':missing_referenced_placeholder')


def _scan_for_forbidden_content(value: Any, path: str, problems: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized_key = _normalize_key(key)
            child_path = path + '.' + str(key)
            if normalized_key in _FORBIDDEN_KEYS:
                problems.append(child_path + ':forbidden_artifact_key')
            if child is True and _is_mutation_flag(normalized_key):
                problems.append(child_path + ':forbidden_mutation_flag')
            _scan_for_forbidden_content(child, child_path, problems)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_for_forbidden_content(child, f'{path}[{index}]', problems)
    elif isinstance(value, str):
        lowered = value.lower()
        for code, needles in _FORBIDDEN_TEXT:
            if any(needle in lowered for needle in needles):
                problems.append(path + ':' + code)


def _is_mutation_flag(normalized_key: str) -> bool:
    return any(domain in normalized_key for domain in _MUTATION_DOMAINS) and any(term in normalized_key for term in _MUTATION_TERMS)


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [row for row in value if isinstance(row, Mapping)]


def _field_values(value: Any, field: str) -> set[str]:
    output: set[str] = set()
    for row in _rows(value):
        field_value = row.get(field)
        if isinstance(field_value, str) and field_value.strip():
            output.add(field_value)
    return output


def _has_prefix(value: Any, prefix: str) -> bool:
    return isinstance(value, str) and value.startswith(prefix)


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _normalize_key(value: Any) -> str:
    return str(value).strip().lower().replace('-', '_').replace(' ', '_')


__all__ = [
    'ActivePromotionApplicationManifestV1Error',
    'ActivePromotionApplicationManifestV1Result',
    'REQUIRED_SCHEMA_ID',
    'REQUIRED_SCHEMA_VERSION',
    'require_active_promotion_application_manifest_v1_valid',
    'validate_active_promotion_application_manifest_v1',
]
