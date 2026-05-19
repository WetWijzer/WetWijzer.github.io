# packet-000035

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000035/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000035/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000035-20260519_110224

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-98d71289d1024937` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-98d71289d1024937` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-07c4ab75c15649a0", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-33-1201-60f5f89ed95507b4", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.992318572177, "hint_id": "modal-synthesis-af1e121a96081a52", "predicted_family": "frame", "priority": 1.142318572177, "sample_id": "us-code-49-44747.-8d818087c914239d", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.912021725113, "hint_id": "modal-synthesis-ed70c9e0efa3129c", "predicted_family": "frame", "priority": 1.062021725113, "sample_id": "us-code-15-2-6d3ed4712172ef72", "target_family": "deontic"}`
- `program-f1a239b5a5a13864` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-98d71289d1024937` score `0.987665`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.567455418399, "hint_id": "modal-synthesis-32c6e665d7f51d88", "predicted_family": "frame", "priority": 0.717455418399, "sample_id": "us-code-5-3315a-09989b04501a91c8", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.410394828098, "hint_id": "modal-synthesis-9705faa65de734f0", "predicted_family": "frame", "priority": 0.560394828098, "sample_id": "us-code-5-8K-54652e103b9e1518", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.059244309703, "hint_id": "modal-synthesis-99288fd3d6a39514", "predicted_family": "deontic", "priority": 0.209244309703, "sample_id": "us-code-7-1471d-9350e269eb381cda", "target_family": "conditional_normative"}`
- `program-44396394abe0dbdd` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","deontic->temporal","epistemic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-98d71289d1024937` score `0.962937`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.580200369329, "hint_id": "modal-synthesis-478d5ae8be3706c6", "predicted_family": "frame", "priority": 0.730200369329, "sample_id": "us-code-25-656-6c4924729d0853e0", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.850785409535, "hint_id": "modal-synthesis-8e2fdaabc7ff5d1e", "predicted_family": "deontic", "priority": 1.000785409535, "sample_id": "us-code-42-12752.-22fb1fe07b4c5173", "target_family": "frame"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-ab3f09cc260a8a9f", "predicted_family": "epistemic", "priority": 0.15, "sample_id": "us-code-22-283r-976899bf26d8db15", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.254624624015, "hint_id": "modal-synthesis-feedc5bccc5ee356", "predicted_family": "deontic", "priority": 0.404624624015, "sample_id": "us-code-7-7982-10d3c84e1544afa8", "target_family": "temporal"}`

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

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-98d71289d1024937`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-98d71289d1024937` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.784780099097`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-49-44747.-8d818087c914239d, us-code-15-2-6d3ed4712172ef72, us-code-33-1201-60f5f89ed95507b4`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-07c4ab75c15649a0", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-33-1201-60f5f89ed95507b4", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.992318572177, "hint_id": "modal-synthesis-af1e121a96081a52", "predicted_family": "frame", "priority": 1.142318572177, "sample_id": "us-code-49-44747.-8d818087c914239d", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.912021725113, "hint_id": "modal-synthesis-ed70c9e0efa3129c", "predicted_family": "frame", "priority": 1.062021725113, "sample_id": "us-code-15-2-6d3ed4712172ef72", "target_family": "deontic"}`
- `program-f1a239b5a5a13864`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-98d71289d1024937` score `0.987665`
  loss: `autoencoder_residual_cluster` = `0.4956981854`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-5-3315a-09989b04501a91c8, us-code-5-8K-54652e103b9e1518, us-code-7-1471d-9350e269eb381cda`
  evidence: `{"family_margin": -0.567455418399, "hint_id": "modal-synthesis-32c6e665d7f51d88", "predicted_family": "frame", "priority": 0.717455418399, "sample_id": "us-code-5-3315a-09989b04501a91c8", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.410394828098, "hint_id": "modal-synthesis-9705faa65de734f0", "predicted_family": "frame", "priority": 0.560394828098, "sample_id": "us-code-5-8K-54652e103b9e1518", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.059244309703, "hint_id": "modal-synthesis-99288fd3d6a39514", "predicted_family": "deontic", "priority": 0.209244309703, "sample_id": "us-code-7-1471d-9350e269eb381cda", "target_family": "conditional_normative"}`
- `program-44396394abe0dbdd`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","deontic->temporal","epistemic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-98d71289d1024937` score `0.962937`
  loss: `autoencoder_residual_cluster` = `0.57140260072`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-12752.-22fb1fe07b4c5173, us-code-25-656-6c4924729d0853e0, us-code-7-7982-10d3c84e1544afa8, us-code-22-283r-976899bf26d8db15`
  evidence: `{"family_margin": -0.580200369329, "hint_id": "modal-synthesis-478d5ae8be3706c6", "predicted_family": "frame", "priority": 0.730200369329, "sample_id": "us-code-25-656-6c4924729d0853e0", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.850785409535, "hint_id": "modal-synthesis-8e2fdaabc7ff5d1e", "predicted_family": "deontic", "priority": 1.000785409535, "sample_id": "us-code-42-12752.-22fb1fe07b4c5173", "target_family": "frame"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-ab3f09cc260a8a9f", "predicted_family": "epistemic", "priority": 0.15, "sample_id": "us-code-22-283r-976899bf26d8db15", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.254624624015, "hint_id": "modal-synthesis-feedc5bccc5ee356", "predicted_family": "deontic", "priority": 0.404624624015, "sample_id": "us-code-7-7982-10d3c84e1544afa8", "target_family": "temporal"}`
