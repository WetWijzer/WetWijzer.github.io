# packet-000028

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-ir_decompiler/packet-000028/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-ir_decompiler/packet-000028/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000028-20260519_091247

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/logic/modal/decompiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_ir.py`

## TODOs
- `program-b12c19ba39527b29` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-b12c19ba39527b29` score `1.0`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": 0.21831952826, "hint_id": "modal-synthesis-0c5221fa19d17cf3", "priority": 0.393930054009, "reconstruction_loss": 0.393930054009, "sample_id": "us-code-16-198a-69c109aec60f214a"}`
  evidence: `{"cosine_similarity": 0.254358231612, "hint_id": "modal-synthesis-1edb15cbeacdff7e", "priority": 0.276060016095, "reconstruction_loss": 0.276060016095, "sample_id": "us-code-25-450a-1-b25ed1d7e3a8d3a7"}`
  evidence: `{"cosine_similarity": 0.132854920842, "hint_id": "modal-synthesis-699ee0050c4a7e95", "priority": 0.309809220678, "reconstruction_loss": 0.309809220678, "sample_id": "us-code-22-1642e-0a4a6e0aa906f829"}`
  evidence: `{"cosine_similarity": -0.153577077166, "hint_id": "modal-synthesis-cf5250bf4ac196ca", "priority": 0.518242019652, "reconstruction_loss": 0.518242019652, "sample_id": "us-code-46-12107.-ac993296d58346dd"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
