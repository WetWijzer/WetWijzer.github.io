Implemented a scoped IR/decompiler refinement for provenance number alignment: citation/source-id numeric signatures are now explicitly compared (pair/match/presence) for title, section primary, and section terminal numbers.

- Added deterministic numeric-signature alignment emission in decompiler slot generation:
  - [_PROVENANCE_NUMERIC_ALIGNMENT_SIGNATURES + helpers in decompiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000034-20260518_230743/ipfs_datasets_py/logic/modal/decompiler.py:161)
  - Integrated into provenance alignment flow for title/primary/terminal number comparisons:
    - [decompiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000034-20260518_230743/ipfs_datasets_py/logic/modal/decompiler.py:1819)

- Mirrored the same logic for F-logic triple projection:
  - [_PROVENANCE_NUMERIC_ALIGNMENT_SIGNATURES + helpers in codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000034-20260518_230743/ipfs_datasets_py/logic/modal/codec.py:196)
  - Integrated into provenance alignment components:
    - [codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000034-20260518_230743/ipfs_datasets_py/logic/modal/codec.py:2640)

- Extended regression coverage for both decoded slot maps and triples:
  - [test_ir_decompiler_slots.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000034-20260518_230743/ipfs_datasets_py/logic/modal/test_ir_decompiler_slots.py:3670)

Validation run:
- `pytest -q ipfs_datasets_py/logic/modal/test_ir_decompiler_slots.py` (66 passed)