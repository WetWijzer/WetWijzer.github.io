from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

PACKET_VERSION = 'public_source_recrawl_inactive_patch_preview_v1'
REVIEWER_PACKET_VERSION = 'public_source_recrawl_reviewer_disposition_packet_v1'
APPROVED_DECISION = 'approve_for_metadata_only_recrawl'
INACTIVE_STATE = 'inactive_preview_only'

VALIDATION_COMMANDS = (
    ('python3', 'ppd/daemon/ppd_daemon.py', '--self-test'),
    ('python3', '-m', 'unittest', 'ppd.tests.test_public_source_recrawl_inactive_patch_preview_v1'),
)

FALSE_FLAGS = (
    'live_network_invoked',
    'crawl_executed',
    'recrawl_executed',
    'documents_downloaded',
    'payloads_stored',
    'devhub_accessed',
    'authenticated_session_used',
    'browser_artifacts_created',
    'active_artifacts_mutated',
    'active_source_artifacts_mutated',
    'active_process_artifacts_mutated',
    'active_requirement_artifacts_mutated',
    'active_guardrail_artifacts_mutated',
    'active_prompt_artifacts_mutated',
    'active_release_state_mutated',
)

UNSAFE_KEYS = {
    'auth_state_ref',
    'authenticated_session_ref',
    'browser_artifact_ref',
    'cookie_artifact_ref',
    'downloaded_document_ref',
    'har_artifact_ref',
    'private_artifact_ref',
    'session_artifact_ref',
}

UNSAFE_TEXT = {
    'live_execution_claim': ('live network', 'network request executed', 'crawl was executed', 'recrawl was executed'),
    'payload_or_download_claim': ('downloaded document', 'downloaded pdf', 'raw crawl', 'raw response', 'response body retained'),
    'consequential_devhub_action_language': ('submit permit', 'submit application', 'upload correction', 'pay fee', 'schedule inspection', 'purchase permit', 'certify acknowledgement'),
    'legal_or_permitting_outcome_guarantee': ('permit will be approved', 'approval is guaranteed', 'will pass inspection', 'legal determination'),
    'active_mutation_claim': ('active artifact mutation', 'active guardrail mutation', 'active prompt mutation', 'active release-state mutation'),
}


@dataclass(frozen=True)
class PublicSourceRecrawlInactivePatchPreviewIssue:
    code: str
    path: str
    message: str


class PublicSourceRecrawlInactivePatchPreviewError(ValueError):
    def __init__(self, issues: Sequence[PublicSourceRecrawlInactivePatchPreviewIssue]) -> None:
        self.issues = tuple(issues)
        super().__init__('; '.join(f'{issue.path}: {issue.code}: {issue.message}' for issue in self.issues))


def build_public_source_recrawl_inactive_patch_preview_v1(disposition_packet: Mapping[str, Any]) -> dict[str, Any]:
    manifest_ref = disposition_packet.get('dry_run_manifest_ref')
    if not isinstance(manifest_ref, Mapping):
        manifest_ref = {}

    decisions = [row for row in _rows(disposition_packet.get('reviewer_decisions'))]
    approved = [row for row in decisions if _text(row.get('decision')) == APPROVED_DECISION]
    held = [row for row in decisions if _text(row.get('decision')) != APPROVED_DECISION]

    registry = []
    archive = []
    documents = []
    freshness = []
    for row in approved:
        source_id = _text(row.get('source_id'))
        url = _text(row.get('canonical_url'))
        registry.append({
            'delta_id': f'inactive-source-registry-delta-{source_id}',
            'source_id': source_id,
            'canonical_url': url,
            'inactive_patch_state': INACTIVE_STATE,
            'operation': 'metadata_placeholder_delta_after_future_review',
            'privacy_classification': 'public_metadata_only',
            'metadata_only_artifact_expectation_id': _text(row.get('metadata_only_artifact_expectation_id')),
        })
        archive.append({
            'delta_id': f'inactive-archive-manifest-delta-{source_id}',
            'source_id': source_id,
            'canonical_url': url,
            'inactive_patch_state': INACTIVE_STATE,
            'requested_url_placeholder': url,
            'http_status_placeholder': 'pending_future_metadata_capture',
            'content_type_placeholder': 'pending_future_metadata_capture',
            'content_hash_placeholder': f'pending-content-hash-{source_id}',
            'processor_name_placeholder': 'pending_processor_suite_metadata_adapter',
            'normalized_document_id_placeholder': f'pending-normalized-document-{source_id}',
            'no_payload_persisted': True,
        })
        documents.append({
            'document_reference_id': f'inactive-normalized-document-ref-{source_id}',
            'source_id': source_id,
            'canonical_url': url,
            'inactive_patch_state': INACTIVE_STATE,
            'document_id_placeholder': f'pending-normalized-document-{source_id}',
            'title_placeholder': f'Pending normalized public document metadata for {source_id}',
            'citation_span_placeholder': f'citation-placeholder-{source_id}',
        })
        freshness.append({
            'replay_note_id': f'inactive-freshness-replay-note-{source_id}',
            'source_id': source_id,
            'source_freshness_update_placeholder_id': _text(row.get('source_freshness_update_placeholder_id')),
            'inactive_patch_state': INACTIVE_STATE,
            'expected_replay_note': 'Replay reviewer disposition and metadata placeholders before any later active promotion gate.',
        })

    packet: dict[str, Any] = {
        'packet_version': PACKET_VERSION,
        'fixture_first': True,
        'inactive_patch_preview': True,
        'metadata_only': True,
        'reviewer_disposition_packet_ref': {
            'packet_version': _text(disposition_packet.get('packet_version')) or REVIEWER_PACKET_VERSION,
            'dry_run_manifest_id': _text(manifest_ref.get('manifest_id')),
            'dry_run_manifest_version': _text(manifest_ref.get('manifest_version')),
        },
        'approved_reviewer_disposition_rows': tuple(dict(row) for row in approved),
        'source_registry_delta_placeholders': registry,
        'archive_manifest_delta_placeholders': archive,
        'normalized_document_reference_placeholders': documents,
        'freshness_monitor_replay_notes': freshness,
        'held_or_skipped_reviewer_disposition_notes': [
            {
                'source_id': _text(row.get('source_id')),
                'canonical_url': _text(row.get('canonical_url')),
                'decision': _text(row.get('decision')),
                'inactive_patch_state': INACTIVE_STATE,
                'preview_effect': 'excluded_from_inactive_delta_placeholders',
            }
            for row in held
        ],
        'validation_commands': VALIDATION_COMMANDS,
    }
    for flag in FALSE_FLAGS:
        packet[flag] = False
    return packet


def validate_public_source_recrawl_inactive_patch_preview_v1(packet: Mapping[str, Any]) -> list[PublicSourceRecrawlInactivePatchPreviewIssue]:
    issues: list[PublicSourceRecrawlInactivePatchPreviewIssue] = []
    if not isinstance(packet, Mapping):
        return [PublicSourceRecrawlInactivePatchPreviewIssue('invalid_packet', '$', 'packet must be an object')]
    if packet.get('packet_version') != PACKET_VERSION:
        issues.append(PublicSourceRecrawlInactivePatchPreviewIssue('invalid_packet_version', '$.packet_version', f'packet_version must be {PACKET_VERSION}'))
    for key in ('fixture_first', 'inactive_patch_preview', 'metadata_only'):
        if packet.get(key) is not True:
            issues.append(PublicSourceRecrawlInactivePatchPreviewIssue('missing_required_true_flag', f'$.{key}', f'{key} must be true'))
    for flag in FALSE_FLAGS:
        if packet.get(flag) is not False:
            issues.append(PublicSourceRecrawlInactivePatchPreviewIssue('unsafe_execution_or_mutation_flag', f'$.{flag}', 'execution, DevHub access, payload storage, and active mutation flags must be false'))

    ref = packet.get('reviewer_disposition_packet_ref')
    if not isinstance(ref, Mapping) or _text(ref.get('packet_version')) != REVIEWER_PACKET_VERSION or not _text(ref.get('dry_run_manifest_id')):
        issues.append(PublicSourceRecrawlInactivePatchPreviewIssue('missing_reviewer_disposition_ref', '$.reviewer_disposition_packet_ref', 'reviewer disposition packet reference and manifest id are required'))

    approved = _source_ids(packet.get('approved_reviewer_disposition_rows'), '$.approved_reviewer_disposition_rows', issues)
    for key in ('source_registry_delta_placeholders', 'archive_manifest_delta_placeholders', 'normalized_document_reference_placeholders', 'freshness_monitor_replay_notes'):
        ids = _source_ids(packet.get(key), f'$.{key}', issues)
        if approved and ids != approved:
            issues.append(PublicSourceRecrawlInactivePatchPreviewIssue('placeholder_source_mismatch', f'$.{key}', 'placeholder source_ids must exactly match approved reviewer disposition rows'))
        for index, row in enumerate(_rows(packet.get(key))):
            if _text(row.get('inactive_patch_state')) != INACTIVE_STATE:
                issues.append(PublicSourceRecrawlInactivePatchPreviewIssue('not_inactive_preview', f'$.{key}[{index}].inactive_patch_state', 'placeholder row must be inactive_preview_only'))

    if _commands(packet.get('validation_commands')) != VALIDATION_COMMANDS:
        issues.append(PublicSourceRecrawlInactivePatchPreviewIssue('missing_validation_commands', '$.validation_commands', 'exact offline validation commands are required'))
    _scan(packet, '$', issues)
    return _dedupe(issues)


def require_valid_public_source_recrawl_inactive_patch_preview_v1(packet: Mapping[str, Any]) -> None:
    issues = validate_public_source_recrawl_inactive_patch_preview_v1(packet)
    if issues:
        raise PublicSourceRecrawlInactivePatchPreviewError(issues)


def _source_ids(value: Any, path: str, issues: list[PublicSourceRecrawlInactivePatchPreviewIssue]) -> set[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        issues.append(PublicSourceRecrawlInactivePatchPreviewIssue('missing_placeholder_rows', path, 'placeholder rows must be a non-empty list'))
        return set()
    ids = set()
    for index, row in enumerate(value):
        if not isinstance(row, Mapping):
            issues.append(PublicSourceRecrawlInactivePatchPreviewIssue('invalid_placeholder_row', f'{path}[{index}]', 'row must be an object'))
            continue
        source_id = _text(row.get('source_id'))
        if source_id:
            ids.add(source_id)
        else:
            issues.append(PublicSourceRecrawlInactivePatchPreviewIssue('missing_source_id', f'{path}[{index}].source_id', 'source_id is required'))
    return ids


def _scan(value: Any, path: str, issues: list[PublicSourceRecrawlInactivePatchPreviewIssue]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f'{path}.{key}' if path != '$' else f'$.{key}'
            if str(key).lower() in UNSAFE_KEYS and _has_content(child):
                issues.append(PublicSourceRecrawlInactivePatchPreviewIssue('unsafe_artifact_reference', child_path, 'private, authenticated, session, browser, or downloaded artifacts are not allowed'))
            _scan(child, child_path, issues)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _scan(child, f'{path}[{index}]', issues)
        return
    if isinstance(value, str) and '.validation_commands' not in path:
        lowered = ' '.join(value.lower().split())
        for code, patterns in UNSAFE_TEXT.items():
            if any(pattern in lowered for pattern in patterns):
                issues.append(PublicSourceRecrawlInactivePatchPreviewIssue(code, path, 'preview text must not claim unsafe artifacts, execution, outcomes, consequential DevHub action, or active mutation'))


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _commands(value: Any) -> tuple[tuple[str, ...], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    commands = []
    for command in value:
        if not isinstance(command, Sequence) or isinstance(command, (str, bytes)):
            return ()
        command_tuple = tuple(item for item in command if isinstance(item, str))
        if not command_tuple:
            return ()
        commands.append(command_tuple)
    return tuple(commands)


def _has_content(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return bool(value)
    if isinstance(value, Mapping):
        return bool(value)
    return True


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ''


def _dedupe(issues: Sequence[PublicSourceRecrawlInactivePatchPreviewIssue]) -> list[PublicSourceRecrawlInactivePatchPreviewIssue]:
    seen = set()
    deduped = []
    for issue in issues:
        key = (issue.code, issue.path, issue.message)
        if key not in seen:
            seen.add(key)
            deduped.append(issue)
    return deduped
