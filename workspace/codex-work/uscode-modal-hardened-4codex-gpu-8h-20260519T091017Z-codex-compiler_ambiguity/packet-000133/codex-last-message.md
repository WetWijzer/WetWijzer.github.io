Implemented the ambiguity-policy update for this packet.

**Changes**
- Added `epistemic -> epistemic` to the compiler-required adaptive ambiguity pair table in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000133-20260519_113816/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:67).
- Added a regression test that forces a low-margin epistemic self-pair from adaptive logits and asserts explicit ambiguity emission is marked as compiler-required policy in [test_legal_modal_parser_deterministic_rules.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000133-20260519_113816/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py:858).

**Validation**
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py -k "deontic_to_frame_and_temporal or deontic_self or frame_to_conditional or epistemic_self_policy"` passed (`4 passed`).
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py` passed (`26 passed`).