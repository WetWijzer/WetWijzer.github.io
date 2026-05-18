# packet-000077

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/packet-000077/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/packet-000077/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000077-20260518_192054

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/logic/modal/decompiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_ir.py`

## TODOs
- `program-1b1f30534e99b5ce` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-1b1f30534e99b5ce` score `1.0`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": 0.057124794138, "hint_id": "modal-synthesis-221c173c7c8b8563", "priority": 0.381950762952, "reconstruction_loss": 0.381950762952, "sample_id": "us-code-10-2216-fd634bec8b2ae0f5"}`
  evidence: `{"cosine_similarity": -0.698266473901, "hint_id": "modal-synthesis-2c93a6d7af597b4e", "priority": 0.711412560924, "reconstruction_loss": 0.711412560924, "sample_id": "us-code-46-30525.-99a6422ab828fa0c"}`
  evidence: `{"cosine_similarity": -0.376175238058, "hint_id": "modal-synthesis-5379b4a4ee03e17b", "priority": 0.50225786335, "reconstruction_loss": 0.50225786335, "sample_id": "us-code-12-59-693f71484c6a9a7a"}`
  evidence: `{"cosine_similarity": 0.189514843063, "hint_id": "modal-synthesis-5b8f8d09da904eed", "priority": 0.370480311271, "reconstruction_loss": 0.370480311271, "sample_id": "us-code-48-1422b.-1024d577005506f9"}`

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

- Queue run: `uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-1b1f30534e99b5ce`
  action: `refine_typed_ir_or_decompiler_slots`
  role: `program_synthesis`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-1b1f30534e99b5ce` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.491525374624`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  samples: `us-code-46-30525.-99a6422ab828fa0c, us-code-12-59-693f71484c6a9a7a, us-code-10-2216-fd634bec8b2ae0f5, us-code-48-1422b.-1024d577005506f9`
  evidence: `{"cosine_similarity": 0.057124794138, "hint_id": "modal-synthesis-221c173c7c8b8563", "priority": 0.381950762952, "reconstruction_loss": 0.381950762952, "sample_id": "us-code-10-2216-fd634bec8b2ae0f5"}`
  evidence: `{"cosine_similarity": -0.698266473901, "hint_id": "modal-synthesis-2c93a6d7af597b4e", "priority": 0.711412560924, "reconstruction_loss": 0.711412560924, "sample_id": "us-code-46-30525.-99a6422ab828fa0c"}`
  evidence: `{"cosine_similarity": -0.376175238058, "hint_id": "modal-synthesis-5379b4a4ee03e17b", "priority": 0.50225786335, "reconstruction_loss": 0.50225786335, "sample_id": "us-code-12-59-693f71484c6a9a7a"}`
  evidence: `{"cosine_similarity": 0.189514843063, "hint_id": "modal-synthesis-5b8f8d09da904eed", "priority": 0.370480311271, "reconstruction_loss": 0.370480311271, "sample_id": "us-code-48-1422b.-1024d577005506f9"}`
