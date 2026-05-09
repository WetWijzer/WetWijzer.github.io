"""Deterministic PP&D requirement extraction helpers for fixture validation."""

from __future__ import annotations

import re
from typing import Dict, List

_REQUIREMENT_PATTERNS = [
    ("prohibition", re.compile(r"\b(?:must not|may not|shall not|is prohibited from)\b", re.IGNORECASE)),
    ("permission", re.compile(r"\b(?:may|is allowed to|is permitted to)\b", re.IGNORECASE)),
    ("precondition", re.compile(r"\b(?:before|prior to|only after)\b", re.IGNORECASE)),
    ("deadline", re.compile(r"\b(?:within|no later than|by)\b.*\b(?:day|days|hour|hours|date)\b", re.IGNORECASE)),
    ("fee_trigger", re.compile(r"\b(?:fee|charge|payment)\b.*\b(?:is due|must be paid|applies|required)\b", re.IGNORECASE)),
    ("license_requirement", re.compile(r"\b(?:license|licensed|contractor registration)\b", re.IGNORECASE)),
    ("document_requirement", re.compile(r"\b(?:submit|provide|upload|attach)\b.*\b(?:document|plan|drawing|form|affidavit|report)\b", re.IGNORECASE)),
    ("action_gate", re.compile(r"\b(?:until|unless|only after)\b.*\b(?:approved|approval|inspection|review|issued)\b", re.IGNORECASE)),
    ("obligation", re.compile(r"\b(?:must|shall|required to|is required to)\b", re.IGNORECASE)),
]

_EVIDENCE_RE = re.compile(r"^\s*\[(E\d+)\]\s*(.+?)\s*$")


def extract_requirement_nodes(guidance_text: str) -> List[Dict[str, str]]:
    """Extract requirement nodes from evidence-marked synthetic guidance text.

    Each non-empty input line should start with an evidence marker such as ``[E1]``.
    The first matching requirement pattern determines the node type for that line.
    """

    nodes: List[Dict[str, str]] = []
    for raw_line in guidance_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        evidence_match = _EVIDENCE_RE.match(line)
        if not evidence_match:
            continue

        evidence_id, text = evidence_match.groups()
        for node_type, pattern in _REQUIREMENT_PATTERNS:
            if pattern.search(text):
                nodes.append(
                    {
                        "id": f"{evidence_id.lower()}_{node_type}",
                        "type": node_type,
                        "text": text,
                        "source_evidence_id": evidence_id,
                    }
                )
                break

    return nodes
