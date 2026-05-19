# packet-000058

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/packet-000058/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/packet-000058/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000058-20260519_001121

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-6c8fbb8adc5c4624` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["epistemic->epistemic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6c8fbb8adc5c4624` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-32abc49efbb619fb", "predicted_family": "epistemic", "priority": 0.15, "sample_id": "us-code-2-1612-e16ee1803f4650eb", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.968177985389, "hint_id": "modal-synthesis-867875cd9eb166db", "predicted_family": "frame", "priority": 1.118177985389, "sample_id": "us-code-30-22-41b0706c6dfe0563", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.845499941677, "hint_id": "modal-synthesis-edf00fc3490f7378", "predicted_family": "frame", "priority": 0.995499941677, "sample_id": "us-code-10-2452-9f8cf05c0b023e33", "target_family": "deontic"}`

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

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-6c8fbb8adc5c4624`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["epistemic->epistemic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6c8fbb8adc5c4624` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.754559309022`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-30-22-41b0706c6dfe0563, us-code-10-2452-9f8cf05c0b023e33, us-code-2-1612-e16ee1803f4650eb`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-32abc49efbb619fb", "predicted_family": "epistemic", "priority": 0.15, "sample_id": "us-code-2-1612-e16ee1803f4650eb", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.968177985389, "hint_id": "modal-synthesis-867875cd9eb166db", "predicted_family": "frame", "priority": 1.118177985389, "sample_id": "us-code-30-22-41b0706c6dfe0563", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.845499941677, "hint_id": "modal-synthesis-edf00fc3490f7378", "predicted_family": "frame", "priority": 0.995499941677, "sample_id": "us-code-10-2452-9f8cf05c0b023e33", "target_family": "deontic"}`
