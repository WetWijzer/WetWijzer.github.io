# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-29b61699ea1f3893`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-29b61699ea1f3893` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.920926371324`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-1462 to 1464.-d3f2aa981c9b2a49, us-code-42-629c.-0c65fdd9d705e10f, us-code-5-3322-9e1940d99b2f959b`
  evidence: `{"family_margin": -0.100948406036, "hint_id": "modal-synthesis-8768c9939816e9b5", "predicted_family": "temporal", "priority": 0.764453719249, "sample_id": "us-code-5-3322-9e1940d99b2f959b", "target_family": "conditional_normative", "target_probability": 0.235546280751}`
  evidence: `{"family_margin": -0.993831777206, "hint_id": "modal-synthesis-c974ea50d7be0636", "predicted_family": "frame", "priority": 0.99899953049, "sample_id": "us-code-42-629c.-0c65fdd9d705e10f", "target_family": "conditional_normative", "target_probability": 0.00100046951}`
  evidence: `{"family_margin": -0.997248992505, "hint_id": "modal-synthesis-fe96efe546093b57", "predicted_family": "frame", "priority": 0.999325864232, "sample_id": "us-code-42-1462 to 1464.-d3f2aa981c9b2a49", "target_family": "conditional_normative", "target_probability": 0.000674135768}`
- `program-3a5ac960b1b59f70`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-29b61699ea1f3893` score `0.93961`
  loss: `autoencoder_residual_cluster` = `0.807545136751`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-49-47145.-6f26cd3923bc5e97, us-code-7-7938-2cfe2905ba85c147, us-code-16-3839bb-4-2e2cffbbcd871d5d, us-code-43-3206.-3d30a15d59827936`
  evidence: `{"family_margin": -0.963701676952, "hint_id": "modal-synthesis-36faac540c2a1781", "predicted_family": "frame", "priority": 0.985631723782, "sample_id": "us-code-49-47145.-6f26cd3923bc5e97", "target_family": "deontic", "target_probability": 0.014368276218}`
  evidence: `{"family_margin": -0.855052736961, "hint_id": "modal-synthesis-979ec08ce8b7f55a", "predicted_family": "deontic", "priority": 0.959604765032, "sample_id": "us-code-7-7938-2cfe2905ba85c147", "target_family": "conditional_normative", "target_probability": 0.040395234968}`
  evidence: `{"family_margin": -0.257220043655, "hint_id": "modal-synthesis-efe187dc28060a0d", "predicted_family": "deontic", "priority": 0.742779956345, "sample_id": "us-code-16-3839bb-4-2e2cffbbcd871d5d", "target_family": "conditional_normative", "target_probability": 0.257220043655}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-f7b5e4668880eca8", "predicted_family": "deontic", "priority": 0.542164101845, "sample_id": "us-code-43-3206.-3d30a15d59827936", "target_family": "deontic", "target_probability": 0.457835898155}`
- `program-3b00d9463252c37c`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-29b61699ea1f3893` score `0.937306`
  loss: `autoencoder_residual_cluster` = `0.889303436024`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-12-4517-b1c5aba229b723b7, us-code-6-591h-bb53b6b6583b4a41, us-code-7-1379c-0abb909cfabdc378, us-code-10-8724-f0e36a7d35395997`
  evidence: `{"family_margin": -0.459134623027, "hint_id": "modal-synthesis-1d3a1bfd8a737748", "predicted_family": "frame", "priority": 0.874518945736, "sample_id": "us-code-7-1379c-0abb909cfabdc378", "target_family": "deontic", "target_probability": 0.125481054264}`
  evidence: `{"family_margin": -0.58228743692, "hint_id": "modal-synthesis-7f4489e68eb151b0", "predicted_family": "deontic", "priority": 0.987339668289, "sample_id": "us-code-6-591h-bb53b6b6583b4a41", "target_family": "frame", "target_probability": 0.012660331711}`
  evidence: `{"family_margin": -0.99126278774, "hint_id": "modal-synthesis-8dddb35b08317294", "predicted_family": "frame", "priority": 0.996290991492, "sample_id": "us-code-12-4517-b1c5aba229b723b7", "target_family": "deontic", "target_probability": 0.003709008508}`
  evidence: `{"family_margin": -0.356459015591, "hint_id": "modal-synthesis-929956092d5a8f7a", "predicted_family": "frame", "priority": 0.699064138578, "sample_id": "us-code-10-8724-f0e36a7d35395997", "target_family": "temporal", "target_probability": 0.300935861422}`
