# packet-000113

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000113/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000113/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000113-20260519_113146

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-a145929d89e0b28a` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a145929d89e0b28a` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.98293533675, "hint_id": "modal-synthesis-a274d95822360311", "predicted_family": "frame", "priority": 1.13293533675, "sample_id": "us-code-29-1851-f2b8bca48c79ea5b", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.788983986003, "hint_id": "modal-synthesis-faace54db2dd6c6a", "predicted_family": "frame", "priority": 0.938983986003, "sample_id": "us-code-20-1087cc-7df79972ab6270a9", "target_family": "deontic"}`
- `program-c33a418ec8f55ad2` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->temporal","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a145929d89e0b28a` score `0.924884`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.495628881718, "hint_id": "modal-synthesis-6155b4cd1a92a7fe", "predicted_family": "temporal", "priority": 0.645628881718, "sample_id": "us-code-2-5303-d859402e8a787491", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.907679549796, "hint_id": "modal-synthesis-8c7c3a10c10d47ea", "predicted_family": "frame", "priority": 1.057679549796, "sample_id": "us-code-42-1396u-57bec3d2de18e889", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.480261147937, "hint_id": "modal-synthesis-d4c82f2b5af7d483", "predicted_family": "deontic", "priority": 0.630261147937, "sample_id": "us-code-42-11043.-a349cc422cfb814d", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-de5d252036f12b20", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-22-9614-25ece758489d6025", "target_family": "deontic"}`

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
- TODO count: `2`

## TODOs
- `program-a145929d89e0b28a`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a145929d89e0b28a` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.035959661376`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-29-1851-f2b8bca48c79ea5b, us-code-20-1087cc-7df79972ab6270a9`
  evidence: `{"family_margin": -0.98293533675, "hint_id": "modal-synthesis-a274d95822360311", "predicted_family": "frame", "priority": 1.13293533675, "sample_id": "us-code-29-1851-f2b8bca48c79ea5b", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.788983986003, "hint_id": "modal-synthesis-faace54db2dd6c6a", "predicted_family": "frame", "priority": 0.938983986003, "sample_id": "us-code-20-1087cc-7df79972ab6270a9", "target_family": "deontic"}`
- `program-c33a418ec8f55ad2`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->temporal","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a145929d89e0b28a` score `0.924884`
  loss: `autoencoder_residual_cluster` = `0.620892394863`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-1396u-57bec3d2de18e889, us-code-2-5303-d859402e8a787491, us-code-42-11043.-a349cc422cfb814d, us-code-22-9614-25ece758489d6025`
  evidence: `{"family_margin": -0.495628881718, "hint_id": "modal-synthesis-6155b4cd1a92a7fe", "predicted_family": "temporal", "priority": 0.645628881718, "sample_id": "us-code-2-5303-d859402e8a787491", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.907679549796, "hint_id": "modal-synthesis-8c7c3a10c10d47ea", "predicted_family": "frame", "priority": 1.057679549796, "sample_id": "us-code-42-1396u-57bec3d2de18e889", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.480261147937, "hint_id": "modal-synthesis-d4c82f2b5af7d483", "predicted_family": "deontic", "priority": 0.630261147937, "sample_id": "us-code-42-11043.-a349cc422cfb814d", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-de5d252036f12b20", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-22-9614-25ece758489d6025", "target_family": "deontic"}`
