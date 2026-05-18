# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-19d5dd97b8be0198`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-19d5dd97b8be0198` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.148769354484`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-15-657d-be08838ed78ea48c, us-code-10-1030-6ebd847628f9a7da`
  evidence: `{"family_margin": -0.997538709134, "hint_id": "modal-synthesis-1dc73c9892eec91a", "predicted_family": "deontic", "priority": 1.147538709134, "sample_id": "us-code-10-1030-6ebd847628f9a7da", "target_family": "frame"}`
  evidence: `{"family_margin": -0.999999999835, "hint_id": "modal-synthesis-8ccd2596d5737855", "predicted_family": "deontic", "priority": 1.149999999835, "sample_id": "us-code-15-657d-be08838ed78ea48c", "target_family": "temporal"}`
