# packet-000048

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-ir_decompiler/packet-000048/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-ir_decompiler/packet-000048/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-ir_decompiler/worktrees/agent-codex-ir_decompiler-packet-000048-20260519_072807

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/codec.py`
- `ipfs_datasets_py/logic/modal/decompiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_ir.py`

## TODOs
- `program-4ccc55b8f1b83151` `refine_typed_ir_or_decompiler_slots`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-4ccc55b8f1b83151` score `1.0`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  support: 4
  evidence: `{"cosine_similarity": -0.066331679647, "hint_id": "modal-synthesis-312b602e5fb1680d", "priority": 0.419096848998, "reconstruction_loss": 0.419096848998, "sample_id": "us-code-36-21705-3316728336d2c123"}`
  evidence: `{"cosine_similarity": -0.224225263833, "hint_id": "modal-synthesis-896fa4e9fcef694b", "priority": 0.47797374648, "reconstruction_loss": 0.47797374648, "sample_id": "us-code-38-1722A-36a73cb7e6dbf73e"}`
  evidence: `{"cosine_similarity": -0.448760861403, "hint_id": "modal-synthesis-daa02ea10baba0cd", "priority": 0.461261702004, "reconstruction_loss": 0.461261702004, "sample_id": "us-code-42-5041-53ccc938f3473016"}`
  evidence: `{"cosine_similarity": -0.038886576724, "hint_id": "modal-synthesis-f4c1b511688795e5", "priority": 0.464553735483, "reconstruction_loss": 0.464553735483, "sample_id": "us-code-29-794c-686bfc4da3dd44d6"}`

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

- Queue run: `uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-4ccc55b8f1b83151`
  action: `refine_typed_ir_or_decompiler_slots`
  role: `program_synthesis`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-4ccc55b8f1b83151` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.455721508241`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  samples: `us-code-38-1722A-36a73cb7e6dbf73e, us-code-29-794c-686bfc4da3dd44d6, us-code-42-5041-53ccc938f3473016, us-code-36-21705-3316728336d2c123`
  evidence: `{"cosine_similarity": -0.066331679647, "hint_id": "modal-synthesis-312b602e5fb1680d", "priority": 0.419096848998, "reconstruction_loss": 0.419096848998, "sample_id": "us-code-36-21705-3316728336d2c123"}`
  evidence: `{"cosine_similarity": -0.224225263833, "hint_id": "modal-synthesis-896fa4e9fcef694b", "priority": 0.47797374648, "reconstruction_loss": 0.47797374648, "sample_id": "us-code-38-1722A-36a73cb7e6dbf73e"}`
  evidence: `{"cosine_similarity": -0.448760861403, "hint_id": "modal-synthesis-daa02ea10baba0cd", "priority": 0.461261702004, "reconstruction_loss": 0.461261702004, "sample_id": "us-code-42-5041-53ccc938f3473016"}`
  evidence: `{"cosine_similarity": -0.038886576724, "hint_id": "modal-synthesis-f4c1b511688795e5", "priority": 0.464553735483, "reconstruction_loss": 0.464553735483, "sample_id": "us-code-29-794c-686bfc4da3dd44d6"}`
