"""Deterministic user gap analysis helpers for PP&D workflows.

The rule in this module intentionally uses only caller-provided local facts and
source evidence ids. It does not fetch, infer, or enrich facts from external
systems.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class UserGap:
    """A missing user fact required by a source-grounded workflow."""

    fact_id: str
    label: str
    source_evidence_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "fact_id": self.fact_id,
            "label": self.label,
            "source_evidence_ids": list(self.source_evidence_ids),
        }


def _has_value(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return bool(value)
    if isinstance(value, Mapping):
        return bool(value)
    return True


def find_user_gaps(
    *,
    local_user_facts: Mapping[str, object],
    required_facts: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Return missing required user facts in deterministic order.

    Each required fact must provide:
    - fact_id: stable local fact key
    - label: user-facing description of the fact
    - source_evidence_ids: non-empty source evidence id list

    The function deliberately treats the supplied mappings as the full universe
    of facts. It performs no source lookup and makes no eligibility inference.
    """

    gaps: list[UserGap] = []
    for required in required_facts:
        fact_id = str(required.get("fact_id", "")).strip()
        label = str(required.get("label", fact_id)).strip()
        evidence_raw = required.get("source_evidence_ids", ())
        if isinstance(evidence_raw, str):
            source_evidence_ids = (evidence_raw,)
        else:
            source_evidence_ids = tuple(str(item).strip() for item in evidence_raw if str(item).strip())

        if not fact_id:
            raise ValueError("required fact is missing fact_id")
        if not source_evidence_ids:
            raise ValueError(f"required fact {fact_id!r} is missing source_evidence_ids")

        if not _has_value(local_user_facts.get(fact_id)):
            gaps.append(
                UserGap(
                    fact_id=fact_id,
                    label=label or fact_id,
                    source_evidence_ids=source_evidence_ids,
                )
            )

    return [gap.as_dict() for gap in gaps]
