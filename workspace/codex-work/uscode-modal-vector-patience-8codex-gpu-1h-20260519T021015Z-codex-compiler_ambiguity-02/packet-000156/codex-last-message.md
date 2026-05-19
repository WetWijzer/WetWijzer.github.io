Implemented a `compiler_ambiguity` policy fix to always preserve declared directional adaptive pair coverage when compiled family and ranked family differ.

- Updated [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000156-20260519_023649/ipfs_datasets_py/logic/modal/compiler.py#L805): replaced hardcoded `compiled_primary_targets` branches with registry-driven `signal_free_adaptive_ambiguity_targets(compiled_primary_family)` (excluding self-pairs). This closes gaps like `conditional_normative->temporal` and `temporal->frame` in compiled-primary fallback handling.
- Added regressions in [test_legal_modal_parser_deterministic_rules.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000156-20260519_023649/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py#L474):
  - `test_compiler_preserves_temporal_to_frame_pair_from_compiled_primary_policy`
  - `test_compiler_preserves_conditional_to_temporal_pair_from_compiled_primary_policy`

Validation run:

1. `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py -k 'compiled_primary_policy'` (5 passed)
2. `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k 'compiled_primary or conditional_temporal or temporal_frame or frame_conditional_normative or conditional_normative_deontic'` (6 passed)