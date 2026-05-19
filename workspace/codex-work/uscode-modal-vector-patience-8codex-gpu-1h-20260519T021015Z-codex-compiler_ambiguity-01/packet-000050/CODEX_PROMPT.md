# packet-000050

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/packet-000050/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/packet-000050/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000050-20260519_022533

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-713f946dc29b61d3` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-713f946dc29b61d3` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.999963367228, "hint_id": "modal-synthesis-5cbed5e75ea39504", "predicted_family": "conditional_normative", "priority": 1.149963367228, "sample_id": "us-code-10-3456-64343e4f4335b1a1", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.384757772757, "hint_id": "modal-synthesis-cf64510eaf2bee13", "predicted_family": "deontic", "priority": 0.534757772757, "sample_id": "us-code-15-9034-d76b15a4901912d0", "target_family": "temporal"}`
- `program-773b96c9b8159d41` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->frame","deontic->conditional_normative","frame->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-713f946dc29b61d3` score `0.967871`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.567886584382, "hint_id": "modal-synthesis-73eac24bd9876471", "predicted_family": "deontic", "priority": 0.717886584382, "sample_id": "us-code-38-3314-2a109138039e1736", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999999950162, "hint_id": "modal-synthesis-bf5e83fb623876ac", "predicted_family": "conditional_normative", "priority": 1.149999950162, "sample_id": "us-code-18-2-dup1-64bd7795ee7cbbcc", "target_family": "frame"}`
  evidence: `{"family_margin": -0.358398369222, "hint_id": "modal-synthesis-eb10da042fdef9d7", "predicted_family": "frame", "priority": 0.508398369222, "sample_id": "us-code-22-2271-cad11cc172c48069", "target_family": "epistemic"}`
- `program-09c9b8cf92534f0a` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-713f946dc29b61d3` score `0.93166`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-2dd1ad1671a288a5", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-25-746-88b773e186c78138", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.044951128918, "hint_id": "modal-synthesis-2eb2cff52738463f", "predicted_family": "deontic", "priority": 0.105048871082, "sample_id": "us-code-20-2569-bdccc2d39a45b47e", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.18771949257, "hint_id": "modal-synthesis-d48e74b2d450a24e", "predicted_family": "frame", "priority": 0.33771949257, "sample_id": "us-code-36-154108-10b5a65ddc888004", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.567455418399, "hint_id": "modal-synthesis-f4c34917a4dfb255", "predicted_family": "frame", "priority": 0.717455418399, "sample_id": "us-code-30-208-2-aa31c042c6e309e5", "target_family": "temporal"}`

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
- TODO count: `3`

## TODOs
- `program-713f946dc29b61d3`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-713f946dc29b61d3` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.842360569993`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-3456-64343e4f4335b1a1, us-code-15-9034-d76b15a4901912d0`
  evidence: `{"family_margin": -0.999963367228, "hint_id": "modal-synthesis-5cbed5e75ea39504", "predicted_family": "conditional_normative", "priority": 1.149963367228, "sample_id": "us-code-10-3456-64343e4f4335b1a1", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.384757772757, "hint_id": "modal-synthesis-cf64510eaf2bee13", "predicted_family": "deontic", "priority": 0.534757772757, "sample_id": "us-code-15-9034-d76b15a4901912d0", "target_family": "temporal"}`
- `program-773b96c9b8159d41`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->frame","deontic->conditional_normative","frame->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-713f946dc29b61d3` score `0.967871`
  loss: `autoencoder_residual_cluster` = `0.792094967922`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-18-2-dup1-64bd7795ee7cbbcc, us-code-38-3314-2a109138039e1736, us-code-22-2271-cad11cc172c48069`
  evidence: `{"family_margin": -0.567886584382, "hint_id": "modal-synthesis-73eac24bd9876471", "predicted_family": "deontic", "priority": 0.717886584382, "sample_id": "us-code-38-3314-2a109138039e1736", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999999950162, "hint_id": "modal-synthesis-bf5e83fb623876ac", "predicted_family": "conditional_normative", "priority": 1.149999950162, "sample_id": "us-code-18-2-dup1-64bd7795ee7cbbcc", "target_family": "frame"}`
  evidence: `{"family_margin": -0.358398369222, "hint_id": "modal-synthesis-eb10da042fdef9d7", "predicted_family": "frame", "priority": 0.508398369222, "sample_id": "us-code-22-2271-cad11cc172c48069", "target_family": "epistemic"}`
- `program-09c9b8cf92534f0a`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-713f946dc29b61d3` score `0.93166`
  loss: `autoencoder_residual_cluster` = `0.559349747139`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-25-746-88b773e186c78138, us-code-30-208-2-aa31c042c6e309e5, us-code-36-154108-10b5a65ddc888004, us-code-20-2569-bdccc2d39a45b47e`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-2dd1ad1671a288a5", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-25-746-88b773e186c78138", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.044951128918, "hint_id": "modal-synthesis-2eb2cff52738463f", "predicted_family": "deontic", "priority": 0.105048871082, "sample_id": "us-code-20-2569-bdccc2d39a45b47e", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.18771949257, "hint_id": "modal-synthesis-d48e74b2d450a24e", "predicted_family": "frame", "priority": 0.33771949257, "sample_id": "us-code-36-154108-10b5a65ddc888004", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.567455418399, "hint_id": "modal-synthesis-f4c34917a4dfb255", "predicted_family": "frame", "priority": 0.717455418399, "sample_id": "us-code-30-208-2-aa31c042c6e309e5", "target_family": "temporal"}`
