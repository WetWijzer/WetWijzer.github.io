# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-d54a92a96009beaf`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["hybrid->frame","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-d54a92a96009beaf` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.75836678081`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-16-2622-7b3b0068d25f5128, us-code-2-60e-3-49bb3eb4baff92b8`
  evidence: `{"family_margin": -0.216733561973, "hint_id": "modal-synthesis-003d5945a2786d35", "predicted_family": "hybrid", "priority": 0.366733561973, "sample_id": "us-code-2-60e-3-49bb3eb4baff92b8", "target_family": "frame"}`
  evidence: `{"family_margin": -0.999999999646, "hint_id": "modal-synthesis-5541a584b90f7d70", "predicted_family": "temporal", "priority": 1.149999999646, "sample_id": "us-code-16-2622-7b3b0068d25f5128", "target_family": "frame"}`
