# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-9c31480099dd7c97`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","frame->deontic","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-9c31480099dd7c97` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.462776048854`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-12604.-1d234db6b2b96dae, us-code-16-5201-032991f8a1d37d4e, us-code-5-2904-6a34aeff644bc118, us-code-20-6432-cef881b033466057`
  evidence: `{"family_margin": -0.983862874993, "hint_id": "modal-synthesis-23c6ed547aaee99e", "predicted_family": "frame", "priority": 1.133862874993, "sample_id": "us-code-42-12604.-1d234db6b2b96dae", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.271151104314, "hint_id": "modal-synthesis-38e84b324fb1c499", "predicted_family": "deontic", "priority": 0.421151104314, "sample_id": "us-code-16-5201-032991f8a1d37d4e", "target_family": "frame"}`
  evidence: `{"family_margin": -0.135415317285, "hint_id": "modal-synthesis-befff9633973ddad", "predicted_family": "frame", "priority": 0.285415317285, "sample_id": "us-code-5-2904-6a34aeff644bc118", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.139325101176, "hint_id": "modal-synthesis-c45e97d0e92335d6", "predicted_family": "temporal", "priority": 0.010674898824, "sample_id": "us-code-20-6432-cef881b033466057", "target_family": "temporal"}`
