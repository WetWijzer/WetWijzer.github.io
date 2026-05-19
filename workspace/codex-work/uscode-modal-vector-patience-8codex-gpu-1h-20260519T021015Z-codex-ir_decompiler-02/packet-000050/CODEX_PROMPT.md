# packet-000050

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-ir_decompiler-02/packet-000050/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-ir_decompiler-02/packet-000050/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-ir_decompiler-02/worktrees/agent-codex-ir_decompiler-02-packet-000050-20260519_021438

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/logic/modal/decompiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_ir.py`

## TODOs
- `program-ef6b99cd4e339e3e` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-ef6b99cd4e339e3e` score `1.0`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": 0.324418763621, "hint_id": "modal-synthesis-1d53ea970a1a1816", "priority": 0.275042659172, "reconstruction_loss": 0.275042659172, "sample_id": "us-code-12-2279aa-2-6a09ee84391e5f19"}`
  evidence: `{"cosine_similarity": -0.759276386399, "hint_id": "modal-synthesis-60a89ffeb94b56a8", "priority": 0.957229707661, "reconstruction_loss": 0.957229707661, "sample_id": "us-code-36-904-23d13763f249af22"}`
  evidence: `{"cosine_similarity": 0.399483647303, "hint_id": "modal-synthesis-6d25193602eeba8e", "priority": 0.265579222737, "reconstruction_loss": 0.265579222737, "sample_id": "us-code-42-8262g.-4d0259caef5347ae"}`
  evidence: `{"cosine_similarity": -0.35377637053, "hint_id": "modal-synthesis-9d58ff6911a0056d", "priority": 0.73957747429, "reconstruction_loss": 0.73957747429, "sample_id": "us-code-42-18363.-2c1c33e4b656cb38"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.


## Execution Instructions
Work only inside the packet worktree.
Your worktree edits may be applied back to the source checkout and validated automatically when this packet finishes.
Do not create changes.patch or other patch artifact files; leave source and test edits directly in the worktree.
Treat the packet's program_synthesis_scope metadata as the AST/write-scope boundary; keep edits inside that lane unless a test requires a small adjacent change.
When multiple TODOs are present, treat their semantic_bundle_key or vector_bundle metadata as evidence for one generalized compiler/decompiler/frame improvement over one-off sample fixes.
Implement a narrow deterministic parser, IR, decoder, or frame-logic improvement for the claimed TODOs.
Prefer explainable compiler/decompiler code over learned weights when the TODO concerns modal or frame semantics.
Use local repository files and tests only; do not use web search for this packet.
Run the smallest relevant tests you can before finishing.
Leave unrelated files alone.

## Claimed Autoencoder TODO List
# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-ef6b99cd4e339e3e`
  action: `refine_typed_ir_or_decompiler_slots`
  role: `program_synthesis`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-ef6b99cd4e339e3e` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.559357265965`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  samples: `us-code-36-904-23d13763f249af22, us-code-42-18363.-2c1c33e4b656cb38, us-code-12-2279aa-2-6a09ee84391e5f19, us-code-42-8262g.-4d0259caef5347ae`
  evidence: `{"cosine_similarity": 0.324418763621, "hint_id": "modal-synthesis-1d53ea970a1a1816", "priority": 0.275042659172, "reconstruction_loss": 0.275042659172, "sample_id": "us-code-12-2279aa-2-6a09ee84391e5f19"}`
  evidence: `{"cosine_similarity": -0.759276386399, "hint_id": "modal-synthesis-60a89ffeb94b56a8", "priority": 0.957229707661, "reconstruction_loss": 0.957229707661, "sample_id": "us-code-36-904-23d13763f249af22"}`
  evidence: `{"cosine_similarity": 0.399483647303, "hint_id": "modal-synthesis-6d25193602eeba8e", "priority": 0.265579222737, "reconstruction_loss": 0.265579222737, "sample_id": "us-code-42-8262g.-4d0259caef5347ae"}`
  evidence: `{"cosine_similarity": -0.35377637053, "hint_id": "modal-synthesis-9d58ff6911a0056d", "priority": 0.73957747429, "reconstruction_loss": 0.73957747429, "sample_id": "us-code-42-18363.-2c1c33e4b656cb38"}`
