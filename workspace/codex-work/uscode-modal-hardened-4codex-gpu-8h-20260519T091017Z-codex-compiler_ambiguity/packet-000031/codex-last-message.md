Implemented a narrow compiler-ambiguity hardening for the requested low-margin modal family pairs, plus focused regression tests.

**Changes**
- Added a canonical required-pair set for compiler ambiguity policy and injected it into both signal-free and priority adaptive policy tables (dedup still preserves stable ordering):
  - [modal_registry.py:33](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000031-20260519_103627/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:33)
  - [modal_registry.py:193](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000031-20260519_103627/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:193)
  - [modal_registry.py:302](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000031-20260519_103627/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:302)
  - Exported constant in [modal_registry.py:692](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000031-20260519_103627/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:692)

- Added registry test that asserts every compiler-required pair is covered by both policy layers:
  - [test_modal_registry.py:168](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000031-20260519_103627/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:168)

- Added two compiler-level adaptive ambiguity tests:
  - Signal-free `conditional_normative -> temporal` low-margin explicit ambiguity: [test_modal_codec.py:2466](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000031-20260519_103627/tests/unit_tests/logic/modal/test_modal_codec.py:2466)
  - Positive low-margin `deontic -> deontic` contested explicit ambiguity: [test_modal_codec.py:2565](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000031-20260519_103627/tests/unit_tests/logic/modal/test_modal_codec.py:2565)

**Validation**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` (14 passed)
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "conditional_temporal_adaptive or contested_deontic_self_adaptive or signal_free_pair_policy_for_temporal_deontic_adaptive_ambiguity"` (4 passed)
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "adaptive"` (73 passed)