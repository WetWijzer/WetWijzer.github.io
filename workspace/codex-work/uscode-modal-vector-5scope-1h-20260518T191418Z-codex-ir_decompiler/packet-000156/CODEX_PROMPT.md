# packet-000156

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/packet-000156/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/packet-000156/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000156-20260518_200811

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/logic/modal/decompiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_ir.py`

## TODOs
- `program-392e57529c3b504a` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-392e57529c3b504a` score `1.0`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": -0.301024463613, "hint_id": "modal-synthesis-08d5534bfade39d4", "priority": 0.424340100329, "reconstruction_loss": 0.424340100329, "sample_id": "us-code-42-1962d-982c099c7b80957b", "top_embedding_features": ["flogic:citation_section_style_alnum_segment_kind_positioned:4:alpha", "flogic:source_id_section_style_alnum_segment_kind_positioned:4:alpha", "flogic:support_span_start_char_hundreds_block:0", "slot:citation_section_style_alnum_segment_kind_positioned:4_alpha", "slot:source_id_section_style_alnum_segment_kind_positioned:4_alpha", "slot:support_span_start_char_hundreds_block:0", "flogic:modal_operator:X", "flogic:modal_operator_label:next"]}`
  evidence: `{"cosine_similarity": -0.122951312362, "hint_id": "modal-synthesis-2999507d766f2f43", "priority": 0.45023400221, "reconstruction_loss": 0.45023400221, "sample_id": "us-code-26-7520-ad4e4c590b70c936", "top_embedding_features": ["flogic:citation_section_component_signature:N4", "flogic:citation_section_component_signature_positioned:1:N4", "flogic:citation_section_number_digit_count:4", "flogic:citation_section_number_digit_count_bucket:4_digit", "flogic:citation_section_number_digit_count_bucket_positioned:1:4_digit", "flogic:citation_section_number_digit_count_positioned:1:4", "flogic:citation_section_number_magnitude_bucket:1k_to_9k", "flogic:citation_section_number_magnitude_bucket_positioned:1:1k_to_9k"]}`
  evidence: `{"cosine_similarity": -0.505194641114, "hint_id": "modal-synthesis-701615c98edf88f3", "priority": 0.813175235894, "reconstruction_loss": 0.813175235894, "sample_id": "us-code-51-40504.-daa7d9a7e25305f4", "top_embedding_features": ["flogic:modal_span_coverage_percent_leading_digit:4", "lemma:establishment", "lemma:national", "slot:modal_span_coverage_percent_leading_digit:4", "cue:deontic:O:shall", "family:selected_frame:deontic", "flogic:modal_cue:shall", "flogic:modal_family:deontic"]}`
  evidence: `{"cosine_similarity": -0.513407387818, "hint_id": "modal-synthesis-b7d73023cfa9a5d2", "priority": 0.423608886264, "reconstruction_loss": 0.423608886264, "sample_id": "us-code-46-55101.-18bef3d2cb36f938", "top_embedding_features": ["family:frame:1", "flogic:modal_family_count:frame:1", "flogic:modal_family_count_frame:1", "flogic:modal_family_count_ranked:2:frame:1", "flogic:modal_span_char_count_trailing_two_digits:95", "flogic:predicate_alnum_segment_positioned:4:apply", "lemma:relating", "slot:modal_family_count:frame_1"]}`

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
- `program-392e57529c3b504a`
  action: `refine_typed_ir_or_decompiler_slots`
  role: `program_synthesis`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-392e57529c3b504a` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.527839556174`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  samples: `us-code-51-40504.-daa7d9a7e25305f4, us-code-26-7520-ad4e4c590b70c936, us-code-42-1962d-982c099c7b80957b, us-code-46-55101.-18bef3d2cb36f938`
  evidence: `{"cosine_similarity": -0.301024463613, "hint_id": "modal-synthesis-08d5534bfade39d4", "priority": 0.424340100329, "reconstruction_loss": 0.424340100329, "sample_id": "us-code-42-1962d-982c099c7b80957b", "top_embedding_features": ["flogic:citation_section_style_alnum_segment_kind_positioned:4:alpha", "flogic:source_id_section_style_alnum_segment_kind_positioned:4:alpha", "flogic:support_span_start_char_hundreds_block:0", "slot:citation_section_style_alnum_segment_kind_positioned:4_alpha", "slot:source_id_section_style_alnum_segment_kind_positioned:4_alpha", "slot:support_span_start_char_hundreds_block:0", "flogic:modal_operator:X", "flogic:modal_operator_label:next"]}`
  evidence: `{"cosine_similarity": -0.122951312362, "hint_id": "modal-synthesis-2999507d766f2f43", "priority": 0.45023400221, "reconstruction_loss": 0.45023400221, "sample_id": "us-code-26-7520-ad4e4c590b70c936", "top_embedding_features": ["flogic:citation_section_component_signature:N4", "flogic:citation_section_component_signature_positioned:1:N4", "flogic:citation_section_number_digit_count:4", "flogic:citation_section_number_digit_count_bucket:4_digit", "flogic:citation_section_number_digit_count_bucket_positioned:1:4_digit", "flogic:citation_section_number_digit_count_positioned:1:4", "flogic:citation_section_number_magnitude_bucket:1k_to_9k", "flogic:citation_section_number_magnitude_bucket_positioned:1:1k_to_9k"]}`
  evidence: `{"cosine_similarity": -0.505194641114, "hint_id": "modal-synthesis-701615c98edf88f3", "priority": 0.813175235894, "reconstruction_loss": 0.813175235894, "sample_id": "us-code-51-40504.-daa7d9a7e25305f4", "top_embedding_features": ["flogic:modal_span_coverage_percent_leading_digit:4", "lemma:establishment", "lemma:national", "slot:modal_span_coverage_percent_leading_digit:4", "cue:deontic:O:shall", "family:selected_frame:deontic", "flogic:modal_cue:shall", "flogic:modal_family:deontic"]}`
  evidence: `{"cosine_similarity": -0.513407387818, "hint_id": "modal-synthesis-b7d73023cfa9a5d2", "priority": 0.423608886264, "reconstruction_loss": 0.423608886264, "sample_id": "us-code-46-55101.-18bef3d2cb36f938", "top_embedding_features": ["family:frame:1", "flogic:modal_family_count:frame:1", "flogic:modal_family_count_frame:1", "flogic:modal_family_count_ranked:2:frame:1", "flogic:modal_span_char_count_trailing_two_digits:95", "flogic:predicate_alnum_segment_positioned:4:apply", "lemma:relating", "slot:modal_family_count:frame_1"]}`
