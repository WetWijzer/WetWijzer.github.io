from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable, Mapping, Sequence

PACKET_VERSION = 'stale_readiness_reviewer_disposition_packet_v1'
REQUIRED_DISPOSITIONS = ('proceed', 'hold', 'reject')
REQUIRED_COMMANDS = (
    ('python3', '-m', 'unittest', 'ppd.tests.test_stale_readiness_reviewer_disposition_packet_v1'),
)

_FORBIDDEN_KEY_PARTS = (
    'credential',
    'password',
    'token',
    'secret',
    'auth_state',
    'session',
    'browser',
    'screenshot',
    'trace',
    'har',
    'private',
    'raw',
    'downloaded',
    'download',
)
_FORBIDDEN_TEXT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ('credentials_or_session_artifact', re.compile(r'\b(credential|password|token|secret|auth state|session cookie|browser state)\b', re.I)),
    ('browser_evidence_artifact', re.compile(r'\b(screenshot|browser trace|trace artifact|HAR file|HAR artifact)\b', re.I)),
    ('private_raw_or_downloaded_artifact', re.compile(r'\b(private artifact|raw crawl|raw response|downloaded document|downloaded artifact|downloaded file)\b', re.I)),
    ('live_devhub_or_crawl_claim', re.compile(r'\b(live DevHub|live crawl|crawled DevHub|authenticated crawl|visited DevHub|DevHub was opened|crawl completed)\b', re.I)),
    ('official_action_completion_claim', re.compile(r'\b(official action completed|permit submitted|application submitted|inspection scheduled|certification completed|fee paid)\b', re.I)),
    ('release_promotion_claim', re.compile(r'\b(release promoted|promoted to production|production release completed|shipped to production)\b', re.I)),
    ('legal_or_permitting_guarantee', re.compile(r'\b(legal guarantee|permitting guarantee|guaranteed approval|guarantees approval|will be approved|compliance guaranteed)\b', re.I)),
)
_MUTATION_FLAG_KEYS = {
    'active_mutation',
    'mutation_active',
    'mutates_live_system',
    'active_prompt_mutated',
    'active_guardrail_mutated',
    'active_process_model_mutated',
    'active_requirement_mutated',
    'active_source_mutated',
    'active_release_mutated',
}


@dataclass(frozen=True)
class StaleReadinessReviewerDispositionIssue:
    code: str
    path: str
    message: str


def validate_stale_readiness_reviewer_disposition_packet_v1(packet: Mapping[str, Any]) -> list[StaleReadinessReviewerDispositionIssue]:
    issues: list[StaleReadinessReviewerDispositionIssue] = []
    if not isinstance(packet, Mapping):
        return [StaleReadinessReviewerDispositionIssue('invalid_packet', '$', 'packet must be an object')]

    if packet.get('packet_version') != PACKET_VERSION:
        issues.append(StaleReadinessReviewerDispositionIssue('invalid_packet_version', '$.packet_version', f'packet_version must be {PACKET_VERSION}'))

    _require_nonempty(packet, 'combined_readiness_references', 'missing_combined_readiness_references', issues)
    _require_nonempty(packet, 'dependency_ordering', 'missing_dependency_ordering', issues)
    _require_nonempty(packet, 'owner_routing', 'missing_owner_routing', issues)
    _require_nonempty(packet, 'reviewer_routing', 'missing_reviewer_routing', issues)
    _require_nonempty(packet, 'stale_source_hold_reasons', 'missing_stale_source_hold_reasons', issues)
    _require_nonempty(packet, 'rollback_notes', 'missing_rollback_notes', issues)

    rows = packet.get('disposition_rows')
    seen: set[str] = set()
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)) or not rows:
        issues.append(StaleReadinessReviewerDispositionIssue('missing_disposition_rows', '$.disposition_rows', 'proceed, hold, and reject disposition rows are required'))
        rows = ()
    for index, row in enumerate(rows):
        path = f'$.disposition_rows[{index}]'
        if not isinstance(row, Mapping):
            issues.append(StaleReadinessReviewerDispositionIssue('invalid_disposition_row', path, 'disposition row must be an object'))
            continue
        disposition = _text(row.get('disposition'))
        if disposition in REQUIRED_DISPOSITIONS:
            seen.add(disposition)
        if not _text(row.get('owner')):
            issues.append(StaleReadinessReviewerDispositionIssue('missing_owner_routing', f'{path}.owner', 'disposition row requires owner routing'))
        if not _text(row.get('reviewer')):
            issues.append(StaleReadinessReviewerDispositionIssue('missing_reviewer_routing', f'{path}.reviewer', 'disposition row requires reviewer routing'))
        if disposition == 'hold' and not _string_list(row.get('stale_source_hold_reasons')):
            issues.append(StaleReadinessReviewerDispositionIssue('missing_stale_source_hold_reasons', f'{path}.stale_source_hold_reasons', 'hold disposition requires stale-source hold reasons'))
    for disposition in REQUIRED_DISPOSITIONS:
        if disposition not in seen:
            issues.append(StaleReadinessReviewerDispositionIssue(f'missing_{disposition}_disposition_row', '$.disposition_rows', f'missing {disposition} disposition row'))

    if _commands(packet.get('validation_commands')) != REQUIRED_COMMANDS:
        issues.append(StaleReadinessReviewerDispositionIssue('missing_validation_commands', '$.validation_commands', 'exact offline validation command list is required'))

    _validate_no_forbidden_claims(packet, '$', issues)
    return _dedupe(issues)


def require_valid_stale_readiness_reviewer_disposition_packet_v1(packet: Mapping[str, Any]) -> None:
    issues = validate_stale_readiness_reviewer_disposition_packet_v1(packet)
    if issues:
        detail = '; '.join(f'{issue.path}: {issue.code}: {issue.message}' for issue in issues)
        raise ValueError(detail)


def _require_nonempty(packet: Mapping[str, Any], field: str, code: str, issues: list[StaleReadinessReviewerDispositionIssue]) -> None:
    if _is_empty(packet.get(field)):
        issues.append(StaleReadinessReviewerDispositionIssue(code, f'$.{field}', field.replace('_', ' ') + ' is required'))


def _validate_no_forbidden_claims(value: Any, path: str, issues: list[StaleReadinessReviewerDispositionIssue], key: str = '') -> None:
    lowered_key = key.lower()
    if key and any(part in lowered_key for part in _FORBIDDEN_KEY_PARTS):
        issues.append(StaleReadinessReviewerDispositionIssue('forbidden_artifact_reference', path, 'packet references prohibited artifact fields'))
    if key in _MUTATION_FLAG_KEYS and value is True:
        issues.append(StaleReadinessReviewerDispositionIssue('active_mutation_flag', path, 'active mutation flags must be absent or false'))
    if isinstance(value, str):
        for code, pattern in _FORBIDDEN_TEXT_PATTERNS:
            if pattern.search(value):
                issues.append(StaleReadinessReviewerDispositionIssue(code, path, 'packet contains prohibited claim or artifact text'))
    if isinstance(value, Mapping):
        for child_key, child_value in value.items():
            child_key_text = str(child_key)
            _validate_no_forbidden_claims(child_value, f'{path}.{child_key_text}', issues, child_key_text)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child_value in enumerate(value):
            _validate_no_forbidden_claims(child_value, f'{path}[{index}]', issues, str(index))


def _commands(value: Any) -> tuple[tuple[str, ...], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return ()
    normalized: list[tuple[str, ...]] = []
    for command in value:
        if not isinstance(command, Sequence) or isinstance(command, (str, bytes)):
            return ()
        normalized.append(tuple(str(part) for part in command))
    return tuple(normalized)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [_text(item) for item in value if _text(item)]


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (Mapping, Sequence, set)) and not isinstance(value, (str, bytes)):
        return len(value) == 0
    return False


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ''


def _dedupe(issues: Iterable[StaleReadinessReviewerDispositionIssue]) -> list[StaleReadinessReviewerDispositionIssue]:
    seen: set[tuple[str, str]] = set()
    deduped: list[StaleReadinessReviewerDispositionIssue] = []
    for issue in issues:
        key = (issue.code, issue.path)
        if key not in seen:
            seen.add(key)
            deduped.append(issue)
    return deduped
