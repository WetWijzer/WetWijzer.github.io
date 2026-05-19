Implemented a compiler-ambiguity policy expansion for the required modal family pairs, and updated focused tests.

**Changes**
- Added missing compiler-required adaptive ambiguity pairs in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000034-20260519_105718/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:33):
  - `frame->conditional_normative`
  - `frame->temporal`
  - `temporal->conditional_normative`
- Updated compiler-required registry assertions in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000034-20260519_105718/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:188) to match expanded policy targets and pair checks.
- Expanded required-bundle compiler ambiguity test scenarios (including the new pair families and explicit types) in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000034-20260519_105718/tests/unit_tests/logic/modal/test_modal_codec.py:12043).

**Validation**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` passed (`15 passed`).
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "required_margin_bundle_pairs"` passed (`1 passed`).
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "compiled_primary_policy_pairs_cover_compiler_ambiguity_bundle"` passed (`1 passed`).