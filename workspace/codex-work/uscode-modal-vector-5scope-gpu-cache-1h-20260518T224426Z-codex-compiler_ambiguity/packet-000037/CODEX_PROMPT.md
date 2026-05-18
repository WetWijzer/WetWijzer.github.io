# packet-000037

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/packet-000037/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/packet-000037/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000037-20260518_225133

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-fa0931c8d1790b66` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->frame","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-fa0931c8d1790b66` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-650cd7768fed886d", "predicted_family": "deontic", "priority": 1.15, "sample_id": "us-code-10-311-44edc8d123967701", "target_family": "frame"}`
  evidence: `{"family_margin": -0.999999999922, "hint_id": "modal-synthesis-70f3063930daa8e3", "predicted_family": "deontic", "priority": 1.149999999922, "sample_id": "us-code-18-3523-ca8dbe79c9121836", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999997739674, "hint_id": "modal-synthesis-c3f1c6f1263c1e20", "predicted_family": "deontic", "priority": 1.149997739674, "sample_id": "us-code-27-204-58e3ac010eeacfce", "target_family": "temporal"}`
- `program-a0d7e6406647c391` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-fa0931c8d1790b66` score `0.976342`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-7ee3cc5c31349ae5", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-25-677x-a4b45221cb9ce4af", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.442067654021, "hint_id": "modal-synthesis-98419040febffda1", "predicted_family": "frame", "priority": 0.592067654021, "sample_id": "us-code-33-496-00362c8ed02df86c", "target_family": "deontic"}`
- `program-435ed2e8c21e65d5` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-fa0931c8d1790b66` score `0.972311`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.98608349919, "hint_id": "modal-synthesis-7135241324adbed0", "predicted_family": "frame", "priority": 1.13608349919, "sample_id": "us-code-22-4210-84a1442bd9c70a2c", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-b8b005f9ff859e17", "predicted_family": "frame", "priority": 0.668545682385, "sample_id": "us-code-27-63a-d96647eafbc3dd46", "target_family": "temporal"}`
- `program-eafa3ee2f33d0259` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->epistemic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-fa0931c8d1790b66` score `0.972286`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.031508900693, "hint_id": "modal-synthesis-17aca10f842ab367", "predicted_family": "frame", "priority": 0.181508900693, "sample_id": "us-code-15-171-15968f6d84c5fbe5", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.91864724793, "hint_id": "modal-synthesis-2203100413e75fd5", "predicted_family": "conditional_normative", "priority": 1.06864724793, "sample_id": "us-code-22-2360-7fe8ccb179c7e3e4", "target_family": "epistemic"}`

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

- Queue run: `uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-autoencoder.jsonl`
- TODO count: `4`

## TODOs
- `program-fa0931c8d1790b66`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->frame","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-fa0931c8d1790b66` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.149999246532`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-311-44edc8d123967701, us-code-18-3523-ca8dbe79c9121836, us-code-27-204-58e3ac010eeacfce`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-650cd7768fed886d", "predicted_family": "deontic", "priority": 1.15, "sample_id": "us-code-10-311-44edc8d123967701", "target_family": "frame"}`
  evidence: `{"family_margin": -0.999999999922, "hint_id": "modal-synthesis-70f3063930daa8e3", "predicted_family": "deontic", "priority": 1.149999999922, "sample_id": "us-code-18-3523-ca8dbe79c9121836", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999997739674, "hint_id": "modal-synthesis-c3f1c6f1263c1e20", "predicted_family": "deontic", "priority": 1.149997739674, "sample_id": "us-code-27-204-58e3ac010eeacfce", "target_family": "temporal"}`
- `program-a0d7e6406647c391`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-fa0931c8d1790b66` score `0.976342`
  loss: `autoencoder_residual_cluster` = `0.673625813162`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-25-677x-a4b45221cb9ce4af, us-code-33-496-00362c8ed02df86c`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-7ee3cc5c31349ae5", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-25-677x-a4b45221cb9ce4af", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.442067654021, "hint_id": "modal-synthesis-98419040febffda1", "predicted_family": "frame", "priority": 0.592067654021, "sample_id": "us-code-33-496-00362c8ed02df86c", "target_family": "deontic"}`
- `program-435ed2e8c21e65d5`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-fa0931c8d1790b66` score `0.972311`
  loss: `autoencoder_residual_cluster` = `0.902314590787`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-4210-84a1442bd9c70a2c, us-code-27-63a-d96647eafbc3dd46`
  evidence: `{"family_margin": -0.98608349919, "hint_id": "modal-synthesis-7135241324adbed0", "predicted_family": "frame", "priority": 1.13608349919, "sample_id": "us-code-22-4210-84a1442bd9c70a2c", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-b8b005f9ff859e17", "predicted_family": "frame", "priority": 0.668545682385, "sample_id": "us-code-27-63a-d96647eafbc3dd46", "target_family": "temporal"}`
- `program-eafa3ee2f33d0259`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->epistemic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-fa0931c8d1790b66` score `0.972286`
  loss: `autoencoder_residual_cluster` = `0.625078074311`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-2360-7fe8ccb179c7e3e4, us-code-15-171-15968f6d84c5fbe5`
  evidence: `{"family_margin": -0.031508900693, "hint_id": "modal-synthesis-17aca10f842ab367", "predicted_family": "frame", "priority": 0.181508900693, "sample_id": "us-code-15-171-15968f6d84c5fbe5", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.91864724793, "hint_id": "modal-synthesis-2203100413e75fd5", "predicted_family": "conditional_normative", "priority": 1.06864724793, "sample_id": "us-code-22-2360-7fe8ccb179c7e3e4", "target_family": "epistemic"}`
