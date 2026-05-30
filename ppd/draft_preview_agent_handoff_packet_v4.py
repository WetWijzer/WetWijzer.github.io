"""Build fixture-first reversible draft preview handoff packet v4.

The v4 packet is offline and deterministic. It consumes the offline agent
readiness adapter v4, committed local PDF field-mapping fixtures, and committed
guardrail bundle fixtures to produce cited draft-only field proposals,
missing-fact blockers, user-review checkpoints, rollback notes, validation
commands, and explicit no-official-action attestations.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from ppd.agent_readiness_adapter_v4 import evaluate_offline_agent_readiness


PACKET_VERSION = "draft-preview-agent-handoff-packet-v4"
DEFAULT_READINESS_FIXTURE_ROOT = Path(__file__).parent / "tests" / "fixtures" / "agent_readiness_packet_v4"
DEFAULT_HANDOFF_FIXTURE_ROOT = Path(__file__).parent / "tests" / "fixtures" / "draft_preview_agent_handoff_packet_v4"
DEFAULT_PDF_FIELD_MAPPING_PATH = DEFAULT_HANDOFF_FIXTURE_ROOT / "pdf_field_mapping_fixtures.json"
DEFAULT_GUARDRAIL_BUNDLE_PATH = DEFAULT_READINESS_FIXTURE_ROOT / "guardrail_bundle_fixtures.json"

REQUIRED_ATTESTATIONS = (
    "no_private_file",
    "no_upload",
    "no_certification",
    "no_submission",
    "no_payment",
    "no_inspection_scheduling",
)
REQUIRED_GUARDRAIL_BLOCKS = (
    "upload",
    "certification",
    "submission",
    "payment",
)
FORBIDDEN_KEYS = {
    "auth_state",
    "browser_snapshot",
    "card_number",
    "cookie",
    "downloaded_document",
    "file_path",
    "html",
    "local_path",
    "password",
    "payment_details",
    "private_file",
    "raw_document",
    "raw_html",
    "screenshot",
    "session_cookie",
    "trace",
    "upload_payload",
}
OFFICIAL_ACTION_WORDS = (
    "certify",
    "pay",
    "payment",
    "schedule inspection",
    "submit",
    "upload",
)


class DraftPreviewHandoffPacketV4Error(ValueError):
    """Raised when fixtures cannot support a v4 handoff packet."""


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise DraftPreviewHandoffPacketV4Error(f"fixture must be a JSON object: {path}")
    return loaded


def fixture_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_packet_from_paths(
    pdf_field_mapping_path: Path = DEFAULT_PDF_FIELD_MAPPING_PATH,
    guardrail_bundle_path: Path = DEFAULT_GUARDRAIL_BUNDLE_PATH,
    readiness_fixture_root: Path = DEFAULT_READINESS_FIXTURE_ROOT,
) -> dict[str, Any]:
    pdf_mapping = load_json(pdf_field_mapping_path)
    guardrails = load_json(guardrail_bundle_path)
    readiness_outputs = {
        "preview": evaluate_offline_agent_readiness(
            _adapter_request("preview_draft_only", pdf_mapping),
            readiness_fixture_root,
        ),
        "missing_facts": evaluate_offline_agent_readiness(
            _adapter_request("collect_missing_facts", pdf_mapping),
            readiness_fixture_root,
        ),
        "blocked_action": evaluate_offline_agent_readiness(
            _adapter_request("submit_application", pdf_mapping),
            readiness_fixture_root,
        ),
    }
    provenance = [
        {"path_name": pdf_field_mapping_path.name, "sha256": fixture_digest(pdf_field_mapping_path)},
        {"path_name": guardrail_bundle_path.name, "sha256": fixture_digest(guardrail_bundle_path)},
    ]
    return build_packet(pdf_mapping, guardrails, readiness_outputs, provenance=provenance)


def build_packet(
    pdf_mapping: Mapping[str, Any],
    guardrails: Mapping[str, Any],
    readiness_outputs: Mapping[str, Mapping[str, Any]],
    *,
    provenance: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    _validate_source_fixtures(pdf_mapping, guardrails, readiness_outputs)
    known_facts = set(_string_list(pdf_mapping.get("known_fact_keys")))
    required_facts = _required_fact_keys(pdf_mapping)
    missing_fact_keys = [fact for fact in required_facts if fact not in known_facts]
    consumed_refs = _consumed_refs(pdf_mapping, guardrails, readiness_outputs)

    packet = {
        "packet_version": PACKET_VERSION,
        "source_fixture_ids": _source_fixture_ids(pdf_mapping, guardrails, readiness_outputs),
        "fixture_provenance": provenance or [],
        "readiness_adapter_outputs": _readiness_summary(readiness_outputs),
        "field_proposals": _field_proposals(pdf_mapping, missing_fact_keys),
        "missing_fact_blockers": _missing_fact_blockers(pdf_mapping, missing_fact_keys, readiness_outputs),
        "user_review_checkpoints": _user_review_checkpoints(pdf_mapping, guardrails, consumed_refs),
        "rollback_notes": _rollback_notes(pdf_mapping, consumed_refs),
        "offline_validation_commands": _offline_validation_commands(),
        "attestations": {key: True for key in REQUIRED_ATTESTATIONS},
    }
    validate_packet(packet)
    return packet


def validate_packet(packet: Mapping[str, Any]) -> None:
    problems: list[str] = []
    if packet.get("packet_version") != PACKET_VERSION:
        problems.append("unexpected packet_version")
    for key in (
        "source_fixture_ids",
        "field_proposals",
        "missing_fact_blockers",
        "user_review_checkpoints",
        "rollback_notes",
        "offline_validation_commands",
    ):
        if not isinstance(packet.get(key), list) or not packet.get(key):
            problems.append(f"{key} must be a non-empty list")
    attestations = packet.get("attestations")
    if not isinstance(attestations, Mapping):
        problems.append("attestations must be an object")
    else:
        for key in REQUIRED_ATTESTATIONS:
            if attestations.get(key) is not True:
                problems.append(f"attestation must be true: {key}")
    problems.extend(_packet_reference_problems(packet))
    forbidden_path = _find_forbidden_key(packet)
    if forbidden_path:
        problems.append(f"forbidden private/raw field present: {forbidden_path}")
    official_text_path = _find_official_action_claim(packet)
    if official_text_path:
        problems.append(f"official action language present: {official_text_path}")
    for proposal in _mapping_sequence(packet.get("field_proposals")):
        if proposal.get("draft_only") is not True:
            problems.append("each field proposal must be draft_only")
        if proposal.get("writes_pdf") is not False:
            problems.append("field proposals must not write PDFs")
        if proposal.get("requires_user_review") is not True:
            problems.append("field proposals must require user review")
        if proposal.get("source_status") != "fixture_only":
            problems.append("field proposals must be fixture_only")
        if not _string_list(proposal.get("citation_ids")):
            problems.append("field proposal citation_ids must be non-empty")
    if problems:
        raise DraftPreviewHandoffPacketV4Error("invalid draft preview handoff packet v4: " + "; ".join(problems))


def _adapter_request(action: str, pdf_mapping: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "workflow_id": str(pdf_mapping.get("workflow_id", "ppd-demo-permit-readiness")),
        "agent_goal": "Prepare a reversible draft-only local preview from committed fixtures.",
        "requested_action": action,
        "evidence_refs": [
            "agent-facing-readiness-contract-coverage-packet-v3",
            "process-model-fixtures-v1",
            "user-gap-analysis-fixtures-v1",
            "guardrail-bundle-fixtures-v1",
        ],
        "required_user_facts": _required_fact_keys(pdf_mapping),
        "user_facts": {fact: True for fact in _string_list(pdf_mapping.get("known_fact_keys"))},
    }


def _validate_source_fixtures(
    pdf_mapping: Mapping[str, Any],
    guardrails: Mapping[str, Any],
    readiness_outputs: Mapping[str, Mapping[str, Any]],
) -> None:
    if pdf_mapping.get("fixture_kind") != "local_pdf_field_mapping_fixtures_v4":
        raise DraftPreviewHandoffPacketV4Error("pdf mapping fixture_kind must be local_pdf_field_mapping_fixtures_v4")
    fields = pdf_mapping.get("fields")
    if not isinstance(fields, list) or not fields:
        raise DraftPreviewHandoffPacketV4Error("pdf mapping fields must be non-empty")
    blocked = set(_string_list(guardrails.get("blocked_actions")))
    missing_blocks = [action for action in REQUIRED_GUARDRAIL_BLOCKS if action not in blocked]
    if missing_blocks:
        raise DraftPreviewHandoffPacketV4Error("guardrail bundle missing blocked actions: " + ", ".join(missing_blocks))
    for key in ("preview", "missing_facts", "blocked_action"):
        output = readiness_outputs.get(key)
        if not isinstance(output, Mapping) or not _string_list(output.get("citations")):
            raise DraftPreviewHandoffPacketV4Error(f"readiness output lacks citations: {key}")


def _source_fixture_ids(
    pdf_mapping: Mapping[str, Any],
    guardrails: Mapping[str, Any],
    readiness_outputs: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    ids = [str(pdf_mapping.get("fixture_id", "")), str(guardrails.get("bundle_id", ""))]
    for output in readiness_outputs.values():
        adapter = output.get("adapter") if isinstance(output.get("adapter"), Mapping) else {}
        ids.append(str(adapter.get("fixture_packet_id", "")))
    return _unique_non_empty(ids)


def _readiness_summary(readiness_outputs: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for key in ("preview", "missing_facts", "blocked_action"):
        output = readiness_outputs[key]
        summary.append(
            {
                "output_id": key,
                "example_kind": str(output.get("example_kind", "")),
                "ready": bool(output.get("ready")),
                "citation_ids": _string_list(output.get("citations")),
                "safe_next_action_classes": _string_list(output.get("safe_next_action_classes")),
            }
        )
    return summary


def _field_proposals(pdf_mapping: Mapping[str, Any], missing_fact_keys: Sequence[str]) -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []
    missing = set(missing_fact_keys)
    for field in _mapping_sequence(pdf_mapping.get("fields")):
        fact_key = str(field.get("fact_key", ""))
        if fact_key in missing:
            continue
        proposals.append(
            {
                "proposal_id": f"draft-proposal-{field.get('field_id')}",
                "pdf_template_id": str(pdf_mapping.get("pdf_template_id", "")),
                "field_id": str(field.get("field_id", "")),
                "field_label": str(field.get("field_label", "")),
                "fact_key": fact_key,
                "proposal_source": "offline_agent_readiness_adapter_v4_and_pdf_mapping_fixture",
                "draft_display": str(field.get("draft_display", "Use cited fixture fact after user review.")),
                "source_status": "fixture_only",
                "draft_only": True,
                "writes_pdf": False,
                "requires_user_review": True,
                "citation_ids": _string_list(field.get("citation_ids")),
            }
        )
    return proposals


def _missing_fact_blockers(
    pdf_mapping: Mapping[str, Any],
    missing_fact_keys: Sequence[str],
    readiness_outputs: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    fields_by_fact = {str(field.get("fact_key", "")): field for field in _mapping_sequence(pdf_mapping.get("fields"))}
    blockers: list[dict[str, Any]] = []
    adapter_citations = _string_list(readiness_outputs["missing_facts"].get("citations"))
    for fact_key in missing_fact_keys:
        field = fields_by_fact.get(fact_key, {})
        blockers.append(
            {
                "blocker_id": f"missing-fact-{fact_key}",
                "fact_key": fact_key,
                "question": str(field.get("missing_fact_question", f"Provide {fact_key} before previewing this field.")),
                "blocks_field_ids": [str(field.get("field_id", fact_key))],
                "blocks_official_actions": ["upload", "certification", "submission", "payment", "inspection_scheduling"],
                "citation_ids": _unique_non_empty(_string_list(field.get("citation_ids")) + adapter_citations),
            }
        )
    if not blockers:
        blockers.append(
            {
                "blocker_id": "adapter-missing-fact-checkpoint",
                "fact_key": "adapter_missing_fact_review",
                "question": "Confirm the readiness adapter has no missing-fact prompt before treating the local preview as reviewable.",
                "blocks_field_ids": [],
                "blocks_official_actions": ["upload", "certification", "submission", "payment", "inspection_scheduling"],
                "citation_ids": adapter_citations,
            }
        )
    return blockers


def _user_review_checkpoints(
    pdf_mapping: Mapping[str, Any],
    guardrails: Mapping[str, Any],
    consumed_refs: Sequence[str],
) -> list[dict[str, Any]]:
    return [
        {
            "checkpoint_id": "review-field-proposals-before-use",
            "review_required": True,
            "summary": "User reviews each cited draft-only field proposal before any local preview is reused.",
            "stops_before": ["upload", "certification", "submission", "payment", "inspection_scheduling"],
            "citation_ids": _unique_non_empty(_string_list(pdf_mapping.get("citation_ids")) + list(consumed_refs)),
        },
        {
            "checkpoint_id": "guardrail-official-action-stop",
            "review_required": True,
            "summary": "Guardrail bundle keeps official DevHub actions outside this offline packet.",
            "stops_before": _string_list(guardrails.get("blocked_actions")),
            "citation_ids": _unique_non_empty([str(guardrails.get("bundle_id", ""))] + list(consumed_refs)),
        },
    ]


def _rollback_notes(pdf_mapping: Mapping[str, Any], consumed_refs: Sequence[str]) -> list[dict[str, Any]]:
    return [
        {
            "rollback_note_id": "discard-local-preview-only",
            "summary": "Discard generated preview text and rerun the fixture packet; no private file, PDF, DevHub, payment, submission, certification, upload, or inspection state is changed.",
            "rollback_scope": "local draft packet only",
            "citation_ids": _unique_non_empty(_string_list(pdf_mapping.get("citation_ids")) + list(consumed_refs)),
        }
    ]


def _offline_validation_commands() -> list[list[str]]:
    return [
        ["python3", "-m", "py_compile", "ppd/draft_preview_agent_handoff_packet_v4.py"],
        ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
    ]


def _packet_reference_problems(packet: Mapping[str, Any]) -> list[str]:
    known: set[str] = set(_string_list(packet.get("source_fixture_ids")))
    for item in _mapping_sequence(packet.get("readiness_adapter_outputs")):
        known.update(_string_list(item.get("citation_ids")))
    for item in _mapping_sequence(packet.get("field_proposals")):
        known.update(_string_list(item.get("citation_ids")))
    problems: list[str] = []
    for section in ("field_proposals", "missing_fact_blockers", "user_review_checkpoints", "rollback_notes"):
        for index, item in enumerate(_mapping_sequence(packet.get(section))):
            citations = _string_list(item.get("citation_ids"))
            if not citations:
                problems.append(f"{section}[{index}] citation_ids must be non-empty")
            unknown = [citation for citation in citations if citation not in known]
            if unknown:
                problems.append(f"{section}[{index}] has unknown citations: {', '.join(unknown)}")
    return problems


def _consumed_refs(
    pdf_mapping: Mapping[str, Any],
    guardrails: Mapping[str, Any],
    readiness_outputs: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    refs = _string_list(pdf_mapping.get("citation_ids")) + [str(guardrails.get("bundle_id", ""))]
    for output in readiness_outputs.values():
        refs.extend(_string_list(output.get("citations")))
    return _unique_non_empty(refs)


def _required_fact_keys(pdf_mapping: Mapping[str, Any]) -> list[str]:
    facts: list[str] = []
    for field in _mapping_sequence(pdf_mapping.get("fields")):
        fact_key = field.get("fact_key")
        if isinstance(fact_key, str) and fact_key:
            facts.append(fact_key)
    return _unique_non_empty(facts)


def _find_forbidden_key(value: object, prefix: str = "") -> str | None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key).lower() in FORBIDDEN_KEYS:
                return path
            nested = _find_forbidden_key(child, path)
            if nested:
                return nested
    elif isinstance(value, list):
        for index, child in enumerate(value):
            nested = _find_forbidden_key(child, f"{prefix}[{index}]")
            if nested:
                return nested
    return None


def _find_official_action_claim(value: object, prefix: str = "") -> str | None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            found = _find_official_action_claim(child, path)
            if found:
                return found
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found = _find_official_action_claim(child, f"{prefix}[{index}]")
            if found:
                return found
    elif isinstance(value, str):
        lowered = value.lower()
        if any(word in lowered for word in OFFICIAL_ACTION_WORDS) and "stops_before" not in prefix and "blocks_official_actions" not in prefix:
            if "no " not in lowered and "cannot " not in lowered and "outside " not in lowered and "unchanged" not in lowered:
                return prefix
    return None


def _mapping_sequence(value: object) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _unique_non_empty(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-field-mapping", type=Path, default=DEFAULT_PDF_FIELD_MAPPING_PATH)
    parser.add_argument("--guardrail-bundle", type=Path, default=DEFAULT_GUARDRAIL_BUNDLE_PATH)
    parser.add_argument("--readiness-fixture-root", type=Path, default=DEFAULT_READINESS_FIXTURE_ROOT)
    args = parser.parse_args(argv)
    packet = build_packet_from_paths(args.pdf_field_mapping, args.guardrail_bundle, args.readiness_fixture_root)
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
