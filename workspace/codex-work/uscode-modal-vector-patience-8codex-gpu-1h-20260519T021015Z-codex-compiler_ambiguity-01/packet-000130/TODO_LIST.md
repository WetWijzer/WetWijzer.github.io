# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-4f22b8b0f8d3efd3`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4f22b8b0f8d3efd3` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.145287040469`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-12-4903-c51b25897c2970fa, us-code-42-19038.-c2a8a75459132351, us-code-42-10905.-8d64d69700c2a65f`
  evidence: `{"family_margin": -0.996101512482, "hint_id": "modal-synthesis-9b935e21b9e0de1a", "predicted_family": "frame", "priority": 1.146101512482, "sample_id": "us-code-42-19038.-c2a8a75459132351", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.992795485564, "hint_id": "modal-synthesis-c6d99be15849ac5e", "predicted_family": "temporal", "priority": 1.142795485564, "sample_id": "us-code-42-10905.-8d64d69700c2a65f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.996964123361, "hint_id": "modal-synthesis-faa8120d3ad0236a", "predicted_family": "conditional_normative", "priority": 1.146964123361, "sample_id": "us-code-12-4903-c51b25897c2970fa", "target_family": "deontic"}`
- `program-e21d1db86265d12c`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4f22b8b0f8d3efd3` score `0.992702`
  loss: `autoencoder_residual_cluster` = `0.848244113985`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-4369.-7326d01e59fb968d, us-code-22-2719c-3a5433eebe61d2d1, us-code-16-460ccc-2-50d796783c99a93f`
  evidence: `{"family_margin": -0.993897627543, "hint_id": "modal-synthesis-4177e249d3f52c6f", "predicted_family": "frame", "priority": 1.143897627543, "sample_id": "us-code-42-4369.-7326d01e59fb968d", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.699184261763, "hint_id": "modal-synthesis-4b7caab715f569b0", "predicted_family": "deontic", "priority": 0.849184261763, "sample_id": "us-code-22-2719c-3a5433eebe61d2d1", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.401650452649, "hint_id": "modal-synthesis-be8d5145a0dbad42", "predicted_family": "conditional_normative", "priority": 0.551650452649, "sample_id": "us-code-16-460ccc-2-50d796783c99a93f", "target_family": "deontic"}`
