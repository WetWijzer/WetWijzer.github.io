Implemented a deterministic cue-weighting refinement for modal family ranking focused on `frame/temporal -> deontic` misclassifications.

Changed files:
- [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000020-20260518_234129/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py)
- [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000020-20260518_234129/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py)

What changed:
- Expanded generic frame cue set to include `administered by`.
- Strengthened generic frame debiasing by compressing repeated generic frame cue counts with `log1p(...)` before applying the debias factor.
- Allowed generic frame debias trigger when `has_deontic_scope` is present (not only direct deontic cue).
- Added a new temporal debias path for sequence-only temporal cues (`after`, `before`, `following`, `next`) when deontic force is present and strong temporal anchors are absent (no calendar date, no temporal scope phrase, no temporal `within` scope).
- Kept existing deontic soft-cap behavior for heavy repeated deontic cues.

Added regressions:
- Repeated generic frame cues no longer outvote deontic.
- Sequence-only temporal cues no longer outvote deontic in ranking.
- Sequence-only temporal cues no longer outvote deontic in decoder logits.

Validation run:
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py` → `46 passed`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py` → `126 passed`
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` → `9 passed`