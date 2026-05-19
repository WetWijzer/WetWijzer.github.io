# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-7ebe6d569fc90257`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->epistemic","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-7ebe6d569fc90257` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.804612321983`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-3535.-739d47b019f8aeeb, us-code-7-4801-315be0aeb7c40c29, us-code-38-2102A-088b75a4bc313043`
  evidence: `{"family_margin": -0.230774719777, "hint_id": "modal-synthesis-0cdac334515214ac", "predicted_family": "deontic", "priority": 0.380774719777, "sample_id": "us-code-38-2102A-088b75a4bc313043", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999908583756, "hint_id": "modal-synthesis-36b00cb4cba16cf7", "predicted_family": "frame", "priority": 1.149908583756, "sample_id": "us-code-42-3535.-739d47b019f8aeeb", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.733153662417, "hint_id": "modal-synthesis-6dc8183cdc524ff8", "predicted_family": "deontic", "priority": 0.883153662417, "sample_id": "us-code-7-4801-315be0aeb7c40c29", "target_family": "epistemic"}`
