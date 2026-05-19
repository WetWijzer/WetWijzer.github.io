# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-1d7c7b63b86efff4`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","deontic->conditional_normative","deontic->temporal","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1d7c7b63b86efff4` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.926540963725`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-46-3303.-262060b4e52c28d7, us-code-43-883.-4cf3c55207a7042d, us-code-2-2182-5a4da71f9b7ed715, us-code-50-3533.-fbe9761d5d5aa91b`
  evidence: `{"family_margin": -0.988780738882, "hint_id": "modal-synthesis-63397fdd094905b0", "predicted_family": "frame", "priority": 0.996355208515, "sample_id": "us-code-46-3303.-262060b4e52c28d7", "target_family": "conditional_normative", "target_probability": 0.003644791485}`
  evidence: `{"family_margin": -0.360131386457, "hint_id": "modal-synthesis-7ca49c680b49f476", "predicted_family": "alethic", "priority": 0.76161165946, "sample_id": "us-code-50-3533.-fbe9761d5d5aa91b", "target_family": "deontic", "target_probability": 0.23838834054}`
  evidence: `{"family_margin": -0.75246836579, "hint_id": "modal-synthesis-86644f86470af9de", "predicted_family": "deontic", "priority": 0.973649584925, "sample_id": "us-code-2-2182-5a4da71f9b7ed715", "target_family": "temporal", "target_probability": 0.026350415075}`
  evidence: `{"family_margin": -0.914900774437, "hint_id": "modal-synthesis-e158162074edc44e", "predicted_family": "deontic", "priority": 0.974547402, "sample_id": "us-code-43-883.-4cf3c55207a7042d", "target_family": "conditional_normative", "target_probability": 0.025452598}`
- `program-1491268228188532`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->conditional_normative","deontic->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1d7c7b63b86efff4` score `0.971899`
  loss: `autoencoder_residual_cluster` = `0.544060754135`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-33-4263-53178b47b118c70f, us-code-34-12101-27653168422ea77c, us-code-20-5121-8e05875a84512b39`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-6ad05964012b4b97", "predicted_family": "deontic", "priority": 0.614068880211, "sample_id": "us-code-33-4263-53178b47b118c70f", "target_family": "deontic", "target_probability": 0.385931119789}`
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-90a0e73f7a68b169", "predicted_family": "deontic", "priority": 0.50390312837, "sample_id": "us-code-20-5121-8e05875a84512b39", "target_family": "deontic", "target_probability": 0.49609687163}`
  evidence: `{"family_margin": 0.191143370946, "hint_id": "modal-synthesis-a4424a2fa863d346", "predicted_family": "conditional_normative", "priority": 0.514210253825, "sample_id": "us-code-34-12101-27653168422ea77c", "target_family": "conditional_normative", "target_probability": 0.485789746175}`
