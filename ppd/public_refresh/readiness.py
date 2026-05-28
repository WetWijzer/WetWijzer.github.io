"""Metadata-only public refresh promotion readiness packets.

The packet builder is intentionally fixture-first and side-effect free. It joins
already-produced public refresh metadata and reports whether those outputs are
ready to promote into downstream PP&D guardrails. It never fetches sources and
rejects inputs that appear to contain raw page bodies, downloaded documents,
private paths, private URLs, authenticated URLs, stale citations, incomplete
human review, or guardrail promotion without refreshed process-model evidence.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse

_METADATA_ONLY_FORBIDDEN_KEYS = {
    "body",
    "content",
    "document_body",
    "downloaded_document_path",
    "downloaded_path",
    "file_path",
    "html",
    "local_path",
    "markdown",
    "path_on_disk",
    "raw_body",
    "raw_content",
    "raw_html",
    "saved_path",
    "text",
}
_READY_STATUSES = {"approved", "current", "formalized", "not_required", "ready", "valid"}
_REVIEW_COMPLETE_STATUSES = {"approved", "not_required"}
_FORMALIZED_STATUSES = {"formalized", "not_required"}
_CURRENT_FRESHNESS_STATUSES = {"current", "unchanged", "accepted_change"}
_PUBLIC_HOSTS = {"portland.gov", "www.portland.gov", "www.portlandoregon.gov", "devhub.portlandoregon.gov"}
_AUTHENTICATED_URL_HINTS = (
    "/account",
    "/accounts",
    "/application",
    "/applications",
    "/dashboard",
    "/login",
    "/logout",
    "/my",
    "/permit/",
    "/permits/",
    "/register",
    "/signin",
    "/sign-in",
    "/user",
)
_AUTHENTICATED_QUERY_HINTS = {"access_token", "auth", "code", "session", "state", "token"}


def build_readiness_packet_from_files(
    *,
    ingestion_outputs_path: Path,
    requirement_delta_status_path: Path,
    process_model_versions_path: Path,
    source_freshness_path: Path,
    human_review_state_path: Path,
    generated_at: str = "fixture-generated-at",
) -> dict[str, Any]:
    """Build a readiness packet from committed fixture or run metadata files."""

    return build_readiness_packet(
        ingestion_outputs=_load_json(ingestion_outputs_path),
        requirement_delta_status=_load_json(requirement_delta_status_path),
        process_model_versions=_load_json(process_model_versions_path),
        source_freshness=_load_json(source_freshness_path),
        human_review_state=_load_json(human_review_state_path),
        generated_at=generated_at,
    )


def build_readiness_packet(
    *,
    ingestion_outputs: Mapping[str, Any],
    requirement_delta_status: Mapping[str, Any],
    process_model_versions: Mapping[str, Any],
    source_freshness: Mapping[str, Any],
    human_review_state: Mapping[str, Any],
    generated_at: str = "fixture-generated-at",
) -> dict[str, Any]:
    """Return one metadata-only blocked-or-ready promotion packet."""

    inputs = {
        "ingestion_outputs": dict(ingestion_outputs),
        "requirement_delta_status": dict(requirement_delta_status),
        "process_model_versions": dict(process_model_versions),
        "source_freshness": dict(source_freshness),
        "human_review_state": dict(human_review_state),
    }
    context = _ReadinessContext(inputs)
    gates = [
        _ingestion_gate(inputs["ingestion_outputs"]),
        _requirement_delta_gate(inputs["requirement_delta_status"], context),
        _process_model_gate(inputs["process_model_versions"], context),
        _source_freshness_gate(inputs["source_freshness"], context),
        _human_review_gate(inputs["human_review_state"], context),
        _guardrail_process_evidence_gate(context),
    ]
    blockers = [blocker for gate in gates for blocker in gate["blockers"]]
    status = "ready" if not blockers else "blocked"

    return {
        "packet_type": "ppd_public_refresh_promotion_readiness",
        "packet_version": "1.1",
        "packet_id": _stable_packet_id(inputs),
        "generated_at": generated_at,
        "status": status,
        "metadata_only": True,
        "live_crawl_performed": False,
        "raw_bodies_persisted": False,
        "inputs": _input_summary(inputs),
        "gates": gates,
        "blockers": blockers,
        "ready_items": [gate["gate"] for gate in gates if gate["status"] == "ready"],
    }


class _ReadinessContext:
    def __init__(self, inputs: Mapping[str, Mapping[str, Any]]) -> None:
        self.ingestion_outputs = _list(inputs["ingestion_outputs"], "outputs")
        self.requirement_deltas = _list(inputs["requirement_delta_status"], "deltas")
        self.process_models = _list(inputs["process_model_versions"], "process_models")
        self.sources = _list(inputs["source_freshness"], "sources")
        self.reviews = _list(inputs["human_review_state"], "reviews")
        self.current_evidence_ids = _current_evidence_ids(self.ingestion_outputs)
        self.current_source_hashes = _source_hashes(self.sources)
        self.ingestion_source_hashes = _source_hashes(self.ingestion_outputs)
        self.completed_review_subjects = {
            _text(review.get("subject_id"))
            for review in self.reviews
            if _text(review.get("status")).lower() in _REVIEW_COMPLETE_STATUSES
        }


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object in {path}")
    return data


def _stable_packet_id(inputs: Mapping[str, Any]) -> str:
    encoded = json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "ppd-refresh-ready-" + hashlib.sha256(encoded).hexdigest()[:16]


def _input_summary(inputs: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    ingestion_outputs = _list(inputs["ingestion_outputs"], "outputs")
    requirement_deltas = _list(inputs["requirement_delta_status"], "deltas")
    process_models = _list(inputs["process_model_versions"], "process_models")
    sources = _list(inputs["source_freshness"], "sources")
    reviews = _list(inputs["human_review_state"], "reviews")
    return {
        "refresh_id": inputs["ingestion_outputs"].get("refresh_id"),
        "ingestion_output_count": len(ingestion_outputs),
        "requirement_delta_count": len(requirement_deltas),
        "process_model_count": len(process_models),
        "source_count": len(sources),
        "human_review_count": len(reviews),
        "source_ids": sorted(_string_values(item.get("source_id") for item in ingestion_outputs + sources)),
        "process_ids": sorted(_string_values(item.get("process_id") for item in process_models)),
        "requirement_ids": sorted(_string_values(item.get("requirement_id") for item in requirement_deltas)),
    }


def _ingestion_gate(data: Mapping[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    outputs = _list(data, "outputs")
    if not outputs:
        blockers.append("public refresh ingestion outputs are missing")

    for index, output in enumerate(outputs):
        label = _label(output, index, "source_id")
        forbidden = sorted(_find_forbidden_body_keys(output))
        if forbidden:
            blockers.append(f"{label} includes raw body-like or downloaded document path keys: {', '.join(forbidden)}")
        if output.get("no_raw_body_persisted") is not True:
            blockers.append(f"{label} does not assert no_raw_body_persisted=true")
        if output.get("metadata_only") is not True:
            blockers.append(f"{label} does not assert metadata_only=true")
        if not output.get("content_hash") and not output.get("skipped_reason"):
            blockers.append(f"{label} lacks content_hash or skipped_reason metadata")
        if not output.get("normalized_document_id") and not output.get("skipped_reason"):
            blockers.append(f"{label} lacks normalized_document_id or skipped_reason metadata")
        for url_key in ("canonical_url", "requested_url", "source_url"):
            url_blocker = _public_url_blocker(output.get(url_key), label, url_key)
            if url_blocker:
                blockers.append(url_blocker)

    return _gate("public_refresh_ingestion_metadata", blockers)


def _requirement_delta_gate(data: Mapping[str, Any], context: _ReadinessContext) -> dict[str, Any]:
    blockers: list[str] = []
    deltas = _list(data, "deltas")
    if not deltas:
        blockers.append("requirement delta status records are missing")

    for index, delta in enumerate(deltas):
        label = _label(delta, index, "delta_id")
        delta_id = _text(delta.get("delta_id") or delta.get("id"))
        formalization_status = _text(delta.get("formalization_status")).lower()
        if formalization_status not in _FORMALIZED_STATUSES:
            blockers.append(f"{label} formalization_status is {formalization_status or 'missing'}")
        review_status = _text(delta.get("human_review_status") or delta.get("review_status")).lower()
        if review_status not in _REVIEW_COMPLETE_STATUSES:
            blockers.append(f"{label} human_review_status is {review_status or 'missing'}")
        if delta_id and review_status != "not_required" and delta_id not in context.completed_review_subjects:
            blockers.append(f"{label} lacks completed human review record")
        if not delta.get("requirement_id"):
            blockers.append(f"{label} lacks requirement_id")
        if not _sequence(delta.get("affected_process_ids") or delta.get("process_ids")):
            blockers.append(f"{label} lacks affected_process_ids")
        if not _sequence(delta.get("affected_guardrail_ids") or delta.get("guardrail_ids") or delta.get("guardrail_bundle_ids")):
            blockers.append(f"{label} lacks affected_guardrail_ids")
        citation_ids = _sequence(delta.get("source_evidence_ids") or delta.get("citation_ids") or delta.get("citation_spans"))
        if not citation_ids:
            blockers.append(f"{label} lacks citation evidence")
        stale_ids = [citation_id for citation_id in citation_ids if citation_id not in context.current_evidence_ids]
        if stale_ids:
            blockers.append(f"{label} cites stale or missing evidence ids: {', '.join(stale_ids)}")
        if _text(delta.get("refreshed_guardrail_status")).lower() == "ready" and review_status not in _REVIEW_COMPLETE_STATUSES:
            blockers.append(f"{label} marks guardrails ready before human review is complete")

    return _gate("requirement_delta_formalization", blockers)


def _process_model_gate(data: Mapping[str, Any], context: _ReadinessContext) -> dict[str, Any]:
    blockers: list[str] = []
    process_models = _list(data, "process_models")
    if not process_models:
        blockers.append("process model version records are missing")

    for index, model in enumerate(process_models):
        label = _label(model, index, "process_id")
        validation_status = _text(model.get("validation_status")).lower()
        if validation_status != "valid":
            blockers.append(f"{label} validation_status is {validation_status or 'missing'}")
        for required_key in ("process_id", "version", "guardrail_bundle_id"):
            if not model.get(required_key):
                blockers.append(f"{label} lacks {required_key}")
        evidence_ids = _sequence(model.get("source_evidence_ids") or model.get("citation_ids"))
        if not evidence_ids:
            blockers.append(f"{label} lacks refreshed source_evidence_ids")
        stale_ids = [evidence_id for evidence_id in evidence_ids if evidence_id not in context.current_evidence_ids]
        if stale_ids:
            blockers.append(f"{label} has stale or missing refreshed source_evidence_ids: {', '.join(stale_ids)}")

    return _gate("process_model_versions", blockers)


def _source_freshness_gate(data: Mapping[str, Any], context: _ReadinessContext) -> dict[str, Any]:
    blockers: list[str] = []
    sources = _list(data, "sources")
    if not sources:
        blockers.append("source freshness records are missing")

    for index, source in enumerate(sources):
        label = _label(source, index, "source_id")
        freshness_status = _text(source.get("freshness_status")).lower()
        if freshness_status not in _CURRENT_FRESHNESS_STATUSES:
            blockers.append(f"{label} freshness_status is {freshness_status or 'missing'}")
        if not source.get("last_seen_at"):
            blockers.append(f"{label} lacks last_seen_at")
        source_key = _text(source.get("source_id") or source.get("canonical_url"))
        expected_hash = _text(source.get("content_hash"))
        observed_hash = context.ingestion_source_hashes.get(source_key, "")
        if expected_hash and observed_hash and expected_hash != observed_hash:
            blockers.append(f"{label} content_hash does not match refreshed ingestion output")
        for url_key in ("canonical_url", "requested_url", "source_url"):
            url_blocker = _public_url_blocker(source.get(url_key), label, url_key)
            if url_blocker:
                blockers.append(url_blocker)

    return _gate("source_freshness", blockers)


def _human_review_gate(data: Mapping[str, Any], context: _ReadinessContext) -> dict[str, Any]:
    blockers: list[str] = []
    reviews = _list(data, "reviews")
    if not reviews:
        blockers.append("human review state records are missing")

    for index, review in enumerate(reviews):
        label = _label(review, index, "review_id")
        status = _text(review.get("status")).lower()
        if status not in _REVIEW_COMPLETE_STATUSES:
            blockers.append(f"{label} review status is {status or 'missing'}")
        for required_key in ("subject_id", "subject_type"):
            if not review.get(required_key):
                blockers.append(f"{label} lacks {required_key}")

    expected_subjects = {
        _text(delta.get("delta_id") or delta.get("id"))
        for delta in context.requirement_deltas
        if _text(delta.get("human_review_status") or delta.get("review_status")).lower() != "not_required"
    }
    missing_subjects = sorted(subject for subject in expected_subjects if subject and subject not in context.completed_review_subjects)
    if missing_subjects:
        blockers.append("human review state is incomplete for subjects: " + ", ".join(missing_subjects))

    return _gate("human_review_state", blockers)


def _guardrail_process_evidence_gate(context: _ReadinessContext) -> dict[str, Any]:
    blockers: list[str] = []
    ready_models = [model for model in context.process_models if _text(model.get("validation_status")).lower() == "valid"]

    for index, delta in enumerate(context.requirement_deltas):
        label = _label(delta, index, "delta_id")
        delta_process_ids = set(_sequence(delta.get("affected_process_ids") or delta.get("process_ids")))
        delta_guardrail_ids = set(_sequence(delta.get("affected_guardrail_ids") or delta.get("guardrail_ids") or delta.get("guardrail_bundle_ids")))
        delta_evidence_ids = set(_sequence(delta.get("source_evidence_ids") or delta.get("citation_ids") or delta.get("citation_spans")))
        for guardrail_id in sorted(delta_guardrail_ids):
            if not _has_refreshed_process_version_evidence(guardrail_id, delta_process_ids, delta_evidence_ids, ready_models):
                blockers.append(
                    f"{label} ready guardrail {guardrail_id} lacks refreshed process-version evidence"
                )

    return _gate("guardrail_process_version_evidence", blockers)


def _has_refreshed_process_version_evidence(
    guardrail_id: str,
    process_ids: set[str],
    evidence_ids: set[str],
    process_models: Iterable[Mapping[str, Any]],
) -> bool:
    for model in process_models:
        model_guardrails = set(_sequence(model.get("guardrail_bundle_id") or model.get("guardrail_bundle_ids") or model.get("affected_guardrail_ids")))
        if guardrail_id not in model_guardrails:
            continue
        model_process_id = _text(model.get("process_id"))
        if process_ids and model_process_id not in process_ids:
            continue
        model_evidence_ids = set(_sequence(model.get("source_evidence_ids") or model.get("citation_ids")))
        if evidence_ids and model_evidence_ids and not model_evidence_ids.intersection(evidence_ids):
            continue
        if model_evidence_ids:
            return True
    return False


def _gate(name: str, blockers: list[str]) -> dict[str, Any]:
    return {
        "gate": name,
        "status": "ready" if not blockers else "blocked",
        "ready": not blockers,
        "blockers": blockers,
    }


def _list(data: Mapping[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key, [])
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _label(item: Mapping[str, Any], index: int, preferred_key: str) -> str:
    return _text(item.get(preferred_key) or item.get("source_id") or item.get("requirement_id") or f"record[{index}]")


def _find_forbidden_body_keys(value: Any, prefix: str = "") -> set[str]:
    found: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            dotted = f"{prefix}.{key_text}" if prefix else key_text
            if key_text.lower() in _METADATA_ONLY_FORBIDDEN_KEYS:
                found.add(dotted)
            found.update(_find_forbidden_body_keys(child, dotted))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.update(_find_forbidden_body_keys(child, f"{prefix}[{index}]"))
    return found


def _public_url_blocker(value: object, label: str, url_key: str) -> str:
    url = _text(value)
    if not url:
        return ""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return f"{label} {url_key} must be an https public URL"
    if parsed.username or parsed.password:
        return f"{label} {url_key} must not include credentials"
    host = (parsed.hostname or "").lower()
    if host not in _PUBLIC_HOSTS:
        return f"{label} {url_key} is outside the PP&D public allowlist"
    lower_path = parsed.path.lower()
    lower_query = parsed.query.lower()
    if any(hint in lower_path for hint in _AUTHENTICATED_URL_HINTS):
        return f"{label} {url_key} appears to require authentication"
    query_keys = {part.split("=", 1)[0].lower() for part in lower_query.split("&") if part}
    if query_keys.intersection(_AUTHENTICATED_QUERY_HINTS):
        return f"{label} {url_key} appears to include private authentication parameters"
    return ""


def _current_evidence_ids(outputs: Iterable[Mapping[str, Any]]) -> set[str]:
    evidence_ids: set[str] = set()
    for output in outputs:
        for key in ("normalized_document_id", "document_id", "source_id"):
            value = _text(output.get(key))
            if value:
                evidence_ids.add(value)
    return evidence_ids


def _source_hashes(items: Iterable[Mapping[str, Any]]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for item in items:
        content_hash = _text(item.get("content_hash"))
        if not content_hash:
            continue
        for key in ("source_id", "canonical_url", "normalized_document_id", "document_id"):
            source_key = _text(item.get(key))
            if source_key:
                hashes[source_key] = content_hash
    return hashes


def _sequence(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        text = value.strip()
        return (text,) if text else ()
    if isinstance(value, Mapping):
        return ()
    if isinstance(value, Iterable):
        return tuple(text for item in value if (text := _text(item)))
    text = _text(value)
    return (text,) if text else ()


def _text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _string_values(values: Any) -> list[str]:
    return [str(value) for value in values if value]
