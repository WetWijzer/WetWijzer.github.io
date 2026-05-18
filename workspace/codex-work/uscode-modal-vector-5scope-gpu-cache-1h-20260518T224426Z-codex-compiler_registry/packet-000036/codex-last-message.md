Implemented a narrow deterministic cue-rule refinement to reduce `frame -> deontic` misclassification when frame evidence is only generic (`authority` / `jurisdiction`) and explicit deontic force is present.

- Updated [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000036-20260518_224737/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:361):
  - Added generic frame cue constants and a de-bias gate.
  - Added weighted family counting for ranking (`ranked_modal_families`) so generic frame cues are downweighted in deontic contexts.
  - Updated `SpaCyModalDecoder.family_logits` to use weighted counts and suppress frame bonus in that same de-bias context.
  - Added helper functions for deterministic gating and weighting.

- Added regression coverage in [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000036-20260518_224737/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:388):
  - Verifies deontic outranks frame for generic frame cues + deontic force.
  - Verifies deontic logit is above frame logit for that pattern.

Tests run (all passed):

- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py`