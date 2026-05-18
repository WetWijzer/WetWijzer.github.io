# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-89ee4a8b30571264`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["hybrid->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-89ee4a8b30571264` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.366733561973`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-5771.-02e64c6fbb913aae, us-code-36-30104-bb1cedfd16c58ba3`
  evidence: `{"family_margin": -0.216733561973, "hint_id": "modal-synthesis-81b2bfe7074c603d", "predicted_family": "hybrid", "priority": 0.366733561973, "sample_id": "us-code-42-5771.-02e64c6fbb913aae", "target_family": "frame"}`
  evidence: `{"family_margin": -0.216733561973, "hint_id": "modal-synthesis-9b29a936ddca7ed0", "predicted_family": "hybrid", "priority": 0.366733561973, "sample_id": "us-code-36-30104-bb1cedfd16c58ba3", "target_family": "frame"}`
