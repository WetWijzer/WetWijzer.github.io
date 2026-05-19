# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-b8890f82aa6570e1`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->epistemic","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-b8890f82aa6570e1` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.952979533175`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-3535.-739d47b019f8aeeb, us-code-7-4801-315be0aeb7c40c29, us-code-38-2102A-088b75a4bc313043`
  evidence: `{"family_margin": -0.999908583756, "hint_id": "modal-synthesis-40f38af8ccc63076", "predicted_family": "frame", "priority": 0.999999999939, "sample_id": "us-code-42-3535.-739d47b019f8aeeb", "target_family": "temporal", "target_probability": 6.1e-11}`
  evidence: `{"family_margin": -0.733153662417, "hint_id": "modal-synthesis-81af78dee67c97e2", "predicted_family": "deontic", "priority": 0.974325959474, "sample_id": "us-code-7-4801-315be0aeb7c40c29", "target_family": "epistemic", "target_probability": 0.025674040526}`
  evidence: `{"family_margin": -0.230774719777, "hint_id": "modal-synthesis-bab8fde237229906", "predicted_family": "deontic", "priority": 0.884612640111, "sample_id": "us-code-38-2102A-088b75a4bc313043", "target_family": "temporal", "target_probability": 0.115387359889}`
