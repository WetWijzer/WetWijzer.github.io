Implemented a targeted modal-ambiguity hardening change and added coverage for the packet’s family-pair bundles.

**Code changes**
- Updated self-pair adaptive ambiguity handling in [ipfs_datasets_py/logic/modal/compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000027-20260519_100901/ipfs_datasets_py/logic/modal/compiler.py):
  - When evaluating a self-pair (`family->family`), the compiler now also checks whether the runner-up pair is a priority policy pair.
  - This allows zero-margin self-pairs to be marked `outvoted` when tied against a priority competing family.
  - Added `runner_up_is_priority_policy_pair` to ambiguity metadata for auditability.
- Expanded recurrent policy-pair coverage in [tests/unit_tests/logic/modal/test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000027-20260519_100901/tests/unit_tests/logic/modal/test_modal_codec.py):
  - Added `deontic->dynamic` expectations.
  - Added a `temporal` scenario validating `temporal->deontic` and `temporal->temporal`.
- Added a focused regression test in [tests/unit_tests/logic/modal/test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000027-20260519_100901/tests/unit_tests/logic/modal/test_modal_codec.py) for zero-margin `temporal->temporal` with deontic runner-up to ensure explicit `adaptive_temporal_temporal_outvoted_margin_low`.

**Validation**
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py` → `177 passed`
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py -q` → `13 passed`