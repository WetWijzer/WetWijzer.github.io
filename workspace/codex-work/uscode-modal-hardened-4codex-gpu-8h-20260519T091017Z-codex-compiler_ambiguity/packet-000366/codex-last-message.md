Implemented a focused `compiler_ambiguity` policy hardening for the missing family transition.

- Added `hybrid->frame` to the compiler ambiguity bundle in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000366-20260519_142642/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:182).
- Updated registry bundle expectations and helper assertion in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000366-20260519_142642/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:270).
- Strengthened hybrid/frame adaptive ambiguity test to require compiler-bundle metadata in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000366-20260519_142642/tests/unit_tests/logic/modal/test_modal_codec.py:4254).

Validation run:

- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py -k "compiler_ambiguity_policy_pair_helper"` passed.
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "signal_free_pair_policy_for_hybrid_frame_adaptive_ambiguity"` passed.