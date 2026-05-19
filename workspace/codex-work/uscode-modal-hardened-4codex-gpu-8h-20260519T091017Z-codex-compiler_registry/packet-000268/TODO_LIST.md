# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-b01fbaf4d0b6d092`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-b01fbaf4d0b6d092` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.882686596656`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-22-1354-6747db394be7d16a, us-code-42-5844.-0a161e6c2d8d9e38, us-code-2-194b-c95de1cc8c49a0e9, us-code-20-1059b-743ed93e96671aec`
  evidence: `{"family_margin": -0.970679750509, "hint_id": "modal-synthesis-0f2d7102b6ed3a3d", "predicted_family": "frame", "priority": 0.996421931426, "sample_id": "us-code-22-1354-6747db394be7d16a", "target_family": "temporal", "target_probability": 0.003578068574}`
  evidence: `{"family_margin": -0.921643636648, "hint_id": "modal-synthesis-2fd68178ef372c79", "predicted_family": "frame", "priority": 0.97154495939, "sample_id": "us-code-42-5844.-0a161e6c2d8d9e38", "target_family": "deontic", "target_probability": 0.02845504061}`
  evidence: `{"family_margin": -0.785893947088, "hint_id": "modal-synthesis-60b874b27616f6bd", "predicted_family": "frame", "priority": 0.912427237685, "sample_id": "us-code-2-194b-c95de1cc8c49a0e9", "target_family": "conditional_normative", "target_probability": 0.087572762315}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-a3a932aaa805a657", "predicted_family": "temporal", "priority": 0.650352258125, "sample_id": "us-code-20-1059b-743ed93e96671aec", "target_family": "deontic", "target_probability": 0.349647741875}`
- `program-fc8e4948ae342a83`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-b01fbaf4d0b6d092` score `0.972025`
  loss: `autoencoder_residual_cluster` = `0.87349921889`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-49-14705.-ce33e074ffa4430f, us-code-43-737.-159ba480db3e5864, us-code-8-1186-866b0788007b45ad, us-code-13-184-f64c50d8f2db025c`
  evidence: `{"family_margin": -0.832441698483, "hint_id": "modal-synthesis-2da155551dbc495b", "predicted_family": "frame", "priority": 0.943149448469, "sample_id": "us-code-8-1186-866b0788007b45ad", "target_family": "temporal", "target_probability": 0.056850551531}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-6f4085426babaced", "predicted_family": "temporal", "priority": 0.576518842273, "sample_id": "us-code-13-184-f64c50d8f2db025c", "target_family": "conditional_normative", "target_probability": 0.423481157727}`
  evidence: `{"family_margin": -0.628952442126, "hint_id": "modal-synthesis-9433fd925082cf45", "predicted_family": "frame", "priority": 0.982331920334, "sample_id": "us-code-43-737.-159ba480db3e5864", "target_family": "temporal", "target_probability": 0.017668079666}`
  evidence: `{"family_margin": -0.979274746583, "hint_id": "modal-synthesis-ee5d697b81d135ae", "predicted_family": "frame", "priority": 0.991996664484, "sample_id": "us-code-49-14705.-ce33e074ffa4430f", "target_family": "temporal", "target_probability": 0.008003335516}`
