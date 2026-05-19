# packet-000025

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000025/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000025/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000025-20260519_115134

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-c41f1b93847737ba` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->conditional_normative","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-c41f1b93847737ba` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.858265621341, "hint_id": "modal-synthesis-2f6b22e5c7cbe58c", "predicted_family": "frame", "priority": 0.954908058958, "sample_id": "us-code-42-300j-51e286d3b4f6aa47", "target_family": "deontic", "target_probability": 0.045091941042}`
  evidence: `{"family_margin": -0.479417759252, "hint_id": "modal-synthesis-4f1c41a5a1bc34fc", "predicted_family": "frame", "priority": 0.971487452706, "sample_id": "us-code-42-5161.-8dac7a75a629d81d", "target_family": "conditional_normative", "target_probability": 0.028512547294}`
  evidence: `{"family_margin": -0.8417531115, "hint_id": "modal-synthesis-8a74fcf33baaf410", "predicted_family": "frame", "priority": 0.955775600547, "sample_id": "us-code-42-8321.-18cda303b32a8b79", "target_family": "temporal", "target_probability": 0.044224399453}`
  evidence: `{"family_margin": -0.339465897704, "hint_id": "modal-synthesis-d0475629332eb4d8", "predicted_family": "deontic", "priority": 0.80243875476, "sample_id": "us-code-7-2209c-9e364338270ca36c", "target_family": "temporal", "target_probability": 0.19756124524}`
- `program-ab204dd983014e00` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-c41f1b93847737ba` score `0.949481`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.94331159456, "hint_id": "modal-synthesis-a00735592b56357f", "predicted_family": "frame", "priority": 0.975109194302, "sample_id": "us-code-20-1161b-1fb334a71e66301b", "target_family": "deontic", "target_probability": 0.024890805698}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-bc289f39f70552cb", "predicted_family": "temporal", "priority": 0.733471287091, "sample_id": "us-code-22-1571-8ee22a2210e4b14d", "target_family": "temporal", "target_probability": 0.266528712909}`
  evidence: `{"family_margin": -0.804489585093, "hint_id": "modal-synthesis-c92a72de26dad229", "predicted_family": "frame", "priority": 0.939556471999, "sample_id": "us-code-5-8102a-c38142dd6938d00d", "target_family": "deontic", "target_probability": 0.060443528001}`

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
- `program-c41f1b93847737ba`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->conditional_normative","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-c41f1b93847737ba` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.921152466743`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-5161.-8dac7a75a629d81d, us-code-42-8321.-18cda303b32a8b79, us-code-42-300j-51e286d3b4f6aa47, us-code-7-2209c-9e364338270ca36c`
  evidence: `{"family_margin": -0.858265621341, "hint_id": "modal-synthesis-2f6b22e5c7cbe58c", "predicted_family": "frame", "priority": 0.954908058958, "sample_id": "us-code-42-300j-51e286d3b4f6aa47", "target_family": "deontic", "target_probability": 0.045091941042}`
  evidence: `{"family_margin": -0.479417759252, "hint_id": "modal-synthesis-4f1c41a5a1bc34fc", "predicted_family": "frame", "priority": 0.971487452706, "sample_id": "us-code-42-5161.-8dac7a75a629d81d", "target_family": "conditional_normative", "target_probability": 0.028512547294}`
  evidence: `{"family_margin": -0.8417531115, "hint_id": "modal-synthesis-8a74fcf33baaf410", "predicted_family": "frame", "priority": 0.955775600547, "sample_id": "us-code-42-8321.-18cda303b32a8b79", "target_family": "temporal", "target_probability": 0.044224399453}`
  evidence: `{"family_margin": -0.339465897704, "hint_id": "modal-synthesis-d0475629332eb4d8", "predicted_family": "deontic", "priority": 0.80243875476, "sample_id": "us-code-7-2209c-9e364338270ca36c", "target_family": "temporal", "target_probability": 0.19756124524}`
- `program-ab204dd983014e00`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-c41f1b93847737ba` score `0.949481`
  loss: `autoencoder_residual_cluster` = `0.882712317797`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-20-1161b-1fb334a71e66301b, us-code-5-8102a-c38142dd6938d00d, us-code-22-1571-8ee22a2210e4b14d`
  evidence: `{"family_margin": -0.94331159456, "hint_id": "modal-synthesis-a00735592b56357f", "predicted_family": "frame", "priority": 0.975109194302, "sample_id": "us-code-20-1161b-1fb334a71e66301b", "target_family": "deontic", "target_probability": 0.024890805698}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-bc289f39f70552cb", "predicted_family": "temporal", "priority": 0.733471287091, "sample_id": "us-code-22-1571-8ee22a2210e4b14d", "target_family": "temporal", "target_probability": 0.266528712909}`
  evidence: `{"family_margin": -0.804489585093, "hint_id": "modal-synthesis-c92a72de26dad229", "predicted_family": "frame", "priority": 0.939556471999, "sample_id": "us-code-5-8102a-c38142dd6938d00d", "target_family": "deontic", "target_probability": 0.060443528001}`
