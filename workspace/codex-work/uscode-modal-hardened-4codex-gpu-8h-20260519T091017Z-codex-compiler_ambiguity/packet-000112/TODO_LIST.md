# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-1937bd928d032b2c`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-1937bd928d032b2c` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.647817879079`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-50-855.-6b18aaa5a6c9cf83, us-code-43-326.-5500eb218f8a7886, us-code-22-4071k-55a17ec8c5e3db3e, us-code-50-3305.-3e025318340f6f2a`
  evidence: `{"family_margin": -0.376889143959, "hint_id": "modal-synthesis-6f507a1e50335586", "predicted_family": "frame", "priority": 0.526889143959, "sample_id": "us-code-22-4071k-55a17ec8c5e3db3e", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.992896805877, "hint_id": "modal-synthesis-d5361f2945534ff0", "predicted_family": "frame", "priority": 1.142896805877, "sample_id": "us-code-50-855.-6b18aaa5a6c9cf83", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.436671018642, "hint_id": "modal-synthesis-e3f2c2dfc7954fc4", "predicted_family": "temporal", "priority": 0.586671018642, "sample_id": "us-code-43-326.-5500eb218f8a7886", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.18481454784, "hint_id": "modal-synthesis-f9daf67597897bdd", "predicted_family": "frame", "priority": 0.33481454784, "sample_id": "us-code-50-3305.-3e025318340f6f2a", "target_family": "temporal"}`
