"""Formal guardrail bundle contract for reviewed PP&D requirement nodes.

The compiler in this module is intentionally small and deterministic. It accepts
already-reviewed requirement nodes and emits a serializable guardrail bundle that
can be consumed by higher-level PP&D planning or automation code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

REVIEWED_STATUSES = frozenset({"reviewed", "approved", "accepted"})


@dataclass(frozen=True)
class GuardrailBundle:
    """Serializable bundle of formal guardrail facts."""

    obligations: list[dict[str, Any]] = field(default_factory=list)
    prerequisites: list[dict[str, Any]] = field(default_factory=list)
    temporal_ordering: list[dict[str, Any]] = field(default_factory=list)
    missing_fact_prompts: list[dict[str, Any]] = field(default_factory=list)
    exact_confirmation_gates: list[dict[str, Any]] = field(default_factory=list)
    refused_official_action_predicates: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": 1,
            "obligations": self.obligations,
            "prerequisites": self.prerequisites,
            "temporal_ordering": self.temporal_ordering,
            "missing_fact_prompts": self.missing_fact_prompts,
            "exact_confirmation_gates": self.exact_confirmation_gates,
            "refused_official_action_predicates": self.refused_official_action_predicates,
        }


def compile_guardrail_bundle(nodes: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Compile reviewed requirement nodes into a formal guardrail bundle.

    Input nodes are plain mappings so fixture data can be loaded directly from
    JSON. Nodes whose status is not reviewed/approved/accepted are ignored.
    """

    reviewed_nodes = [node for node in nodes if _is_reviewed(node)]
    reviewed_nodes.sort(key=lambda node: str(node.get("id", "")))

    obligations: list[dict[str, Any]] = []
    prerequisites: list[dict[str, Any]] = []
    temporal_ordering: list[dict[str, Any]] = []
    missing_fact_prompts: list[dict[str, Any]] = []
    exact_confirmation_gates: list[dict[str, Any]] = []
    refused_predicates: list[dict[str, Any]] = []

    reviewed_ids = {str(node["id"]) for node in reviewed_nodes if node.get("id")}

    for node in reviewed_nodes:
        node_id = _required_text(node, "id")
        text = _required_text(node, "text")
        source = str(node.get("source", "reviewed_ppd_requirement"))

        obligations.append(
            {
                "id": f"obligation:{node_id}",
                "node_id": node_id,
                "predicate": "must_satisfy_requirement",
                "text": text,
                "source": source,
            }
        )

        for prerequisite_id in _text_list(node.get("prerequisites")):
            if prerequisite_id in reviewed_ids:
                prerequisites.append(
                    {
                        "id": f"prerequisite:{node_id}:{prerequisite_id}",
                        "node_id": node_id,
                        "requires_node_id": prerequisite_id,
                        "predicate": "requires_prior_satisfied_requirement",
                    }
                )

        for predecessor_id in _text_list(node.get("temporal_after")):
            if predecessor_id in reviewed_ids:
                temporal_ordering.append(
                    {
                        "id": f"after:{predecessor_id}:{node_id}",
                        "before_node_id": predecessor_id,
                        "after_node_id": node_id,
                        "predicate": "must_occur_after",
                    }
                )

        for fact_name in _text_list(node.get("missing_facts")):
            missing_fact_prompts.append(
                {
                    "id": f"missing_fact:{node_id}:{fact_name}",
                    "node_id": node_id,
                    "fact": fact_name,
                    "prompt": f"Confirm {fact_name} before satisfying {node_id}.",
                    "predicate": "requires_missing_fact_answer",
                }
            )

        if bool(node.get("exact_confirmation")):
            exact_confirmation_gates.append(
                {
                    "id": f"exact_confirmation:{node_id}",
                    "node_id": node_id,
                    "required_text": text,
                    "predicate": "requires_exact_user_confirmation",
                }
            )

        for action_name in _text_list(node.get("refused_official_actions")):
            refused_predicates.append(
                {
                    "id": f"refuse:{node_id}:{action_name}",
                    "node_id": node_id,
                    "official_action": action_name,
                    "predicate": "refuse_official_action_without_authority",
                }
            )

    bundle = GuardrailBundle(
        obligations=obligations,
        prerequisites=prerequisites,
        temporal_ordering=temporal_ordering,
        missing_fact_prompts=missing_fact_prompts,
        exact_confirmation_gates=exact_confirmation_gates,
        refused_official_action_predicates=refused_predicates,
    )
    return bundle.to_dict()


def _is_reviewed(node: Mapping[str, Any]) -> bool:
    return str(node.get("status", "")).strip().lower() in REVIEWED_STATUSES


def _required_text(node: Mapping[str, Any], key: str) -> str:
    value = node.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"reviewed requirement node is missing non-empty {key!r}")
    return value.strip()


def _text_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("guardrail list fields must be JSON arrays")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError("guardrail list fields must contain non-empty strings")
        result.append(item.strip())
    return result
