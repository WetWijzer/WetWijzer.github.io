Implemented the `compiler_ambiguity` policy gap by adding `frame -> conditional_normative` to the signal-free adaptive ambiguity pairs and covering it with tests.

**Changes**
- Added missing signal-free adaptive pair:
  - [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000039-20260518_230154/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:33)
- Updated registry expectations for required bundle pairs and directional target ordering:
  - [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000039-20260518_230154/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:69)
- Added regression test proving compiler emits explicit adaptive ambiguity for signal-free `frame -> conditional_normative`:
  - [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000039-20260518_230154/tests/unit_tests/logic/modal/test_modal_codec.py:2504)

**Validation**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` -> `9 passed`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "frame_conditional_adaptive_ambiguity or frame_deontic_adaptive_ambiguity or frame_temporal_adaptive_ambiguity"` -> `3 passed, 114 deselected`
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py -k "frame_to_conditional_and_temporal_adaptive_pairs"` -> `1 passed, 5 deselected`