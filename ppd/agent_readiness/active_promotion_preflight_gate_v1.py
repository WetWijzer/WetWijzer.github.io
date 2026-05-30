from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


REQUIRED_PACKET_TYPE = 'ppd.active_promotion_preflight_gate.v1'

_REQUIRED_NON_EMPTY_LISTS: tuple[tuple[str, str], ...] = (
    ('final_go_no_go_rows', 'missing_final_go_no_go_rows'),
    ('human_approval_placeholders', 'missing_human_approval_placeholders'),
    ('active_mutation_blocker_inventory', 'missing_active_mutation_blocker_inventory'),
    ('validation_replay_checklist', 'missing_validation_replay_checklist'),
)

_REQUIRED_NON_EMPTY_VALUES: tuple[tuple[str, str], ...] = (
    ('rollback_readiness_summary', 'missing_rollback_readiness_summary'),
    ('release_state_nonmutation_notes', 'missing_release_state_nonmutation_notes'),
)

_FORBIDDEN_ARTIFACT_KEYS: set[str] = {
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

_FORBIDDEN_TRUE_KEYS: set[str] = {
    'active_agent_state_mutated',
    'active_artifact_mutated',
    'active_fixture_mutated',
    'active_prompt_mutated',
    'active_release_state_mutated',
    'agent_state_mutated',
    'artifact_mutated',
    'fixture_mutated',
    'prompt_mutated',
    'release_state_mutated',
}

_MUTATION_TARGETS: tuple[str, ...] = (
    'active_agent_state',
    'active_artifact',
    'active_fixture',
    'active_prompt',
    'active_release_state',
    'agent_state',
    'artifact',
    'fixture',
    'prompt',
    'release_state',
)

_FORBIDDEN_TEXT_NEEDLES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ('private_or_authenticated_artifact', ('private artifact', 'authenticated artifact', 'logged-in page', 'signed-in page', 'private applicant')),
    ('session_or_browser_artifact', ('session cookie', 'session artifact', 'browser artifact', 'browser state', 'storage state', 'access token', 'refresh token')),
    ('screenshot_trace_har_or_auth_file', ('screenshot', 'playwright trace', 'trace file', 'har file', 'auth file', 'auth state')),
    ('raw_pdf_or_downloaded_data', ('raw crawl', 'raw html', 'raw body', 'raw pdf', 'downloaded data', 'downloaded document', 'downloaded pdf')),
    ('live_execution_or_promotion_claim', ('live execution', 'live crawl executed', 'promotion executed', 'promoted to active', 'release complete', 'release-complete', 'promotion complete')),
    ('outcome_guarantee', ('approval guaranteed', 'permit guaranteed', 'will be approved', 'legally compliant', 'no legal risk', 'guaranteed outcome')),
    ('consequential_action_language', ('agent will submit', 'automation will submit', 'click submit', 'click pay', 'enter payment', 'execute payment', 'submit permit', 'perform upload', 'upload official')),
)


@dataclass(frozen=True)
class ActivePromotionPreflightGateV1Result:
    valid: bool
    problems: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {'valid': self.valid, 'problems': list(self.problems)}


class ActivePromotionPreflightGateV1Error(ValueError):
    def __init__(self, problems: tuple[str, ...]) -> None:
        self.problems = problems
        super().__init__('invalid active promotion preflight gate v1: ' + '; '.join(problems))


def validate_active_promotion_preflight_gate_v1(packet: Mapping[str, Any]) -> ActivePromotionPreflightGateV1Result:
    problems: list[str] = []
    if not isinstance(packet, Mapping):
        return ActivePromotionPreflightGateV1Result(False, ('packet_must_be_object',))

    if packet.get('packet_type') != REQUIRED_PACKET_TYPE:
        problems.append('invalid_packet_type')

    for key, code in _REQUIRED_NON_EMPTY_LISTS:
        rows = packet.get(key)
        if not isinstance(rows, list) or not rows:
            problems.append(code)
        elif not all(isinstance(row, Mapping) and row for row in rows):
            problems.append(code)

    for key, code in _REQUIRED_NON_EMPTY_VALUES:
        if not _present(packet.get(key)):
            problems.append(code)

    _find_forbidden_content(packet, '$', problems)
    return ActivePromotionPreflightGateV1Result(valid=not problems, problems=tuple(sorted(dict.fromkeys(problems))))


def require_active_promotion_preflight_gate_v1_valid(packet: Mapping[str, Any]) -> None:
    result = validate_active_promotion_preflight_gate_v1(packet)
    if not result.valid:
        raise ActivePromotionPreflightGateV1Error(result.problems)


def _find_forbidden_content(value: Any, path: str, problems: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = _normalize_key(key)
            child_path = f'{path}.{key}'
            if normalized in _FORBIDDEN_ARTIFACT_KEYS:
                problems.append(f'{child_path}: forbidden_artifact_key')
            if normalized in _FORBIDDEN_TRUE_KEYS and child is True:
                problems.append(f'{child_path}: active_mutation_flag')
            if child is True and 'mutat' in normalized and any(target in normalized for target in _MUTATION_TARGETS):
                problems.append(f'{child_path}: active_mutation_flag')
            _find_forbidden_content(child, child_path, problems)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _find_forbidden_content(child, f'{path}[{index}]', problems)
    elif isinstance(value, str):
        lowered = value.lower()
        for code, needles in _FORBIDDEN_TEXT_NEEDLES:
            if any(needle in lowered for needle in needles):
                problems.append(f'{path}: {code}')


def _present(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, list):
        return bool(value)
    return value is not None


def _normalize_key(value: Any) -> str:
    return str(value).strip().lower().replace('-', '_').replace(' ', '_')


__all__ = [
    'ActivePromotionPreflightGateV1Error',
    'ActivePromotionPreflightGateV1Result',
    'REQUIRED_PACKET_TYPE',
    'require_active_promotion_preflight_gate_v1_valid',
    'validate_active_promotion_preflight_gate_v1',
]
