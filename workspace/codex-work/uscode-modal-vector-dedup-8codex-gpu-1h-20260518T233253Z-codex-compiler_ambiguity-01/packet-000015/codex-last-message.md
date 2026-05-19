Implemented a narrow compiler-ambiguity policy hardening for the `deontic <-> frame` pair.

**Changes**
- Added `deontic -> frame` to priority adaptive ambiguity pairs so zero-margin conflicts are explicitly treated as outvoted/requires-rule, matching `frame -> deontic`.
  - [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000015-20260518_235143/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py):112
- Added regression test for zero-margin `frame -> deontic` priority behavior.
  - [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000015-20260518_235143/tests/unit_tests/logic/modal/test_modal_codec.py):2504
- Added regression test for zero-margin `deontic -> frame` priority behavior (this is the new bidirectional gap coverage).
  - [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000015-20260518_235143/tests/unit_tests/logic/modal/test_modal_codec.py):3684

**Validation**
- Ran:
  - `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "zero_margin_frame_deontic_priority_pair or zero_margin_deontic_frame_priority_pair or signal_free_pair_policy_for_frame_deontic_adaptive_ambiguity or signal_free_pair_policy_for_deontic_frame_adaptive_ambiguity"`
  - `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "zero_margin and priority_pair_as_outvoted_adaptive_ambiguity"`
  - `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "deontic_frame_adaptive_ambiguity or frame_deontic_adaptive_ambiguity"`
- Result: all selected tests passed.