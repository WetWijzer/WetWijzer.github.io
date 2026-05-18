# packet-000019

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000019/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000019/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000019-20260518_233441

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-748277528fe79902` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","deontic->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-748277528fe79902` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.997538709134, "hint_id": "modal-synthesis-785f19662bc2ac33", "predicted_family": "deontic", "priority": 0.998770604452, "sample_id": "us-code-10-1030-6ebd847628f9a7da", "target_family": "frame", "target_probability": 0.001229395548}`
  evidence: `{"family_margin": -0.999999999835, "hint_id": "modal-synthesis-7a5f641fb1bda708", "predicted_family": "deontic", "priority": 0.999999999995, "sample_id": "us-code-15-657d-be08838ed78ea48c", "target_family": "temporal", "target_probability": 5e-12}`

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
- `program-748277528fe79902`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","deontic->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-748277528fe79902` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.999385302223`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-15-657d-be08838ed78ea48c, us-code-10-1030-6ebd847628f9a7da`
  evidence: `{"family_margin": -0.997538709134, "hint_id": "modal-synthesis-785f19662bc2ac33", "predicted_family": "deontic", "priority": 0.998770604452, "sample_id": "us-code-10-1030-6ebd847628f9a7da", "target_family": "frame", "target_probability": 0.001229395548}`
  evidence: `{"family_margin": -0.999999999835, "hint_id": "modal-synthesis-7a5f641fb1bda708", "predicted_family": "deontic", "priority": 0.999999999995, "sample_id": "us-code-15-657d-be08838ed78ea48c", "target_family": "temporal", "target_probability": 5e-12}`
