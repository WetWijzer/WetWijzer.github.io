# packet-000080

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/packet-000080/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/packet-000080/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000080-20260518_194637

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/logic/modal/decompiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_ir.py`

## TODOs
- `program-3aae8bfbff4fd274` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-3aae8bfbff4fd274` score `1.0`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": 0.141826338261, "hint_id": "modal-synthesis-1eb79e56dfc9339b", "priority": 0.531739974903, "reconstruction_loss": 0.531739974903, "sample_id": "us-code-10-508-3c4daeb3fdaf30d2", "top_embedding_features": ["flogic:citation_section_number_parity:even", "flogic:citation_section_number_parity_positioned:1:even", "flogic:citation_section_primary_number_parity:even", "flogic:citation_section_terminal_number_parity:even", "flogic:modal_span_coverage_percent_parity:even", "flogic:predicate_alnum_segment_count:1", "flogic:predicate_token_count:1", "flogic:source_id_section_number_parity:even"]}`
  evidence: `{"cosine_similarity": 0.000491733577, "hint_id": "modal-synthesis-a7dcf589289da690", "priority": 0.396096459524, "reconstruction_loss": 0.396096459524, "sample_id": "us-code-7-8758-6c50bb2c1676bbf9", "top_embedding_features": ["flogic:modal_formula_count_digit_count_bucket:1_digit", "slot:modal_formula_count_digit_count_bucket:1_digit", "flogic:citation_title_section_primary_number_span_trailing_zero_count:0", "flogic:citation_title_section_terminal_number_span_trailing_zero_count:0", "flogic:modal_family_count_value:1", "flogic:modal_formula_count_parity:odd", "flogic:source_id_title_section_primary_number_span_trailing_zero_count:0", "flogic:source_id_title_section_terminal_number_span_trailing_zero_count:0"]}`
  evidence: `{"cosine_similarity": 0.384930214879, "hint_id": "modal-synthesis-ca2245e955d618ed", "priority": 0.371278499662, "reconstruction_loss": 0.371278499662, "sample_id": "us-code-2-1516-e49d03132a8b32ab", "top_embedding_features": ["flogic:citation_section_has_trailing_punct:false", "flogic:citation_section_number_has_zero_digit:false", "flogic:citation_section_number_has_zero_digit_positioned:1:false", "flogic:citation_section_number_zero_digit_count:0", "flogic:citation_section_number_zero_digit_count_positioned:1:0", "flogic:citation_section_primary_number_has_zero_digit:false", "flogic:citation_section_primary_number_zero_digit_count:0", "flogic:citation_section_punctuation_style:clean"]}`
  evidence: `{"cosine_similarity": -0.498705131653, "hint_id": "modal-synthesis-cb6866a00afa2594", "priority": 0.582112001088, "reconstruction_loss": 0.582112001088, "sample_id": "us-code-5-8464a-7b232fae83466b72", "top_embedding_features": ["family:selected_frame:temporal", "flogic:candidate_ontology_frame:administrative_notice_hearing", "flogic:candidate_ontology_frame:criminal_penalty_enforcement", "flogic:candidate_ontology_frame:housing_voucher_benefits", "flogic:candidate_ontology_term:accommodation", "flogic:candidate_ontology_term:administrative", "flogic:candidate_ontology_term:administrative_notice_hearing", "flogic:candidate_ontology_term:agency"]}`
- `program-5902b52bef6ca61f` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-3aae8bfbff4fd274` score `0.990363`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": 0.691624251586, "hint_id": "modal-synthesis-028d0afa54c22b45", "priority": 0.192148253501, "reconstruction_loss": 0.192148253501, "sample_id": "us-code-54-101511.-54b6ccb5549961cf", "top_embedding_features": ["flogic:modal_span_count_leading_digit:1", "flogic:support_span_end_char_parity:odd", "lemma:added", "lemma:annual", "lemma:general", "lemma:service", "slot:modal_span_count_leading_digit:1", "slot:support_span_end_char_parity:odd"]}`
  evidence: `{"cosine_similarity": 0.370638524576, "hint_id": "modal-synthesis-064de8e5c8b30c64", "priority": 0.323023176344, "reconstruction_loss": 0.323023176344, "sample_id": "us-code-22-2779a-2f9baaa9ac52eacf", "top_embedding_features": ["flogic:citation_title_number_parity:even", "flogic:source_id_title_number_parity:even", "slot:citation_title_number_parity:even", "slot:source_id_title_number_parity:even", "flogic:citation_title_section_primary_number_span_trailing_zero_count:0", "flogic:citation_title_section_terminal_number_span_trailing_zero_count:0", "flogic:modal_span_char_count_parity:odd", "flogic:source_context_span_char_count_parity:even"]}`
  evidence: `{"cosine_similarity": 0.33470375162, "hint_id": "modal-synthesis-58e80b94785cf501", "priority": 0.356852997198, "reconstruction_loss": 0.356852997198, "sample_id": "us-code-26-646-0cfbbfe0c86b90ae", "top_embedding_features": ["flogic:citation_title_section_primary_number_span_parity:even", "flogic:citation_title_section_terminal_number_span_parity:even", "flogic:interpreted_in_frame:administrative_notice_hearing", "flogic:interpreted_in_frame_term:administrative", "flogic:interpreted_in_frame_term:administrative_notice_hearing", "flogic:interpreted_in_frame_term:agency", "flogic:interpreted_in_frame_term:appeal", "flogic:interpreted_in_frame_term:deadline"]}`
  evidence: `{"cosine_similarity": -0.333937737347, "hint_id": "modal-synthesis-ced12415d41ceee2", "priority": 0.41847466304, "reconstruction_loss": 0.41847466304, "sample_id": "us-code-38-7310A-219731bd25fca43f", "top_embedding_features": ["flogic:exception_alnum_segment_kind_positioned:5:alpha", "flogic:exception_scope_alnum_segment_kind_positioned:4:alpha", "flogic:modal_span_char_count_parity:even", "flogic:predicate_alnum_segment:c", "flogic:predicate_alnum_segment:respect", "flogic:predicate_token:c", "flogic:predicate_token:respect", "flogic:source_text_char_count_has_zero_digit:true"]}`
- `program-d402a6ead5290784` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-3aae8bfbff4fd274` score `0.988706`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": -0.041150743536, "hint_id": "modal-synthesis-114b70e65e5fe3b8", "priority": 0.319096629099, "reconstruction_loss": 0.319096629099, "sample_id": "us-code-16-831r-67ffc5b229e2bd75", "top_embedding_features": ["flogic:citation_title_section_primary_number_span_trailing_zero_count:0", "flogic:citation_title_section_terminal_number_span_trailing_zero_count:0", "flogic:modal_family_count_value:1", "flogic:modal_formula_count_parity:odd", "flogic:source_id_title_section_primary_number_span_trailing_zero_count:0", "flogic:source_id_title_section_terminal_number_span_trailing_zero_count:0", "flogic:source_text_char_count_has_zero_digit:false", "flogic:source_text_char_count_zero_digit_count:0"]}`
  evidence: `{"cosine_similarity": -0.250653589932, "hint_id": "modal-synthesis-140abe7815dde58a", "priority": 0.687328500451, "reconstruction_loss": 0.687328500451, "sample_id": "us-code-34-11294-0a6981caa505e06b", "top_embedding_features": ["flogic:citation_section_number_leading_digit:1", "flogic:citation_section_number_leading_digit_positioned:1:1", "flogic:citation_section_primary_number_leading_digit:1", "flogic:citation_section_terminal_number_leading_digit:1", "flogic:citation_title_section_primary_number_span_leading_digit:1", "flogic:citation_title_section_primary_number_span_trailing_zero_count:1", "flogic:citation_title_section_terminal_number_span_leading_digit:1", "flogic:citation_title_section_terminal_number_span_trailing_zero_count:1"]}`
  evidence: `{"cosine_similarity": 0.255615873322, "hint_id": "modal-synthesis-42d8c2b2aec28c97", "priority": 0.464871476043, "reconstruction_loss": 0.464871476043, "sample_id": "us-code-29-1662-e7516434dca445ba", "top_embedding_features": ["flogic:citation_title_section_primary_number_span_has_zero_digit:false", "flogic:citation_title_section_primary_number_span_zero_digit_count:0", "flogic:citation_title_section_terminal_number_span_has_zero_digit:false", "flogic:citation_title_section_terminal_number_span_zero_digit_count:0", "flogic:source_id_title_section_primary_number_span_has_zero_digit:false", "flogic:source_id_title_section_primary_number_span_zero_digit_count:0", "flogic:source_id_title_section_terminal_number_span_has_zero_digit:false", "flogic:source_id_title_section_terminal_number_span_zero_digit_count:0"]}`
  evidence: `{"cosine_similarity": -0.17427808111, "hint_id": "modal-synthesis-42e178deb3a82a84", "priority": 0.407276740782, "reconstruction_loss": 0.407276740782, "sample_id": "us-code-22-2078-b00052cd8a98ed8d", "top_embedding_features": ["cue:temporal:F:by", "flogic:citation_section_has_trailing_punct:false", "flogic:citation_section_punctuation_style:clean", "flogic:citation_section_style:single_numeric_clean", "flogic:citation_section_style_alnum_segment:clean", "flogic:citation_section_style_alnum_segment_count:3", "flogic:citation_section_style_alnum_segment_positioned:3:clean", "flogic:citation_section_style_alnum_segment_suffix:clean"]}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
