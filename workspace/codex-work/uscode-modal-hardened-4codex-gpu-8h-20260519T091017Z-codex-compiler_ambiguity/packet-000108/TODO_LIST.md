# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-686e83a07f71f9b7`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->temporal","deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-686e83a07f71f9b7` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.061652217994`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-15-2625-828287ed4e5bfa4c, us-code-29-718-b58562ccab445aec, us-code-42-1962c-a74c16e37e82d6a3`
  evidence: `{"family_margin": -0.955419320628, "hint_id": "modal-synthesis-504c188faf472026", "predicted_family": "alethic", "priority": 1.105419320628, "sample_id": "us-code-15-2625-828287ed4e5bfa4c", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.833750467481, "hint_id": "modal-synthesis-a124116375f16f4d", "predicted_family": "deontic", "priority": 0.983750467481, "sample_id": "us-code-42-1962c-a74c16e37e82d6a3", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.945786865874, "hint_id": "modal-synthesis-b0166aedcdab44cf", "predicted_family": "frame", "priority": 1.095786865874, "sample_id": "us-code-29-718-b58562ccab445aec", "target_family": "conditional_normative"}`
- `program-b646f04aa15b7910`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","frame->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-686e83a07f71f9b7` score `0.97344`
  loss: `autoencoder_residual_cluster` = `0.467290090105`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-15-4601-6e7f8f28b8562add, us-code-42-300gg-5bf9852741930d4a`
  evidence: `{"family_margin": -0.453607166209, "hint_id": "modal-synthesis-ca46fd3c2cce150f", "predicted_family": "frame", "priority": 0.603607166209, "sample_id": "us-code-15-4601-6e7f8f28b8562add", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.180973014, "hint_id": "modal-synthesis-fa883b5d7e707f69", "predicted_family": "conditional_normative", "priority": 0.330973014, "sample_id": "us-code-42-300gg-5bf9852741930d4a", "target_family": "deontic"}`
