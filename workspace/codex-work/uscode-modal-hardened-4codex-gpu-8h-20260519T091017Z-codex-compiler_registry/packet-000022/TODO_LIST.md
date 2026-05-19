# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-c867b6a350bd0a60`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->temporal","deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-c867b6a350bd0a60` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.990950928817`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-29-718-b58562ccab445aec, us-code-15-2625-828287ed4e5bfa4c, us-code-42-1962c-a74c16e37e82d6a3`
  evidence: `{"family_margin": -0.833750467481, "hint_id": "modal-synthesis-3bf15b259da08789", "predicted_family": "deontic", "priority": 0.976805008724, "sample_id": "us-code-42-1962c-a74c16e37e82d6a3", "target_family": "conditional_normative", "target_probability": 0.023194991276}`
  evidence: `{"family_margin": -0.955419320628, "hint_id": "modal-synthesis-b1597749450f163f", "predicted_family": "alethic", "priority": 0.996687125333, "sample_id": "us-code-15-2625-828287ed4e5bfa4c", "target_family": "temporal", "target_probability": 0.003312874667}`
  evidence: `{"family_margin": -0.945786865874, "hint_id": "modal-synthesis-f0156f14297b9a6d", "predicted_family": "frame", "priority": 0.999360652395, "sample_id": "us-code-29-718-b58562ccab445aec", "target_family": "conditional_normative", "target_probability": 0.000639347605}`
- `program-a0d6f347c1ce6b83`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-c867b6a350bd0a60` score `0.962727`
  loss: `autoencoder_residual_cluster` = `0.808177064344`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-15-4601-6e7f8f28b8562add, us-code-42-300gg-5bf9852741930d4a`
  evidence: `{"family_margin": -0.453607166209, "hint_id": "modal-synthesis-01d90e51cc27dafd", "predicted_family": "frame", "priority": 0.869716348288, "sample_id": "us-code-15-4601-6e7f8f28b8562add", "target_family": "epistemic", "target_probability": 0.130283651712}`
  evidence: `{"family_margin": -0.180973014, "hint_id": "modal-synthesis-41f6222d1e57ac89", "predicted_family": "conditional_normative", "priority": 0.7466377804, "sample_id": "us-code-42-300gg-5bf9852741930d4a", "target_family": "deontic", "target_probability": 0.2533622196}`
- `program-5d6d0e65b9246c9c`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->dynamic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-c867b6a350bd0a60` score `0.957901`
  loss: `autoencoder_residual_cluster` = `0.96754537071`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-1437u.-0904464f49467b7f, us-code-5-556-333c12c1b5eab192, us-code-12-2403-0e192b428d978f5b, us-code-42-9858h.-c26cffb188ec1c8c`
  evidence: `{"family_margin": -0.999091091691, "hint_id": "modal-synthesis-4aa33a2b7a967804", "predicted_family": "frame", "priority": 0.999920600418, "sample_id": "us-code-42-1437u.-0904464f49467b7f", "target_family": "deontic", "target_probability": 7.9399582e-05}`
  evidence: `{"family_margin": -0.231207676845, "hint_id": "modal-synthesis-6a4605724aeba8fb", "predicted_family": "deontic", "priority": 0.884396161578, "sample_id": "us-code-42-9858h.-c26cffb188ec1c8c", "target_family": "conditional_normative", "target_probability": 0.115603838422}`
  evidence: `{"family_margin": -0.986993978813, "hint_id": "modal-synthesis-9512820d86a4b479", "predicted_family": "frame", "priority": 0.995812470179, "sample_id": "us-code-5-556-333c12c1b5eab192", "target_family": "deontic", "target_probability": 0.004187529821}`
  evidence: `{"family_margin": -0.431079117926, "hint_id": "modal-synthesis-aa8b247ddb3a2304", "predicted_family": "deontic", "priority": 0.990052250667, "sample_id": "us-code-12-2403-0e192b428d978f5b", "target_family": "dynamic", "target_probability": 0.009947749333}`
