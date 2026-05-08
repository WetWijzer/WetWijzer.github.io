from __future__ import annotations

import json
from pathlib import Path

from ppd.source_registry_validation import validate_source_entry, validate_source_registry


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "source_registry" / "surfaces.json"


def test_expected_surface_categories_are_classified() -> None:
    entries = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    results = {result.source_id: result for result in validate_source_registry(entries)}

    assert results["public-permit-index"].allowed is True
    assert results["devhub-account-permits"].allowed is True
    assert results["devhub-draft-application"].allowed is True
    assert results["issued-permit-certification"].allowed is False
    assert results["fee-payment"].allowed is False
    assert results["unknown-third-party-form"].allowed is False


def test_authenticated_read_only_requires_read_only_declaration() -> None:
    result = validate_source_entry(
        {
            "id": "mutable-authenticated-workflow",
            "surface": "authenticated_read_only",
            "authenticated": True,
            "read_only": False,
        }
    )

    assert result.allowed is False
    assert "read_only=true" in result.reason


def test_reversible_draft_requires_reversible_declaration() -> None:
    result = validate_source_entry(
        {
            "id": "irreversible-draft-workflow",
            "surface": "reversible_draft",
            "reversible": False,
        }
    )

    assert result.allowed is False
    assert "reversible=true" in result.reason


def test_unknown_surface_is_rejected() -> None:
    result = validate_source_entry({"id": "surprise-workflow", "surface": "mystery"})

    assert result.allowed is False
    assert result.reason == "unknown surface category"
