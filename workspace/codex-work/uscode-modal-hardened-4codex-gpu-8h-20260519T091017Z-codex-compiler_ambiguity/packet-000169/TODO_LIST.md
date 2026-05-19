# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `2`

## TODOs
- `program-a8a34ccf7fb6a9f8`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["epistemic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a8a34ccf7fb6a9f8` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.794412401092`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-862-40c2d7c8f9a77d41, us-code-42-248a.-9261c2a788f1cbcf, us-code-16-1311-014f0ec1c47a5cce`
  evidence: `{"family_margin": -0.960878504821, "hint_id": "modal-synthesis-0de2caade2d5d32c", "predicted_family": "frame", "priority": 1.110878504821, "sample_id": "us-code-42-248a.-9261c2a788f1cbcf", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-1408b661ad18c091", "predicted_family": "epistemic", "priority": 0.15, "sample_id": "us-code-16-1311-014f0ec1c47a5cce", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.972358698454, "hint_id": "modal-synthesis-709cd9561bdb31c0", "predicted_family": "frame", "priority": 1.122358698454, "sample_id": "us-code-10-862-40c2d7c8f9a77d41", "target_family": "temporal"}`
- `program-0e5164c7b779355f`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-a8a34ccf7fb6a9f8` score `0.988814`
  loss: `autoencoder_residual_cluster` = `0.433389405105`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-15-1847-830b651eb663dca8, us-code-34-12404-4c3ffacca50adfcf, us-code-7-7424-e7673f78fca9418a`
  evidence: `{"family_margin": -0.676448880695, "hint_id": "modal-synthesis-2df2b72b28134769", "predicted_family": "deontic", "priority": 0.826448880695, "sample_id": "us-code-15-1847-830b651eb663dca8", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-60b0932527fe5590", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-7-7424-e7673f78fca9418a", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.17371933462, "hint_id": "modal-synthesis-fed884f3607428a0", "predicted_family": "frame", "priority": 0.32371933462, "sample_id": "us-code-34-12404-4c3ffacca50adfcf", "target_family": "temporal"}`
