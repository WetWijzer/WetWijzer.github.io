Implemented a narrow frame-logic audit fix for modal cue stopwords.

**Changes made**
- Updated stopword handling so `modal_cue` values are preserved as frame ontology terms during deterministic audit extraction.
  - [frame_bm25_selector.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000141-20260518_201007/ipfs_datasets_py/optimizers/logic_theorem_optimizer/frame_bm25_selector.py#L1390)

- Added regression tests proving `modal_cue:by` is retained for both feature-key and triple paths.
  - [test_frame_bm25_selector.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000141-20260518_201007/tests/unit/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py#L262)
  - [test_frame_bm25_selector.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000141-20260518_201007/tests/unit/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py#L916)

- Extended codec audit regression to assert `flogic:modal_cue:by` appears in computed frame audit terms.
  - [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000141-20260518_201007/tests/unit_tests/logic/modal/test_modal_codec.py#L5340)

**Tests run**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py -k "modal_cue_stopwords or support_plain_contextual_flogic_predicates"` (passed)
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "test_frame_ontology_audit_terms_contextualize_low_signal_frame_features"` (passed)
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py` (77 passed)