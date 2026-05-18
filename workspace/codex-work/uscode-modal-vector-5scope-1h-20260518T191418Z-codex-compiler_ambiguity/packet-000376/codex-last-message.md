Implemented a narrow compiler-ambiguity improvement for the `hybrid -> frame` adaptive policy by preserving raw margin/share values while keeping existing rounded fields stable.

**What changed**
- Added share extraction helper and used it consistently in family ranking math so fallback rankings can use unrounded values when available: [compiler.py:265](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000376-20260518_202053/ipfs_datasets_py/logic/modal/compiler.py#L265)
- Fallback adaptive ranking now emits both `share_raw` and rounded `share`: [compiler.py:560](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000376-20260518_202053/ipfs_datasets_py/logic/modal/compiler.py#L560)
- Adaptive ambiguity metadata now includes:
  - `family_margin_raw`
  - `predicted_share_raw`
  - `target_share_raw`
  while preserving legacy rounded `family_margin`/`predicted_share`/`target_share`: [compiler.py:595](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000376-20260518_202053/ipfs_datasets_py/logic/modal/compiler.py#L595)

**Test update**
- Added regression assertions for raw hybrid/frame fallback margin precision and raw-vs-rounded consistency: [test_modal_codec.py:2435](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000376-20260518_202053/tests/unit_tests/logic/modal/test_modal_codec.py#L2435)

**Validation run**
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "logit_fallback_ranking_for_hybrid_frame_adaptive_ambiguity or signal_free_pair_policy_for_hybrid_frame or zero_margin_hybrid_frame_priority_pair"` → 3 passed
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "adaptive and (signal_free or fallback or hybrid_frame or temporal_frame or deontic_temporal)"` → 10 passed
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` → 9 passed