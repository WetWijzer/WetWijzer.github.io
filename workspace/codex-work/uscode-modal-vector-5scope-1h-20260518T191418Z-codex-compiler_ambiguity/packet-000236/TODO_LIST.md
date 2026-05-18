# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-139849e64ce59278`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["hybrid->frame","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-139849e64ce59278` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.708344868036`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-34-11294-0a6981caa505e06b, us-code-16-831r-67ffc5b229e2bd75, us-code-29-1662-e7516434dca445ba`
  evidence: `{"family_margin": -0.216733561973, "hint_id": "modal-synthesis-a05880749cc9422c", "predicted_family": "hybrid", "priority": 0.366733561973, "sample_id": "us-code-29-1662-e7516434dca445ba", "target_family": "frame"}`
  evidence: `{"family_margin": -0.99962738107, "hint_id": "modal-synthesis-b6f7b3b94418499b", "predicted_family": "temporal", "priority": 1.14962738107, "sample_id": "us-code-34-11294-0a6981caa505e06b", "target_family": "frame"}`
  evidence: `{"family_margin": -0.458673661066, "hint_id": "modal-synthesis-ef4b906f91f18367", "predicted_family": "temporal", "priority": 0.608673661066, "sample_id": "us-code-16-831r-67ffc5b229e2bd75", "target_family": "frame"}`
