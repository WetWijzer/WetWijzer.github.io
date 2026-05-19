# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-5c90599b77c1b484`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5c90599b77c1b484` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.99968162822`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-12-4903-c51b25897c2970fa, us-code-42-10905.-8d64d69700c2a65f, us-code-42-19038.-c2a8a75459132351`
  evidence: `{"family_margin": -0.996964123361, "hint_id": "modal-synthesis-49451289e81526f8", "predicted_family": "conditional_normative", "priority": 0.999943660133, "sample_id": "us-code-12-4903-c51b25897c2970fa", "target_family": "deontic", "target_probability": 5.6339867e-05}`
  evidence: `{"family_margin": -0.992795485564, "hint_id": "modal-synthesis-a1ddacad1d54ddf5", "predicted_family": "temporal", "priority": 0.999774584604, "sample_id": "us-code-42-10905.-8d64d69700c2a65f", "target_family": "deontic", "target_probability": 0.000225415396}`
  evidence: `{"family_margin": -0.996101512482, "hint_id": "modal-synthesis-d62b80d082e62720", "predicted_family": "frame", "priority": 0.999326639923, "sample_id": "us-code-42-19038.-c2a8a75459132351", "target_family": "conditional_normative", "target_probability": 0.000673360077}`
- `program-d1e0789cd1f60b69`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-5c90599b77c1b484` score `0.986374`
  loss: `autoencoder_residual_cluster` = `0.872518183983`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-4369.-7326d01e59fb968d, us-code-22-2719c-3a5433eebe61d2d1, us-code-16-460ccc-2-50d796783c99a93f`
  evidence: `{"family_margin": -0.993897627543, "hint_id": "modal-synthesis-ab0ad5c6c2c0384f", "predicted_family": "frame", "priority": 0.999957075933, "sample_id": "us-code-42-4369.-7326d01e59fb968d", "target_family": "temporal", "target_probability": 4.2924067e-05}`
  evidence: `{"family_margin": -0.401650452649, "hint_id": "modal-synthesis-da693c2c8b6d575f", "predicted_family": "conditional_normative", "priority": 0.73412818631, "sample_id": "us-code-16-460ccc-2-50d796783c99a93f", "target_family": "deontic", "target_probability": 0.26587181369}`
  evidence: `{"family_margin": -0.699184261763, "hint_id": "modal-synthesis-fbf855ab4459409e", "predicted_family": "deontic", "priority": 0.883469289706, "sample_id": "us-code-22-2719c-3a5433eebe61d2d1", "target_family": "temporal", "target_probability": 0.116530710294}`
