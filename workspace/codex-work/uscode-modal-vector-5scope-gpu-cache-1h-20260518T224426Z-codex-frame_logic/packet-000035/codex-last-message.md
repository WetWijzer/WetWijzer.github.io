Implemented a narrow frame-logic audit improvement for family-count signals.

- Updated [frame_bm25_selector.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000035-20260518_231627/ipfs_datasets_py/optimizers/logic_theorem_optimizer/frame_bm25_selector.py:1176):
  - `modal_family_count` and `modal_family_count_ranked` now retain `family:count` in normalized raw values (for contextual audit generation).
  - Added explicit contextualization trigger for `modal_family_count` and `modal_family_count_ranked` predicates.
- Updated [flogic_optimizer.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000035-20260518_231627/ipfs_datasets_py/logic/flogic_optimizer.py:361):
  - `frame_ontology_terms` metadata now merges contextualized terms with feature/triple terms, so these audited family-count terms are not dropped.
- Added regression tests:
  - [tests/unit/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000035-20260518_231627/tests/unit/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py:773)
  - [ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000035-20260518_231627/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py:423)
  - [tests/unit/logic/test_flogic_integration.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-frame_logic/worktrees/agent-codex-frame_logic-packet-000035-20260518_231627/tests/unit/logic/test_flogic_integration.py:459)

Validation run:

- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py -q` -> `81 passed`
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_frame_bm25_selector.py -q` -> `23 passed`
- `pytest -q tests/unit/logic/test_flogic_integration.py -q` -> `41 passed`