# packet-000157

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/packet-000157/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/packet-000157/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000157-20260518_201940

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/logic/modal/decompiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_ir.py`

## TODOs
- `program-633dee8134da1c8d` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-633dee8134da1c8d` score `1.0`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": 0.026462964975, "hint_id": "modal-synthesis-3e210529e06158fc", "priority": 0.535311339146, "reconstruction_loss": 0.535311339146, "sample_id": "us-code-16-2622-7b3b0068d25f5128", "top_embedding_features": ["cue:temporal:F:by", "flogic:citation_section_style:single_numeric_clean", "flogic:citation_section_style_alnum_segment_count:3", "flogic:citation_section_style_alnum_segment_positioned:3:clean", "flogic:citation_section_style_stem:single_numeric_clean", "flogic:citation_section_style_token_count:3", "flogic:citation_source_id_section_style_pair:single_numeric_clean|single_numeric_clean", "flogic:modal_cue:by"]}`
  evidence: `{"cosine_similarity": -0.723402430895, "hint_id": "modal-synthesis-573e788c5f52afb4", "priority": 0.793015334449, "reconstruction_loss": 0.793015334449, "sample_id": "us-code-14-944-8be0e29f8ef88af3", "top_embedding_features": ["cue:alethic:\u25a1:necessary", "family:alethic:1", "family:selected_frame:alethic", "flogic:candidate_ontology_term:final", "flogic:condition_alnum_segment_count:7", "flogic:condition_alnum_segment_positioned:6:the", "flogic:condition_scope_alnum_segment_count:6", "flogic:condition_scope_token_count:6"]}`
  evidence: `{"cosine_similarity": -0.047680814711, "hint_id": "modal-synthesis-8b66cc124a556c4f", "priority": 0.552485503397, "reconstruction_loss": 0.552485503397, "sample_id": "us-code-2-60e-3-49bb3eb4baff92b8", "top_embedding_features": ["flogic:support_span_end_char_parity:even", "slot:support_span_end_char_parity:even", "flogic:citation_title_number_has_zero_digit:false", "flogic:citation_title_number_trailing_zero_count:0", "flogic:citation_title_number_zero_digit_count:0", "flogic:source_id_title_number_has_zero_digit:false", "flogic:source_id_title_number_trailing_zero_count:0", "flogic:source_id_title_number_zero_digit_count:0"]}`
  evidence: `{"cosine_similarity": -0.350692277784, "hint_id": "modal-synthesis-aa75b79a176f59f9", "priority": 0.58753821666, "reconstruction_loss": 0.58753821666, "sample_id": "us-code-10-2514-26b4c42b97b7f6af", "top_embedding_features": ["flogic:support_span_width_digit_count_bucket:3_digit", "lemma:relating", "slot:support_span_width_digit_count_bucket:3_digit", "flogic:modal_span_char_count_digit_count_bucket:3_digit", "slot:modal_span_char_count_digit_count_bucket:3_digit", "lemma:subchapter", "family:temporal:1", "flogic:citation_title_number_parity:even"]}`
- `program-84237e0e9b017ae5` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-633dee8134da1c8d` score `0.992792`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": -0.175209114999, "hint_id": "modal-synthesis-16637ded53483243", "priority": 0.54018466368, "reconstruction_loss": 0.54018466368, "sample_id": "us-code-12-4307-d8adf804365b9891", "top_embedding_features": ["flogic:citation_section_alnum_segment_count:1", "flogic:citation_section_component_kind:numeric", "flogic:citation_section_component_kind_positioned:1:numeric", "flogic:citation_section_component_profile:single_numeric", "flogic:citation_section_has_mixed_token:false", "flogic:citation_section_has_suffix:false", "flogic:citation_section_mixed_token_count:0", "flogic:citation_section_primary_component_kind:numeric"]}`
  evidence: `{"cosine_similarity": 0.21513337204, "hint_id": "modal-synthesis-467e75b5b47af334", "priority": 0.311949960939, "reconstruction_loss": 0.311949960939, "sample_id": "us-code-41-8105-aadc79523092741d", "top_embedding_features": ["cue:epistemic:K:determines", "flogic:candidate_ontology_term:final", "flogic:condition_alnum_segment:in", "flogic:condition_alnum_segment_count:7", "flogic:condition_alnum_segment_positioned:3:the", "flogic:condition_scope_alnum_segment:in", "flogic:condition_scope_alnum_segment_count:6", "flogic:condition_scope_token:in"]}`
  evidence: `{"cosine_similarity": -0.214858955294, "hint_id": "modal-synthesis-a9157c0f67b9c14f", "priority": 0.590178933827, "reconstruction_loss": 0.590178933827, "sample_id": "us-code-46-2104.-968c80c773abaeae", "top_embedding_features": ["lemma:authorities", "lemma:personnel", "lemma:relating", "cue:frame:Frame:authority", "flogic:modal_cue:authority", "lemma:authority", "slot:cue:authority", "family:selected_frame:frame"]}`
  evidence: `{"cosine_similarity": 0.134283470671, "hint_id": "modal-synthesis-cdecea9c91aff473", "priority": 0.439344837216, "reconstruction_loss": 0.439344837216, "sample_id": "us-code-10-986-edca8f211d40c8ce", "top_embedding_features": ["flogic:citation_section_number_parity:even", "flogic:citation_section_number_parity_positioned:1:even", "flogic:citation_section_primary_number_parity:even", "flogic:citation_section_terminal_number_parity:even", "flogic:modal_span_coverage_percent_parity:even", "flogic:predicate:pub", "flogic:predicate_alnum_segment:pub", "flogic:predicate_alnum_segment_count:1"]}`
- `program-6f9200157f038b30` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-633dee8134da1c8d` score `0.992164`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": -0.10284038067, "hint_id": "modal-synthesis-11a987ee0d421773", "priority": 0.515037288903, "reconstruction_loss": 0.515037288903, "sample_id": "us-code-42-13414.-92c7f7f926991bb1", "top_embedding_features": ["cue:deontic:O:shall", "family:selected_frame:deontic", "flogic:modal_cue:shall", "flogic:modal_family:deontic", "flogic:modal_family_count_family:deontic", "flogic:modal_operator:O", "flogic:modal_operator_label:obligation", "flogic:modal_span_coverage_percent_has_zero_digit:false"]}`
  evidence: `{"cosine_similarity": 0.003524030401, "hint_id": "modal-synthesis-3a9b310407deddcf", "priority": 0.446186598448, "reconstruction_loss": 0.446186598448, "sample_id": "us-code-36-30104-bb1cedfd16c58ba3", "top_embedding_features": ["lemma:ii", "flogic:citation_title_number_leading_digit:3", "flogic:source_id_title_number_leading_digit:3", "flogic:support_span_start_char_hundreds_block:3", "flogic:support_span_start_char_leading_digit:3", "flogic:support_span_start_char_prefix_two_digits:33", "lemma:executed", "lemma:including"]}`
  evidence: `{"cosine_similarity": -0.278006691911, "hint_id": "modal-synthesis-52f542dfdd1544a8", "priority": 0.4889179023, "reconstruction_loss": 0.4889179023, "sample_id": "us-code-42-5771.-02e64c6fbb913aae", "top_embedding_features": ["flogic:citation_title_section_primary_number_span_has_zero_digit:false", "flogic:citation_title_section_primary_number_span_zero_digit_count:0", "flogic:citation_title_section_terminal_number_span_has_zero_digit:false", "flogic:citation_title_section_terminal_number_span_zero_digit_count:0", "flogic:source_id_title_section_primary_number_span_has_zero_digit:false", "flogic:source_id_title_section_primary_number_span_zero_digit_count:0", "flogic:source_id_title_section_terminal_number_span_has_zero_digit:false", "flogic:source_id_title_section_terminal_number_span_zero_digit_count:0"]}`
  evidence: `{"cosine_similarity": 0.57770481554, "hint_id": "modal-synthesis-9f6dcd348545798a", "priority": 0.246436284403, "reconstruction_loss": 0.246436284403, "sample_id": "us-code-46-13106.-1fd00cdf20630972", "top_embedding_features": ["lemma:renumbered", "lemma:related", "flogic:citation_title_section_primary_number_span_has_zero_digit:true", "flogic:citation_title_section_terminal_number_span_has_zero_digit:true", "flogic:source_id_title_section_primary_number_span_has_zero_digit:true", "flogic:source_id_title_section_terminal_number_span_has_zero_digit:true", "slot:citation_title_section_primary_number_span_has_zero_digit:true", "slot:citation_title_section_terminal_number_span_has_zero_digit:true"]}`
- `program-69b670f503e41d6d` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-633dee8134da1c8d` score `0.991904`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": -0.269751833604, "hint_id": "modal-synthesis-1f2d20b56ab746e1", "priority": 0.534896406497, "reconstruction_loss": 0.534896406497, "sample_id": "us-code-22-3649-f991a9b1c373d11a", "top_embedding_features": ["flogic:modal_span_coverage_percent_has_zero_digit:false", "flogic:modal_span_coverage_percent_trailing_zero_count:0", "flogic:modal_span_coverage_percent_zero_digit_count:0", "flogic:predicate_alnum_segment_count:6", "flogic:predicate_alnum_segment_kind_positioned:2:alpha", "flogic:predicate_alnum_segment_kind_positioned:3:alpha", "flogic:predicate_alnum_segment_kind_positioned:4:alpha", "flogic:predicate_alnum_segment_kind_positioned:5:alpha"]}`
  evidence: `{"cosine_similarity": 0.1101703283, "hint_id": "modal-synthesis-3a9bb4a8b114ccb9", "priority": 0.450584468941, "reconstruction_loss": 0.450584468941, "sample_id": "us-code-18-2233-ee88be17d0c51761", "top_embedding_features": ["flogic:citation_section_alnum_segment_count:1", "flogic:citation_section_component_kind:numeric", "flogic:citation_section_component_kind_positioned:1:numeric", "flogic:citation_section_component_profile:single_numeric", "flogic:citation_section_has_mixed_token:false", "flogic:citation_section_has_suffix:false", "flogic:citation_section_mixed_token_count:0", "flogic:citation_section_primary_component_kind:numeric"]}`
  evidence: `{"cosine_similarity": 0.198195707748, "hint_id": "modal-synthesis-a2aa57174e4ffe5a", "priority": 0.355557978547, "reconstruction_loss": 0.355557978547, "sample_id": "us-code-20-888-9088542f47a22f56", "top_embedding_features": ["flogic:citation_title_section_primary_number_span_parity:even", "flogic:citation_title_section_terminal_number_span_parity:even", "flogic:source_id_title_section_primary_number_span_parity:even", "flogic:source_id_title_section_terminal_number_span_parity:even", "slot:citation_title_section_primary_number_span_parity:even", "slot:citation_title_section_terminal_number_span_parity:even", "slot:source_id_title_section_primary_number_span_parity:even", "slot:source_id_title_section_terminal_number_span_parity:even"]}`
  evidence: `{"cosine_similarity": 0.152282844853, "hint_id": "modal-synthesis-cf9475641393e8b2", "priority": 0.419562943998, "reconstruction_loss": 0.419562943998, "sample_id": "us-code-50-2736.-7d020c287985eabd", "top_embedding_features": ["cue:deontic:P:may", "flogic:modal_cue:may", "flogic:modal_formula_count_digit_count_bucket:2_digit", "flogic:modal_operator:P", "flogic:modal_operator_label:permission", "flogic:modal_span_char_count_digit_count_bucket:4_digit", "flogic:modal_span_char_count_magnitude_bucket:1k_to_9k", "flogic:modal_system:S5"]}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
