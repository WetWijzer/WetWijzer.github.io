# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-6adb2f0085805d94`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-6adb2f0085805d94` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.974220251361`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-29-1851-f2b8bca48c79ea5b, us-code-20-1087cc-7df79972ab6270a9`
  evidence: `{"family_margin": -0.98293533675, "hint_id": "modal-synthesis-50cc0076dfa2fb69", "predicted_family": "frame", "priority": 0.999335540198, "sample_id": "us-code-29-1851-f2b8bca48c79ea5b", "target_family": "epistemic", "target_probability": 0.000664459802}`
  evidence: `{"family_margin": -0.788983986003, "hint_id": "modal-synthesis-f0fea968e172dbe9", "predicted_family": "frame", "priority": 0.949104962523, "sample_id": "us-code-20-1087cc-7df79972ab6270a9", "target_family": "deontic", "target_probability": 0.050895037477}`
- `program-459322b0177702ff`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-6adb2f0085805d94` score `0.932947`
  loss: `autoencoder_residual_cluster` = `0.873538051977`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-50-855.-6b18aaa5a6c9cf83, us-code-43-326.-5500eb218f8a7886, us-code-22-4071k-55a17ec8c5e3db3e, us-code-50-3305.-3e025318340f6f2a`
  evidence: `{"family_margin": -0.376889143959, "hint_id": "modal-synthesis-3a31ed870ee84a20", "predicted_family": "frame", "priority": 0.917791077775, "sample_id": "us-code-22-4071k-55a17ec8c5e3db3e", "target_family": "temporal", "target_probability": 0.082208922225}`
  evidence: `{"family_margin": -0.992896805877, "hint_id": "modal-synthesis-56a34ac03a423e9e", "predicted_family": "frame", "priority": 0.99932880629, "sample_id": "us-code-50-855.-6b18aaa5a6c9cf83", "target_family": "deontic", "target_probability": 0.00067119371}`
  evidence: `{"family_margin": -0.436671018642, "hint_id": "modal-synthesis-6d2b8d4def6ae606", "predicted_family": "temporal", "priority": 0.968306905012, "sample_id": "us-code-43-326.-5500eb218f8a7886", "target_family": "conditional_normative", "target_probability": 0.031693094988}`
  evidence: `{"family_margin": -0.18481454784, "hint_id": "modal-synthesis-c87cbfc171aa17a2", "predicted_family": "frame", "priority": 0.608725418832, "sample_id": "us-code-50-3305.-3e025318340f6f2a", "target_family": "temporal", "target_probability": 0.391274581168}`
- `program-7449908df84e1d1b`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->temporal","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-6adb2f0085805d94` score `0.917552`
  loss: `autoencoder_residual_cluster` = `0.892896823633`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-1396u-57bec3d2de18e889, us-code-2-5303-d859402e8a787491, us-code-42-11043.-a349cc422cfb814d, us-code-22-9614-25ece758489d6025`
  evidence: `{"family_margin": -0.907679549796, "hint_id": "modal-synthesis-10c41a9ca37bfa75", "predicted_family": "frame", "priority": 0.999665223016, "sample_id": "us-code-42-1396u-57bec3d2de18e889", "target_family": "deontic", "target_probability": 0.000334776984}`
  evidence: `{"family_margin": -0.495628881718, "hint_id": "modal-synthesis-289dd1c70315c638", "predicted_family": "temporal", "priority": 0.990228790792, "sample_id": "us-code-2-5303-d859402e8a787491", "target_family": "deontic", "target_probability": 0.009771209208}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-83c93de522d2bdcf", "predicted_family": "deontic", "priority": 0.682800890818, "sample_id": "us-code-22-9614-25ece758489d6025", "target_family": "deontic", "target_probability": 0.317199109182}`
  evidence: `{"family_margin": -0.480261147937, "hint_id": "modal-synthesis-8443a92785660a75", "predicted_family": "deontic", "priority": 0.898892389908, "sample_id": "us-code-42-11043.-a349cc422cfb814d", "target_family": "temporal", "target_probability": 0.101107610092}`
