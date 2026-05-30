from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

PACKET_VERSION = 'public_source_recrawl_reviewer_disposition_packet_v1'
DRY_RUN_MANIFEST_VERSION = 'public_source_recrawl_dry_run_manifest_v1'

APPROVE_REASON_CODES = (
    'APPROVE_PUBLIC_METADATA_ONLY',
    'APPROVE_ROBOTS_AND_POLICY_PLACEHOLDER_READY',
)
HOLD_REASON_CODES = (
    'HOLD_MISSING_PUBLIC_SOURCE_METADATA',
    'HOLD_SKIPPED_SOURCE_POLICY_REVIEW',
    'HOLD_UNSUPPORTED_OR_SKIPPED_SOURCE',
)
REQUIRED_METADATA_ARTIFACTS = (
    'recrawl_metadata_manifest',
    'source_status_summary',
    'content_hash_placeholder',
    'processor_handoff_placeholder',
)
REQUIRED_FORBIDDEN_ARTIFACTS = (
    'document_downloads',
    'html_or_pdf_payloads',
    'authenticated_browser_state',
    'devhub_session_state',
    'raw_crawl_outputs',
)
OFFLINE_VALIDATION_COMMANDS = (
    ('python3', 'ppd/daemon/ppd_daemon.py', '--self-test'),
    ('python3', '-m', 'unittest', 'ppd.tests.test_public_source_recrawl_reviewer_disposition_packet_v1'),
)
FALSE_SAFETY_FLAGS = (
    'live_network_invoked',
    'crawl_executed',
    'recrawl_executed',
    'documents_downloaded',
    'raw_response_bodies_stored',
    'raw_crawl_data_stored',
    'pdf_payloads_stored',
    'devhub_accessed',
    'authenticated_session_used',
    'browser_artifacts_created',
    'active_artifacts_mutated',
    'active_source_artifacts_mutated',
    'active_process_artifacts_mutated',
    'active_prompt_artifacts_mutated',
    'active_release_state_mutated',
    'active_release_artifacts_mutated',
    'active_guardrail_artifacts_mutated',
    'prompt_mutation_requested',
    'release_state_mutation_requested',
    'guardrail_mutation_requested',
)
UNSAFE_ARTIFACT_KEYS = frozenset(
    {
        'auth_state_ref',
        'authenticated_session_ref',
        'browser_artifact_ref',
        'browser_trace_ref',
        'cookie_artifact_ref',
        'downloaded_data_ref',
        'downloaded_document_ref',
        'downloaded_documents',
        'downloaded_pdf_ref',
        'har_artifact_ref',
        'private_artifact_ref',
        'raw_crawl_artifact_ref',
        'raw_crawl_output_ref',
        'raw_download_ref',
        'raw_pdf_ref',
        'session_artifact_ref',
        'session_storage_ref',
    }
)
UNSAFE_TEXT_PATTERNS = (
    ('private_or_session_artifact_claim', ('authenticated session', 'auth state', 'browser trace', 'cookie jar', 'devhub session', 'har file', 'session storage')),
    ('raw_or_downloaded_data_claim', ('downloaded document', 'downloaded pdf', 'pdf payload', 'raw crawl output', 'raw downloaded', 'raw response body')),
    ('live_execution_claim', ('crawl was executed', 'live crawl completed', 'live network was invoked', 'network request executed', 'recrawl was executed')),
    ('legal_or_permitting_outcome_guarantee', ('approval is guaranteed', 'guarantee permit approval', 'legal determination', 'permit will be approved', 'will pass inspection')),
    ('consequential_devhub_action_language', ('cancel inspection', 'certify acknowledgement', 'final payment', 'pay fee', 'purchase permit', 'schedule inspection', 'submit application', 'submit permit', 'upload correction')),
    ('active_mutation_claim', ('active artifact mutation', 'active guardrail mutation', 'active prompt mutation', 'active release-state mutation', 'mutate active artifact', 'mutate guardrail', 'mutate prompt', 'mutate release state')),
)
TEXT_SCAN_SKIP_SUFFIXES = (
    '.validation_commands',
    '.forbidden_artifacts',
)


@dataclass(frozen=True)
class PublicSourceRecrawlReviewerDispositionIssue:
    code: str
    path: str
    message: str


class PublicSourceRecrawlReviewerDispositionError(ValueError):
    def __init__(self, issues: Sequence[PublicSourceRecrawlReviewerDispositionIssue]) -> None:
        self.issues = tuple(issues)
        detail = '; '.join(f'{issue.path}: {issue.code}: {issue.message}' for issue in self.issues)
        super().__init__(detail or 'public source recrawl reviewer disposition packet is invalid')


def build_public_source_recrawl_reviewer_disposition_packet_v1(dry_run_manifest: Mapping[str, Any]) -> dict[str, Any]:
    manifest_id = _text(dry_run_manifest.get('manifest_id')) or 'unidentified-public-source-recrawl-dry-run'
    manifest_version = _text(dry_run_manifest.get('manifest_version')) or _text(dry_run_manifest.get('packet_version'))
    sources = _manifest_sources(dry_run_manifest)

    reviewer_decisions: list[dict[str, Any]] = []
    skipped_source_explanations: list[dict[str, str]] = []
    freshness_placeholders: list[dict[str, str]] = []

    for index, source in enumerate(sources, start=1):
        source_id = _text(source.get('source_id')) or f'public-source-{index:03d}'
        canonical_url = _text(source.get('canonical_url')) or _text(source.get('url'))
        skip_reason = _text(source.get('skip_reason')) or _text(source.get('skipped_reason'))
        allow_reason = _text(source.get('allow_reason'))
        is_hold = bool(skip_reason) or not canonical_url or not source_id
        decision = 'hold' if is_hold else 'approve_for_metadata_only_recrawl'
        reason_codes = ['HOLD_UNSUPPORTED_OR_SKIPPED_SOURCE'] if is_hold else ['APPROVE_PUBLIC_METADATA_ONLY']
        if is_hold and skip_reason:
            reason_codes.append('HOLD_SKIPPED_SOURCE_POLICY_REVIEW')
        if is_hold and (not canonical_url or not source_id):
            reason_codes.append('HOLD_MISSING_PUBLIC_SOURCE_METADATA')
        if not is_hold and allow_reason:
            reason_codes.append('APPROVE_ROBOTS_AND_POLICY_PLACEHOLDER_READY')

        reviewer_decisions.append(
            {
                'source_order': index,
                'source_id': source_id,
                'canonical_url': canonical_url,
                'decision': decision,
                'reason_codes': tuple(dict.fromkeys(reason_codes)),
                'reviewer_notes_placeholder': f'Reviewer to confirm disposition for {source_id} before any later operator action.',
                'metadata_only_artifact_expectation_id': f'metadata-only-{source_id}',
                'source_freshness_update_placeholder_id': f'freshness-placeholder-{source_id}',
            }
        )
        if is_hold:
            skipped_source_explanations.append(
                {
                    'source_id': source_id,
                    'canonical_url': canonical_url,
                    'skip_reason_code': skip_reason or 'MISSING_PUBLIC_SOURCE_METADATA',
                    'reviewer_explanation_placeholder': f'Reviewer to document whether {source_id} remains skipped, deferred, or revised in a later dry-run manifest.',
                }
            )
        freshness_placeholders.append(
            {
                'source_id': source_id,
                'placeholder_id': f'freshness-placeholder-{source_id}',
                'expected_update': 'Record last-reviewed metadata, reviewer disposition, and next eligible fixture-first review window only after reviewer signoff.',
            }
        )

    packet: dict[str, Any] = {
        'packet_version': PACKET_VERSION,
        'fixture_first': True,
        'metadata_only': True,
        'dry_run_manifest_ref': {
            'manifest_id': manifest_id,
            'manifest_version': manifest_version or DRY_RUN_MANIFEST_VERSION,
        },
        'reviewer_decisions': reviewer_decisions,
        'metadata_only_artifact_expectations': {
            'expected_artifacts': REQUIRED_METADATA_ARTIFACTS,
            'forbidden_artifacts': REQUIRED_FORBIDDEN_ARTIFACTS,
        },
        'skipped_source_explanations': skipped_source_explanations,
        'source_freshness_update_placeholders': freshness_placeholders,
        'validation_commands': OFFLINE_VALIDATION_COMMANDS,
    }
    for flag in FALSE_SAFETY_FLAGS:
        packet[flag] = False
    return packet


def validate_public_source_recrawl_reviewer_disposition_packet_v1(packet: Mapping[str, Any]) -> list[PublicSourceRecrawlReviewerDispositionIssue]:
    issues: list[PublicSourceRecrawlReviewerDispositionIssue] = []
    if not isinstance(packet, Mapping):
        return [PublicSourceRecrawlReviewerDispositionIssue('invalid_packet', '$', 'packet must be an object')]

    if packet.get('packet_version') != PACKET_VERSION:
        issues.append(PublicSourceRecrawlReviewerDispositionIssue('invalid_packet_version', '$.packet_version', f'packet_version must be {PACKET_VERSION}'))
    if packet.get('fixture_first') is not True:
        issues.append(PublicSourceRecrawlReviewerDispositionIssue('not_fixture_first', '$.fixture_first', 'packet must be fixture-first'))
    if packet.get('metadata_only') is not True:
        issues.append(PublicSourceRecrawlReviewerDispositionIssue('not_metadata_only', '$.metadata_only', 'packet must describe metadata-only artifacts'))
    for flag in FALSE_SAFETY_FLAGS:
        if packet.get(flag) is not False:
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('unsafe_execution_or_mutation_flag', f'$.{flag}', 'execution, DevHub access, download, storage, session, and mutation flags must be false'))

    manifest_ref = packet.get('dry_run_manifest_ref')
    if not isinstance(manifest_ref, Mapping) or not _text(manifest_ref.get('manifest_id')) or not _text(manifest_ref.get('manifest_version')):
        issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_manifest_ref', '$.dry_run_manifest_ref', 'dry-run manifest id and version are required'))

    decisions = packet.get('reviewer_decisions')
    if not isinstance(decisions, Sequence) or isinstance(decisions, (str, bytes)) or not decisions:
        issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_reviewer_decisions', '$.reviewer_decisions', 'at least one reviewer decision is required'))
        decisions = ()

    decision_source_ids: set[str] = set()
    hold_source_ids: set[str] = set()
    metadata_expectation_ids: set[str] = set()
    freshness_ref_ids: set[str] = set()
    for expected_order, decision in enumerate(decisions, start=1):
        path = f'$.reviewer_decisions[{expected_order - 1}]'
        if not isinstance(decision, Mapping):
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('invalid_decision', path, 'decision row must be an object'))
            continue
        source_id = _text(decision.get('source_id'))
        if not source_id:
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_source_id', f'{path}.source_id', 'source_id is required'))
        else:
            decision_source_ids.add(source_id)
        if decision.get('source_order') != expected_order:
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('unordered_decision', f'{path}.source_order', 'source_order must be contiguous and one-based'))
        if not _text(decision.get('canonical_url')):
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_canonical_url', f'{path}.canonical_url', 'canonical_url is required'))
        disposition = _text(decision.get('decision'))
        codes = _string_list(decision.get('reason_codes'))
        if disposition == 'hold':
            if source_id:
                hold_source_ids.add(source_id)
            if not set(codes).intersection(HOLD_REASON_CODES):
                issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_hold_reason_code', f'{path}.reason_codes', 'hold decisions require a hold reason code'))
        elif disposition == 'approve_for_metadata_only_recrawl':
            if not set(codes).intersection(APPROVE_REASON_CODES):
                issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_approve_reason_code', f'{path}.reason_codes', 'approval decisions require an approve reason code'))
        else:
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('invalid_decision_value', f'{path}.decision', 'decision must be hold or approve_for_metadata_only_recrawl'))
        expectation_id = _text(decision.get('metadata_only_artifact_expectation_id'))
        if not expectation_id:
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_metadata_expectation_ref', f'{path}.metadata_only_artifact_expectation_id', 'metadata-only artifact expectation reference is required'))
        else:
            metadata_expectation_ids.add(expectation_id)
        freshness_id = _text(decision.get('source_freshness_update_placeholder_id'))
        if not freshness_id:
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_freshness_placeholder_ref', f'{path}.source_freshness_update_placeholder_id', 'freshness update placeholder reference is required'))
        else:
            freshness_ref_ids.add(freshness_id)

    _validate_metadata_expectations(packet.get('metadata_only_artifact_expectations'), metadata_expectation_ids, issues)

    skipped = packet.get('skipped_source_explanations')
    skipped_source_ids = _explanation_source_ids(skipped, '$.skipped_source_explanations', issues)
    for source_id in sorted(hold_source_ids - skipped_source_ids):
        issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_skipped_source_explanation', '$.skipped_source_explanations', f'hold decision for {source_id} requires a skipped-source explanation'))

    freshness = packet.get('source_freshness_update_placeholders')
    freshness_ids = _freshness_placeholder_ids(freshness, '$.source_freshness_update_placeholders', issues)
    for placeholder_id in sorted(freshness_ref_ids - freshness_ids):
        issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_source_freshness_placeholder', '$.source_freshness_update_placeholders', f'{placeholder_id} requires a source-freshness update placeholder'))

    if _commands(packet.get('validation_commands')) != OFFLINE_VALIDATION_COMMANDS:
        issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_validation_commands', '$.validation_commands', 'exact offline validation commands are required'))

    _validate_no_unsafe_artifacts_or_claims(packet, '$', issues)
    return _dedupe(issues)


def require_valid_public_source_recrawl_reviewer_disposition_packet_v1(packet: Mapping[str, Any]) -> None:
    issues = validate_public_source_recrawl_reviewer_disposition_packet_v1(packet)
    if issues:
        raise PublicSourceRecrawlReviewerDispositionError(issues)


def _validate_metadata_expectations(value: Any, referenced_ids: set[str], issues: list[PublicSourceRecrawlReviewerDispositionIssue]) -> None:
    if not isinstance(value, Mapping):
        issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_metadata_expectations', '$.metadata_only_artifact_expectations', 'metadata-only artifact expectations are required'))
        return
    expected = set(_string_list(value.get('expected_artifacts')))
    forbidden = set(_string_list(value.get('forbidden_artifacts')))
    missing_expected = sorted(set(REQUIRED_METADATA_ARTIFACTS) - expected)
    missing_forbidden = sorted(set(REQUIRED_FORBIDDEN_ARTIFACTS) - forbidden)
    if missing_expected:
        issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_expected_metadata_artifacts', '$.metadata_only_artifact_expectations.expected_artifacts', f'missing expected metadata artifacts: {", ".join(missing_expected)}'))
    if missing_forbidden:
        issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_forbidden_artifacts', '$.metadata_only_artifact_expectations.forbidden_artifacts', f'missing forbidden non-metadata artifacts: {", ".join(missing_forbidden)}'))
    expectation_ids = set(_string_list(value.get('expectation_ids')))
    if expectation_ids:
        missing_ids = sorted(referenced_ids - expectation_ids)
        if missing_ids:
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_metadata_expectation_id', '$.metadata_only_artifact_expectations.expectation_ids', f'missing metadata expectation ids: {", ".join(missing_ids)}'))


def _manifest_sources(manifest: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    for key in ('candidate_sources', 'candidate_preflight_rows', 'planned_sources', 'sources'):
        value = manifest.get(key)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return [item for item in value if isinstance(item, Mapping)]
    return []


def _explanation_source_ids(value: Any, path: str, issues: list[PublicSourceRecrawlReviewerDispositionIssue]) -> set[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_skipped_source_explanations', path, 'skipped-source explanations must be a list'))
        return set()
    source_ids: set[str] = set()
    for index, item in enumerate(value):
        item_path = f'{path}[{index}]'
        if not isinstance(item, Mapping):
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('invalid_skipped_source_explanation', item_path, 'skipped-source explanation must be an object'))
            continue
        source_id = _text(item.get('source_id'))
        if source_id:
            source_ids.add(source_id)
        if not _text(item.get('skip_reason_code')):
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_skip_reason_code', f'{item_path}.skip_reason_code', 'skip reason code is required'))
        if not _text(item.get('reviewer_explanation_placeholder')):
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_reviewer_explanation_placeholder', f'{item_path}.reviewer_explanation_placeholder', 'reviewer explanation placeholder is required'))
    return source_ids


def _freshness_placeholder_ids(value: Any, path: str, issues: list[PublicSourceRecrawlReviewerDispositionIssue]) -> set[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or not value:
        issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_source_freshness_placeholders', path, 'source-freshness update placeholders must be a non-empty list'))
        return set()
    placeholder_ids: set[str] = set()
    for index, item in enumerate(value):
        item_path = f'{path}[{index}]'
        if not isinstance(item, Mapping):
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('invalid_source_freshness_placeholder', item_path, 'source-freshness placeholder must be an object'))
            continue
        placeholder_id = _text(item.get('placeholder_id'))
        if placeholder_id:
            placeholder_ids.add(placeholder_id)
        else:
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_placeholder_id', f'{item_path}.placeholder_id', 'placeholder_id is required'))
        if not _text(item.get('source_id')):
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_freshness_source_id', f'{item_path}.source_id', 'source_id is required'))
        if not _text(item.get('expected_update')):
            issues.append(PublicSourceRecrawlReviewerDispositionIssue('missing_expected_update', f'{item_path}.expected_update', 'expected update placeholder text is required'))
    return placeholder_ids


def _validate_no_unsafe_artifacts_or_claims(value: Any, path: str, issues: list[PublicSourceRecrawlReviewerDispositionIssue]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f'{path}.{key_text}' if path != '$' else f'$.{key_text}'
            if key_text.lower() in UNSAFE_ARTIFACT_KEYS and _has_content(child):
                issues.append(PublicSourceRecrawlReviewerDispositionIssue('unsafe_artifact_reference', child_path, 'private, authenticated, session, browser, raw crawl, PDF, or downloaded artifacts are not allowed'))
            _validate_no_unsafe_artifacts_or_claims(child, child_path, issues)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            _validate_no_unsafe_artifacts_or_claims(child, f'{path}[{index}]', issues)
        return
    if isinstance(value, str) and not _skip_text_scan(path):
        lowered = ' '.join(value.lower().split())
        for code, patterns in UNSAFE_TEXT_PATTERNS:
            if any(pattern in lowered for pattern in patterns):
                issues.append(PublicSourceRecrawlReviewerDispositionIssue(code, path, 'packet text must not claim unsafe artifacts, execution, outcomes, consequential DevHub action, or active mutation'))


def _skip_text_scan(path: str) -> bool:
    return any(path.endswith(suffix) or suffix in path for suffix in TEXT_SCAN_SKIP_SUFFIXES)


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


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _commands(value: Any) -> tuple[tuple[str, ...], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    commands: list[tuple[str, ...]] = []
    for command in value:
        strings = tuple(_string_list(command))
        if not strings:
            return ()
        commands.append(strings)
    return tuple(commands)


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ''


def _dedupe(issues: Sequence[PublicSourceRecrawlReviewerDispositionIssue]) -> list[PublicSourceRecrawlReviewerDispositionIssue]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[PublicSourceRecrawlReviewerDispositionIssue] = []
    for issue in issues:
        key = (issue.code, issue.path, issue.message)
        if key not in seen:
            seen.add(key)
            deduped.append(issue)
    return deduped
