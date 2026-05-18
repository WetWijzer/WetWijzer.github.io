# packet-000031

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/packet-000031/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/packet-000031/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000031-20260518_224711

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/logic/modal/decompiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_ir.py`

## TODOs
- `program-9bd7469d29661bf0` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-9bd7469d29661bf0` score `1.0`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": 0.044685397113, "hint_id": "modal-synthesis-4c7e057acaaa33a0", "priority": 0.399878073115, "reconstruction_loss": 0.399878073115, "sample_id": "us-code-25-2453-6148409606ae76c3"}`
  evidence: `{"cosine_similarity": 0.434773424891, "hint_id": "modal-synthesis-7bf7685eb1a9171c", "priority": 0.281865141048, "reconstruction_loss": 0.281865141048, "sample_id": "us-code-48-912.-591af0277276625b"}`
  evidence: `{"cosine_similarity": 0.264333586782, "hint_id": "modal-synthesis-88fd1a92228db5e6", "priority": 0.266796957902, "reconstruction_loss": 0.266796957902, "sample_id": "us-code-18-9-b33f6d6a250bd8aa"}`
  evidence: `{"cosine_similarity": 0.149104087326, "hint_id": "modal-synthesis-dbc98de613b444d0", "priority": 0.390771545825, "reconstruction_loss": 0.390771545825, "sample_id": "us-code-21-360ccc-2-1dfff84fbecab91a"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
