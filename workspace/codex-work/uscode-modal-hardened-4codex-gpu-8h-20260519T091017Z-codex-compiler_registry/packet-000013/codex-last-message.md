Implemented a generalized deterministic modal-family cue refinement across registry, compiler ambiguity targeting, and cue weighting/backfill.

**What changed**
- Expanded signal-free adaptive pair coverage for missing directions:
  - `temporal -> epistemic`
  - `frame -> alethic`
  - [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000013-20260519_094048/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py:119)
- Extended compiler-side adaptive signal mapping:
  - `predicted=temporal` now considers epistemic signals
  - `predicted=frame` now considers alethic signals
  - [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000013-20260519_094048/ipfs_datasets_py/logic/modal/compiler.py:1027)
- Refined cue/backfill logic to reduce frame over-dominance and improve competing-family evidence:
  - Added frame competing-scope weight and new triggers for `frame -> alethic/dynamic`
  - Added `temporal -> epistemic` backfill for dense temporal contexts
  - Allowed conditional->dynamic backfill with single conditional cue when dynamic scope phrase is present
  - Included alethic/dynamic in generic-frame debias-context detection
  - Added alethic scope logit boost (scope-only case)
  - [spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000013-20260519_094048/ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py:431)

**Tests updated**
- Registry pair/ordering expectations:
  - [test_modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000013-20260519_094048/tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py:138)
- New codec tests for new backfills:
  - frame->alethic
  - frame->dynamic
  - conditional(single cue)->dynamic
  - temporal(dense)->epistemic
  - [test_spacy_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000013-20260519_094048/tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py:1528)

**Validation run**
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py` → 11 passed
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_spacy_modal_codec.py` → 94 passed
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "orders_priority_adaptive_targets_before_non_priority_targets or caps_repeated_generic_frame_cues or frame_adaptive_ambiguity or temporal_adaptive_ambiguity"` → 16 passed