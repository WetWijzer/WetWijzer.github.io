# packet-000078

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/packet-000078/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/packet-000078/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000078-20260518_193116

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/optimizers/logic/flogic_optimizer.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/frame_bm25_selector.py`

## TODOs
- `program-d4a8673ceb7b32c1` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-d4a8673ceb7b32c1` score `1.0`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["family:selected_frame:temporal", "flogic:candidate_ontology_frame:administrative_notice_hearing", "flogic:candidate_ontology_frame:criminal_penalty_enforcement", "flogic:candidate_ontology_frame:housing_voucher_benefits", "flogic:candidate_ontology_term:accommodation", "flogic:candidate_ontology_term:administrative", "flogic:candidate_ontology_term:administrative_notice_hearing"], "hint_id": "modal-synthesis-1d734f8b2b7f9071", "priority": 0.225804795961, "sample_id": "us-code-7-61a-5c0aef0f5a34145e"}`
  evidence: `{"frame_features": ["flogic:citation_section_has_trailing_punct:false", "flogic:citation_section_number_has_zero_digit:false", "flogic:citation_section_number_has_zero_digit_positioned:1:false", "flogic:citation_section_number_leading_digit:2", "flogic:citation_section_number_leading_digit_positioned:1:2", "flogic:citation_section_number_parity:even", "flogic:citation_section_number_parity_positioned:1:even"], "hint_id": "modal-synthesis-8d31030534247082", "priority": 0.677111206587, "sample_id": "us-code-16-282-4a605941ea71845d"}`
  evidence: `{"frame_features": ["family:selected_frame:conditional_normative", "family:selected_frame:deontic", "flogic:condition_alnum_segment:if", "flogic:condition_alnum_segment:of", "flogic:condition_alnum_segment:the"], "hint_id": "modal-synthesis-a96f2366a07ccb07", "priority": 0.327564072981, "sample_id": "us-code-10-864-47dfb7b7e13861a9"}`
  evidence: `{"frame_features": ["flogic:citation_section_has_trailing_punct:false", "flogic:citation_section_number_has_zero_digit:false", "flogic:citation_section_number_parity:even", "flogic:citation_section_number_parity_positioned:1:even", "flogic:citation_section_number_zero_digit_count:0", "flogic:citation_section_primary_number_parity:even", "flogic:citation_section_punctuation_style:clean"], "hint_id": "modal-synthesis-dff628efe9ba343e", "priority": 0.384031539684, "sample_id": "us-code-16-460aaa-4-1abeafecdd6d6499"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.


## Execution Instructions
Work only inside the packet worktree.
Your worktree edits may be applied back to the source checkout and validated automatically when this packet finishes.
Do not create changes.patch or other patch artifact files; leave source and test edits directly in the worktree.
Treat the packet's program_synthesis_scope metadata as the AST/write-scope boundary; keep edits inside that lane unless a test requires a small adjacent change.
When multiple TODOs are present, treat their semantic_bundle_key or vector_bundle metadata as evidence for one generalized compiler/decompiler/frame improvement over one-off sample fixes.
Implement a narrow deterministic parser, IR, decoder, or frame-logic improvement for the claimed TODOs.
Prefer explainable compiler/decompiler code over learned weights when the TODO concerns modal or frame semantics.
Use local repository files and tests only; do not use web search for this packet.
Run the smallest relevant tests you can before finishing.
Leave unrelated files alone.

## Claimed Autoencoder TODO List
# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-d4a8673ceb7b32c1`
  action: `audit_frame_logic_terms`
  role: `program_synthesis`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-d4a8673ceb7b32c1` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.403627903803`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  samples: `us-code-16-282-4a605941ea71845d, us-code-16-460aaa-4-1abeafecdd6d6499, us-code-10-864-47dfb7b7e13861a9, us-code-7-61a-5c0aef0f5a34145e`
  evidence: `{"frame_features": ["family:selected_frame:temporal", "flogic:candidate_ontology_frame:administrative_notice_hearing", "flogic:candidate_ontology_frame:criminal_penalty_enforcement", "flogic:candidate_ontology_frame:housing_voucher_benefits", "flogic:candidate_ontology_term:accommodation", "flogic:candidate_ontology_term:administrative", "flogic:candidate_ontology_term:administrative_notice_hearing"], "hint_id": "modal-synthesis-1d734f8b2b7f9071", "priority": 0.225804795961, "sample_id": "us-code-7-61a-5c0aef0f5a34145e"}`
  evidence: `{"frame_features": ["flogic:citation_section_has_trailing_punct:false", "flogic:citation_section_number_has_zero_digit:false", "flogic:citation_section_number_has_zero_digit_positioned:1:false", "flogic:citation_section_number_leading_digit:2", "flogic:citation_section_number_leading_digit_positioned:1:2", "flogic:citation_section_number_parity:even", "flogic:citation_section_number_parity_positioned:1:even"], "hint_id": "modal-synthesis-8d31030534247082", "priority": 0.677111206587, "sample_id": "us-code-16-282-4a605941ea71845d"}`
  evidence: `{"frame_features": ["family:selected_frame:conditional_normative", "family:selected_frame:deontic", "flogic:condition_alnum_segment:if", "flogic:condition_alnum_segment:of", "flogic:condition_alnum_segment:the"], "hint_id": "modal-synthesis-a96f2366a07ccb07", "priority": 0.327564072981, "sample_id": "us-code-10-864-47dfb7b7e13861a9"}`
  evidence: `{"frame_features": ["flogic:citation_section_has_trailing_punct:false", "flogic:citation_section_number_has_zero_digit:false", "flogic:citation_section_number_parity:even", "flogic:citation_section_number_parity_positioned:1:even", "flogic:citation_section_number_zero_digit_count:0", "flogic:citation_section_primary_number_parity:even", "flogic:citation_section_punctuation_style:clean"], "hint_id": "modal-synthesis-dff628efe9ba343e", "priority": 0.384031539684, "sample_id": "us-code-16-460aaa-4-1abeafecdd6d6499"}`
