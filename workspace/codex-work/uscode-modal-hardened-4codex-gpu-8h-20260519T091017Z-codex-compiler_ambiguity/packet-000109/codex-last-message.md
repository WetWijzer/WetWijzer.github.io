Implemented the compiler ambiguity policy hardening for this packet by promoting `deontic->dynamic` into the compiler-required bundle and extending regression coverage for the requested pair set.

Changes made:
- Added `("deontic", "dynamic")` to compiler-required adaptive ambiguity pairs in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000109-20260519_111904/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:33).
- Updated required-bundle registry assertions and deontic target ordering in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000109-20260519_111904/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:188).
- Added explicit required-margin scenarios for:
  - `deontic->conditional_normative` (`family_margin=-0.231207676845`, `adaptive_priority=0.381207676845`)
  - `deontic->dynamic` (`family_margin=-0.431079117926`, `adaptive_priority=0.581079117926`)
  in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000109-20260519_111904/tests/unit_tests/logic/modal/test_modal_codec.py:12131).

Validation run:
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` (15 passed)
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "required_margin_bundle_pairs or signal_free_pair_policy_for_deontic_dynamic or signal_free_pair_policy_for_deontic_conditional or signal_free_pair_policy_for_frame_deontic"` (4 passed)