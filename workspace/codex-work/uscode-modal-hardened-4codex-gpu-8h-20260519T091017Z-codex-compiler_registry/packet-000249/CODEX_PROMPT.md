# packet-000249

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000249/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000249/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000249-20260519_151120

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-934e6a6b63a845ff` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-934e6a6b63a845ff` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.99993840758, "hint_id": "modal-synthesis-10ed39b5aebc6550", "predicted_family": "alethic", "priority": 0.999999913564, "sample_id": "us-code-43-1606.-83d1d5ae16abd934", "target_family": "conditional_normative", "target_probability": 8.6436e-08}`
  evidence: `{"family_margin": -0.975049399881, "hint_id": "modal-synthesis-854baacd758a312a", "predicted_family": "frame", "priority": 0.991964715178, "sample_id": "us-code-6-643-d2f444bfd0b4972c", "target_family": "temporal", "target_probability": 0.008035284822}`
- `program-36408576ba27e263` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","deontic->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-934e6a6b63a845ff` score `0.96818`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.341249605235, "hint_id": "modal-synthesis-31507440e86e0f74", "predicted_family": "frame", "priority": 0.979704766207, "sample_id": "us-code-16-539o-897733ba41e32ea2", "target_family": "temporal", "target_probability": 0.020295233793}`
  evidence: `{"family_margin": -0.707285876684, "hint_id": "modal-synthesis-3f7a08158c3046b1", "predicted_family": "deontic", "priority": 0.901145890833, "sample_id": "us-code-5-5926-04ed56c4405105b0", "target_family": "conditional_normative", "target_probability": 0.098854109167}`
  evidence: `{"family_margin": -0.142093573089, "hint_id": "modal-synthesis-d3b4de7ad0ae981a", "predicted_family": "alethic", "priority": 0.604351474701, "sample_id": "us-code-22-4505-791882220c69dc3d", "target_family": "deontic", "target_probability": 0.395648525299}`

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
- `program-934e6a6b63a845ff`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-934e6a6b63a845ff` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.995982314371`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-43-1606.-83d1d5ae16abd934, us-code-6-643-d2f444bfd0b4972c`
  evidence: `{"family_margin": -0.99993840758, "hint_id": "modal-synthesis-10ed39b5aebc6550", "predicted_family": "alethic", "priority": 0.999999913564, "sample_id": "us-code-43-1606.-83d1d5ae16abd934", "target_family": "conditional_normative", "target_probability": 8.6436e-08}`
  evidence: `{"family_margin": -0.975049399881, "hint_id": "modal-synthesis-854baacd758a312a", "predicted_family": "frame", "priority": 0.991964715178, "sample_id": "us-code-6-643-d2f444bfd0b4972c", "target_family": "temporal", "target_probability": 0.008035284822}`
- `program-36408576ba27e263`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","deontic->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-934e6a6b63a845ff` score `0.96818`
  loss: `autoencoder_residual_cluster` = `0.82840071058`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-539o-897733ba41e32ea2, us-code-5-5926-04ed56c4405105b0, us-code-22-4505-791882220c69dc3d`
  evidence: `{"family_margin": -0.341249605235, "hint_id": "modal-synthesis-31507440e86e0f74", "predicted_family": "frame", "priority": 0.979704766207, "sample_id": "us-code-16-539o-897733ba41e32ea2", "target_family": "temporal", "target_probability": 0.020295233793}`
  evidence: `{"family_margin": -0.707285876684, "hint_id": "modal-synthesis-3f7a08158c3046b1", "predicted_family": "deontic", "priority": 0.901145890833, "sample_id": "us-code-5-5926-04ed56c4405105b0", "target_family": "conditional_normative", "target_probability": 0.098854109167}`
  evidence: `{"family_margin": -0.142093573089, "hint_id": "modal-synthesis-d3b4de7ad0ae981a", "predicted_family": "alethic", "priority": 0.604351474701, "sample_id": "us-code-22-4505-791882220c69dc3d", "target_family": "deontic", "target_probability": 0.395648525299}`
