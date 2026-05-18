# packet-000140

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/packet-000140/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/packet-000140/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000140-20260518_195913

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/optimizers/logic/flogic_optimizer.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/frame_bm25_selector.py`

## TODOs
- `program-3650c724ac8ade75` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-3650c724ac8ade75` score `1.0`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["flogic:citation_section_has_trailing_punct:false", "flogic:citation_section_number_has_zero_digit:false", "flogic:citation_section_number_has_zero_digit_positioned:1:false", "flogic:citation_section_number_zero_digit_count:0", "flogic:citation_section_number_zero_digit_count_positioned:1:0", "flogic:citation_section_primary_number_has_zero_digit:false", "flogic:citation_section_primary_number_zero_digit_count:0"], "hint_id": "modal-synthesis-d1da368c34758e26", "priority": 0.649413377199, "sample_id": "us-code-38-8163-dc4c9191b09f4a3d"}`
  evidence: `{"frame_features": ["family:selected_frame:epistemic", "flogic:condition_alnum_segment:a", "flogic:condition_alnum_segment:such", "flogic:condition_alnum_segment_count:6", "flogic:condition_scope_alnum_segment:a", "flogic:condition_scope_alnum_segment:such"], "hint_id": "modal-synthesis-d24b1deb5bac4a92", "priority": 0.429088394263, "sample_id": "us-code-42-1395c.-da5383050c7a2c5e"}`
  evidence: `{"frame_features": ["flogic:citation_section_number_parity:odd", "flogic:citation_section_number_parity_positioned:1:odd", "flogic:citation_section_primary_number_parity:odd", "flogic:citation_section_terminal_number_parity:odd", "flogic:source_id_section_number_parity:odd", "flogic:source_id_section_number_parity_positioned:1:odd", "flogic:source_id_section_primary_number_parity:odd"], "hint_id": "modal-synthesis-df5c4a2ad5c51086", "priority": 0.44941495653, "sample_id": "us-code-10-649j-49b85ae09715be03"}`
  evidence: `{"frame_features": ["flogic:citation_section_component_signature:N4", "flogic:citation_section_component_signature_positioned:1:N4", "flogic:citation_section_number_digit_count:4", "flogic:citation_section_number_digit_count_bucket:4_digit", "flogic:citation_section_number_digit_count_bucket_positioned:1:4_digit", "flogic:citation_section_number_digit_count_positioned:1:4", "flogic:citation_section_number_magnitude_bucket:1k_to_9k", "flogic:citation_section_number_magnitude_bucket_positioned:1:1k_to_9k"], "hint_id": "modal-synthesis-fada2a1ed1eee936", "priority": 0.687431488212, "sample_id": "us-code-26-3305-53aaebf91aa3d889"}`

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
- `program-3650c724ac8ade75`
  action: `audit_frame_logic_terms`
  role: `program_synthesis`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-3650c724ac8ade75` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.553837054051`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  samples: `us-code-26-3305-53aaebf91aa3d889, us-code-38-8163-dc4c9191b09f4a3d, us-code-10-649j-49b85ae09715be03, us-code-42-1395c.-da5383050c7a2c5e`
  evidence: `{"frame_features": ["flogic:citation_section_has_trailing_punct:false", "flogic:citation_section_number_has_zero_digit:false", "flogic:citation_section_number_has_zero_digit_positioned:1:false", "flogic:citation_section_number_zero_digit_count:0", "flogic:citation_section_number_zero_digit_count_positioned:1:0", "flogic:citation_section_primary_number_has_zero_digit:false", "flogic:citation_section_primary_number_zero_digit_count:0"], "hint_id": "modal-synthesis-d1da368c34758e26", "priority": 0.649413377199, "sample_id": "us-code-38-8163-dc4c9191b09f4a3d"}`
  evidence: `{"frame_features": ["family:selected_frame:epistemic", "flogic:condition_alnum_segment:a", "flogic:condition_alnum_segment:such", "flogic:condition_alnum_segment_count:6", "flogic:condition_scope_alnum_segment:a", "flogic:condition_scope_alnum_segment:such"], "hint_id": "modal-synthesis-d24b1deb5bac4a92", "priority": 0.429088394263, "sample_id": "us-code-42-1395c.-da5383050c7a2c5e"}`
  evidence: `{"frame_features": ["flogic:citation_section_number_parity:odd", "flogic:citation_section_number_parity_positioned:1:odd", "flogic:citation_section_primary_number_parity:odd", "flogic:citation_section_terminal_number_parity:odd", "flogic:source_id_section_number_parity:odd", "flogic:source_id_section_number_parity_positioned:1:odd", "flogic:source_id_section_primary_number_parity:odd"], "hint_id": "modal-synthesis-df5c4a2ad5c51086", "priority": 0.44941495653, "sample_id": "us-code-10-649j-49b85ae09715be03"}`
  evidence: `{"frame_features": ["flogic:citation_section_component_signature:N4", "flogic:citation_section_component_signature_positioned:1:N4", "flogic:citation_section_number_digit_count:4", "flogic:citation_section_number_digit_count_bucket:4_digit", "flogic:citation_section_number_digit_count_bucket_positioned:1:4_digit", "flogic:citation_section_number_digit_count_positioned:1:4", "flogic:citation_section_number_magnitude_bucket:1k_to_9k", "flogic:citation_section_number_magnitude_bucket_positioned:1:1k_to_9k"], "hint_id": "modal-synthesis-fada2a1ed1eee936", "priority": 0.687431488212, "sample_id": "us-code-26-3305-53aaebf91aa3d889"}`
