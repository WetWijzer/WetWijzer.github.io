Implemented the ambiguity-policy gap for `modal.compiler.ambiguity` by extending the signal-free adaptive pair set to include `temporal -> conditional_normative`.

Changes made:
- Added the missing pair in [`compiler.py:700`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000077-20260518_192053/ipfs_datasets_py/logic/modal/compiler.py:700) so adaptive ambiguity is surfaced even without lexical target signals for that pair.
- Added regression coverage in [`test_modal_codec.py:1979`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000077-20260518_192053/tests/unit_tests/logic/modal/test_modal_codec.py:1979) via `test_modal_compiler_uses_signal_free_pair_policy_for_temporal_conditional_adaptive_ambiguity`.

Validation run:
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "signal_free_pair_policy_for_temporal_deontic_adaptive_ambiguity or signal_free_pair_policy_for_temporal_conditional_adaptive_ambiguity or signal_free_pair_policy_for_deontic_conditional_adaptive_ambiguity"`
- Result: `3 passed, 99 deselected`