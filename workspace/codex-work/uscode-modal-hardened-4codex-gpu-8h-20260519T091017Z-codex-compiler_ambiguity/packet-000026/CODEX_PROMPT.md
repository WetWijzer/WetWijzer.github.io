# packet-000026

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000026/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000026/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000026-20260519_100114

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-d01cbd95b3d7e90e` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d01cbd95b3d7e90e` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.994218937689, "hint_id": "modal-synthesis-383e1ff74a4fb2e1", "predicted_family": "frame", "priority": 1.144218937689, "sample_id": "us-code-22-284k-c185a8e2d551552b", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.937024346101, "hint_id": "modal-synthesis-439b8fad7211a3f8", "predicted_family": "alethic", "priority": 1.087024346101, "sample_id": "us-code-12-1701x-35de22523d1972e3", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.468704933225, "hint_id": "modal-synthesis-e12802f6c99d1477", "predicted_family": "frame", "priority": 0.618704933225, "sample_id": "us-code-18-1792-2edc2940775cc98a", "target_family": "deontic"}`
- `program-ae7b3c381e065bf6` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d01cbd95b3d7e90e` score `0.978987`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.230665609524, "hint_id": "modal-synthesis-1d9bee3286a53a77", "predicted_family": "frame", "priority": 0.380665609524, "sample_id": "us-code-48-487 to 487b.-20c793cbf965675e", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-66a77bbb41aaaca5", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-21-205-62b4ecc5f3c47e77", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.21898271845, "hint_id": "modal-synthesis-d10f98cbf72fef0e", "predicted_family": "temporal", "priority": 0.36898271845, "sample_id": "us-code-22-290h-7-fc7abec921bbc03b", "target_family": "frame"}`
- `program-041fb55e9f9aef5d` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d01cbd95b3d7e90e` score `0.965817`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.558274622881, "hint_id": "modal-synthesis-3c4d00f2d0810b27", "predicted_family": "frame", "priority": 0.708274622881, "sample_id": "us-code-8-1105a-08372dfcfc646b54", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-b40350f48260378b", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-36-110106-99b683bc037f56bc", "target_family": "conditional_normative"}`

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
- `program-d01cbd95b3d7e90e`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d01cbd95b3d7e90e` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.949982739005`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-284k-c185a8e2d551552b, us-code-12-1701x-35de22523d1972e3, us-code-18-1792-2edc2940775cc98a`
  evidence: `{"family_margin": -0.994218937689, "hint_id": "modal-synthesis-383e1ff74a4fb2e1", "predicted_family": "frame", "priority": 1.144218937689, "sample_id": "us-code-22-284k-c185a8e2d551552b", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.937024346101, "hint_id": "modal-synthesis-439b8fad7211a3f8", "predicted_family": "alethic", "priority": 1.087024346101, "sample_id": "us-code-12-1701x-35de22523d1972e3", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.468704933225, "hint_id": "modal-synthesis-e12802f6c99d1477", "predicted_family": "frame", "priority": 0.618704933225, "sample_id": "us-code-18-1792-2edc2940775cc98a", "target_family": "deontic"}`
- `program-ae7b3c381e065bf6`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d01cbd95b3d7e90e` score `0.978987`
  loss: `autoencoder_residual_cluster` = `0.299882775991`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-48-487 to 487b.-20c793cbf965675e, us-code-22-290h-7-fc7abec921bbc03b, us-code-21-205-62b4ecc5f3c47e77`
  evidence: `{"family_margin": -0.230665609524, "hint_id": "modal-synthesis-1d9bee3286a53a77", "predicted_family": "frame", "priority": 0.380665609524, "sample_id": "us-code-48-487 to 487b.-20c793cbf965675e", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-66a77bbb41aaaca5", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-21-205-62b4ecc5f3c47e77", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.21898271845, "hint_id": "modal-synthesis-d10f98cbf72fef0e", "predicted_family": "temporal", "priority": 0.36898271845, "sample_id": "us-code-22-290h-7-fc7abec921bbc03b", "target_family": "frame"}`
- `program-041fb55e9f9aef5d`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d01cbd95b3d7e90e` score `0.965817`
  loss: `autoencoder_residual_cluster` = `0.731729297591`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-36-110106-99b683bc037f56bc, us-code-8-1105a-08372dfcfc646b54`
  evidence: `{"family_margin": -0.558274622881, "hint_id": "modal-synthesis-3c4d00f2d0810b27", "predicted_family": "frame", "priority": 0.708274622881, "sample_id": "us-code-8-1105a-08372dfcfc646b54", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-b40350f48260378b", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-36-110106-99b683bc037f56bc", "target_family": "conditional_normative"}`
