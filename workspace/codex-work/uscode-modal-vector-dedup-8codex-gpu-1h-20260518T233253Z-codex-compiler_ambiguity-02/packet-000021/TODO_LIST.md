# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-3e5c741f5a120905`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-3e5c741f5a120905` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.149761009424`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-18-924-b00c213963a376b4, us-code-42-9412.-43fc03ac808d8959`
  evidence: `{"family_margin": -0.999999999972, "hint_id": "modal-synthesis-3b606f757af372dc", "predicted_family": "deontic", "priority": 1.149999999972, "sample_id": "us-code-18-924-b00c213963a376b4", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.999522018876, "hint_id": "modal-synthesis-865c60dc58c867a0", "predicted_family": "frame", "priority": 1.149522018876, "sample_id": "us-code-42-9412.-43fc03ac808d8959", "target_family": "temporal"}`
- `program-30d0a9ed2815bc30`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-3e5c741f5a120905` score `0.977205`
  loss: `autoencoder_residual_cluster` = `0.802896168795`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-7901-56b92850b247621c, us-code-38-3562-8a247b2f38b8df8e, us-code-7-6414-09089729e9ca74c3`
  evidence: `{"family_margin": -0.963558080623, "hint_id": "modal-synthesis-0bf29c45382bd811", "predicted_family": "deontic", "priority": 1.113558080623, "sample_id": "us-code-22-7901-56b92850b247621c", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.544325473206, "hint_id": "modal-synthesis-1193133c6d53fded", "predicted_family": "frame", "priority": 0.694325473206, "sample_id": "us-code-38-3562-8a247b2f38b8df8e", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.450804952557, "hint_id": "modal-synthesis-bfa4f75c9a413833", "predicted_family": "deontic", "priority": 0.600804952557, "sample_id": "us-code-7-6414-09089729e9ca74c3", "target_family": "temporal"}`
- `program-1648efbbdf0b9136`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","deontic->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-3e5c741f5a120905` score `0.930464`
  loss: `autoencoder_residual_cluster` = `0.994517929407`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-20-1099d-1a13f73711413296, us-code-33-414-265961b5912a94f4, us-code-11-1121-6a8c23d4a586d504, us-code-33-3029-bf3535c0ce8ad1ed`
  evidence: `{"family_margin": -0.37838315063, "hint_id": "modal-synthesis-4d9230c185802ce1", "predicted_family": "deontic", "priority": 0.52838315063, "sample_id": "us-code-33-3029-bf3535c0ce8ad1ed", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999752379489, "hint_id": "modal-synthesis-9e1d5616e9ec2cd1", "predicted_family": "temporal", "priority": 1.149752379489, "sample_id": "us-code-11-1121-6a8c23d4a586d504", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999999999995, "hint_id": "modal-synthesis-b3b0cb43c3762898", "predicted_family": "deontic", "priority": 1.149999999995, "sample_id": "us-code-20-1099d-1a13f73711413296", "target_family": "frame"}`
  evidence: `{"family_margin": -0.999936187516, "hint_id": "modal-synthesis-cd5fb93900869166", "predicted_family": "deontic", "priority": 1.149936187516, "sample_id": "us-code-33-414-265961b5912a94f4", "target_family": "temporal"}`
