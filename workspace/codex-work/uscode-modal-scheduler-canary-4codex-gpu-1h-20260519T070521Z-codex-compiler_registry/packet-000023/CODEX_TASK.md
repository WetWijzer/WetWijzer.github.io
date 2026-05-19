# packet-000023

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary-4codex-gpu-1h-20260519T070521Z-codex-compiler_registry/packet-000023/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary-4codex-gpu-1h-20260519T070521Z-codex-compiler_registry/packet-000023/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary-4codex-gpu-1h-20260519T070521Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000023-20260519_070727

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-5a7c0eb6c0be2972` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->temporal","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5a7c0eb6c0be2972` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.969650667457, "hint_id": "modal-synthesis-32af0111dab5be45", "predicted_family": "temporal", "priority": 0.997961428363, "sample_id": "us-code-49-50101.-bf43ad4fa78dfc58", "target_family": "deontic", "target_probability": 0.002038571637}`
  evidence: `{"family_margin": -0.795302542954, "hint_id": "modal-synthesis-6604b284ec1af42b", "predicted_family": "alethic", "priority": 0.99802374344, "sample_id": "us-code-42-6000-dcd75b3ed70b7a18", "target_family": "temporal", "target_probability": 0.00197625656}`
  evidence: `{"family_margin": -0.39599023273, "hint_id": "modal-synthesis-6748764972049fb4", "predicted_family": "frame", "priority": 0.886264906277, "sample_id": "us-code-37-1003-27a3ce51f0d5bf8b", "target_family": "temporal", "target_probability": 0.113735093723}`
  evidence: `{"family_margin": -0.415268435064, "hint_id": "modal-synthesis-d2f93f1d595a4397", "predicted_family": "temporal", "priority": 0.935003163436, "sample_id": "us-code-10-2709-1aff355b49ebbf04", "target_family": "deontic", "target_probability": 0.064996836564}`
- `program-d9e34da235906d43` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5a7c0eb6c0be2972` score `0.973293`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.370263121745, "hint_id": "modal-synthesis-34d0be50b19174cb", "predicted_family": "frame", "priority": 0.837372251507, "sample_id": "us-code-44-2909.-f0577602d56b513a", "target_family": "deontic", "target_probability": 0.162627748493}`
  evidence: `{"family_margin": -0.957471214953, "hint_id": "modal-synthesis-8acdf5f7a1fab6b0", "predicted_family": "frame", "priority": 0.982089009976, "sample_id": "us-code-33-2341a-994f6f747bb40821", "target_family": "deontic", "target_probability": 0.017910990024}`
  evidence: `{"family_margin": -0.201545898387, "hint_id": "modal-synthesis-e17bd86f8959d12e", "predicted_family": "frame", "priority": 0.929465913907, "sample_id": "us-code-36-150402-30542ec4e64a3fa9", "target_family": "temporal", "target_probability": 0.070534086093}`
- `program-98fdeca6e8b9e4b5` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5a7c0eb6c0be2972` score `0.938862`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.99421734177, "hint_id": "modal-synthesis-20a40ad201178ddd", "predicted_family": "frame", "priority": 0.998170955262, "sample_id": "us-code-33-2282f-4795ec70b8a5c6da", "target_family": "temporal", "target_probability": 0.001829044738}`
  evidence: `{"family_margin": -0.26204093192, "hint_id": "modal-synthesis-7f8eb8eea8ec722f", "predicted_family": "frame", "priority": 0.730930358865, "sample_id": "us-code-20-107e-1-43ac50498bf68122", "target_family": "conditional_normative", "target_probability": 0.269069641135}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
