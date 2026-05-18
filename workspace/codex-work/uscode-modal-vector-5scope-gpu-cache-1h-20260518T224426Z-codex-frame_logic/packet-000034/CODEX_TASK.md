# packet-000034

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/packet-000034/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/packet-000034/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000034-20260518_231201

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/optimizers/logic/flogic_optimizer.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/frame_bm25_selector.py`

## TODOs
- `program-e12cef72b53d3a4d` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-e12cef72b53d3a4d` score `1.0`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"hint_id": "modal-synthesis-60ba2b683b4df66f", "priority": 0.673734404385, "sample_id": "us-code-50-2656.-10e19e6cd88e6b96"}`
  evidence: `{"frame_features": ["flogic:citation_title_section_terminal_number_span_leading_digit:1", "flogic:source_id_title_section_terminal_number_span_leading_digit:1", "slot:citation_title_section_terminal_number_span_leading_digit:1", "slot:source_id_title_section_terminal_number_span_leading_digit:1", "flogic:citation_section_number_leading_digit:1", "flogic:citation_section_number_leading_digit_positioned:1:1", "flogic:citation_section_primary_number_leading_digit:1", "flogic:citation_section_terminal_number_leading_digit:1"], "hint_id": "modal-synthesis-85f0326e9d4398f1", "priority": 0.718942559026, "sample_id": "us-code-19-135-0ca7d371ef06381b"}`
  evidence: `{"frame_features": ["flogic:citation_section_number_has_zero_digit_positioned:1:false", "flogic:citation_section_number_zero_digit_count_positioned:1:0", "flogic:citation_section_primary_number_has_zero_digit:false", "flogic:citation_section_primary_number_zero_digit_count:0"], "hint_id": "modal-synthesis-b5fbbc2b6d6dd1ef", "priority": 0.733245036245, "sample_id": "us-code-46-7113.-352a3c716bd8efb0"}`
  evidence: `{"frame_features": ["flogic:citation_title_number_leading_digit:2", "flogic:source_id_title_number_leading_digit:2", "slot:citation_title_number_leading_digit:2", "slot:source_id_title_number_leading_digit:2", "flogic:citation_title_section_primary_number_distance_profile_alnum_segment:1", "flogic:citation_title_section_primary_number_distance_profile_token:1k"], "hint_id": "modal-synthesis-ea9a8b42fd6eca1b", "priority": 0.304714846489, "sample_id": "us-code-2-1511-313ca032e8ac0971"}`
- `program-60ec15eaa0eb9bf0` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-e12cef72b53d3a4d` score `0.985394`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["flogic:citation_section_number_leading_digit:1", "flogic:citation_section_number_leading_digit_positioned:1:1", "flogic:citation_section_primary_number_leading_digit:1", "flogic:citation_section_terminal_number_leading_digit:1", "flogic:citation_title_section_primary_number_span_leading_digit:1", "flogic:source_id_section_number_leading_digit:1", "flogic:source_id_section_number_leading_digit_positioned:1:1", "flogic:source_id_section_primary_number_leading_digit:1"], "hint_id": "modal-synthesis-25fba2baf9a4e265", "priority": 0.468189488508, "sample_id": "us-code-29-1751-4fcafe787ea80cb4"}`
  evidence: `{"frame_features": ["flogic:citation_title_number_leading_digit:2", "flogic:source_id_title_number_leading_digit:2", "slot:citation_title_number_leading_digit:2"], "hint_id": "modal-synthesis-3f787a266027a51a", "priority": 0.165101420752, "sample_id": "us-code-29-431-5c5f795ae7ad35f1"}`
  evidence: `{"frame_features": ["flogic:citation_title_number_parity:odd", "flogic:predicate_alnum_segment_positioned:5:section", "flogic:source_id_title_number_parity:odd", "slot:citation_title_number_parity:odd", "slot:predicate_alnum_segment_positioned:5_section", "slot:source_id_title_number_parity:odd"], "hint_id": "modal-synthesis-6b1d31836d828612", "priority": 0.419693942639, "sample_id": "us-code-25-1104-9da8c383bf9a6c33"}`
  evidence: `{"frame_features": ["flogic:predicate_alnum_segment:pub", "flogic:predicate_token:pub", "flogic:predicate_token_suffix:pub"], "hint_id": "modal-synthesis-96e0568a1c96c645", "priority": 0.293965177029, "sample_id": "us-code-6-673-d9b9bb9f63235910"}`
- `program-a8a54c9c3938e205` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-e12cef72b53d3a4d` score `0.977519`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["flogic:citation_section_number_has_zero_digit_positioned:1:false", "flogic:citation_section_number_zero_digit_count_positioned:1:0", "flogic:citation_section_primary_number_has_zero_digit:false", "flogic:citation_section_primary_number_zero_digit_count:0", "flogic:source_id_section_number_has_zero_digit_positioned:1:false", "flogic:source_id_section_number_zero_digit_count_positioned:1:0", "flogic:source_id_section_primary_number_has_zero_digit:false", "flogic:source_id_section_primary_number_zero_digit_count:0"], "hint_id": "modal-synthesis-59188462db85c046", "priority": 0.716733599722, "sample_id": "us-code-42-287d-12048fdb8d950dfc"}`
  evidence: `{"frame_features": ["family:selected_frame:deontic", "flogic:citation_section_component_kind:numeric", "flogic:citation_section_terminal_component_kind:numeric", "flogic:citation_section_terminal_has_suffix:false", "flogic:citation_source_id_section_terminal_suffix_pair:none|none"], "hint_id": "modal-synthesis-5e010a1d8d26b03f", "priority": 0.442962053431, "sample_id": "us-code-18-3171-74abf39e24bc8cfa"}`
  evidence: `{"frame_features": ["flogic:predicate_alnum_segment:order", "flogic:predicate_token:order"], "hint_id": "modal-synthesis-aab81f30ad60d497", "priority": 0.450323073511, "sample_id": "us-code-23-311-2894ae9887b66364"}`
  evidence: `{"frame_features": ["flogic:modal_cue:in accordance with"], "hint_id": "modal-synthesis-de441cbab645f083", "priority": 0.483719181283, "sample_id": "us-code-26-269B-3799f65839ae152e"}`
- `program-159b4a0e5ccfdd0d` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-e12cef72b53d3a4d` score `0.973934`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"frame_features": ["family:selected_frame:temporal", "flogic:citation_title_section_primary_number_span_parity:odd", "flogic:citation_title_section_terminal_number_span_parity:odd"], "hint_id": "modal-synthesis-20f46b0a358555ed", "priority": 0.277878782966, "sample_id": "us-code-10-2685-b40ce2c88f2dda0c"}`
  evidence: `{"frame_features": ["flogic:predicate_alnum_segment:pub", "flogic:predicate_token:pub", "flogic:predicate_token_suffix:pub"], "hint_id": "modal-synthesis-37d94769e14a61af", "priority": 0.443838303878, "sample_id": "us-code-16-1407-47a01906676ff5af"}`
  evidence: `{"frame_features": ["flogic:citation_title_section_primary_number_span_has_zero_digit:false", "flogic:citation_title_section_primary_number_span_zero_digit_count:0", "flogic:citation_title_section_terminal_number_span_has_zero_digit:false", "flogic:citation_title_section_terminal_number_span_zero_digit_count:0", "flogic:source_id_title_section_primary_number_span_has_zero_digit:false", "flogic:source_id_title_section_primary_number_span_zero_digit_count:0", "flogic:source_id_title_section_terminal_number_span_has_zero_digit:false", "flogic:source_id_title_section_terminal_number_span_zero_digit_count:0"], "hint_id": "modal-synthesis-892c4834861480cb", "priority": 0.291750012295, "sample_id": "us-code-46-53723.-c79c0fa010e0afe2"}`
  evidence: `{"hint_id": "modal-synthesis-e936e6657d564260", "priority": 0.244936127654, "sample_id": "us-code-46-53513.-4951b7ed362e76de"}`
- `program-7778bde4754e7672` `audit_frame_logic_terms`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-e12cef72b53d3a4d` score `0.973474`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  support: 4
  evidence: `{"hint_id": "modal-synthesis-22fc37bc85930ab2", "priority": 0.596486911761, "sample_id": "us-code-33-4218-6fe7606f408cbe9b"}`
  evidence: `{"frame_features": ["flogic:citation_section_number_has_zero_digit_positioned:1:false", "flogic:citation_section_number_zero_digit_count_positioned:1:0", "flogic:citation_section_primary_number_has_zero_digit:false", "flogic:citation_section_primary_number_zero_digit_count:0"], "hint_id": "modal-synthesis-4d0da0ca92d672b9", "priority": 0.107091369284, "sample_id": "us-code-42-5676.-866d984f96b6f7dd"}`
  evidence: `{"frame_features": ["flogic:citation_section_number_magnitude_bucket:lt_1k", "flogic:citation_section_number_magnitude_bucket_positioned:1:lt_1k", "flogic:citation_section_number_thousands_block:0", "flogic:citation_section_number_thousands_block_positioned:1:0", "flogic:citation_section_primary_number_magnitude_bucket:lt_1k", "flogic:citation_section_primary_number_thousands_block:0", "flogic:citation_section_terminal_number_magnitude_bucket:lt_1k", "flogic:citation_section_terminal_number_thousands_block:0"], "hint_id": "modal-synthesis-a81681c515fd25b4", "priority": 0.381281195043, "sample_id": "us-code-20-79-ba208672775d506a"}`
  evidence: `{"frame_features": ["flogic:citation_section_number_parity:odd", "flogic:citation_section_number_parity_positioned:1:odd", "flogic:citation_section_primary_number_parity:odd", "flogic:citation_section_terminal_number_parity:odd"], "hint_id": "modal-synthesis-e0875d03205d07e4", "priority": 0.373429873822, "sample_id": "us-code-24-131a-1127fb38290a8f23"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
