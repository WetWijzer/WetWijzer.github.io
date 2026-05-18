Implemented a deterministic slot-family refinement in `modal.ir_decompiler` by adding **title+section-style composite slots** for both citation and source-id paths, and mirroring it in triple emission.

### Changes made
- Added new composite slot/component generation:
  - `*_title_section_style`
  - `*_title_section_style_normalized`
  - `*_title_section_style_canonical`
  - `*_title_section_style_canonical_normalized`
  - plus typed token/alnum derivatives via existing typed-slot helpers.
- Applied this in both citation and source-id extraction flows so decompiler output and F-logic triples stay aligned.

Updated files:
- [decompiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000031-20260518_224711/ipfs_datasets_py/logic/modal/decompiler.py)
- [codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000031-20260518_224711/ipfs_datasets_py/logic/modal/codec.py)
- [test_ir_decompiler_slots.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000031-20260518_224711/ipfs_datasets_py/logic/modal/test_ir_decompiler_slots.py)

### Validation
Ran:
- `pytest -q ipfs_datasets_py/logic/modal/test_ir_decompiler_slots.py -k "section_style_slots"`
- `pytest -q ipfs_datasets_py/logic/modal/test_ir_decompiler_slots.py`

Result:
- `64 passed` (full slot regression file).