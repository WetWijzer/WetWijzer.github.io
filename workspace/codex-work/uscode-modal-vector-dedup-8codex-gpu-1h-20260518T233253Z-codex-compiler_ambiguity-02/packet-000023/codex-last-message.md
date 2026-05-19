Implemented a narrow `modal.compiler.ambiguity` policy update for adaptive-family ambiguity handling:

1. Promoted `deontic -> epistemic` to **priority** signal-free adaptive ambiguity policy in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000023-20260518_235759/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py).  
2. Updated priority-directionality assertions in [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000023-20260518_235759/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py).  
3. Added regression coverage for zero-margin `deontic/epistemic` behavior in [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000023-20260518_235759/tests/unit_tests/logic/modal/test_modal_codec.py), ensuring explicit `adaptive_deontic_epistemic_outvoted_margin_low` emission and `requires_rule` severity when margin is zero.

Validation run (focused):
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` ✅
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "deontic_epistemic and adaptive"` ✅
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "frame_deontic or frame_temporal or deontic_epistemic"` ✅