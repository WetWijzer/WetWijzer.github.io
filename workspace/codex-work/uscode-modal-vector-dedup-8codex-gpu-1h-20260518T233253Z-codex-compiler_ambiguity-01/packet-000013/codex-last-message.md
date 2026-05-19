Implemented a narrow `compiler_ambiguity` policy extension so frame-family low-margin self-cases emit explicit adaptive ambiguity.

- Added `("frame", "frame")` to signal-free adaptive ambiguity policy in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000013-20260518_233849/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:98).
- Updated registry policy tests to cover `frame->frame` support and ordering in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000013-20260518_233849/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:69).
- Added compiler regression for low-runner-up `frame` self-pair explicit ambiguity (`adaptive_frame_frame_contested_margin_low`) in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000013-20260518_233849/tests/unit_tests/logic/modal/test_modal_codec.py:3288).

Validation run:

- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` (9 passed)
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "temporal_self_pair or frame_self_pair"` (2 passed, 124 deselected)
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py` (9 passed)