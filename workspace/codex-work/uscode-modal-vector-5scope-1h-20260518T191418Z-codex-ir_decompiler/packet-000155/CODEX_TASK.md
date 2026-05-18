# packet-000155

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/packet-000155/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/packet-000155/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000155-20260518_195913

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/logic/modal/decompiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_ir.py`

## TODOs
- `program-868f63b59d1a51e8` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-868f63b59d1a51e8` score `1.0`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": -0.554204796198, "hint_id": "modal-synthesis-81958e03d12c0a12", "priority": 0.687431488212, "reconstruction_loss": 0.687431488212, "sample_id": "us-code-26-3305-53aaebf91aa3d889", "top_embedding_features": ["flogic:citation_section_component_signature:N4", "flogic:citation_section_component_signature_positioned:1:N4", "flogic:citation_section_number_digit_count:4", "flogic:citation_section_number_digit_count_bucket:4_digit", "flogic:citation_section_number_digit_count_bucket_positioned:1:4_digit", "flogic:citation_section_number_digit_count_positioned:1:4", "flogic:citation_section_number_magnitude_bucket:1k_to_9k", "flogic:citation_section_number_magnitude_bucket_positioned:1:1k_to_9k"]}`
  evidence: `{"cosine_similarity": -0.041927800557, "hint_id": "modal-synthesis-8baa35da3410bd37", "priority": 0.429088394263, "reconstruction_loss": 0.429088394263, "sample_id": "us-code-42-1395c.-da5383050c7a2c5e", "top_embedding_features": ["cue:conditional_normative:O|:except", "cue:deontic:P:may", "family:selected_frame:epistemic", "flogic:condition_alnum_segment:a", "flogic:condition_alnum_segment:such", "flogic:condition_alnum_segment_count:6", "flogic:condition_scope_alnum_segment:a", "flogic:condition_scope_alnum_segment:such"]}`
  evidence: `{"cosine_similarity": 0.052833614927, "hint_id": "modal-synthesis-9ea2a1707bff20b3", "priority": 0.649413377199, "reconstruction_loss": 0.649413377199, "sample_id": "us-code-38-8163-dc4c9191b09f4a3d", "top_embedding_features": ["cue:temporal:F:by", "flogic:citation_section_has_trailing_punct:false", "flogic:citation_section_number_has_zero_digit:false", "flogic:citation_section_number_has_zero_digit_positioned:1:false", "flogic:citation_section_number_zero_digit_count:0", "flogic:citation_section_number_zero_digit_count_positioned:1:0", "flogic:citation_section_primary_number_has_zero_digit:false", "flogic:citation_section_primary_number_zero_digit_count:0"]}`
  evidence: `{"cosine_similarity": -0.153736828969, "hint_id": "modal-synthesis-b044f4e2885d4888", "priority": 0.44941495653, "reconstruction_loss": 0.44941495653, "sample_id": "us-code-10-649j-49b85ae09715be03", "top_embedding_features": ["flogic:citation_section_number_parity:odd", "flogic:citation_section_number_parity_positioned:1:odd", "flogic:citation_section_primary_number_parity:odd", "flogic:citation_section_terminal_number_parity:odd", "flogic:modal_span_coverage_percent_parity:odd", "flogic:source_id_section_number_parity:odd", "flogic:source_id_section_number_parity_positioned:1:odd", "flogic:source_id_section_primary_number_parity:odd"]}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
