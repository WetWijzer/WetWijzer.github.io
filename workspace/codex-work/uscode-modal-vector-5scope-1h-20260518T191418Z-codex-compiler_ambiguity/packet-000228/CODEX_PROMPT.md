# packet-000228

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/packet-000228/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/packet-000228/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000228-20260518_193634

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-57791b5ad35bf1a0` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["temporal->conditional_normative","temporal->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-57791b5ad35bf1a0` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.999999999976, "hint_id": "modal-synthesis-1f8ba84764cface6", "predicted_family": "temporal", "priority": 1.149999999976, "sample_id": "us-code-31-5312-039372e5e9300b7d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999999999986, "hint_id": "modal-synthesis-9557736a33de85a0", "predicted_family": "temporal", "priority": 1.149999999986, "sample_id": "us-code-7-1631-2e645b217b50b0bc", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.737725781832, "hint_id": "modal-synthesis-ed1ce34a235f7a3c", "predicted_family": "temporal", "priority": 0.887725781832, "sample_id": "us-code-43-270-9753303f57791aad", "target_family": "conditional_normative"}`

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
- `program-57791b5ad35bf1a0`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["temporal->conditional_normative","temporal->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-57791b5ad35bf1a0` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.062575260598`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-7-1631-2e645b217b50b0bc, us-code-31-5312-039372e5e9300b7d, us-code-43-270-9753303f57791aad`
  evidence: `{"family_margin": -0.999999999976, "hint_id": "modal-synthesis-1f8ba84764cface6", "predicted_family": "temporal", "priority": 1.149999999976, "sample_id": "us-code-31-5312-039372e5e9300b7d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999999999986, "hint_id": "modal-synthesis-9557736a33de85a0", "predicted_family": "temporal", "priority": 1.149999999986, "sample_id": "us-code-7-1631-2e645b217b50b0bc", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.737725781832, "hint_id": "modal-synthesis-ed1ce34a235f7a3c", "predicted_family": "temporal", "priority": 0.887725781832, "sample_id": "us-code-43-270-9753303f57791aad", "target_family": "conditional_normative"}`
