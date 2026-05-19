Implemented a targeted compiler-ambiguity hardening for adaptive family-pair policy coverage.

- Updated [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000029-20260519_102309/ipfs_datasets_py/logic/modal/compiler.py:1035) so `_ordered_adaptive_target_families(...)` always includes priority policy targets, even if the incoming signal map is sparse.
- Added regression coverage in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000029-20260519_102309/tests/unit_tests/logic/modal/test_modal_codec.py:11448) to ensure priority targets are still surfaced when only minimal signal keys are present.

Validation run:

- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "orders_priority_adaptive_targets_before_non_priority_targets or includes_priority_adaptive_targets_even_when_signal_map_is_sparse or recurrent_policy_pairs or compiled_primary_policy_pairs_cover_compiler_ambiguity_bundle"` → `4 passed`
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` → `13 passed`
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py -k "compiled_primary_policy and (frame_to_conditional or temporal_to_deontic or temporal_to_frame or conditional_to_deontic or conditional_to_temporal)"` → `5 passed`