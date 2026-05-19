Implemented a targeted `compiler_registry` family-cue refinement that covers the requested pair patterns.

**Changes**
- Added `epistemic -> epistemic` signal-free adaptive policy support in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000024-20260519_001420/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py).
- Added frame→epistemic lexical-signal mapping in [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000024-20260519_001420/ipfs_datasets_py/logic/modal/compiler.py) so epistemic cues are treated as explicit evidence (not only signal-free fallback).
- Refined deterministic cue weighting in [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000024-20260519_001420/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py):
  - Generic frame debias now also triggers when epistemic cues are present.
  - Added dynamic scope-based logit boosts (guarded to avoid frame-editorial contexts).

**Tests updated**
- [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000024-20260519_001420/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py)
- [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000024-20260519_001420/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py)
- [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000024-20260519_001420/tests/unit_tests/logic/modal/test_modal_codec.py)

**Executed tests**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` → `10 passed`
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py -k "debiases_generic_frame_logits_when_epistemic_cues_are_present or boosts_dynamic_logits_from_scope_without_dynamic_cues"` → `2 passed`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "frame_epistemic_adaptive_ambiguity or epistemic_self_pair_adaptive_ambiguity"` → `3 passed`