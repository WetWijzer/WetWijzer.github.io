from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REQUIRED_WORKFLOWS = {
    "synthetic_building",
    "synthetic_trade",
    "synthetic_solar",
    "synthetic_demolition",
    "synthetic_sign",
    "synthetic_urban_forestry",
    "synthetic_corrections",
}

PROHIBITED_COMMAND_TOKENS = {
    "curl",
    "wget",
    "playwright",
    "devhub",
    "upload",
    "submit",
    "download",
}

EXPECTED_OFFLINE_COMMANDS = [
    ["python3", "-m", "ppd.document_requirement_matrix_packet_v2", "--fixture", "ppd/tests/fixtures/document_requirement_matrix_v2/packet.json"],
    ["python3", "-m", "pytest", "ppd/tests/test_document_requirement_matrix_packet_v2.py"],
]

ACTIVE_MUTATION_FLAG_KEYS = {
    "mutates_active_requirements",
    "mutates_active_requirement_nodes",
    "mutates_active_process_models",
    "mutates_active_guardrails",
    "mutates_active_guardrail_bundles",
    "mutates_active_prompts",
    "mutates_active_contracts",
    "mutates_active_sources",
    "mutates_active_source_registry",
    "mutates_active_devhub_surfaces",
    "mutates_active_release_state",
}

PRIVATE_PATH_RE = re.compile(r"(^|[\\s'\"])(/home/|/Users/|/private/|/var/folders/|file://|[A-Za-z]:\\\\)")
RAW_OR_DOWNLOADED_PDF_RE = re.compile(r"\\b(raw|downloaded)[ _-]?(pdf|document|file)s?\\b")
UPLOAD_STAGING_RE = re.compile(r"\\b(upload staging completed|uploads? staged|staged uploads?|official upload staged)\\b")
LIVE_DEVHUB_RE = re.compile(r"\\b(live devhub|opened devhub|authenticated devhub session|devhub browser session)\\b")
GUARANTEE_RE = re.compile(r"\\b(guarantee(?:d|s)?|will be approved|approval assured|permit approval assured|legal advice|legally compliant)\\b")


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _walk(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], Any]]:
    rows: list[tuple[tuple[str, ...], Any]] = [(path, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            rows.extend(_walk(child, (*path, str(key))))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(_walk(child, (*path, str(index))))
    return rows


def _path_label(path: tuple[str, ...]) -> str:
    return ".".join(path) if path else ""


def _is_boundary_list_path(path: tuple[str, ...]) -> bool:
    return bool(path) and path[0] == "prohibited_actions"


def _is_truthy_claim(value: Any) -> bool:
    return value is True or (isinstance(value, str) and bool(value.strip())) or (isinstance(value, list) and bool(value)) or (isinstance(value, dict) and bool(value))


def _validate_no_unsafe_artifact_claims(packet: dict[str, Any], errors: list[str]) -> None:
    for path, value in _walk(packet):
        key = path[-1] if path else ""
        key_lower = key.lower()
        path_text = _path_label(path)

        if key_lower in ACTIVE_MUTATION_FLAG_KEYS and _is_truthy_claim(value):
            errors.append(f"{path_text} must not set an active mutation flag")

        if _is_boundary_list_path(path):
            continue

        if isinstance(value, str):
            value_lower = value.lower()
            if PRIVATE_PATH_RE.search(value):
                errors.append(f"{path_text} contains a private or local document path")
            if RAW_OR_DOWNLOADED_PDF_RE.search(value_lower):
                errors.append(f"{path_text} claims raw or downloaded PDF retention")
            if UPLOAD_STAGING_RE.search(value_lower):
                errors.append(f"{path_text} claims upload staging")
            if LIVE_DEVHUB_RE.search(value_lower):
                errors.append(f"{path_text} claims live DevHub access")
            if GUARANTEE_RE.search(value_lower):
                errors.append(f"{path_text} contains a legal or permitting guarantee")

        if key_lower in {"private_document_path", "local_document_path", "document_path", "raw_pdf_path", "downloaded_pdf_path"} and _is_truthy_claim(value):
            errors.append(f"{path_text} must not contain private/local/raw PDF paths")
        if key_lower in {"raw_pdf", "raw_pdfs", "downloaded_pdf", "downloaded_pdfs", "raw_pdf_artifact", "downloaded_pdf_artifact"} and _is_truthy_claim(value):
            errors.append(f"{path_text} must not retain raw or downloaded PDFs")
        if key_lower in {"upload_staging_claim", "uploads_staged", "staged_uploads", "official_upload_staged"} and _is_truthy_claim(value):
            errors.append(f"{path_text} must not claim upload staging")
        if key_lower in {"live_devhub_claim", "opened_devhub", "devhub_session_live", "authenticated_devhub_session"} and _is_truthy_claim(value):
            errors.append(f"{path_text} must not claim live DevHub access")
        if key_lower in {"legal_guarantee", "permitting_guarantee", "approval_guarantee"} and _is_truthy_claim(value):
            errors.append(f"{path_text} must not contain legal or permitting guarantees")


def validate_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    _require(packet.get("packet_id") == "document_requirement_matrix_packet_v2", "packet_id must be document_requirement_matrix_packet_v2", errors)
    _require(packet.get("fixture_first") is True, "fixture_first must be true", errors)
    _require(packet.get("synthetic_only") is True, "synthetic_only must be true", errors)
    _require(packet.get("does_not_mutate_active_requirements") is True, "packet must not mutate active requirements", errors)

    prohibited_actions = _as_list(packet.get("prohibited_actions"))
    for expected in ["read_private_files", "download_pdfs", "stage_uploads", "open_devhub", "mutate_active_requirements"]:
        _require(expected in prohibited_actions, f"missing prohibited action: {expected}", errors)

    workflows = _as_list(packet.get("workflows"))
    workflow_ids = {row.get("workflow_id") for row in workflows if isinstance(row, dict)}
    _require(workflow_ids == REQUIRED_WORKFLOWS, f"workflow coverage mismatch: {sorted(workflow_ids)}", errors)

    source_ids = set()
    for source in _as_list(packet.get("source_evidence_placeholders")):
        if not isinstance(source, dict):
            errors.append("source evidence placeholder must be an object")
            continue
        source_id = source.get("source_evidence_id")
        if isinstance(source_id, str):
            source_ids.add(source_id)
        _require(source.get("placeholder_kind") == "official_public_source_pending_capture", f"{source_id} must remain a public source placeholder", errors)
        _require(source.get("private_or_authenticated") is False, f"{source_id} must not be private/authenticated", errors)
        _require(source.get("citation_status") == "placeholder_not_promoted", f"{source_id} must not be promoted as cited evidence", errors)

    for row in workflows:
        if not isinstance(row, dict):
            errors.append("workflow row must be an object")
            continue
        workflow_id = row.get("workflow_id", "")
        labels = _as_list(row.get("required_document_labels"))
        _require(len(labels) >= 2, f"{workflow_id} must list at least two required document labels", errors)
        for label in labels:
            _require(isinstance(label, str) and label.strip(), f"{workflow_id} contains an empty document label", errors)
        _require(isinstance(row.get("upload_grouping_expectation"), str) and row.get("upload_grouping_expectation"), f"{workflow_id} missing upload grouping expectation", errors)
        _require(isinstance(row.get("single_pdf_reference"), str) and "Single PDF" in row.get("single_pdf_reference", ""), f"{workflow_id} missing Single PDF reference", errors)
        _require(isinstance(row.get("file_naming_reference"), str) and "file naming" in row.get("file_naming_reference", "").lower(), f"{workflow_id} missing file naming reference", errors)
        evidence = _as_list(row.get("source_evidence_placeholders"))
        _require(bool(evidence), f"{workflow_id} missing source evidence placeholders", errors)
        for source_id in evidence:
            _require(source_id in source_ids, f"{workflow_id} references unknown source placeholder {source_id}", errors)
        _require(row.get("status") == "fixture_only_reviewer_hold", f"{workflow_id} must remain on reviewer hold", errors)

    hold_rows = _as_list(packet.get("reviewer_hold_rows"))
    hold_ids = {row.get("workflow_id") for row in hold_rows if isinstance(row, dict)}
    _require(hold_ids == REQUIRED_WORKFLOWS, "reviewer hold rows must cover every workflow", errors)
    for row in hold_rows:
        if not isinstance(row, dict):
            errors.append("reviewer hold row must be an object")
            continue
        workflow_id = row.get("workflow_id", "")
        _require(row.get("hold_reason") == "awaiting_official_source_capture_and_human_review", f"{workflow_id} has an unexpected hold reason", errors)
        _require(row.get("may_promote_to_active") is False, f"{workflow_id} must not be promotable", errors)

    commands = _as_list(packet.get("offline_validation_commands"))
    _require(commands == EXPECTED_OFFLINE_COMMANDS, "offline validation commands do not match the exact expected commands", errors)
    for command in commands:
        flattened = " ".join(str(part).lower() for part in _as_list(command))
        for token in PROHIBITED_COMMAND_TOKENS:
            _require(token not in flattened, f"offline command contains prohibited token: {token}", errors)

    _validate_no_unsafe_artifact_claims(packet, errors)
    return errors


def load_packet(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("packet fixture must contain a JSON object")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the PP&D document requirement matrix packet v2 fixture.")
    parser.add_argument("--fixture", type=Path, required=True)
    args = parser.parse_args()

    packet = load_packet(args.fixture)
    errors = validate_packet(packet)
    if errors:
        for error in errors:
            print(error)
        return 1
    print("document_requirement_matrix_packet_v2 fixture is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
