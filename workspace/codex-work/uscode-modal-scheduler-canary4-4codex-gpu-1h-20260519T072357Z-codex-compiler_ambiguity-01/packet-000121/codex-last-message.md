Implemented a focused compiler ambiguity-policy fix for compiled-primary adaptive margins.

**What changed**
- Updated compiled-primary adaptive ambiguity logic to treat zero-margin self cases as priority when the *runner-up directional pair* is priority, not only when `family->family` is priority.
- Added explicit runner-up policy metadata for traceability.

Code changes:
- [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000121-20260519_082338/ipfs_datasets_py/logic/modal/compiler.py:1082)
- [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000121-20260519_082338/ipfs_datasets_py/logic/modal/compiler.py:1242)

New metadata fields emitted in compiled-primary adaptive ambiguities:
- `adaptive_runner_up_policy_pair`
- `runner_up_is_priority_policy_pair`

**Regression coverage added**
- Added a targeted test covering zero-margin compiled-primary self-pair scenarios where runner-up pairs are priority:
  - `frame->deontic`
  - `frame->conditional_normative`
  - `temporal->deontic`

Test added:
- [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000121-20260519_082338/tests/unit_tests/logic/modal/test_modal_codec.py:2388)

**Validation run**
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "compiled_primary_self_pair or compiled_primary_deontic_self_pair or runner_up_priority_pair"` → 3 passed
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "zero_margin and (frame or temporal or deontic or conditional) and adaptive_ambiguity"` → 11 passed
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py -k "priority_signal_free_adaptive_targets_are_ordered_directional_subsets or priority_signal_free_adaptive_ambiguity_pair_policy_is_directional"` → 2 passed