"""Source-backed contract for processor-suite PP&D handoff."""

from __future__ import annotations


def processor_suite_contract() -> dict[str, object]:
    return {
        "capability": "processor_suite_handoff",
        "processorSuite": "ipfs_datasets_py.processors",
        "requiredInputs": [
            "public_source_url",
            "robots_decision",
            "content_type",
            "canonical_document_id",
        ],
        "requiredOutputs": [
            "processor_handoff_manifest",
            "pdf_metadata_record",
            "normalized_public_document",
            "formal_logic_source_evidence_id",
        ],
        "rawBodyPersistenceAllowed": False,
    }
