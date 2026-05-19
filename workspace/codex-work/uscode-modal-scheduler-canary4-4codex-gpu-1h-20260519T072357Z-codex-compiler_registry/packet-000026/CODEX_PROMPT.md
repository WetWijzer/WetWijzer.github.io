# packet-000026

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/packet-000026/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/packet-000026/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000026-20260519_072617

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-8ee4c11758e233dd` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8ee4c11758e233dd` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-8fd83335bf3837a9", "predicted_family": "frame", "priority": 0.851064907891, "sample_id": "us-code-14-2738-a8d887e67903d179", "target_family": "deontic", "target_probability": 0.148935092109}`
  evidence: `{"family_margin": -0.158692188725, "hint_id": "modal-synthesis-c355e5e59423a80f", "predicted_family": "frame", "priority": 0.755376930135, "sample_id": "us-code-28-107-589461080f66274a", "target_family": "deontic", "target_probability": 0.244623069865}`
  evidence: `{"family_margin": -0.437373806715, "hint_id": "modal-synthesis-dcaee4f18122e8ef", "predicted_family": "frame", "priority": 0.951263102916, "sample_id": "us-code-22-3145-1a5a37638bc87aa3", "target_family": "temporal", "target_probability": 0.048736897084}`
  evidence: `{"family_margin": -0.941680926619, "hint_id": "modal-synthesis-e27f38f9fd6fefca", "predicted_family": "frame", "priority": 0.993595314065, "sample_id": "us-code-49-13904.-4e1b7e85f94fb3a8", "target_family": "deontic", "target_probability": 0.006404685935}`
- `program-b0d8db32a2078edd` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8ee4c11758e233dd` score `0.967006`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.626923020311, "hint_id": "modal-synthesis-0eac5c9805859b2b", "predicted_family": "deontic", "priority": 0.874615395938, "sample_id": "us-code-43-618d.-4e9855b3ebb224b2", "target_family": "conditional_normative", "target_probability": 0.125384604062}`
  evidence: `{"family_margin": 0.059733617643, "hint_id": "modal-synthesis-1e0ddf3848685f04", "predicted_family": "deontic", "priority": 0.66628101796, "sample_id": "us-code-15-278g-2-a465705dc02eccad", "target_family": "deontic", "target_probability": 0.33371898204}`
  evidence: `{"family_margin": -0.88083267146, "hint_id": "modal-synthesis-6899fe5e537134cd", "predicted_family": "temporal", "priority": 0.994024735127, "sample_id": "us-code-46-53111.-d55f3d8fd634aec0", "target_family": "deontic", "target_probability": 0.005975264873}`
- `program-b34aea7872e9dd20` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8ee4c11758e233dd` score `0.94161`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.94805249433, "hint_id": "modal-synthesis-0d40bb58ea82151b", "predicted_family": "frame", "priority": 0.994848590418, "sample_id": "us-code-38-1722A-36a73cb7e6dbf73e", "target_family": "conditional_normative", "target_probability": 0.005151409582}`
  evidence: `{"family_margin": -0.449666884353, "hint_id": "modal-synthesis-669cb82e41b9d09e", "predicted_family": "frame", "priority": 0.802496363587, "sample_id": "us-code-29-794c-686bfc4da3dd44d6", "target_family": "deontic", "target_probability": 0.197503636413}`

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

- Queue run: `uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-8ee4c11758e233dd`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8ee4c11758e233dd` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.887825063752`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-49-13904.-4e1b7e85f94fb3a8, us-code-22-3145-1a5a37638bc87aa3, us-code-14-2738-a8d887e67903d179, us-code-28-107-589461080f66274a`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-8fd83335bf3837a9", "predicted_family": "frame", "priority": 0.851064907891, "sample_id": "us-code-14-2738-a8d887e67903d179", "target_family": "deontic", "target_probability": 0.148935092109}`
  evidence: `{"family_margin": -0.158692188725, "hint_id": "modal-synthesis-c355e5e59423a80f", "predicted_family": "frame", "priority": 0.755376930135, "sample_id": "us-code-28-107-589461080f66274a", "target_family": "deontic", "target_probability": 0.244623069865}`
  evidence: `{"family_margin": -0.437373806715, "hint_id": "modal-synthesis-dcaee4f18122e8ef", "predicted_family": "frame", "priority": 0.951263102916, "sample_id": "us-code-22-3145-1a5a37638bc87aa3", "target_family": "temporal", "target_probability": 0.048736897084}`
  evidence: `{"family_margin": -0.941680926619, "hint_id": "modal-synthesis-e27f38f9fd6fefca", "predicted_family": "frame", "priority": 0.993595314065, "sample_id": "us-code-49-13904.-4e1b7e85f94fb3a8", "target_family": "deontic", "target_probability": 0.006404685935}`
- `program-b0d8db32a2078edd`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8ee4c11758e233dd` score `0.967006`
  loss: `autoencoder_residual_cluster` = `0.844973716342`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-46-53111.-d55f3d8fd634aec0, us-code-43-618d.-4e9855b3ebb224b2, us-code-15-278g-2-a465705dc02eccad`
  evidence: `{"family_margin": -0.626923020311, "hint_id": "modal-synthesis-0eac5c9805859b2b", "predicted_family": "deontic", "priority": 0.874615395938, "sample_id": "us-code-43-618d.-4e9855b3ebb224b2", "target_family": "conditional_normative", "target_probability": 0.125384604062}`
  evidence: `{"family_margin": 0.059733617643, "hint_id": "modal-synthesis-1e0ddf3848685f04", "predicted_family": "deontic", "priority": 0.66628101796, "sample_id": "us-code-15-278g-2-a465705dc02eccad", "target_family": "deontic", "target_probability": 0.33371898204}`
  evidence: `{"family_margin": -0.88083267146, "hint_id": "modal-synthesis-6899fe5e537134cd", "predicted_family": "temporal", "priority": 0.994024735127, "sample_id": "us-code-46-53111.-d55f3d8fd634aec0", "target_family": "deontic", "target_probability": 0.005975264873}`
- `program-b34aea7872e9dd20`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8ee4c11758e233dd` score `0.94161`
  loss: `autoencoder_residual_cluster` = `0.898672477003`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-38-1722A-36a73cb7e6dbf73e, us-code-29-794c-686bfc4da3dd44d6`
  evidence: `{"family_margin": -0.94805249433, "hint_id": "modal-synthesis-0d40bb58ea82151b", "predicted_family": "frame", "priority": 0.994848590418, "sample_id": "us-code-38-1722A-36a73cb7e6dbf73e", "target_family": "conditional_normative", "target_probability": 0.005151409582}`
  evidence: `{"family_margin": -0.449666884353, "hint_id": "modal-synthesis-669cb82e41b9d09e", "predicted_family": "frame", "priority": 0.802496363587, "sample_id": "us-code-29-794c-686bfc4da3dd44d6", "target_family": "deontic", "target_probability": 0.197503636413}`
