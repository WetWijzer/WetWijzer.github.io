# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-748277528fe79902`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","deontic->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-748277528fe79902` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.999385302223`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-15-657d-be08838ed78ea48c, us-code-10-1030-6ebd847628f9a7da`
  evidence: `{"family_margin": -0.997538709134, "hint_id": "modal-synthesis-785f19662bc2ac33", "predicted_family": "deontic", "priority": 0.998770604452, "sample_id": "us-code-10-1030-6ebd847628f9a7da", "target_family": "frame", "target_probability": 0.001229395548}`
  evidence: `{"family_margin": -0.999999999835, "hint_id": "modal-synthesis-7a5f641fb1bda708", "predicted_family": "deontic", "priority": 0.999999999995, "sample_id": "us-code-15-657d-be08838ed78ea48c", "target_family": "temporal", "target_probability": 5e-12}`
