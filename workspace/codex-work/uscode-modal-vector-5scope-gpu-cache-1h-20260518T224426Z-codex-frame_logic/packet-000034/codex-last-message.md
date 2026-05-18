Implemented a deterministic `modal.frame_logic` audit-term improvement: frame-linked numeric/profile features now retain predicate context more consistently (instead of collapsing to generic terms like `pub`/`lt_1k`).

- Updated contextualization policy in [frame_bm25_selector.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000034-20260518_231201/ipfs_datasets_py/optimizers/logic_theorem_optimizer/frame_bm25_selector.py:331) by extending `_FRAME_ONTOLOGY_CONTEXTUAL_ALWAYS_PREDICATE_FRAGMENTS` with:
  - `_magnitude_bucket`
  - `_thousands_block`
  - `predicate_alnum_segment`
  - `predicate_token`
- Added focused selector coverage in [test_frame_bm25_selector.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000034-20260518_231201/tests/unit/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py:1016) to assert contextual terms like:
  - `predicate_token_pub`
  - `predicate_alnum_segment_pub`
  - `citation_section_number_magnitude_bucket_lt_1k`
- Extended modal codec audit test in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000034-20260518_231201/tests/unit_tests/logic/modal/test_modal_codec.py:6303) to verify these contextualized terms flow through `_frame_ontology_audit_terms`.

Validation run:

1. `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py -k "contextualize_distance_profile or contextualize_predicate_token_and_magnitude_bucket"` (2 passed)
2. `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "test_frame_ontology_audit_terms_contextualize_low_signal_frame_features"` (1 passed)
3. `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_flogic_optimizer.py` (18 passed)