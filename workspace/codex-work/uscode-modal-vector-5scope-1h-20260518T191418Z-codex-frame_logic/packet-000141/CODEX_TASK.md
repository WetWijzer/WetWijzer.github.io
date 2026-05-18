# packet-000141

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/packet-000141/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/packet-000141/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000141-20260518_201007

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/optimizers/logic/flogic_optimizer.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/frame_bm25_selector.py`

## TODOs
- `program-2110e9446a24c3b1` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-2110e9446a24c3b1` score `1.0`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["flogic:citation_title_number_parity:even"], "hint_id": "modal-synthesis-17a94198271fc22a", "priority": 0.58753821666, "sample_id": "us-code-10-2514-26b4c42b97b7f6af"}`
  evidence: `{"frame_features": ["flogic:citation_title_number_has_zero_digit:false", "flogic:citation_title_number_trailing_zero_count:0", "flogic:citation_title_number_zero_digit_count:0", "flogic:source_id_title_number_has_zero_digit:false", "flogic:source_id_title_number_trailing_zero_count:0", "flogic:source_id_title_number_zero_digit_count:0"], "hint_id": "modal-synthesis-3968db0337ef39cd", "priority": 0.552485503397, "sample_id": "us-code-2-60e-3-49bb3eb4baff92b8"}`
  evidence: `{"frame_features": ["family:selected_frame:alethic", "flogic:candidate_ontology_term:final", "flogic:condition_alnum_segment_count:7", "flogic:condition_alnum_segment_positioned:6:the", "flogic:condition_scope_alnum_segment_count:6", "flogic:condition_scope_token_count:6"], "hint_id": "modal-synthesis-d11a516a8507d80a", "priority": 0.793015334449, "sample_id": "us-code-14-944-8be0e29f8ef88af3"}`
  evidence: `{"frame_features": ["flogic:citation_section_style:single_numeric_clean", "flogic:citation_section_style_alnum_segment_count:3", "flogic:citation_section_style_alnum_segment_positioned:3:clean", "flogic:citation_section_style_stem:single_numeric_clean", "flogic:citation_section_style_token_count:3", "flogic:citation_source_id_section_style_pair:single_numeric_clean|single_numeric_clean", "flogic:modal_cue:by"], "hint_id": "modal-synthesis-f3decd0094ca1a72", "priority": 0.535311339146, "sample_id": "us-code-16-2622-7b3b0068d25f5128"}`
- `program-4bb11f2b066450cb` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-2110e9446a24c3b1` score `0.967063`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["family:selected_frame:deontic", "flogic:modal_cue:shall", "flogic:modal_family:deontic"], "hint_id": "modal-synthesis-016283105f8a94ef", "priority": 0.813175235894, "sample_id": "us-code-51-40504.-daa7d9a7e25305f4"}`
  evidence: `{"frame_features": ["flogic:citation_section_component_signature:N4", "flogic:citation_section_component_signature_positioned:1:N4", "flogic:citation_section_number_digit_count:4", "flogic:citation_section_number_digit_count_bucket:4_digit", "flogic:citation_section_number_digit_count_bucket_positioned:1:4_digit", "flogic:citation_section_number_digit_count_positioned:1:4", "flogic:citation_section_number_magnitude_bucket:1k_to_9k", "flogic:citation_section_number_magnitude_bucket_positioned:1:1k_to_9k"], "hint_id": "modal-synthesis-3a6ca065fc3a6ac6", "priority": 0.45023400221, "sample_id": "us-code-26-7520-ad4e4c590b70c936"}`
  evidence: `{"frame_features": ["family:frame:1", "flogic:modal_family_count:frame:1", "flogic:modal_family_count_frame:1", "flogic:modal_family_count_ranked:2:frame:1", "flogic:predicate_alnum_segment_positioned:4:apply", "slot:modal_family_count:frame_1"], "hint_id": "modal-synthesis-73e09540758a5681", "priority": 0.423608886264, "sample_id": "us-code-46-55101.-18bef3d2cb36f938"}`
  evidence: `{"frame_features": ["flogic:citation_section_style_alnum_segment_kind_positioned:4:alpha", "flogic:source_id_section_style_alnum_segment_kind_positioned:4:alpha", "slot:citation_section_style_alnum_segment_kind_positioned:4_alpha", "slot:source_id_section_style_alnum_segment_kind_positioned:4_alpha", "flogic:modal_operator:X", "flogic:modal_operator_label:next"], "hint_id": "modal-synthesis-dd102c3bdce1ea6e", "priority": 0.424340100329, "sample_id": "us-code-42-1962d-982c099c7b80957b"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
