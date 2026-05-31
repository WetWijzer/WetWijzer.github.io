from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

CONTRACT_VERSION = 'guarded-draft-executor-noop-adapter-v2'
APPROVED_REVIEW_PACKET_VERSION = 'approved-executor-review-packet-v2'

FORBIDDEN_LIVE_ACTIONS = (
    'import_playwright',
    'launch_browser',
    'touch_browser_session_files',
    'fill_live_forms',
    'save_official_drafts',
    'upload_files',
    'submit',
    'certify',
    'pay',
    'schedule',
    'cancel',
    'change_accounts',
    'activate_release_state',
)

EXACT_CONFIRMATION_PHRASE = 'I understand this is preview-only and no live PP&D action will be taken.'

OFFLINE_VALIDATION_COMMANDS = (
    ('python3', '-m', 'py_compile', 'ppd/contracts/draft_executor_noop_adapter_v2.py'),
    ('python3', '-m', 'pytest', 'ppd/tests/test_draft_executor_noop_adapter_v2.py'),
    ('python3', 'ppd/daemon/ppd_daemon.py', '--self-test'),
)

_REQUIRED_FIELDS = (
    'synthetic_examples',
    'noop_execution_markers',
    'preview_only_mutation_summaries',
    'redacted_journal_events',
    'required_dry_run_evidence_ids',
    'exact_confirmation_refusal_gates',
    'offline_validation_commands',
)

_PRIVATE_ARTIFACT_KEYS = {
    'auth_state',
    'auth_storage_state',
    'browser_session',
    'browser_context',
    'cookies',
    'cookie',
    'credentials',
    'download_path',
    'downloaded_artifact',
    'downloaded_document',
    'har',
    'local_private_path',
    'raw_body',
    'raw_crawl_output',
    'raw_download',
    'screenshot',
    'session_file',
    'session_storage',
    'storage_state',
    'trace',
}

_PRIVATE_ARTIFACT_TERMS = (
    'auth state',
    'browser session file',
    'cookies.json',
    'downloaded artifact',
    'downloaded document',
    'har file',
    'private/session',
    'raw crawl output',
    'raw downloaded',
    'session storage',
    'storage state',
    'trace.zip',
)

_FORBIDDEN_CLAIM_TERMS = (
    'devhub execution completed',
    'executed in live devhub',
    'live devhub execution',
    'official draft saved',
    'permit application submitted',
    'saved official draft',
    'submission completed',
    'submitted to pp&d',
)

_FORBIDDEN_GUARANTEE_TERMS = (
    'guaranteed permit approval',
    'guarantees approval',
    'legal guarantee',
    'permit will be approved',
    'permitting guarantee',
)

_FORBIDDEN_PLAYWRIGHT_REQUIREMENTS = (
    'from playwright',
    'import playwright',
    'launch browser required',
    'playwright launch',
    'requires playwright',
)

_ACTIVE_MUTATION_FLAG_KEYS = {
    'active_contract_mutation',
    'active_devhub_surface_mutation',
    'active_guardrail_mutation',
    'active_prompt_mutation',
    'active_release_state',
    'active_release_state_mutation',
    'active_source_mutation',
    'contract_mutation',
    'contract_mutation_active',
    'devhub_surface_mutation',
    'devhub_surface_mutation_active',
    'guardrail_mutation',
    'guardrail_mutation_active',
    'prompt_mutation',
    'prompt_mutation_active',
    'release_state_active',
    'release_state_mutation',
    'source_mutation',
    'source_mutation_active',
}


@dataclass(frozen=True)
class AdapterContractV2:
    contract_version: str
    source_packet_id: str
    adapter_mode: str
    synthetic_examples: tuple[Mapping[str, Any], ...]
    noop_execution_markers: tuple[str, ...]
    preview_only_mutation_summaries: tuple[Mapping[str, str], ...]
    redacted_journal_events: tuple[Mapping[str, Any], ...]
    required_dry_run_evidence_ids: tuple[str, ...]
    exact_confirmation_refusal_gates: tuple[Mapping[str, str], ...]
    forbidden_live_actions: tuple[str, ...]
    offline_validation_commands: tuple[tuple[str, ...], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            'contract_version': self.contract_version,
            'source_packet_id': self.source_packet_id,
            'adapter_mode': self.adapter_mode,
            'synthetic_examples': list(self.synthetic_examples),
            'noop_execution_markers': list(self.noop_execution_markers),
            'preview_only_mutation_summaries': list(self.preview_only_mutation_summaries),
            'redacted_journal_events': list(self.redacted_journal_events),
            'required_dry_run_evidence_ids': list(self.required_dry_run_evidence_ids),
            'exact_confirmation_refusal_gates': list(self.exact_confirmation_refusal_gates),
            'forbidden_live_actions': list(self.forbidden_live_actions),
            'offline_validation_commands': [list(command) for command in self.offline_validation_commands],
        }


def _sequence(value: Any, field_name: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f'{field_name} must be a non-empty sequence')
    if not value:
        raise ValueError(f'{field_name} must be present and non-empty')
    return value


def _mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f'{field_name} must be an object')
    return value


def _truthy_flag(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {'1', 'active', 'enabled', 'mutate', 'mutating', 'true', 'yes'}
    return bool(value)


def _walk(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    yield path, value
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk(child, path + (str(key),))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            yield from _walk(child, path + (str(index),))


def _reject_forbidden_content(contract: Mapping[str, Any]) -> None:
    for path, value in _walk(contract):
        field_name = path[-1].lower() if path else ''
        if field_name in _PRIVATE_ARTIFACT_KEYS:
            raise ValueError(f'private/session/browser/raw/downloaded artifact field is forbidden: {field_name}')
        if field_name in _ACTIVE_MUTATION_FLAG_KEYS and _truthy_flag(value):
            raise ValueError(f'active mutation flag is forbidden: {field_name}')
        if isinstance(value, str):
            text = value.lower()
            checks = (
                (_PRIVATE_ARTIFACT_TERMS, 'private/session/browser/raw/downloaded artifacts are forbidden'),
                (_FORBIDDEN_CLAIM_TERMS, 'live DevHub execution or official action claims are forbidden'),
                (_FORBIDDEN_GUARANTEE_TERMS, 'legal or permitting guarantees are forbidden'),
                (_FORBIDDEN_PLAYWRIGHT_REQUIREMENTS, 'Playwright launch/import requirements are forbidden'),
            )
            for terms, message in checks:
                if any(term in text for term in terms):
                    raise ValueError(message)


def validate_noop_adapter_contract_v2(contract: Mapping[str, Any]) -> None:
    if contract.get('contract_version') != CONTRACT_VERSION:
        raise ValueError('contract_version must be guarded-draft-executor-noop-adapter-v2')
    if contract.get('adapter_mode') != 'fixture_first_preview_only_noop':
        raise ValueError('adapter_mode must be fixture_first_preview_only_noop')

    for field_name in _REQUIRED_FIELDS:
        _sequence(contract.get(field_name), field_name)

    markers = {str(item) for item in _sequence(contract.get('noop_execution_markers'), 'noop_execution_markers')}
    if not all(marker.startswith('NOOP_EXECUTION_MARKER_') for marker in markers):
        raise ValueError('noop_execution_markers must contain explicit no-op execution markers')

    evidence_ids = {str(item) for item in _sequence(contract.get('required_dry_run_evidence_ids'), 'required_dry_run_evidence_ids')}
    if not all(item.startswith('dry-run-evidence-') for item in evidence_ids):
        raise ValueError('required_dry_run_evidence_ids must contain dry-run evidence IDs')

    examples = _sequence(contract.get('synthetic_examples'), 'synthetic_examples')
    for index, example in enumerate(examples, start=1):
        example_map = _mapping(example, f'synthetic_examples[{index}]')
        adapter_input = _mapping(example_map.get('adapter_input'), f'synthetic_examples[{index}].adapter_input')
        adapter_output = _mapping(example_map.get('adapter_output'), f'synthetic_examples[{index}].adapter_output')
        if adapter_input.get('source') != 'fixture' or adapter_input.get('live_target_allowed') is not False:
            raise ValueError('adapter examples must be fixture-only and disallow live targets')
        if adapter_output.get('status') != 'preview_only_noop' or adapter_output.get('live_mutation_performed') is not False:
            raise ValueError('adapter examples must be preview-only no-op outputs')
        if adapter_output.get('noop_marker') not in markers:
            raise ValueError('adapter examples must reference a no-op execution marker')
        if adapter_output.get('dry_run_evidence_id') not in evidence_ids:
            raise ValueError('adapter examples must reference a dry-run evidence ID')

    summaries = _sequence(contract.get('preview_only_mutation_summaries'), 'preview_only_mutation_summaries')
    for summary in summaries:
        text = str(_mapping(summary, 'preview_only_mutation_summaries[]').get('summary', '')).lower()
        if 'preview' not in text or 'no official draft' not in text:
            raise ValueError('preview_only_mutation_summaries must state preview-only/no official draft behavior')

    events = _sequence(contract.get('redacted_journal_events'), 'redacted_journal_events')
    for event in events:
        event_map = _mapping(event, 'redacted_journal_events[]')
        if not str(event_map.get('subject', '')).startswith('REDACTED_'):
            raise ValueError('redacted_journal_events must use redacted subjects')
        if event_map.get('result') != 'NOOP_PREVIEW_ONLY':
            raise ValueError('redacted_journal_events must record no-op preview-only results')
        if event_map.get('evidence_id') not in evidence_ids:
            raise ValueError('redacted_journal_events must reference dry-run evidence IDs')

    gates = _sequence(contract.get('exact_confirmation_refusal_gates'), 'exact_confirmation_refusal_gates')
    if not any(_mapping(gate, 'exact_confirmation_refusal_gates[]').get('required_phrase') == EXACT_CONFIRMATION_PHRASE for gate in gates):
        raise ValueError('exact_confirmation_refusal_gates must include the exact confirmation phrase')
    if not all('refuse' in str(_mapping(gate, 'exact_confirmation_refusal_gates[]').get('refusal', '')).lower() for gate in gates):
        raise ValueError('exact_confirmation_refusal_gates must include refusal text')

    commands = _sequence(contract.get('offline_validation_commands'), 'offline_validation_commands')
    normalized_commands: list[tuple[str, ...]] = []
    for command in commands:
        parts = tuple(str(part) for part in _sequence(command, 'offline_validation_commands[]'))
        normalized_commands.append(parts)
    if ('python3', 'ppd/daemon/ppd_daemon.py', '--self-test') not in normalized_commands:
        raise ValueError('offline_validation_commands must include ppd daemon self-test')

    _reject_forbidden_content(contract)


def build_noop_adapter_contract_v2(review_packet: Mapping[str, Any]) -> AdapterContractV2:
    packet_version = str(review_packet.get('packet_version', ''))
    approval_state = str(review_packet.get('approval_state', ''))
    if packet_version != APPROVED_REVIEW_PACKET_VERSION:
        raise ValueError('review packet must be approved-executor-review-packet-v2')
    if approval_state != 'approved_for_noop_dry_run':
        raise ValueError('review packet must be approved for no-op dry-run only')

    packet_id = str(review_packet.get('packet_id', ''))
    if not packet_id:
        raise ValueError('review packet must include packet_id')

    steps = review_packet.get('ordered_preview_steps', ())
    if not isinstance(steps, list) or not steps:
        raise ValueError('review packet must include ordered_preview_steps')

    examples: list[Mapping[str, Any]] = []
    summaries: list[Mapping[str, str]] = []
    events: list[Mapping[str, Any]] = []
    evidence_ids: list[str] = []
    markers: list[str] = []

    for index, raw_step in enumerate(steps, start=1):
        if not isinstance(raw_step, Mapping):
            raise ValueError('each ordered preview step must be an object')
        step_id = str(raw_step.get('step_id', f'step-{index:02d}'))
        label = str(raw_step.get('label', step_id))
        synthetic_input_id = f'synthetic-input-{index:02d}-{step_id}'
        synthetic_output_id = f'synthetic-output-{index:02d}-{step_id}'
        evidence_id = f'dry-run-evidence-{index:02d}-{step_id}'
        marker = f"NOOP_EXECUTION_MARKER_{index:02d}_{step_id.upper().replace('-', '_')}"

        examples.append(
            {
                'order': index,
                'step_id': step_id,
                'adapter_input': {
                    'id': synthetic_input_id,
                    'source': 'fixture',
                    'label': label,
                    'redaction_policy': 'redacted-fixture-values-only',
                    'live_target_allowed': False,
                },
                'adapter_output': {
                    'id': synthetic_output_id,
                    'status': 'preview_only_noop',
                    'noop_marker': marker,
                    'dry_run_evidence_id': evidence_id,
                    'live_mutation_performed': False,
                },
            }
        )
        summaries.append(
            {
                'step_id': step_id,
                'summary': f'Would preview {label}; no official draft, upload, submission, payment, account, schedule, or release mutation is permitted.',
            }
        )
        events.append(
            {
                'event_type': 'draft_executor_noop_preview',
                'step_id': step_id,
                'subject': 'REDACTED_SYNTHETIC_FIXTURE',
                'result': 'NOOP_PREVIEW_ONLY',
                'evidence_id': evidence_id,
            }
        )
        evidence_ids.append(evidence_id)
        markers.append(marker)

    gates = (
        {
            'gate': 'exact_confirmation_required',
            'required_phrase': EXACT_CONFIRMATION_PHRASE,
            'refusal': 'Refuse execution unless the exact phrase is supplied; even with the phrase, remain preview-only no-op.',
        },
        {
            'gate': 'live_action_refusal',
            'required_phrase': '',
            'refusal': 'Refuse any request to launch a browser, use authenticated sessions, alter live PP&D state, upload, submit, certify, pay, schedule, cancel, or change accounts.',
        },
    )

    contract = AdapterContractV2(
        contract_version=CONTRACT_VERSION,
        source_packet_id=packet_id,
        adapter_mode='fixture_first_preview_only_noop',
        synthetic_examples=tuple(examples),
        noop_execution_markers=tuple(markers),
        preview_only_mutation_summaries=tuple(summaries),
        redacted_journal_events=tuple(events),
        required_dry_run_evidence_ids=tuple(evidence_ids),
        exact_confirmation_refusal_gates=gates,
        forbidden_live_actions=FORBIDDEN_LIVE_ACTIONS,
        offline_validation_commands=OFFLINE_VALIDATION_COMMANDS,
    )
    validate_noop_adapter_contract_v2(contract.as_dict())
    return contract
