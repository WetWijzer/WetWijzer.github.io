# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-da3192c3055a944d`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-da3192c3055a944d` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.871429205915`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-1-113-cd403ab39cd45f1c, us-code-12-338-e9f61eb9e13a678a, us-code-22-801-5e460b92fcea13cc, us-code-22-7707-cdc74b8d1b080e59`
  evidence: `{"family_margin": -0.046351027126, "hint_id": "modal-synthesis-07913e5b8ff6d18e", "predicted_family": "deontic", "priority": 0.721893837244, "sample_id": "us-code-22-7707-cdc74b8d1b080e59", "target_family": "temporal", "target_probability": 0.278106162756}`
  evidence: `{"family_margin": -0.447743270967, "hint_id": "modal-synthesis-6fd85952e88d79aa", "predicted_family": "conditional_normative", "priority": 0.813440303764, "sample_id": "us-code-22-801-5e460b92fcea13cc", "target_family": "temporal", "target_probability": 0.186559696236}`
  evidence: `{"family_margin": -0.565158419096, "hint_id": "modal-synthesis-cc12bef224da2804", "predicted_family": "deontic", "priority": 0.950474057984, "sample_id": "us-code-12-338-e9f61eb9e13a678a", "target_family": "temporal", "target_probability": 0.049525942016}`
  evidence: `{"family_margin": -0.999373752102, "hint_id": "modal-synthesis-e9988cb9157dfe8b", "predicted_family": "frame", "priority": 0.999908624669, "sample_id": "us-code-1-113-cd403ab39cd45f1c", "target_family": "temporal", "target_probability": 9.1375331e-05}`
- `program-2380152b1f4e4cff`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->deontic","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-da3192c3055a944d` score `0.975418`
  loss: `autoencoder_residual_cluster` = `0.736871031521`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-50-47c.-dad134a96a1b873e, us-code-16-460uu-43-fb997cc1fd28fc71, us-code-10-9414b-072e75b5332bc57b`
  evidence: `{"family_margin": -0.136085692421, "hint_id": "modal-synthesis-0199a96a33dc599d", "predicted_family": "deontic", "priority": 0.727828615158, "sample_id": "us-code-16-460uu-43-fb997cc1fd28fc71", "target_family": "conditional_normative", "target_probability": 0.272171384842}`
  evidence: `{"family_margin": -0.731688096648, "hint_id": "modal-synthesis-2ddfbf9ae42e18e4", "predicted_family": "frame", "priority": 0.956484107946, "sample_id": "us-code-50-47c.-dad134a96a1b873e", "target_family": "conditional_normative", "target_probability": 0.043515892054}`
  evidence: `{"family_margin": 0.128767093112, "hint_id": "modal-synthesis-e78ac69ffa173d3a", "predicted_family": "deontic", "priority": 0.52630037146, "sample_id": "us-code-10-9414b-072e75b5332bc57b", "target_family": "deontic", "target_probability": 0.47369962854}`
