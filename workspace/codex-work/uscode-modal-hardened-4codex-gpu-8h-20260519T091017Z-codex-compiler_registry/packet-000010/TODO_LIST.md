# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-00007f4b0c9438d9`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->frame","deontic->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-00007f4b0c9438d9` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.777818096518`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-4-121-170a4e23192216c5, us-code-15-4013-b282352ae7d2472d`
  evidence: `{"family_margin": 0.175919526786, "hint_id": "modal-synthesis-f38481d1369f406c", "predicted_family": "deontic", "priority": 0.560201183035, "sample_id": "us-code-15-4013-b282352ae7d2472d", "target_family": "deontic", "target_probability": 0.439798816965}`
  evidence: `{"family_margin": -0.528079517054, "hint_id": "modal-synthesis-f701427e888a4e20", "predicted_family": "conditional_normative", "priority": 0.995435010002, "sample_id": "us-code-4-121-170a4e23192216c5", "target_family": "frame", "target_probability": 0.004564989998}`
- `program-74d7b20cc06e0b12`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-00007f4b0c9438d9` score `0.980926`
  loss: `autoencoder_residual_cluster` = `0.763306235049`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-22-1642e-0a4a6e0aa906f829, us-code-16-198a-69c109aec60f214a`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-26089b78405fe36e", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-16-198a-69c109aec60f214a", "target_family": "frame", "target_probability": 0.470915888067}`
  evidence: `{"family_margin": -0.706858138788, "hint_id": "modal-synthesis-57b258b987509f58", "predicted_family": "deontic", "priority": 0.997528358164, "sample_id": "us-code-22-1642e-0a4a6e0aa906f829", "target_family": "frame", "target_probability": 0.002471641836}`
