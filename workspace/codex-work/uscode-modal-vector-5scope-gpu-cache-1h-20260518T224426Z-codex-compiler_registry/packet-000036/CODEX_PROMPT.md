# packet-000036

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_registry/packet-000036/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_registry/packet-000036/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000036-20260518_224737

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-e90be5f04af3c0d7` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-e90be5f04af3c0d7` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-26dd623398f423c9", "predicted_family": "deontic", "priority": 0.532843141424, "sample_id": "us-code-42-247b-c7ce522c2799052d", "target_family": "deontic", "target_probability": 0.467156858576}`
  evidence: `{"family_margin": -0.812513277874, "hint_id": "modal-synthesis-4cb36802fc545782", "predicted_family": "frame", "priority": 0.90946102534, "sample_id": "us-code-42-1395w-5efce1b44ff160c2", "target_family": "deontic", "target_probability": 0.09053897466}`

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
- TODO count: `1`

## TODOs
- `program-e90be5f04af3c0d7`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-e90be5f04af3c0d7` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.721152083382`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-1395w-5efce1b44ff160c2, us-code-42-247b-c7ce522c2799052d`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-26dd623398f423c9", "predicted_family": "deontic", "priority": 0.532843141424, "sample_id": "us-code-42-247b-c7ce522c2799052d", "target_family": "deontic", "target_probability": 0.467156858576}`
  evidence: `{"family_margin": -0.812513277874, "hint_id": "modal-synthesis-4cb36802fc545782", "predicted_family": "frame", "priority": 0.90946102534, "sample_id": "us-code-42-1395w-5efce1b44ff160c2", "target_family": "deontic", "target_probability": 0.09053897466}`
