# packet-000113

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/packet-000113/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/packet-000113/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-1h-20260518T191418Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000113-20260518_195918

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-744d9df1067481c6` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-744d9df1067481c6` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.999909204262, "hint_id": "modal-synthesis-58f49b786e6c6874", "predicted_family": "temporal", "priority": 0.999954602131, "sample_id": "us-code-26-3305-53aaebf91aa3d889", "target_family": "deontic", "target_probability": 4.5397869e-05}`
  evidence: `{"family_margin": -0.999664649245, "hint_id": "modal-synthesis-6fe3fa2934c8cd10", "predicted_family": "deontic", "priority": 0.999999999721, "sample_id": "us-code-38-8163-dc4c9191b09f4a3d", "target_family": "conditional_normative", "target_probability": 2.79e-10}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-e3af8ae656851c9a", "predicted_family": "temporal", "priority": 0.690655817884, "sample_id": "us-code-10-649j-49b85ae09715be03", "target_family": "frame", "target_probability": 0.309344182116}`

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
- `program-744d9df1067481c6`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-744d9df1067481c6` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.896870139912`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-38-8163-dc4c9191b09f4a3d, us-code-26-3305-53aaebf91aa3d889, us-code-10-649j-49b85ae09715be03`
  evidence: `{"family_margin": -0.999909204262, "hint_id": "modal-synthesis-58f49b786e6c6874", "predicted_family": "temporal", "priority": 0.999954602131, "sample_id": "us-code-26-3305-53aaebf91aa3d889", "target_family": "deontic", "target_probability": 4.5397869e-05}`
  evidence: `{"family_margin": -0.999664649245, "hint_id": "modal-synthesis-6fe3fa2934c8cd10", "predicted_family": "deontic", "priority": 0.999999999721, "sample_id": "us-code-38-8163-dc4c9191b09f4a3d", "target_family": "conditional_normative", "target_probability": 2.79e-10}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-e3af8ae656851c9a", "predicted_family": "temporal", "priority": 0.690655817884, "sample_id": "us-code-10-649j-49b85ae09715be03", "target_family": "frame", "target_probability": 0.309344182116}`
