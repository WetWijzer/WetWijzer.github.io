# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-27d76aa2ec8e3669`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-27d76aa2ec8e3669` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.124773769714`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-47-252.-c6634f17d18802f6, us-code-14-5115-dc68d6f5c123e226`
  evidence: `{"family_margin": -0.999999999999, "hint_id": "modal-synthesis-5c7995d5bc4d63dd", "predicted_family": "deontic", "priority": 1.149999999999, "sample_id": "us-code-47-252.-c6634f17d18802f6", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.949547539428, "hint_id": "modal-synthesis-762185fed4288e7f", "predicted_family": "deontic", "priority": 1.099547539428, "sample_id": "us-code-14-5115-dc68d6f5c123e226", "target_family": "conditional_normative"}`
