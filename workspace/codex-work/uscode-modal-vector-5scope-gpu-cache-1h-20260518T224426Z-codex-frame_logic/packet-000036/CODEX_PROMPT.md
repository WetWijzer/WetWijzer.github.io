# packet-000036

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/packet-000036/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/packet-000036/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000036-20260518_232544

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/optimizers/logic/flogic_optimizer.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/frame_bm25_selector.py`

## TODOs
- `program-5ef7fd6482a162f1` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-5ef7fd6482a162f1` score `1.0`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"hint_id": "modal-synthesis-106f39f26afb560c", "priority": 0.600061854299, "sample_id": "us-code-42-3733.-c27417ee223d4a0e"}`
  evidence: `{"frame_features": ["flogic:modal_cue:required"], "hint_id": "modal-synthesis-6ef5a5d047671d0b", "priority": 0.632210268879, "sample_id": "us-code-20-10010-2aa9655012cdfd20"}`
  evidence: `{"frame_features": ["flogic:condition_modal_operator:P", "slot:condition_modal_operator:p", "flogic:condition_alnum_segment:of", "flogic:condition_alnum_segment:the", "flogic:condition_alnum_segment_kind:alpha", "flogic:condition_alnum_segment_kind_positioned:1:alpha", "flogic:condition_alnum_segment_kind_positioned:2:alpha"], "hint_id": "modal-synthesis-bac1168d941d83d3", "priority": 0.679820797215, "sample_id": "us-code-49-44720.-a16b323fdacfff9a"}`
  evidence: `{"frame_features": ["flogic:condition_alnum_segment:is", "flogic:condition_alnum_segment_positioned:2:such", "flogic:condition_alnum_segment_positioned:4:is", "flogic:condition_scope_alnum_segment:is", "flogic:condition_scope_alnum_segment_positioned:3:is", "flogic:condition_scope_token:is", "flogic:condition_token:is"], "hint_id": "modal-synthesis-df59cc4ddb64ea89", "priority": 0.87687966161, "sample_id": "us-code-46-70118.-57e069df517d4903"}`
- `program-a1cb7d87e7e3af23` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-5ef7fd6482a162f1` score `0.967938`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["flogic:candidate_ontology_term:administration", "frame-term:administration"], "hint_id": "modal-synthesis-441e8bc6ad4c5b3b", "priority": 0.625465155784, "sample_id": "us-code-51-60602.-5489692eaff98ebf"}`
  evidence: `{"frame_features": ["flogic:condition_alnum_segment:an", "flogic:condition_scope_alnum_segment:an", "flogic:condition_scope_token:an", "flogic:condition_token:an", "slot:condition_alnum_segment:an", "slot:condition_scope_alnum_segment:an", "slot:condition_scope_token:an"], "hint_id": "modal-synthesis-6522f8cfb8c80591", "priority": 0.625626232713, "sample_id": "us-code-19-1490-1d4271fb0a2e6691"}`
  evidence: `{"frame_features": ["flogic:condition_scope_alnum_segment:to", "flogic:condition_scope_token:to", "slot:condition_scope_alnum_segment:to", "slot:condition_scope_token:to", "flogic:condition_alnum_segment:with", "flogic:condition_scope_alnum_segment:with"], "hint_id": "modal-synthesis-66c27cbb62758a99", "priority": 0.289416977131, "sample_id": "us-code-20-6645-852d6af8a4c5e7aa"}`
  evidence: `{"frame_features": ["flogic:citation_source_id_title_pair:46|46", "flogic:citation_source_id_title_section_profile_pair:46:single_numeric|46:single_numeric", "flogic:citation_source_id_title_section_signature_pair:46:n5|46:n5", "flogic:citation_title:46", "flogic:citation_title_alnum_segment:46", "flogic:citation_title_alnum_segment_positioned:1:46", "flogic:citation_title_alnum_segment_prefix:46", "flogic:citation_title_alnum_segment_suffix:46"], "hint_id": "modal-synthesis-ed357aa0374f061a", "priority": 0.197617454265, "sample_id": "us-code-46-60106.-88d1b607a78712ef"}`
- `program-ae66e264321ea0c0` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-5ef7fd6482a162f1` score `0.966102`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["flogic:exception_alnum_segment_kind:alpha", "flogic:exception_alnum_segment_kind_positioned:1:alpha", "flogic:exception_alnum_segment_kind_positioned:2:alpha", "flogic:exception_alnum_segment_kind_positioned:3:alpha", "flogic:exception_has_mixed_token:false", "flogic:exception_mixed_token_count:0", "flogic:exception_modal_family:conditional_normative", "flogic:exception_modal_operator:O|"], "hint_id": "modal-synthesis-1ae81ce52b61b1a4", "priority": 0.331118149552, "sample_id": "us-code-47-34.-add4da103cc4783e"}`
  evidence: `{"frame_features": ["flogic:predicate_alnum_segment_positioned:4:shall", "slot:predicate_alnum_segment_positioned:4_shall", "flogic:modal_cue:may be"], "hint_id": "modal-synthesis-8ab8f1ad40fb8abe", "priority": 0.345255917399, "sample_id": "us-code-18-2257-d6b40c9abbafb4f2"}`
  evidence: `{"frame_features": ["flogic:modal_system:S5", "slot:modal_system:s5", "family:selected_frame:alethic", "flogic:condition_modal_family:alethic"], "hint_id": "modal-synthesis-9ca2086e0f727f88", "priority": 0.676041039652, "sample_id": "us-code-2-4501-4ee4ed93367b922f"}`
  evidence: `{"frame_features": ["flogic:predicate_alnum_segment:including", "flogic:predicate_token:including", "slot:predicate_alnum_segment:including", "slot:predicate_token:including", "flogic:predicate_alnum_segment:secretary", "flogic:predicate_token:secretary", "slot:predicate_alnum_segment:secretary"], "hint_id": "modal-synthesis-d81bd149ee738663", "priority": 0.420400698336, "sample_id": "us-code-42-3543.-3718f5f6f3f6b9f7"}`
- `program-906546b736cc8e1f` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-5ef7fd6482a162f1` score `0.965507`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["slot:frame_candidate_ranked:3_housing_voucher_benefits"], "hint_id": "modal-synthesis-20318e2f21fb646c", "priority": 0.24782953414, "sample_id": "us-code-25-2402-d2b0b613bb62b381"}`
  evidence: `{"frame_features": ["flogic:condition_alnum_segment:an", "flogic:condition_scope_alnum_segment:an", "flogic:condition_scope_token:an", "flogic:condition_token:an", "slot:condition_alnum_segment:an", "slot:condition_scope_alnum_segment:an"], "hint_id": "modal-synthesis-2901bada74c6b80c", "priority": 0.523659368959, "sample_id": "us-code-5-8338-8843bfb9fff586e8"}`
  evidence: `{"frame_features": ["flogic:predicate_alnum_segment_positioned:4:title", "slot:predicate_alnum_segment_positioned:4_title", "flogic:predicate_alnum_segment_positioned:3:section", "slot:predicate_alnum_segment_positioned:3_section"], "hint_id": "modal-synthesis-46697aebe1dda15a", "priority": 0.521449728956, "sample_id": "us-code-20-5207-97035bc3bbe5872e"}`
  evidence: `{"frame_features": ["flogic:modal_system:S5", "slot:modal_system:s5", "flogic:predicate_alnum_segment_positioned:3:shall", "slot:predicate_alnum_segment_positioned:3_shall", "family:frame:3", "flogic:condition_alnum_segment_positioned:18:the", "flogic:condition_alnum_segment_suffix:the"], "hint_id": "modal-synthesis-a25f361498ba0384", "priority": 0.56599590942, "sample_id": "us-code-8-1188-42be8ee149ed016a"}`
- `program-0fb024f942dc5ce9` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-5ef7fd6482a162f1` score `0.959714`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["flogic:condition_alnum_segment:by", "flogic:condition_alnum_segment_positioned:5:the", "flogic:condition_scope_alnum_segment:by", "flogic:condition_scope_alnum_segment_positioned:4:the", "flogic:condition_scope_alnum_segment_positioned:5:secretary", "flogic:condition_scope_token:by", "flogic:condition_token:by"], "hint_id": "modal-synthesis-161256fb12c76a3a", "priority": 0.419654166452, "sample_id": "us-code-16-691c-14e7b6e3ed33e5e0"}`
  evidence: `{"frame_features": ["flogic:condition_alnum_segment:an", "flogic:condition_alnum_segment:of", "flogic:condition_alnum_segment:secretary", "flogic:condition_alnum_segment:the", "flogic:condition_alnum_segment:to", "flogic:condition_alnum_segment:upon", "flogic:condition_alnum_segment_count:18", "flogic:condition_alnum_segment_kind:alpha"], "hint_id": "modal-synthesis-5d26296752e3fa14", "priority": 0.512608551279, "sample_id": "us-code-47-906.-6879796231f40903"}`
  evidence: `{"frame_features": ["slot:frame_candidate_ranked:2_criminal_penalty_enforcement", "slot:frame_candidate_ranked:3_housing_voucher_benefits", "family:selected_frame:frame"], "hint_id": "modal-synthesis-68aaff9cb64000b5", "priority": 0.491833360538, "sample_id": "us-code-17-410-0758ab00b97b8f33"}`
  evidence: `{"frame_features": ["flogic:citation_section_number_has_zero_digit:false", "flogic:citation_section_number_parity:even", "flogic:citation_section_number_parity_positioned:1:even", "flogic:citation_section_number_zero_digit_count:0", "flogic:citation_section_primary_number_parity:even", "flogic:citation_section_terminal_number_has_zero_digit:false", "flogic:citation_section_terminal_number_zero_digit_count:0", "flogic:source_id_section_number_has_zero_digit:false"], "hint_id": "modal-synthesis-a4ac173b4d500c77", "priority": 0.814680389649, "sample_id": "us-code-15-694-1-19bbe1ebb1be0815"}`

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

- Queue run: `uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder.jsonl`
- TODO count: `5`

## TODOs
- `program-5ef7fd6482a162f1`
  action: `audit_frame_logic_terms`
  role: `program_synthesis`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-5ef7fd6482a162f1` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.697243145501`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  samples: `us-code-46-70118.-57e069df517d4903, us-code-49-44720.-a16b323fdacfff9a, us-code-20-10010-2aa9655012cdfd20, us-code-42-3733.-c27417ee223d4a0e`
  evidence: `{"hint_id": "modal-synthesis-106f39f26afb560c", "priority": 0.600061854299, "sample_id": "us-code-42-3733.-c27417ee223d4a0e"}`
  evidence: `{"frame_features": ["flogic:modal_cue:required"], "hint_id": "modal-synthesis-6ef5a5d047671d0b", "priority": 0.632210268879, "sample_id": "us-code-20-10010-2aa9655012cdfd20"}`
  evidence: `{"frame_features": ["flogic:condition_modal_operator:P", "slot:condition_modal_operator:p", "flogic:condition_alnum_segment:of", "flogic:condition_alnum_segment:the", "flogic:condition_alnum_segment_kind:alpha", "flogic:condition_alnum_segment_kind_positioned:1:alpha", "flogic:condition_alnum_segment_kind_positioned:2:alpha"], "hint_id": "modal-synthesis-bac1168d941d83d3", "priority": 0.679820797215, "sample_id": "us-code-49-44720.-a16b323fdacfff9a"}`
  evidence: `{"frame_features": ["flogic:condition_alnum_segment:is", "flogic:condition_alnum_segment_positioned:2:such", "flogic:condition_alnum_segment_positioned:4:is", "flogic:condition_scope_alnum_segment:is", "flogic:condition_scope_alnum_segment_positioned:3:is", "flogic:condition_scope_token:is", "flogic:condition_token:is"], "hint_id": "modal-synthesis-df59cc4ddb64ea89", "priority": 0.87687966161, "sample_id": "us-code-46-70118.-57e069df517d4903"}`
- `program-a1cb7d87e7e3af23`
  action: `audit_frame_logic_terms`
  role: `program_synthesis`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-5ef7fd6482a162f1` score `0.967938`
  loss: `autoencoder_residual_cluster` = `0.434531454973`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  samples: `us-code-19-1490-1d4271fb0a2e6691, us-code-51-60602.-5489692eaff98ebf, us-code-20-6645-852d6af8a4c5e7aa, us-code-46-60106.-88d1b607a78712ef`
  evidence: `{"frame_features": ["flogic:candidate_ontology_term:administration", "frame-term:administration"], "hint_id": "modal-synthesis-441e8bc6ad4c5b3b", "priority": 0.625465155784, "sample_id": "us-code-51-60602.-5489692eaff98ebf"}`
  evidence: `{"frame_features": ["flogic:condition_alnum_segment:an", "flogic:condition_scope_alnum_segment:an", "flogic:condition_scope_token:an", "flogic:condition_token:an", "slot:condition_alnum_segment:an", "slot:condition_scope_alnum_segment:an", "slot:condition_scope_token:an"], "hint_id": "modal-synthesis-6522f8cfb8c80591", "priority": 0.625626232713, "sample_id": "us-code-19-1490-1d4271fb0a2e6691"}`
  evidence: `{"frame_features": ["flogic:condition_scope_alnum_segment:to", "flogic:condition_scope_token:to", "slot:condition_scope_alnum_segment:to", "slot:condition_scope_token:to", "flogic:condition_alnum_segment:with", "flogic:condition_scope_alnum_segment:with"], "hint_id": "modal-synthesis-66c27cbb62758a99", "priority": 0.289416977131, "sample_id": "us-code-20-6645-852d6af8a4c5e7aa"}`
  evidence: `{"frame_features": ["flogic:citation_source_id_title_pair:46|46", "flogic:citation_source_id_title_section_profile_pair:46:single_numeric|46:single_numeric", "flogic:citation_source_id_title_section_signature_pair:46:n5|46:n5", "flogic:citation_title:46", "flogic:citation_title_alnum_segment:46", "flogic:citation_title_alnum_segment_positioned:1:46", "flogic:citation_title_alnum_segment_prefix:46", "flogic:citation_title_alnum_segment_suffix:46"], "hint_id": "modal-synthesis-ed357aa0374f061a", "priority": 0.197617454265, "sample_id": "us-code-46-60106.-88d1b607a78712ef"}`
- `program-ae66e264321ea0c0`
  action: `audit_frame_logic_terms`
  role: `program_synthesis`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-5ef7fd6482a162f1` score `0.966102`
  loss: `autoencoder_residual_cluster` = `0.443203951235`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  samples: `us-code-2-4501-4ee4ed93367b922f, us-code-42-3543.-3718f5f6f3f6b9f7, us-code-18-2257-d6b40c9abbafb4f2, us-code-47-34.-add4da103cc4783e`
  evidence: `{"frame_features": ["flogic:exception_alnum_segment_kind:alpha", "flogic:exception_alnum_segment_kind_positioned:1:alpha", "flogic:exception_alnum_segment_kind_positioned:2:alpha", "flogic:exception_alnum_segment_kind_positioned:3:alpha", "flogic:exception_has_mixed_token:false", "flogic:exception_mixed_token_count:0", "flogic:exception_modal_family:conditional_normative", "flogic:exception_modal_operator:O|"], "hint_id": "modal-synthesis-1ae81ce52b61b1a4", "priority": 0.331118149552, "sample_id": "us-code-47-34.-add4da103cc4783e"}`
  evidence: `{"frame_features": ["flogic:predicate_alnum_segment_positioned:4:shall", "slot:predicate_alnum_segment_positioned:4_shall", "flogic:modal_cue:may be"], "hint_id": "modal-synthesis-8ab8f1ad40fb8abe", "priority": 0.345255917399, "sample_id": "us-code-18-2257-d6b40c9abbafb4f2"}`
  evidence: `{"frame_features": ["flogic:modal_system:S5", "slot:modal_system:s5", "family:selected_frame:alethic", "flogic:condition_modal_family:alethic"], "hint_id": "modal-synthesis-9ca2086e0f727f88", "priority": 0.676041039652, "sample_id": "us-code-2-4501-4ee4ed93367b922f"}`
  evidence: `{"frame_features": ["flogic:predicate_alnum_segment:including", "flogic:predicate_token:including", "slot:predicate_alnum_segment:including", "slot:predicate_token:including", "flogic:predicate_alnum_segment:secretary", "flogic:predicate_token:secretary", "slot:predicate_alnum_segment:secretary"], "hint_id": "modal-synthesis-d81bd149ee738663", "priority": 0.420400698336, "sample_id": "us-code-42-3543.-3718f5f6f3f6b9f7"}`
- `program-906546b736cc8e1f`
  action: `audit_frame_logic_terms`
  role: `program_synthesis`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-5ef7fd6482a162f1` score `0.965507`
  loss: `autoencoder_residual_cluster` = `0.464733635369`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  samples: `us-code-8-1188-42be8ee149ed016a, us-code-5-8338-8843bfb9fff586e8, us-code-20-5207-97035bc3bbe5872e, us-code-25-2402-d2b0b613bb62b381`
  evidence: `{"frame_features": ["slot:frame_candidate_ranked:3_housing_voucher_benefits"], "hint_id": "modal-synthesis-20318e2f21fb646c", "priority": 0.24782953414, "sample_id": "us-code-25-2402-d2b0b613bb62b381"}`
  evidence: `{"frame_features": ["flogic:condition_alnum_segment:an", "flogic:condition_scope_alnum_segment:an", "flogic:condition_scope_token:an", "flogic:condition_token:an", "slot:condition_alnum_segment:an", "slot:condition_scope_alnum_segment:an"], "hint_id": "modal-synthesis-2901bada74c6b80c", "priority": 0.523659368959, "sample_id": "us-code-5-8338-8843bfb9fff586e8"}`
  evidence: `{"frame_features": ["flogic:predicate_alnum_segment_positioned:4:title", "slot:predicate_alnum_segment_positioned:4_title", "flogic:predicate_alnum_segment_positioned:3:section", "slot:predicate_alnum_segment_positioned:3_section"], "hint_id": "modal-synthesis-46697aebe1dda15a", "priority": 0.521449728956, "sample_id": "us-code-20-5207-97035bc3bbe5872e"}`
  evidence: `{"frame_features": ["flogic:modal_system:S5", "slot:modal_system:s5", "flogic:predicate_alnum_segment_positioned:3:shall", "slot:predicate_alnum_segment_positioned:3_shall", "family:frame:3", "flogic:condition_alnum_segment_positioned:18:the", "flogic:condition_alnum_segment_suffix:the"], "hint_id": "modal-synthesis-a25f361498ba0384", "priority": 0.56599590942, "sample_id": "us-code-8-1188-42be8ee149ed016a"}`
- `program-0fb024f942dc5ce9`
  action: `audit_frame_logic_terms`
  role: `program_synthesis`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-5ef7fd6482a162f1` score `0.959714`
  loss: `autoencoder_residual_cluster` = `0.55969411698`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  samples: `us-code-15-694-1-19bbe1ebb1be0815, us-code-47-906.-6879796231f40903, us-code-17-410-0758ab00b97b8f33, us-code-16-691c-14e7b6e3ed33e5e0`
  evidence: `{"frame_features": ["flogic:condition_alnum_segment:by", "flogic:condition_alnum_segment_positioned:5:the", "flogic:condition_scope_alnum_segment:by", "flogic:condition_scope_alnum_segment_positioned:4:the", "flogic:condition_scope_alnum_segment_positioned:5:secretary", "flogic:condition_scope_token:by", "flogic:condition_token:by"], "hint_id": "modal-synthesis-161256fb12c76a3a", "priority": 0.419654166452, "sample_id": "us-code-16-691c-14e7b6e3ed33e5e0"}`
  evidence: `{"frame_features": ["flogic:condition_alnum_segment:an", "flogic:condition_alnum_segment:of", "flogic:condition_alnum_segment:secretary", "flogic:condition_alnum_segment:the", "flogic:condition_alnum_segment:to", "flogic:condition_alnum_segment:upon", "flogic:condition_alnum_segment_count:18", "flogic:condition_alnum_segment_kind:alpha"], "hint_id": "modal-synthesis-5d26296752e3fa14", "priority": 0.512608551279, "sample_id": "us-code-47-906.-6879796231f40903"}`
  evidence: `{"frame_features": ["slot:frame_candidate_ranked:2_criminal_penalty_enforcement", "slot:frame_candidate_ranked:3_housing_voucher_benefits", "family:selected_frame:frame"], "hint_id": "modal-synthesis-68aaff9cb64000b5", "priority": 0.491833360538, "sample_id": "us-code-17-410-0758ab00b97b8f33"}`
  evidence: `{"frame_features": ["flogic:citation_section_number_has_zero_digit:false", "flogic:citation_section_number_parity:even", "flogic:citation_section_number_parity_positioned:1:even", "flogic:citation_section_number_zero_digit_count:0", "flogic:citation_section_primary_number_parity:even", "flogic:citation_section_terminal_number_has_zero_digit:false", "flogic:citation_section_terminal_number_zero_digit_count:0", "flogic:source_id_section_number_has_zero_digit:false"], "hint_id": "modal-synthesis-a4ac173b4d500c77", "priority": 0.814680389649, "sample_id": "us-code-15-694-1-19bbe1ebb1be0815"}`
