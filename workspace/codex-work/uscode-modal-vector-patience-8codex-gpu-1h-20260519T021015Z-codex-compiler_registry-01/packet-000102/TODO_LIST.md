# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-e33f32b7dbb12e8f`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-e33f32b7dbb12e8f` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.966236554261`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-12-1816-c0b440c716f086be, us-code-20-806-b393baca996842b5, us-code-38-1720I-3410e13660f6b6a4`
  evidence: `{"family_margin": -0.848890749741, "hint_id": "modal-synthesis-62ae8a4efff7f361", "predicted_family": "temporal", "priority": 0.955521777922, "sample_id": "us-code-20-806-b393baca996842b5", "target_family": "deontic", "target_probability": 0.044478222078}`
  evidence: `{"family_margin": -0.814531998077, "hint_id": "modal-synthesis-a0d46f8461636298", "predicted_family": "frame", "priority": 0.952677707098, "sample_id": "us-code-38-1720I-3410e13660f6b6a4", "target_family": "deontic", "target_probability": 0.047322292902}`
  evidence: `{"family_margin": -0.941090534922, "hint_id": "modal-synthesis-a6a45b6964189d34", "predicted_family": "frame", "priority": 0.990510177762, "sample_id": "us-code-12-1816-c0b440c716f086be", "target_family": "deontic", "target_probability": 0.009489822238}`
