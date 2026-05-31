"""Fixture-first reversible PDF draft preview packet v2.

This module intentionally plans local preview-only PDF field values from synthetic
facts. It does not open PDFs, download forms, write generated PDFs, upload files,
submit applications, certify statements, or touch active PDF utilities.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping

Packet = Dict[str, Any]

PACKET_VERSION = "ppd_pdf_draft_preview_packet_v2"

OFFLINE_VALIDATION_COMMANDS: List[List[str]] = [
    ["python3", "-m", "py_compile", "ppd/pdf/draft_preview_packet_v2.py"],
    ["python3", "-m", "py_compile", "ppd/tests/test_pdf_draft_preview_packet_v2.py"],
    ["python3", "-m", "unittest", "ppd.tests.test_pdf_draft_preview_packet_v2"],
    ["python3", "ppd/daemon/ppd_daemon.py", "--self-test"],
]

CITATION_REFERENCES: List[Dict[str, str]] = [
    {
        "citation_id": "ppd_apply_permits_public_guide",
        "title": "Apply for permits",
        "url": "https://www.portland.gov/ppd/get-permit/apply-permits",
        "supports": "Permit application facts should be reviewed against official PP&D application guidance before use.",
    },
    {
        "citation_id": "ppd_submit_plans_single_pdf_guidance",
        "title": "Submit Plans Online / Single PDF Process",
        "url": "https://www.portland.gov/ppd/get-permit/submit-plans-online",
        "supports": "Plans, applications, calculations, and supporting documents have distinct upload and preparation expectations.",
    },
    {
        "citation_id": "ppd_file_naming_pdf_prep",
        "title": "File naming standards and PDF preparation",
        "url": "https://www.portland.gov/ppd/spp-file-naming-standards-preparing-pdfs",
        "supports": "Local preview packets must not be treated as final upload-ready files without file preparation review.",
    },
    {
        "citation_id": "ppd_devhub_application_guide",
        "title": "DevHub permit application guide",
        "url": "https://www.portland.gov/ppd/devhub-guide-submit-permit-application",
        "supports": "DevHub application data entry, acknowledgement, upload, and submission remain attended and confirmation-gated workflows.",
    },
]

FIELD_PLAN_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "fact_key": "site_address",
        "preview_pdf_field": "preview.site_address",
        "label": "Site address",
        "required": True,
        "citations": ["ppd_apply_permits_public_guide"],
    },
    {
        "fact_key": "permit_type",
        "preview_pdf_field": "preview.permit_type",
        "label": "Permit type",
        "required": True,
        "citations": ["ppd_apply_permits_public_guide", "ppd_devhub_application_guide"],
    },
    {
        "fact_key": "project_description",
        "preview_pdf_field": "preview.project_description",
        "label": "Project description",
        "required": True,
        "citations": ["ppd_apply_permits_public_guide"],
    },
    {
        "fact_key": "applicant_name",
        "preview_pdf_field": "preview.applicant_name",
        "label": "Applicant name",
        "required": True,
        "citations": ["ppd_devhub_application_guide"],
    },
    {
        "fact_key": "applicant_email",
        "preview_pdf_field": "preview.applicant_email",
        "label": "Applicant email",
        "required": True,
        "citations": ["ppd_devhub_application_guide"],
    },
    {
        "fact_key": "estimated_project_value_usd",
        "preview_pdf_field": "preview.estimated_project_value_usd",
        "label": "Estimated project value",
        "required": True,
        "citations": ["ppd_apply_permits_public_guide"],
    },
    {
        "fact_key": "work_involves_structural_changes",
        "preview_pdf_field": "preview.structural_work_indicator",
        "label": "Structural work indicator",
        "required": True,
        "citations": ["ppd_submit_plans_single_pdf_guidance"],
    },
    {
        "fact_key": "plan_set_prepared",
        "preview_pdf_field": "preview.plan_set_prepared_indicator",
        "label": "Plan set prepared indicator",
        "required": True,
        "citations": ["ppd_submit_plans_single_pdf_guidance", "ppd_file_naming_pdf_prep"],
    },
]

UNSUPPORTED_FIELD_NOTES: List[Dict[str, str]] = [
    {
        "field_or_action": "signature_or_certification_fields",
        "status": "unsupported_in_preview",
        "reason": "Certification and acknowledgement fields are consequential official actions and require attended user review and exact confirmation.",
    },
    {
        "field_or_action": "official_upload_attachment_controls",
        "status": "unsupported_in_preview",
        "reason": "Upload staging or attachment to an official record is outside this local preview packet.",
    },
    {
        "field_or_action": "payment_or_fee_submission_fields",
        "status": "unsupported_in_preview",
        "reason": "Payment detail entry and final payment execution are financial workflows and are refused by this packet.",
    },
    {
        "field_or_action": "private_file_paths_or_private_pdf_bytes",
        "status": "unsupported_in_preview",
        "reason": "The packet maps synthetic facts only and does not read, store, or reveal private local files.",
    },
]

REVIEW_CHECKPOINTS: List[Dict[str, str]] = [
    {
        "checkpoint_id": "review_synthetic_facts",
        "user_visible_prompt": "Review that the displayed facts are synthetic preview facts and not official filing values.",
        "required_before": "any draft-fill rehearsal beyond this packet",
    },
    {
        "checkpoint_id": "review_required_gaps",
        "user_visible_prompt": "Resolve every required fact gap before treating the field plan as ready for a local draft-fill rehearsal.",
        "required_before": "local preview PDF fill planning",
    },
    {
        "checkpoint_id": "review_unsupported_fields",
        "user_visible_prompt": "Confirm unsupported fields are not filled, signed, uploaded, submitted, certified, or paid through automation.",
        "required_before": "attended DevHub or official form workflow",
    },
    {
        "checkpoint_id": "review_citations",
        "user_visible_prompt": "Check the cited PP&D public guidance before relying on the preview plan for a real case.",
        "required_before": "case-specific use",
    },
]

NO_PRIVATE_FILE_ASSURANCES: List[str] = [
    "Uses caller-provided synthetic facts and committed test fixtures only.",
    "Does not open, inspect, parse, or download any private PDF or official form.",
    "Does not create or persist generated PDF files.",
    "Does not upload files, submit permit applications, certify acknowledgements, schedule inspections, or pay fees.",
    "Does not include private local file paths, credentials, cookies, browser state, screenshots, traces, HAR files, or payment details.",
]

REFUSED_ACTIONS: List[str] = [
    "read_private_pdf",
    "download_official_form",
    "persist_generated_pdf",
    "upload_file",
    "submit_application",
    "certify_acknowledgement",
    "enter_payment_details",
    "execute_payment",
    "mutate_active_pdf_utilities",
    "mutate_prompts_guardrails_process_models_or_release_state",
]


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, (list, tuple, dict, set)) and not value:
        return True
    return False


def _preview_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return deepcopy(value)


def _known_fact_keys(facts: Mapping[str, Any]) -> Iterable[str]:
    for key, value in facts.items():
        if not _is_missing(value):
            yield key


def build_pdf_draft_preview_packet_v2(facts: Mapping[str, Any]) -> Packet:
    """Build a deterministic preview packet from synthetic permit facts.

    The returned packet is an instruction artifact only. It is deliberately free of
    PDF bytes and file paths so downstream code cannot confuse it with a filled or
    upload-ready permit document.
    """

    case_id = str(facts.get("case_id") or "synthetic-preview-case")
    permit_context = {
        "case_id": case_id,
        "fixture_id": facts.get("fixture_id", "synthetic_pdf_draft_preview_packet_v2"),
        "permit_type": facts.get("permit_type"),
        "jurisdiction": "Portland Permitting & Development",
        "mode": "fixture_first_reversible_preview_only",
    }

    field_plan: List[Dict[str, Any]] = []
    required_fact_gaps: List[Dict[str, Any]] = []

    for definition in FIELD_PLAN_DEFINITIONS:
        fact_key = definition["fact_key"]
        value = facts.get(fact_key)
        if _is_missing(value):
            if definition["required"]:
                required_fact_gaps.append(
                    {
                        "fact_key": fact_key,
                        "label": definition["label"],
                        "reason": "Required for local preview field planning but absent from synthetic facts.",
                        "blocking_scope": "local_preview_field_plan_readiness",
                        "citation_ids": list(definition["citations"]),
                    }
                )
            continue

        field_plan.append(
            {
                "fact_key": fact_key,
                "preview_pdf_field": definition["preview_pdf_field"],
                "label": definition["label"],
                "value_preview": _preview_value(value),
                "source": "synthetic_fixture_fact",
                "reversible": True,
                "allowed_action": "plan_local_preview_value_only",
                "disallowed_actions": ["write_pdf", "upload", "submit", "certify"],
                "citation_ids": list(definition["citations"]),
            }
        )

    return {
        "packet_version": PACKET_VERSION,
        "permit_context": permit_context,
        "known_synthetic_fact_keys": sorted(_known_fact_keys(facts)),
        "local_preview_pdf_field_plan": field_plan,
        "required_fact_gaps": required_fact_gaps,
        "unsupported_field_notes": deepcopy(UNSUPPORTED_FIELD_NOTES),
        "citation_references": deepcopy(CITATION_REFERENCES),
        "user_visible_review_checkpoints": deepcopy(REVIEW_CHECKPOINTS),
        "no_private_file_assurances": list(NO_PRIVATE_FILE_ASSURANCES),
        "refused_actions": list(REFUSED_ACTIONS),
        "offline_validation_commands": deepcopy(OFFLINE_VALIDATION_COMMANDS),
        "readiness": {
            "ready_for_local_preview_fill_rehearsal": not required_fact_gaps,
            "ready_for_official_upload_or_submission": False,
            "requires_user_attended_confirmation_before_official_action": True,
        },
    }


def packet_summary(packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a compact deterministic summary useful for acceptance checks."""

    return {
        "packet_version": packet.get("packet_version"),
        "planned_field_count": len(packet.get("local_preview_pdf_field_plan", [])),
        "required_gap_count": len(packet.get("required_fact_gaps", [])),
        "unsupported_note_count": len(packet.get("unsupported_field_notes", [])),
        "review_checkpoint_count": len(packet.get("user_visible_review_checkpoints", [])),
        "ready_for_local_preview_fill_rehearsal": packet.get("readiness", {}).get(
            "ready_for_local_preview_fill_rehearsal"
        ),
        "ready_for_official_upload_or_submission": packet.get("readiness", {}).get(
            "ready_for_official_upload_or_submission"
        ),
    }
