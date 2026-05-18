Implemented a narrow frame-logic audit improvement centered on TODO evidence like `flogic:condition_alnum_segment:if/of/the`.

**Changes**
- Updated [frame_bm25_selector.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000078-20260518_193116/ipfs_datasets_py/optimizers/logic_theorem_optimizer/frame_bm25_selector.py:476) so ontology-term normalization can selectively keep stopword tokens for condition/exception alnum-segment predicates in raw audit terms.
- Added predicate/feature guards for this behavior in [frame_bm25_selector.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000078-20260518_193116/ipfs_datasets_py/optimizers/logic_theorem_optimizer/frame_bm25_selector.py:1337).
- Kept high-signal summaries clean by filtering pure stopword terms (`of`, `the`, etc.) in [frame_bm25_selector.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000078-20260518_193116/ipfs_datasets_py/optimizers/logic_theorem_optimizer/frame_bm25_selector.py:757).
- Added regression tests in:
  - [tests/unit/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000078-20260518_193116/tests/unit/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py:326)
  - [ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000078-20260518_193116/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py:277)

**Tests**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py` (73 passed)
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py` (19 passed)
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "frame_ontology_audit or structured_hint_evidence"` (7 passed)
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_flogic_optimizer.py -k "high_signal_frame_ontology_terms or extracts_frame_features_from_structured_hint_evidence"` (2 passed)