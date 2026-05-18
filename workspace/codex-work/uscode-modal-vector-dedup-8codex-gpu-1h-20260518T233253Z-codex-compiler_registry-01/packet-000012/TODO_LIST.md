# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-9725683f62b1cfab`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-9725683f62b1cfab` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.737959344105`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-22-127-239ab62aacc72ba4, us-code-49-47126.-2322d39a63b9ba2d, us-code-12-639-a6faf86b06383bb9`
  evidence: `{"family_margin": -0.182896227451, "hint_id": "modal-synthesis-a175fb8e874e6b50", "predicted_family": "frame", "priority": 0.718066547666, "sample_id": "us-code-49-47126.-2322d39a63b9ba2d", "target_family": "deontic", "target_probability": 0.281933452334}`
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-eb7b1a9b69b398fd", "predicted_family": "deontic", "priority": 0.50390312837, "sample_id": "us-code-12-639-a6faf86b06383bb9", "target_family": "deontic", "target_probability": 0.49609687163}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-ee015ca86c492a99", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-22-127-239ab62aacc72ba4", "target_family": "temporal", "target_probability": 0.008091643722}`
