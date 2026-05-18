Implemented the `refine_modal_family_cue_rules` packet with deterministic cue/signal updates for the target family pairs (`deontic->conditional_normative`, `temporal->deontic`, `temporal->frame`).

**Code changes**
1. Expanded conditional-normative cue terms for “terms and conditions” constructions in the registry:
- [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000113-20260518_195918/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:248)

2. Added contextual gating for temporal `within` so it only fires in time-like contexts (e.g., `within 30 days`) and not organizational/statutory contexts (e.g., `within the Department`):
- new temporal/non-temporal context rules: [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000113-20260518_195918/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:225)
- cue extraction use of the new `within` gate: [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000113-20260518_195918/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:534)
- shared helper used by cue extraction and signals: [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000113-20260518_195918/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:922)

3. Updated ambiguity signal logic to apply the same `within` context rule and emit `has_temporal_within_scope`:
- [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000113-20260518_195918/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:1045)

**Tests added/updated**
- Registry cue coverage test: [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000113-20260518_195918/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:43)
- spaCy cue/signal tests for `within` disambiguation and terms-and-conditions cue: [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000113-20260518_195918/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:292)
- Compiler ambiguity regression for conditional target share > 0 from terms-and-conditions cue: [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000113-20260518_195918/tests/unit_tests/logic/modal/test_modal_codec.py:2810)

**Validation run**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` -> 8 passed
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py` -> 34 passed
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py` -> 108 passed