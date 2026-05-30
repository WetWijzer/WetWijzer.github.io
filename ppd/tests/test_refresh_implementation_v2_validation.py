from __future__ import annotations

from pathlib import Path
import json

from ppd.proposal_validation.refresh_implementation_v2 import (
    validate_refresh_implementation_proposal_v2,
)


_FIXTURES = Path(__file__).parent / "fixtures" / "refresh_implementation_v2"


def _fixture(name: str) -> dict:
    return json.loads((_FIXTURES / name).read_text(encoding="utf-8"))


def test_refresh_implementation_v2_accepts_minimal_cited_patch_row() -> None:
    errors = validate_refresh_implementation_proposal_v2(_fixture("valid_minimal.json"))
    assert errors == []


def test_refresh_implementation_v2_rejects_missing_row_controls() -> None:
    errors = validate_refresh_implementation_proposal_v2(_fixture("missing_controls.json"))
    joined = "\n".join(errors)

    assert "uncited patch row" in joined
    assert "missing source target id" in joined
    assert "missing surface target id" in joined
    assert "missing guardrail target id" in joined
    assert "missing dependency ordering" in joined
    assert "missing rollback notes" in joined
    assert "missing reviewer owner" in joined


def test_refresh_implementation_v2_rejects_forbidden_claims_and_artifacts() -> None:
    errors = validate_refresh_implementation_proposal_v2(_fixture("forbidden_claims.json"))
    joined = "\n".join(errors)

    assert "raw crawl/pdf/session/browser artifact" in joined
    assert "private or authenticated fact" in joined
    assert "live execution or promotion claim" in joined
    assert "legal or permitting outcome guarantee" in joined
    assert "consequential action language" in joined


def test_refresh_implementation_v2_rejects_active_mutation_flags() -> None:
    errors = validate_refresh_implementation_proposal_v2(_fixture("active_mutations.json"))
    joined = "\n".join(errors)

    assert "active mutation flag active_source_mutation is not allowed" in joined
    assert "active surface-registry mutation is not allowed" in joined
    assert "active prompt mutation is not allowed" in joined
