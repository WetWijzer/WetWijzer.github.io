"""Deterministic GuardrailBundle compiler skeleton.

This module intentionally implements a small validation and normalization layer only.
It gives PP&D tests a stable formal surface for guardrail bundle categories before
any richer logic backend is attached.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


class GuardrailCompileError(ValueError):
    """Raised when a guardrail bundle is malformed."""


@dataclass(frozen=True)
class CompiledGuardrailBundle:
    """Normalized guardrail bundle categories used by downstream PP&D checks."""

    deterministic_predicates: tuple[Mapping[str, Any], ...]
    deontic_rules: tuple[Mapping[str, Any], ...]
    temporal_rules: tuple[Mapping[str, Any], ...]
    exact_confirmation_predicates: tuple[Mapping[str, Any], ...]
    refused_action_predicates: tuple[Mapping[str, Any], ...]
    explanation_support_maps: Mapping[str, tuple[str, ...]]

    def category_counts(self) -> dict[str, int]:
        return {
            "deterministic_predicates": len(self.deterministic_predicates),
            "deontic_rules": len(self.deontic_rules),
            "temporal_rules": len(self.temporal_rules),
            "exact_confirmation_predicates": len(self.exact_confirmation_predicates),
            "refused_action_predicates": len(self.refused_action_predicates),
            "explanation_support_maps": len(self.explanation_support_maps),
        }


class GuardrailBundleCompiler:
    """Compile a raw guardrail bundle into deterministic normalized categories."""

    _LIST_FIELDS = (
        "deterministic_predicates",
        "deontic_rules",
        "temporal_rules",
        "exact_confirmation_predicates",
        "refused_action_predicates",
    )

    def compile(self, bundle: Mapping[str, Any]) -> CompiledGuardrailBundle:
        if not isinstance(bundle, Mapping):
            raise GuardrailCompileError("guardrail bundle must be a mapping")

        normalized_lists = {
            field: self._normalize_rule_list(bundle.get(field, ()), field)
            for field in self._LIST_FIELDS
        }
        support_maps = self._normalize_support_maps(bundle.get("explanation_support_maps", {}))

        known_rule_ids = {
            str(item["id"])
            for field in self._LIST_FIELDS
            for item in normalized_lists[field]
        }
        unknown_support_ids = sorted(set(support_maps) - known_rule_ids)
        if unknown_support_ids:
            joined = ", ".join(unknown_support_ids)
            raise GuardrailCompileError(f"explanation support references unknown rule ids: {joined}")

        return CompiledGuardrailBundle(
            deterministic_predicates=normalized_lists["deterministic_predicates"],
            deontic_rules=normalized_lists["deontic_rules"],
            temporal_rules=normalized_lists["temporal_rules"],
            exact_confirmation_predicates=normalized_lists["exact_confirmation_predicates"],
            refused_action_predicates=normalized_lists["refused_action_predicates"],
            explanation_support_maps=support_maps,
        )

    def _normalize_rule_list(self, value: Any, field: str) -> tuple[Mapping[str, Any], ...]:
        if value is None:
            return ()
        if not isinstance(value, list):
            raise GuardrailCompileError(f"{field} must be a list")

        seen_ids: set[str] = set()
        normalized: list[Mapping[str, Any]] = []
        for index, item in enumerate(value):
            if not isinstance(item, Mapping):
                raise GuardrailCompileError(f"{field}[{index}] must be a mapping")
            rule_id = item.get("id")
            if not isinstance(rule_id, str) or not rule_id.strip():
                raise GuardrailCompileError(f"{field}[{index}].id must be a non-empty string")
            if rule_id in seen_ids:
                raise GuardrailCompileError(f"duplicate guardrail id: {rule_id}")
            seen_ids.add(rule_id)
            normalized.append(dict(item))
        return tuple(normalized)

    def _normalize_support_maps(self, value: Any) -> Mapping[str, tuple[str, ...]]:
        if value is None:
            return {}
        if not isinstance(value, Mapping):
            raise GuardrailCompileError("explanation_support_maps must be a mapping")

        normalized: dict[str, tuple[str, ...]] = {}
        for rule_id, support_ids in value.items():
            if not isinstance(rule_id, str) or not rule_id.strip():
                raise GuardrailCompileError("explanation support rule ids must be non-empty strings")
            if not isinstance(support_ids, list):
                raise GuardrailCompileError(f"explanation support for {rule_id} must be a list")
            cleaned: list[str] = []
            for index, support_id in enumerate(support_ids):
                if not isinstance(support_id, str) or not support_id.strip():
                    raise GuardrailCompileError(
                        f"explanation support for {rule_id}[{index}] must be a non-empty string"
                    )
                cleaned.append(support_id)
            normalized[rule_id] = tuple(cleaned)
        return normalized
