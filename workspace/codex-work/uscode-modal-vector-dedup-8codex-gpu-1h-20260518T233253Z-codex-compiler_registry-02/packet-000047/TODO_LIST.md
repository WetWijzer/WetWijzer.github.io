# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-a1795f58ad6c8d01`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-a1795f58ad6c8d01` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.881665238298`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-25-967b-414b28c838c6ad8b, us-code-43-156.-f144163c12efb2fc`
  evidence: `{"family_margin": -0.735177285536, "hint_id": "modal-synthesis-9e0bc3d7af9addbd", "predicted_family": "frame", "priority": 0.918078633988, "sample_id": "us-code-25-967b-414b28c838c6ad8b", "target_family": "conditional_normative", "target_probability": 0.081921366012}`
  evidence: `{"family_margin": -0.413068740844, "hint_id": "modal-synthesis-e1fa69c7a47a62ea", "predicted_family": "frame", "priority": 0.845251842609, "sample_id": "us-code-43-156.-f144163c12efb2fc", "target_family": "temporal", "target_probability": 0.154748157391}`
