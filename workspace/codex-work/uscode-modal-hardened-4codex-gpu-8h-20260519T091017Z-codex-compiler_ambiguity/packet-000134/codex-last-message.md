Implemented the `compiler_ambiguity` policy update and kept it deterministic.

- Added missing compiler-required adaptive ambiguity pairs in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000134-20260519_114315/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py):
  - `alethic->deontic`
  - `frame->alethic`
- Updated policy/ordering assertions in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000134-20260519_114315/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py) to reflect the expanded required bundle and derived priority targets.
- Expanded ambiguity-coverage tests in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000134-20260519_114315/tests/unit_tests/logic/modal/test_modal_codec.py) so explicit ambiguity emission now explicitly covers:
  - recurrent pair `frame->alethic`
  - compiled-primary scenarios for `frame->alethic` and `alethic->deontic`
  - required-margin bundle scenarios for `frame->alethic` and `alethic->deontic`
  - updated priority target ordering for `frame` to include `alethic`

Validation run:

- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` -> `15 passed`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "orders_priority_adaptive_targets_before_non_priority_targets or emits_explicit_adaptive_ambiguity_for_recurrent_policy_pairs or compiled_primary_policy_pairs_cover_compiler_ambiguity_bundle or emits_explicit_ambiguity_for_required_margin_bundle_pairs"` -> `4 passed`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "priority_adaptive_targets"` -> `2 passed`