# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-481729935f73954b`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-481729935f73954b` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.705035716977`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-22-127-239ab62aacc72ba4, us-code-49-47126.-2322d39a63b9ba2d`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-207eecb2dff41a7d", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-22-127-239ab62aacc72ba4", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.182896227451, "hint_id": "modal-synthesis-aed597e6d328fcc6", "predicted_family": "frame", "priority": 0.332896227451, "sample_id": "us-code-49-47126.-2322d39a63b9ba2d", "target_family": "deontic"}`
