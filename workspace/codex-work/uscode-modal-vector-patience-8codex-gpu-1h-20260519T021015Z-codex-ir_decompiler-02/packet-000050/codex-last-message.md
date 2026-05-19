Implemented a narrow deterministic slot refinement for `modal.ir_decompiler` focused on hyphenated subsection citations (e.g., `2279aa-2` / `360bbb-0`), mirrored across decode and triple projection.

### Changes
- Added new section slots in decompiler/codec when a non-range section matches `alpha-suffixed base` + `hyphen` + `numeric terminal`:
  - `citation_section_has_hyphen_subsection`
  - `citation_section_hyphen_subsection_primary_number`
  - `citation_section_hyphen_subsection_primary_suffix`
  - `citation_section_hyphen_subsection_terminal_number`
  - `citation_section_hyphen_subsection_signature`
  - plus typed token slots for the signature
- These automatically propagate to `source_id_section_*` via existing citation→source-id slot mapping.

### Edited files
- [decompiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-ir_decompiler-02/worktrees/agent-codex-ir_decompiler-02-packet-000050-20260519_021438/ipfs_datasets_py/logic/modal/decompiler.py#L4315)
- [codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-ir_decompiler-02/worktrees/agent-codex-ir_decompiler-02-packet-000050-20260519_021438/ipfs_datasets_py/logic/modal/codec.py#L4022)
- [test_ir_decompiler_slots.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-ir_decompiler-02/worktrees/agent-codex-ir_decompiler-02-packet-000050-20260519_021438/ipfs_datasets_py/logic/modal/test_ir_decompiler_slots.py#L2371)

### Validation
- `pytest -q ipfs_datasets_py/logic/modal/test_ir_decompiler_slots.py -k "section_profile_and_number_relation_slots"` → `2 passed`
- `pytest -q ipfs_datasets_py/logic/modal/test_ir_decompiler_slots.py` → `66 passed`