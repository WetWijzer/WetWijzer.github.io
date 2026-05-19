# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-bee48d56be4ae3cd`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->conditional_normative","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bee48d56be4ae3cd` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.751250691698`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-6853-8c49fca60b12f72e, us-code-36-240106-acd9ba631c2f3033, us-code-48-870.-e8be30bad4b69fe8`
  evidence: `{"family_margin": -0.648572010426, "hint_id": "modal-synthesis-5f105f9d01ce5a5c", "predicted_family": "deontic", "priority": 0.898487037775, "sample_id": "us-code-16-6853-8c49fca60b12f72e", "target_family": "temporal", "target_probability": 0.101512962225}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-9ca28924f4db69e1", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-48-870.-e8be30bad4b69fe8", "target_family": "frame", "target_probability": 0.470915888067}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-f284c4a1382f5f89", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-36-240106-acd9ba631c2f3033", "target_family": "conditional_normative", "target_probability": 0.173819074614}`
