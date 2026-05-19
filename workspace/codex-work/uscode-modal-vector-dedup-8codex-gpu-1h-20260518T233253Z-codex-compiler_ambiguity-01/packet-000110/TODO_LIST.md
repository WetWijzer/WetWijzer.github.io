# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-4465e97a7bc481c1`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-4465e97a7bc481c1` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.72412301319`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-25-967b-414b28c838c6ad8b, us-code-43-156.-f144163c12efb2fc`
  evidence: `{"family_margin": -0.413068740844, "hint_id": "modal-synthesis-928afb8c95b7a93b", "predicted_family": "frame", "priority": 0.563068740844, "sample_id": "us-code-43-156.-f144163c12efb2fc", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.735177285536, "hint_id": "modal-synthesis-981baa85d313c145", "predicted_family": "frame", "priority": 0.885177285536, "sample_id": "us-code-25-967b-414b28c838c6ad8b", "target_family": "conditional_normative"}`
