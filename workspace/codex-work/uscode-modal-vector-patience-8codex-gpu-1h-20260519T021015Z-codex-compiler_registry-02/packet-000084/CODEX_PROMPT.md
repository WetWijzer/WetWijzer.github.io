# packet-000084

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/packet-000084/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/packet-000084/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000084-20260519_021727

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-95e29681ea723eac` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-95e29681ea723eac` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.164578968256, "hint_id": "modal-synthesis-40bf908d98e1c625", "predicted_family": "frame", "priority": 0.775549552138, "sample_id": "us-code-43-25 to 25b.-281e835d4b2de5b0", "target_family": "temporal", "target_probability": 0.224450447862}`
  evidence: `{"family_margin": -0.66708163055, "hint_id": "modal-synthesis-bf2776b32f39083d", "predicted_family": "temporal", "priority": 0.999999249298, "sample_id": "us-code-26-1035-b286ae25b6800758", "target_family": "deontic", "target_probability": 7.50702e-07}`
- `program-b259daf69ddef0eb` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-95e29681ea723eac` score `0.980682`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.720554053002, "hint_id": "modal-synthesis-8d3e7082b8d97bd2", "predicted_family": "frame", "priority": 0.91970811195, "sample_id": "us-code-18-336-fa27971f56c9178b", "target_family": "deontic", "target_probability": 0.08029188805}`
  evidence: `{"family_margin": -0.587469961488, "hint_id": "modal-synthesis-ca9449edec7bff4c", "predicted_family": "frame", "priority": 0.831268688955, "sample_id": "us-code-25-564u-3e5f6016c5496413", "target_family": "conditional_normative", "target_probability": 0.168731311045}`
- `program-8361f734a0ffb36b` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","deontic->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-95e29681ea723eac` score `0.960326`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.453596737625, "hint_id": "modal-synthesis-442bc6b04737abbf", "predicted_family": "conditional_normative", "priority": 0.757352168122, "sample_id": "us-code-16-460ss-5-a29152ca8faf3653", "target_family": "deontic", "target_probability": 0.242647831878}`
  evidence: `{"family_margin": -0.617808664044, "hint_id": "modal-synthesis-a2a9d72927582b51", "predicted_family": "deontic", "priority": 0.982812523493, "sample_id": "us-code-40-6306-aeae94d6d1d8eb01", "target_family": "conditional_normative", "target_probability": 0.017187476507}`

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
- `program-95e29681ea723eac`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-95e29681ea723eac` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.887774400718`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-26-1035-b286ae25b6800758, us-code-43-25 to 25b.-281e835d4b2de5b0`
  evidence: `{"family_margin": -0.164578968256, "hint_id": "modal-synthesis-40bf908d98e1c625", "predicted_family": "frame", "priority": 0.775549552138, "sample_id": "us-code-43-25 to 25b.-281e835d4b2de5b0", "target_family": "temporal", "target_probability": 0.224450447862}`
  evidence: `{"family_margin": -0.66708163055, "hint_id": "modal-synthesis-bf2776b32f39083d", "predicted_family": "temporal", "priority": 0.999999249298, "sample_id": "us-code-26-1035-b286ae25b6800758", "target_family": "deontic", "target_probability": 7.50702e-07}`
- `program-b259daf69ddef0eb`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-95e29681ea723eac` score `0.980682`
  loss: `autoencoder_residual_cluster` = `0.875488400452`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-18-336-fa27971f56c9178b, us-code-25-564u-3e5f6016c5496413`
  evidence: `{"family_margin": -0.720554053002, "hint_id": "modal-synthesis-8d3e7082b8d97bd2", "predicted_family": "frame", "priority": 0.91970811195, "sample_id": "us-code-18-336-fa27971f56c9178b", "target_family": "deontic", "target_probability": 0.08029188805}`
  evidence: `{"family_margin": -0.587469961488, "hint_id": "modal-synthesis-ca9449edec7bff4c", "predicted_family": "frame", "priority": 0.831268688955, "sample_id": "us-code-25-564u-3e5f6016c5496413", "target_family": "conditional_normative", "target_probability": 0.168731311045}`
- `program-8361f734a0ffb36b`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","deontic->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-95e29681ea723eac` score `0.960326`
  loss: `autoencoder_residual_cluster` = `0.870082345807`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-40-6306-aeae94d6d1d8eb01, us-code-16-460ss-5-a29152ca8faf3653`
  evidence: `{"family_margin": -0.453596737625, "hint_id": "modal-synthesis-442bc6b04737abbf", "predicted_family": "conditional_normative", "priority": 0.757352168122, "sample_id": "us-code-16-460ss-5-a29152ca8faf3653", "target_family": "deontic", "target_probability": 0.242647831878}`
  evidence: `{"family_margin": -0.617808664044, "hint_id": "modal-synthesis-a2a9d72927582b51", "predicted_family": "deontic", "priority": 0.982812523493, "sample_id": "us-code-40-6306-aeae94d6d1d8eb01", "target_family": "conditional_normative", "target_probability": 0.017187476507}`
