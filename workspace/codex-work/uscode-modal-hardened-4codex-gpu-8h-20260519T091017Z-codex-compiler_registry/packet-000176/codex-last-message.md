Implemented a deterministic cue-weight refinement focused on the three confusion paths (`deontic→dynamic`, `deontic→temporal`, `frame→deontic`) in the modal codec weighting/boost pipeline.

**Changes made**
- Updated competition/backfill constants and thresholds to surface stronger competing evidence in deontic-heavy clauses:
  - [`spacy_modal_codec.py:495`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000176-20260519_140612/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:495)
  - [`spacy_modal_codec.py:510`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000176-20260519_140612/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:510)
  - [`spacy_modal_codec.py:541`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000176-20260519_140612/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:541)
- Tightened deontic soft-cap behavior when strong temporal/dynamic competition is present:
  - [`spacy_modal_codec.py:1430`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000176-20260519_140612/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:1430)
- Strengthened temporal/dynamic competing-family backfill under dense deontic context:
  - [`spacy_modal_codec.py:2008`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000176-20260519_140612/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:2008)
  - [`spacy_modal_codec.py:2123`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000176-20260519_140612/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:2123)
- Reduced statutory frame backfill aggressiveness when explicit deontic cue is present (to avoid over-favoring frame in `frame→deontic` conflicts):
  - [`spacy_modal_codec.py:2365`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000176-20260519_140612/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:2365)
- Added deontic-aware temporal/dynamic logit boosts for scope-only evidence:
  - [`spacy_modal_codec.py:2463`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000176-20260519_140612/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:2463)

**Tests added**
- New focused tests for strengthened deontic competition handling:
  - [`test_spacy_modal_codec.py:1268`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000176-20260519_140612/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:1268)
  - [`test_spacy_modal_codec.py:1299`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000176-20260519_140612/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:1299)
  - [`test_spacy_modal_codec.py:1904`](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000176-20260519_140612/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:1904)

**Validation run**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py`  
  - Passed: `123 passed`
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "deontic_dynamic or deontic_temporal or frame_deontic or dynamic_scope_family_outvoted or temporal_scope_family_outvoted or frame_scope_family_outvoted"`  
  - Passed: `9 passed`
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py`  
  - 1 failure in existing expectation: `test_priority_signal_free_adaptive_targets_are_ordered_directional_subsets` (registry file unchanged in this packet).