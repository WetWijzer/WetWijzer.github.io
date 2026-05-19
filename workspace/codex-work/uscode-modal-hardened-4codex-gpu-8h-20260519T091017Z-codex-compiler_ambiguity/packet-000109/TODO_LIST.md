# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-2fb35f97044a33c7`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->dynamic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-2fb35f97044a33c7` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.812092966319`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-1437u.-0904464f49467b7f, us-code-5-556-333c12c1b5eab192, us-code-12-2403-0e192b428d978f5b, us-code-42-9858h.-c26cffb188ec1c8c`
  evidence: `{"family_margin": -0.986993978813, "hint_id": "modal-synthesis-29e62c2a2f843120", "predicted_family": "frame", "priority": 1.136993978813, "sample_id": "us-code-5-556-333c12c1b5eab192", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999091091691, "hint_id": "modal-synthesis-2c61528fe24eae81", "predicted_family": "frame", "priority": 1.149091091691, "sample_id": "us-code-42-1437u.-0904464f49467b7f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.431079117926, "hint_id": "modal-synthesis-e93601256162f4c3", "predicted_family": "deontic", "priority": 0.581079117926, "sample_id": "us-code-12-2403-0e192b428d978f5b", "target_family": "dynamic"}`
  evidence: `{"family_margin": -0.231207676845, "hint_id": "modal-synthesis-f7f9529819567f1a", "predicted_family": "deontic", "priority": 0.381207676845, "sample_id": "us-code-42-9858h.-c26cffb188ec1c8c", "target_family": "conditional_normative"}`
