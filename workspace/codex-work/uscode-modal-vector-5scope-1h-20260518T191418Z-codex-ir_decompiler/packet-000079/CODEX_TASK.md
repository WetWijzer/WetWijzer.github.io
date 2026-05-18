# packet-000079

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/packet-000079/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/packet-000079/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000079-20260518_193756

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/logic/modal/decompiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_ir.py`

## TODOs
- `program-854101de191057d0` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-854101de191057d0` score `1.0`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": -0.698783049386, "hint_id": "modal-synthesis-6f89b54f6f6e6ca6", "priority": 0.644212582322, "reconstruction_loss": 0.644212582322, "sample_id": "us-code-43-270-9753303f57791aad", "top_embedding_features": ["cue:temporal:X:after", "family:selected_frame:conditional_normative", "flogic:citation_section_number_has_zero_digit:true", "flogic:citation_section_number_has_zero_digit_positioned:1:true", "flogic:citation_section_number_zero_digit_count:1", "flogic:citation_section_number_zero_digit_count_positioned:1:1", "flogic:citation_section_primary_number_has_zero_digit:true", "flogic:citation_section_primary_number_zero_digit_count:1"]}`
  evidence: `{"cosine_similarity": 0.158722281683, "hint_id": "modal-synthesis-bcce3ca1e1208bbc", "priority": 0.192196230632, "reconstruction_loss": 0.192196230632, "sample_id": "us-code-31-5312-039372e5e9300b7d", "top_embedding_features": ["cue:conditional_normative:O|:if", "cue:deontic:O:shall", "cue:temporal:X:after", "family:selected_frame:conditional_normative", "family:selected_frame:deontic", "flogic:citation_title_number_has_zero_digit:false", "flogic:citation_title_number_trailing_zero_count:0", "flogic:citation_title_number_zero_digit_count:0"]}`
  evidence: `{"cosine_similarity": 0.054394529742, "hint_id": "modal-synthesis-dfc14997de6571da", "priority": 0.439265081335, "reconstruction_loss": 0.439265081335, "sample_id": "us-code-7-1631-2e645b217b50b0bc", "top_embedding_features": ["family:selected_frame:temporal", "flogic:candidate_ontology_frame:administrative_notice_hearing", "flogic:candidate_ontology_frame:criminal_penalty_enforcement", "flogic:candidate_ontology_frame:housing_voucher_benefits", "flogic:candidate_ontology_term:accommodation", "flogic:candidate_ontology_term:administrative", "flogic:candidate_ontology_term:administrative_notice_hearing", "flogic:candidate_ontology_term:agency"]}`
  evidence: `{"cosine_similarity": -0.306155516144, "hint_id": "modal-synthesis-f687106fc30206f9", "priority": 0.678445187698, "reconstruction_loss": 0.678445187698, "sample_id": "us-code-15-145-7b620ef453a3c3c7", "top_embedding_features": ["family:selected_frame:temporal", "flogic:candidate_ontology_frame:administrative_notice_hearing", "flogic:candidate_ontology_frame:criminal_penalty_enforcement", "flogic:candidate_ontology_frame:housing_voucher_benefits", "flogic:candidate_ontology_term:accommodation", "flogic:candidate_ontology_term:administrative", "flogic:candidate_ontology_term:administrative_notice_hearing", "flogic:candidate_ontology_term:agency"]}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
