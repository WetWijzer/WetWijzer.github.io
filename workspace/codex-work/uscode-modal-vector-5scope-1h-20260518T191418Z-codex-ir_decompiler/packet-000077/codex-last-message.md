Implemented a deterministic IR/decompiler slot refinement focused on numeric relation interactions for U.S.C. title/section features.

- Added relation+distance composite slots and span-signature emission for citation/source-id alignment number relations in decompiler and codec:
  - [decompiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000077-20260518_192054/ipfs_datasets_py/logic/modal/decompiler.py:1530)
  - [codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000077-20260518_192054/ipfs_datasets_py/logic/modal/codec.py:2003)
- Added relation+distance composite slots for title→section primary/terminal relation extraction (both decompiler slots and codec triples):
  - [decompiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000077-20260518_192054/ipfs_datasets_py/logic/modal/decompiler.py:2779)
  - [codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000077-20260518_192054/ipfs_datasets_py/logic/modal/codec.py:3628)
- Added shared helper for consistent profile derivation (`<relation>_<magnitude_bucket>`):
  - [decompiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000077-20260518_192054/ipfs_datasets_py/logic/modal/decompiler.py:3620)
  - [codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000077-20260518_192054/ipfs_datasets_py/logic/modal/codec.py:3414)
- Added regression tests for new slots/triples:
  - [test_ir_decompiler_slots.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000077-20260518_192054/ipfs_datasets_py/logic/modal/test_ir_decompiler_slots.py:4184)

Validation run:
- `pytest -q ipfs_datasets_py/logic/modal/test_ir_decompiler_slots.py -k "number_distance_profile_slots"` -> `2 passed`
- `pytest -q ipfs_datasets_py/logic/modal/test_ir_decompiler_slots.py` -> `55 passed`