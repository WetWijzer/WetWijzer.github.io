# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-3cb36ab42716edd1`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-3cb36ab42716edd1` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.999983043995`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-10-14904-7974394caef475f8, us-code-38-6101-2a5b3595efd070b4`
  evidence: `{"family_margin": -0.99916404332, "hint_id": "modal-synthesis-a452d7a8ef730ce4", "predicted_family": "frame", "priority": 0.99996639389, "sample_id": "us-code-38-6101-2a5b3595efd070b4", "target_family": "temporal", "target_probability": 3.360611e-05}`
  evidence: `{"family_margin": -0.999989545576, "hint_id": "modal-synthesis-d81c07c2d6d63639", "predicted_family": "deontic", "priority": 0.999999694101, "sample_id": "us-code-10-14904-7974394caef475f8", "target_family": "temporal", "target_probability": 3.05899e-07}`
- `program-9a30d10a5fe5ded9`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-3cb36ab42716edd1` score `0.96672`
  loss: `autoencoder_residual_cluster` = `0.859108697451`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-47-252.-c6634f17d18802f6, us-code-14-5115-dc68d6f5c123e226, us-code-15-5102-caabbe2b83465e8a`
  evidence: `{"family_margin": 0.193551317998, "hint_id": "modal-synthesis-8db99893ecd4dd23", "predicted_family": "temporal", "priority": 0.595042142978, "sample_id": "us-code-15-5102-caabbe2b83465e8a", "target_family": "temporal", "target_probability": 0.404957857022}`
  evidence: `{"family_margin": -0.999999999999, "hint_id": "modal-synthesis-9dd3ba7b4977ff94", "predicted_family": "deontic", "priority": 1.0, "sample_id": "us-code-47-252.-c6634f17d18802f6", "target_family": "conditional_normative", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.949547539428, "hint_id": "modal-synthesis-b05ab7f031c77cb7", "predicted_family": "deontic", "priority": 0.982283949374, "sample_id": "us-code-14-5115-dc68d6f5c123e226", "target_family": "conditional_normative", "target_probability": 0.017716050626}`
