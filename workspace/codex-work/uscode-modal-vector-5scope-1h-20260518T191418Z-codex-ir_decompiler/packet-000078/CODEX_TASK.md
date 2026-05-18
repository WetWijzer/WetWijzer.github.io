# packet-000078

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/packet-000078/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/packet-000078/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000078-20260518_193051

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/logic/modal/decompiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_ir.py`

## TODOs
- `program-9ad344cc72378e36` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-9ad344cc72378e36` score `1.0`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": 0.224478400376, "hint_id": "modal-synthesis-16ba631163226162", "priority": 0.327564072981, "reconstruction_loss": 0.327564072981, "sample_id": "us-code-10-864-47dfb7b7e13861a9", "top_embedding_features": ["cue:conditional_normative:O|:if", "cue:deontic:O:shall", "cue:temporal:X:after", "family:selected_frame:conditional_normative", "family:selected_frame:deontic", "flogic:condition_alnum_segment:if", "flogic:condition_alnum_segment:of", "flogic:condition_alnum_segment:the"]}`
  evidence: `{"cosine_similarity": -0.086497112648, "hint_id": "modal-synthesis-4836c37dd17ebd2f", "priority": 0.225804795961, "reconstruction_loss": 0.225804795961, "sample_id": "us-code-7-61a-5c0aef0f5a34145e", "top_embedding_features": ["family:selected_frame:temporal", "family:temporal:1", "flogic:candidate_ontology_frame:administrative_notice_hearing", "flogic:candidate_ontology_frame:criminal_penalty_enforcement", "flogic:candidate_ontology_frame:housing_voucher_benefits", "flogic:candidate_ontology_term:accommodation", "flogic:candidate_ontology_term:administrative", "flogic:candidate_ontology_term:administrative_notice_hearing"]}`
  evidence: `{"cosine_similarity": -0.406170170228, "hint_id": "modal-synthesis-4ed3ec3b0788b419", "priority": 0.384031539684, "reconstruction_loss": 0.384031539684, "sample_id": "us-code-16-460aaa-4-1abeafecdd6d6499", "top_embedding_features": ["cue:temporal:F:by", "flogic:citation_section_has_trailing_punct:false", "flogic:citation_section_number_has_zero_digit:false", "flogic:citation_section_number_parity:even", "flogic:citation_section_number_parity_positioned:1:even", "flogic:citation_section_number_zero_digit_count:0", "flogic:citation_section_primary_number_parity:even", "flogic:citation_section_punctuation_style:clean"]}`
  evidence: `{"cosine_similarity": -0.496212965635, "hint_id": "modal-synthesis-bd1ef5098b80e191", "priority": 0.677111206587, "reconstruction_loss": 0.677111206587, "sample_id": "us-code-16-282-4a605941ea71845d", "top_embedding_features": ["cue:temporal:F:by", "flogic:citation_section_has_trailing_punct:false", "flogic:citation_section_number_has_zero_digit:false", "flogic:citation_section_number_has_zero_digit_positioned:1:false", "flogic:citation_section_number_leading_digit:2", "flogic:citation_section_number_leading_digit_positioned:1:2", "flogic:citation_section_number_parity:even", "flogic:citation_section_number_parity_positioned:1:even"]}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
