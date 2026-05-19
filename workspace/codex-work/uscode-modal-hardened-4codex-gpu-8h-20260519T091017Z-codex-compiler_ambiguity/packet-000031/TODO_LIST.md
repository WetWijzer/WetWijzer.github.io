# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-54cd2c2e405b10be`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","deontic->conditional_normative","deontic->frame","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-54cd2c2e405b10be` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.617962089579`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-26-651-ec1f77fec5fb0a62, us-code-16-410aaa-50-d93ecd7b2c265bca, us-code-42-8834.-21377f76b0372f94, us-code-6-677g-31d2665e1caccc9c`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-2403288f11cc5b39", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-6-677g-31d2665e1caccc9c", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.856149561517, "hint_id": "modal-synthesis-5e83d1c78190b68e", "predicted_family": "deontic", "priority": 1.006149561517, "sample_id": "us-code-26-651-ec1f77fec5fb0a62", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.572604759408, "hint_id": "modal-synthesis-a7141e5daa46d622", "predicted_family": "conditional_normative", "priority": 0.722604759408, "sample_id": "us-code-16-410aaa-50-d93ecd7b2c265bca", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.443094037392, "hint_id": "modal-synthesis-fd444a6f940ffb32", "predicted_family": "deontic", "priority": 0.593094037392, "sample_id": "us-code-42-8834.-21377f76b0372f94", "target_family": "frame"}`
- `program-9859927cac8fe290`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-54cd2c2e405b10be` score `0.91926`
  loss: `autoencoder_residual_cluster` = `0.128214167767`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-20-5701-168cf2ab50ae0346, us-code-42-290dd.-2810fb987912153f`
  evidence: `{"family_margin": 0.043571664466, "hint_id": "modal-synthesis-77caba25503a5594", "predicted_family": "deontic", "priority": 0.106428335534, "sample_id": "us-code-42-290dd.-2810fb987912153f", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-b0c9e44ad236cd79", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-20-5701-168cf2ab50ae0346", "target_family": "deontic"}`
