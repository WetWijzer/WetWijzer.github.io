"""Fixture-first public source refresh reviewer queue v1.

This module only transforms metadata supplied by fixtures. It does not crawl,
download, invoke processors, read raw page bodies, or mutate registries.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

QUEUE_VERSION = "public_source_refresh_reviewer_queue_v1"
RAW_BODY_KEYS = frozenset(
    {
        "body",
        "content",
        "document",
        "html",
        "markdown",
        "raw",
        "raw_body",
        "raw_content",
        "response_body",
        "text",
        "text_body",
    }
)
ATTESTATIONS = {
    "no_recrawl": True,
    "no_download": True,
    "no_processor": True,
    "no_raw_body": True,
    "no_registry_mutation": True,
}
DEFAULT_OFFLINE_VALIDATION_COMMANDS = [
    ["python3", "-m", "py_compile", "ppd/public_source_refresh_reviewer_queue.py"],
    ["python3", "-m", "pytest", "ppd/tests/test_public_source_refresh_reviewer_queue.py"],
]


@dataclass(frozen=True)
class QueueInputError(ValueError):
    """Raised when fixture input is not safe metadata-only queue input."""

    message: str

    def __str__(self) -> str:
        return self.message


def _reject_raw_body_fields(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            if key_text.lower() in RAW_BODY_KEYS:
                raise QueueInputError(f"raw body field is not allowed at {path}.{key_text}")
            _reject_raw_body_fields(child, f"{path}.{key_text}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_raw_body_fields(child, f"{path}[{index}]")


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise QueueInputError(f"{name} must be an object")
    return value


def _require_list(value: Any, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise QueueInputError(f"{name} must be a list")
    return value


def _string_list(value: Any, name: str) -> list[str]:
    items = _require_list(value, name)
    result: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, str) or not item.strip():
            raise QueueInputError(f"{name}[{index}] must be a non-empty string")
        result.append(item)
    return result


def _decision_by_source(decision_matrix: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    decisions = decision_matrix.get("decisions", [])
    if isinstance(decisions, Mapping):
        iterable = decisions.values()
    else:
        iterable = _require_list(decisions, "decision_matrix.decisions")

    indexed: dict[str, Mapping[str, Any]] = {}
    for index, decision in enumerate(iterable):
        decision_obj = _require_mapping(decision, f"decision_matrix.decisions[{index}]")
        source_id = decision_obj.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            raise QueueInputError(f"decision_matrix.decisions[{index}].source_id must be a non-empty string")
        indexed[source_id] = decision_obj
    return indexed


def build_public_source_refresh_reviewer_queue(
    evidence_packet: Mapping[str, Any], decision_matrix: Mapping[str, Any]
) -> dict[str, Any]:
    """Build cited metadata-only reviewer queue items from fixture packets."""

    evidence_packet = _require_mapping(evidence_packet, "evidence_packet")
    decision_matrix = _require_mapping(decision_matrix, "decision_matrix")
    _reject_raw_body_fields(evidence_packet, "evidence_packet")
    _reject_raw_body_fields(decision_matrix, "decision_matrix")

    sources = _require_list(evidence_packet.get("sources", []), "evidence_packet.sources")
    decisions = _decision_by_source(decision_matrix)
    items: list[dict[str, Any]] = []

    for index, source in enumerate(sources):
        source_obj = _require_mapping(source, f"evidence_packet.sources[{index}]")
        source_id = source_obj.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            raise QueueInputError(f"evidence_packet.sources[{index}].source_id must be a non-empty string")

        requirement_ids = _string_list(
            source_obj.get("requirement_ids", []),
            f"evidence_packet.sources[{index}].requirement_ids",
        )
        evidence = _require_mapping(source_obj.get("evidence", {}), f"evidence_packet.sources[{index}].evidence")
        decision = decisions.get(source_id, {})

        public_page_title = source_obj.get("public_page_title")
        title_observed = evidence.get("title_observed")
        updated_date_visible = bool(evidence.get("updated_date_visible", False))
        updated_date_text = evidence.get("updated_date_text")

        title_check = {
            "expected_title": public_page_title,
            "observed_title": title_observed,
            "status": "needs_review" if public_page_title != title_observed else "matches_fixture_metadata",
        }
        updated_date_review = {
            "visible": updated_date_visible,
            "observed_text": updated_date_text,
            "status": "needs_review" if not updated_date_visible else "visible_in_fixture_metadata",
        }

        item = {
            "queue_item_id": f"psrrq-v1-{source_id}",
            "queue_version": QUEUE_VERSION,
            "source_id": source_id,
            "requirement_ids": requirement_ids,
            "reviewer_owner": decision.get("reviewer_owner", "ppd-public-source-reviewer"),
            "review_status": decision.get("review_status", "needs_review"),
            "public_url": source_obj.get("public_url"),
            "public_page_title_check": title_check,
            "visible_updated_date_review": updated_date_review,
            "affected_source_ids": [source_id],
            "affected_requirement_ids": requirement_ids,
            "defer_reason": decision.get("defer_reason"),
            "rollback_notes": decision.get("rollback_notes", "Retain current public corpus metadata until reviewer approval."),
            "offline_validation_commands": deepcopy(
                decision.get("offline_validation_commands", DEFAULT_OFFLINE_VALIDATION_COMMANDS)
            ),
            "citations": [
                {
                    "kind": "public_source_refresh_evidence_intake_packet_v1",
                    "packet_id": evidence_packet.get("packet_id"),
                    "source_id": source_id,
                    "metadata_fields": [
                        "public_page_title",
                        "public_url",
                        "evidence.title_observed",
                        "evidence.updated_date_visible",
                        "evidence.updated_date_text",
                    ],
                },
                {
                    "kind": "release_gate_decision_matrix_v1",
                    "matrix_id": decision_matrix.get("matrix_id"),
                    "source_id": source_id,
                    "metadata_fields": [
                        "reviewer_owner",
                        "review_status",
                        "defer_reason",
                        "rollback_notes",
                        "offline_validation_commands",
                    ],
                },
            ],
            "attestations": deepcopy(ATTESTATIONS),
        }
        items.append(item)

    return {
        "queue_version": QUEUE_VERSION,
        "source_packet_id": evidence_packet.get("packet_id"),
        "decision_matrix_id": decision_matrix.get("matrix_id"),
        "metadata_only": True,
        "attestations": deepcopy(ATTESTATIONS),
        "items": items,
    }
