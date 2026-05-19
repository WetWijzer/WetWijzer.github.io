Implemented a narrow compiler-ambiguity policy improvement for conditional-family adaptive conflicts.

- Updated conditional-family adaptive target signal mapping to treat `temporal` and `frame` as signal-backed targets (not only signal-free fallback):  
[compiler.py:901](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000050-20260519_022533/ipfs_datasets_py/logic/modal/compiler.py:901)

- Added regression tests to verify conditional→temporal and conditional→frame ambiguities mark `has_target_signal_evidence=True` and `signal_free_pair_policy_applied=False` when signals exist:  
[test_modal_codec.py:3294](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000050-20260519_022533/tests/unit_tests/logic/modal/test_modal_codec.py:3294)  
[test_modal_codec.py:3643](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000050-20260519_022533/tests/unit_tests/logic/modal/test_modal_codec.py:3643)

Validation run:

1. `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "conditional_temporal_adaptive_ambiguity or conditional_frame_adaptive_ambiguity"`  
Passed (`4 passed`).

2. `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py`  
Passed (`10 passed`).