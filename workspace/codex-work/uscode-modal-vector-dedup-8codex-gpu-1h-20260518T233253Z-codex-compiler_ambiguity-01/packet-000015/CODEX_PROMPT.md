# packet-000015

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/packet-000015/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/packet-000015/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000015-20260518_235143

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-4870701f382931b2` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4870701f382931b2` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.999091663546, "hint_id": "modal-synthesis-6e8aa7add01e4a84", "predicted_family": "deontic", "priority": 1.149091663546, "sample_id": "us-code-42-5422.-5b961f79f3664b3e", "target_family": "frame"}`
  evidence: `{"family_margin": -0.71376499545, "hint_id": "modal-synthesis-9b1534a5e529dbbe", "predicted_family": "frame", "priority": 0.86376499545, "sample_id": "us-code-34-21301-1e886420be029827", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.244804791593, "hint_id": "modal-synthesis-d2a865975a9fceed", "predicted_family": "frame", "priority": 0.394804791593, "sample_id": "us-code-49-60127.-8664408f5c716452", "target_family": "deontic"}`

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
- `program-4870701f382931b2`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4870701f382931b2` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.802553816863`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-5422.-5b961f79f3664b3e, us-code-34-21301-1e886420be029827, us-code-49-60127.-8664408f5c716452`
  evidence: `{"family_margin": -0.999091663546, "hint_id": "modal-synthesis-6e8aa7add01e4a84", "predicted_family": "deontic", "priority": 1.149091663546, "sample_id": "us-code-42-5422.-5b961f79f3664b3e", "target_family": "frame"}`
  evidence: `{"family_margin": -0.71376499545, "hint_id": "modal-synthesis-9b1534a5e529dbbe", "predicted_family": "frame", "priority": 0.86376499545, "sample_id": "us-code-34-21301-1e886420be029827", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.244804791593, "hint_id": "modal-synthesis-d2a865975a9fceed", "predicted_family": "frame", "priority": 0.394804791593, "sample_id": "us-code-49-60127.-8664408f5c716452", "target_family": "deontic"}`
