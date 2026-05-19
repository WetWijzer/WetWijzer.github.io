# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-1ac8a05c998e789a`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->temporal","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1ac8a05c998e789a` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.995714422896`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-18-956-b86919ed0b6b3fa9, us-code-28-1738-a2fdec05f100f657, us-code-49-20101.-2ac3d3010e2c3de8`
  evidence: `{"family_margin": -0.999907091831, "hint_id": "modal-synthesis-58acc60613533975", "predicted_family": "frame", "priority": 0.99999700956, "sample_id": "us-code-18-956-b86919ed0b6b3fa9", "target_family": "temporal", "target_probability": 2.99044e-06}`
  evidence: `{"family_margin": -0.99240219376, "hint_id": "modal-synthesis-824e05365046043e", "predicted_family": "frame", "priority": 0.998174294559, "sample_id": "us-code-28-1738-a2fdec05f100f657", "target_family": "deontic", "target_probability": 0.001825705441}`
  evidence: `{"family_margin": -0.795219252903, "hint_id": "modal-synthesis-a5edf613869b6a2e", "predicted_family": "alethic", "priority": 0.98897196457, "sample_id": "us-code-49-20101.-2ac3d3010e2c3de8", "target_family": "temporal", "target_probability": 0.01102803543}`
- `program-34d9980c5468c3b7`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1ac8a05c998e789a` score `0.984846`
  loss: `autoencoder_residual_cluster` = `0.777160354639`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-19-2372-7a8bb398787d1d34, us-code-26-2010-1d49b3824d22c29f, us-code-36-230310-1fc4e0a5e5a733b8`
  evidence: `{"family_margin": -0.284224385856, "hint_id": "modal-synthesis-14a614d0e9f9734f", "predicted_family": "conditional_normative", "priority": 0.878189548919, "sample_id": "us-code-19-2372-7a8bb398787d1d34", "target_family": "temporal", "target_probability": 0.121810451081}`
  evidence: `{"family_margin": -0.228446639842, "hint_id": "modal-synthesis-3996d297b1781cdf", "predicted_family": "frame", "priority": 0.647850856509, "sample_id": "us-code-36-230310-1fc4e0a5e5a733b8", "target_family": "deontic", "target_probability": 0.352149143491}`
  evidence: `{"family_margin": -0.137812866903, "hint_id": "modal-synthesis-9b84848afdc89bd1", "predicted_family": "temporal", "priority": 0.805440658489, "sample_id": "us-code-26-2010-1d49b3824d22c29f", "target_family": "deontic", "target_probability": 0.194559341511}`
