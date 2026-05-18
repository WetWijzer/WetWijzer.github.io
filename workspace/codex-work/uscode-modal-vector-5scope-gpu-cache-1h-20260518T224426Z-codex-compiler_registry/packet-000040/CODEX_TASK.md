# packet-000040

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_registry/packet-000040/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_registry/packet-000040/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000040-20260518_232336

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-2ebe9629ff0ba7cb` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2ebe9629ff0ba7cb` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.982395937648, "hint_id": "modal-synthesis-0fabb85f03b858fe", "predicted_family": "temporal", "priority": 0.993335764978, "sample_id": "us-code-5-8338-8843bfb9fff586e8", "target_family": "conditional_normative", "target_probability": 0.006664235022}`
  evidence: `{"family_margin": -0.984495929302, "hint_id": "modal-synthesis-577270b2ccd71baa", "predicted_family": "frame", "priority": 0.998277325478, "sample_id": "us-code-25-2402-d2b0b613bb62b381", "target_family": "temporal", "target_probability": 0.001722674522}`
  evidence: `{"family_margin": -0.998993452095, "hint_id": "modal-synthesis-d63685767cd6852e", "predicted_family": "frame", "priority": 0.999796695066, "sample_id": "us-code-20-5207-97035bc3bbe5872e", "target_family": "temporal", "target_probability": 0.000203304934}`
- `program-04ede4cf992be8e5` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2ebe9629ff0ba7cb` score `0.99269`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.644460457227, "hint_id": "modal-synthesis-0d9a4e4c9728db44", "predicted_family": "frame", "priority": 0.928187279402, "sample_id": "us-code-33-1473-42801b64a1a4742c", "target_family": "temporal", "target_probability": 0.071812720598}`
  evidence: `{"family_margin": -0.349808843776, "hint_id": "modal-synthesis-3917933defac1ecb", "predicted_family": "temporal", "priority": 0.796419401065, "sample_id": "us-code-26-3241-51490ac6cfd08db1", "target_family": "conditional_normative", "target_probability": 0.203580598935}`
  evidence: `{"family_margin": -0.783753059191, "hint_id": "modal-synthesis-e7baf6389155d4bc", "predicted_family": "frame", "priority": 0.999470186509, "sample_id": "us-code-42-290aa-78672295385145a2", "target_family": "temporal", "target_probability": 0.000529813491}`
- `program-31f5eaba6c5b3787` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2ebe9629ff0ba7cb` score `0.986915`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.044252858749, "hint_id": "modal-synthesis-466d5cec336082f5", "predicted_family": "frame", "priority": 0.579229129511, "sample_id": "us-code-18-5041-b043586cd971c29a", "target_family": "temporal", "target_probability": 0.420770870489}`
  evidence: `{"family_margin": -0.998958579084, "hint_id": "modal-synthesis-cd3482ec15b39262", "predicted_family": "frame", "priority": 0.999751680272, "sample_id": "us-code-20-1098cc-ec3688903d9caaf0", "target_family": "conditional_normative", "target_probability": 0.000248319728}`
  evidence: `{"family_margin": -0.92798749191, "hint_id": "modal-synthesis-cfba7d86d1aea6fc", "predicted_family": "frame", "priority": 0.964462132888, "sample_id": "us-code-7-511s-d96fcc7f71d0b18b", "target_family": "deontic", "target_probability": 0.035537867112}`
- `program-83ef36dcabb3cc3d` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2ebe9629ff0ba7cb` score `0.985489`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-1b22864b5e60da55", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-15-9005-5ad28bbe0beec57b", "target_family": "temporal", "target_probability": 0.008091643722}`
  evidence: `{"family_margin": -0.906912785226, "hint_id": "modal-synthesis-f64bcc8e54a4cff5", "predicted_family": "frame", "priority": 0.999386931096, "sample_id": "us-code-42-289c.-57f0e54146415340", "target_family": "conditional_normative", "target_probability": 0.000613068904}`
- `program-72067dab8cd03903` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2ebe9629ff0ba7cb` score `0.984166`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.56927588958, "hint_id": "modal-synthesis-0371e2a0fa6e7a9e", "predicted_family": "frame", "priority": 0.998952712826, "sample_id": "us-code-50-2656.-10e19e6cd88e6b96", "target_family": "temporal", "target_probability": 0.001047287174}`
  evidence: `{"family_margin": -0.757541915301, "hint_id": "modal-synthesis-3f07d2544d0d950d", "predicted_family": "deontic", "priority": 0.960308063726, "sample_id": "us-code-2-1511-313ca032e8ac0971", "target_family": "temporal", "target_probability": 0.039691936274}`
  evidence: `{"family_margin": -0.495914480481, "hint_id": "modal-synthesis-ef5dc54a07ac6785", "predicted_family": "conditional_normative", "priority": 0.997383951879, "sample_id": "us-code-46-7113.-352a3c716bd8efb0", "target_family": "temporal", "target_probability": 0.002616048121}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
